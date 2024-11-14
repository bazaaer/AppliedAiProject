# api/api_keys.py
from quart import Blueprint, request, jsonify
from quart_jwt_extended import get_jwt_identity
import bcrypt
import secrets
from db import users_collection, api_keys_collection
from bson import ObjectId
from api.utils import jwt_role_required
from datetime import datetime, timezone, timedelta
import pytz
belgium_tz = pytz.timezone("Europe/Brussels")

api_keys_blueprint = Blueprint('api_keys', __name__)

@api_keys_blueprint.route("/api/api_keys", methods=["POST"])
@jwt_role_required(["admin", "user"])
async def generate_api_key():
    """
    Generates a new API key for the authenticated user.
    This function retrieves the username from the JWT token, verifies the user exists in the database,
    generates a new API key, hashes it, and stores it in the database with an expiration date and other details.
    Returns:
        Response: JSON response containing the new API key and HTTP status code.
    Raises:
        400: If the username is not provided.
        404: If the user is not found in the database.
    """
    username = get_jwt_identity()

    if not username:
        return jsonify({"msg": "Username is required"}), 400

    # Find the user in the database
    user = await users_collection.find_one({"username": username})
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Generate a new API key
    new_api_key = secrets.token_hex(32)
    hashed_key = bcrypt.hashpw(new_api_key.encode('utf-8'), bcrypt.gensalt())

    # Calculate expiration date (one year from creation date)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=60)

    # Store the hashed API key with expiration date and other details
    await api_keys_collection.insert_one({
        "user_id": user["_id"],
        "username": username,
        "api_key": hashed_key,
        "created_at": datetime.now(timezone.utc),
        "expires_at": expires_at,
        "status": "active",
        "visible_key_part": new_api_key[-4:]
    })

    return jsonify({"api_key": new_api_key}), 200

@api_keys_blueprint.route("/api/api_keys", methods=["GET"])
@jwt_role_required(["admin", "user"])
async def list_api_keys():
    """
    Lists all API keys associated with the authenticated user.
    This function retrieves the username from the JWT token, fetches all API keys from the database
    associated with that username, and prepares the API keys for display.
    Returns:
        Response: JSON response containing the list of API keys and HTTP status code
    """
    username = get_jwt_identity()

    # Fetch user's API keys from the api_keys collection
    api_keys = await api_keys_collection.find({"username": username}).to_list(length=None)

    # Prepare the API keys for display
    api_key_list = []
    for key_record in api_keys:
        # Ensure both datetimes are timezone-aware
        expires_at = key_record["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        is_expired = datetime.now(timezone.utc) > expires_at
        api_key_list.append({
            "api_key_id": str(key_record["_id"]),
            "visible_key": "..." + key_record["visible_key_part"],
            "created_at": key_record["created_at"].astimezone(belgium_tz).strftime("%Y-%m-%d %H:%M:%S"),
            "expires_at": expires_at.astimezone(belgium_tz).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "expired" if is_expired else key_record["status"]
        })

    return jsonify({"api_keys": api_key_list}), 200


@api_keys_blueprint.route("/api/api_keys", methods=["DELETE"])
@jwt_role_required(["admin", "user"])
async def revoke_api_key():
    """
    Revokes an API key based on the provided API key ID.
    This function retrieves the API key ID from the request data, verifies the format of the ID,
    fetches the API key from the database, and updates its status to "revoked" if the authenticated
    user is the owner of the API key.
    Returns:
        Response: JSON response indicating the success or failure of the operation and HTTP status code.
    Raises:
        400: If the API key ID is not provided or is in an invalid format.
        404: If the API key is not found in the database.
        403: If the authenticated user is not authorized to revoke the API key.
    """

    data = await request.get_json()
    api_key_id = data.get("api_key_id")

    if not api_key_id:
        return jsonify({"msg": "API Key ID is required"}), 400

    try:
        # Convert the api_key_id to ObjectId
        api_key_object_id = ObjectId(api_key_id)
    except Exception:
        return jsonify({"msg": "Invalid API Key ID format"}), 400

    # Find the API key in the database
    api_key_record = await api_keys_collection.find_one({"_id": api_key_object_id})
    if not api_key_record:
        return jsonify({"msg": "API key not found"}), 404

    username = get_jwt_identity()

    if api_key_record['username'] != username:
        return jsonify({"msg": "You are not authorized to revoke this API key"}), 403

    # Update the status of the API key to "revoked"
    await api_keys_collection.update_one(
        {"_id": api_key_object_id},
        {"$set": {"status": "revoked"}}
    )

    return jsonify({"msg": "API key successfully revoked"}), 200