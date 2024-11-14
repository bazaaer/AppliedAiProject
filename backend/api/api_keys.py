# api/api_keys.py
from quart import Blueprint, request, jsonify
from quart_jwt_extended import get_jwt_identity
import hashlib
import secrets
from db import users_collection, api_keys_collection
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

    user = await users_collection.find_one({"username": username})
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Get the API key name from the request JSON
    data = await request.get_json()
    try:
        key_name = data.get("name")
    except AttributeError:
        key_name = None
    
    if not key_name:
        return jsonify({"msg": "API key name is required"}), 400

    # Check if an API key with the same name already exists for this user
    existing_key = await api_keys_collection.find_one({
        "user_id": user["_id"],
        "name": key_name
    })
    if existing_key:
        return jsonify({"msg": "An API key with this name already exists"}), 400

    # Generate a new API key
    new_api_key = secrets.token_hex(32)
    hashed_key = hashlib.sha256(new_api_key.encode('utf-8')).hexdigest()

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=60)

    # Store the API key with the given name, expiration date, and other details
    await api_keys_collection.insert_one({
        "user_id": user["_id"],
        "username": username,
        "name": key_name,
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
        expires_at = key_record["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        is_expired = datetime.now(timezone.utc) > expires_at
        api_key_list.append({
            "name": key_record["name"],
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
    api_key_name = data.get("name")

    if not api_key_name:
        return jsonify({"msg": "API Key name is required"}), 400

    username = get_jwt_identity()

    # Find the API key by name and username
    api_key_record = await api_keys_collection.find_one({"username": username, "name": api_key_name})
    if not api_key_record:
        return jsonify({"msg": "API key not found"}), 404

    # Update the status of the API key to "revoked"
    await api_keys_collection.update_one(
        {"_id": api_key_record["_id"]},
        {"$set": {"status": "revoked"}}
    )

    return jsonify({"msg": "API key successfully revoked"}), 200