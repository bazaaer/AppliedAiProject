# api/auth.py
from quart import Blueprint, request, jsonify
from quart_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    get_raw_jwt
)
import bcrypt
import secrets
from config import ACCESS_EXPIRES, revoked_store, ADMIN_USERNAME, ADMIN_PASSWORD
from db import users_collection, api_keys_collection
from bson import ObjectId
from api.utils import jwt_role_required
from datetime import datetime, timezone, timedelta
import pytz
belgium_tz = pytz.timezone("Europe/Brussels")

auth_blueprint = Blueprint('auth', __name__)

# Define async function to insert admin user if not exists
async def insert_admin_user():
    existing_admin = await users_collection.find_one({"username": ADMIN_USERNAME})
    if not existing_admin:
        hashed_password = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())
        await users_collection.insert_one({
            "username": ADMIN_USERNAME,
            "password": hashed_password,
            "role": "admin"
        })

@auth_blueprint.route('/api/login', methods=['POST'])
async def login():
    data = await request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'msg': 'Username and password are required'}), 400

    user = await users_collection.find_one({"username": username})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'msg': 'Invalid username or password'}), 401

    user_claims = {
        "role": user.get("role", "user"),
    }
    api_token = create_access_token(
        identity=username,
        user_claims=user_claims
    )

    return jsonify({'api_key': api_token}), 200

@auth_blueprint.route("/api/users", methods=["POST"])
@jwt_role_required(["admin"])
async def create_user():
    data = await request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    await users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "role": role
    })

    return jsonify({"msg": f"User '{username}' with role '{role}' created successfully"}), 201

@auth_blueprint.route("/api/users", methods=["GET"])
@jwt_role_required(["admin"])
async def get_users():
    users = []
    async for user in users_collection.find():
        users.append({
            "username": user["username"],
            "role": user.get("role", "user")
        })

    return jsonify({"users": users}), 200

@auth_blueprint.route("/api/users", methods=["DELETE"])
@jwt_role_required(["admin"])
async def delete_user():
    data = await request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"msg": "Username is required"}), 400

    await users_collection.delete_one({"username": username})
    return jsonify({"msg": f"User '{username}' deleted successfully"}), 200

@auth_blueprint.route("/api/users", methods=["PUT"])
@jwt_role_required(["admin"])
async def update_user():
    data = await request.get_json()
    username = data.get("username")
    new_password = data.get("password")
    new_role = data.get("role", "user")

    if not username:
        return jsonify({"msg": "Username is required"}), 400

    response = ""

    if new_password:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        await users_collection.update_one({"username": username}, {"$set": {"password": hashed_password}})
        response += "Password updated successfully. "
    if new_role:
        await users_collection.update_one({"username": username}, {"$set": {"role": new_role}})
        response += "Role updated successfully."
    
    return jsonify({"msg": f"User '{username}' updated successfully {response}"}), 200

@auth_blueprint.route("/api/api_keys", methods=["POST"])
@jwt_role_required(["admin", "user"])
async def generate_api_key():
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

@auth_blueprint.route("/api/api_keys", methods=["GET"])
@jwt_role_required(["admin", "user"])
async def list_api_keys():
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


@auth_blueprint.route("/api/api_keys", methods=["DELETE"])
@jwt_role_required(["admin", "user"])
async def revoke_api_key():
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

@auth_blueprint.route("/api/logout", methods=["DELETE"])
@jwt_role_required(["admin", "user"])
async def logout():
    jti = get_raw_jwt()["jti"]
    revoked_store.set(jti, "true", ACCESS_EXPIRES * 1.2)
    return jsonify({"msg": "Token successfully revoked"}), 200

@auth_blueprint.route("/api/protected", methods=["GET"])
@jwt_role_required(["admin", "user"])
async def protected():
    current_user = get_jwt_identity()
    return jsonify({'msg': f"welcome: {current_user}"}), 200