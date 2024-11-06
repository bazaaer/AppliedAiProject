# api/auth.py
from app import ACCESS_EXPIRES
from quart import Blueprint, request, jsonify
from quart_jwt_extended import (
    jwt_required,
    create_access_token,
    get_jwt_identity,
    get_jwt_claims,
    get_raw_jwt
)
import bcrypt
import os
from dotenv import load_dotenv

from db import users_collection

import redis

revoked_store = redis.StrictRedis(
    host="KL-redis", port=6379, db=0, decode_responses=True
)

load_dotenv()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "pwd")

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

auth_blueprint = Blueprint('auth', __name__)



@auth_blueprint.route('/api/get_api_key', methods=['POST'])
async def login():
    data = await request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'msg': 'Username and password are required'}), 400

    # Retrieve user and validate password
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

@auth_blueprint.route("/api/create_user", methods=["POST"])
@jwt_required
async def create_user():
    claims = get_jwt_claims()

    # Check if the current user has admin role
    if claims.get("role") != "admin":
        return jsonify({"msg": "Admins only!"}), 403

    # Get data from request
    data = await request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")  # Default to 'user' role if not specified

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert new user into the database
    await users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "role": role
    })

    return jsonify({"msg": f"User '{username}' with role '{role}' created successfully"}), 201

@auth_blueprint.route("/api/protected", methods=["GET"])
@jwt_required
async def protected():
    current_user = get_jwt_identity()
    return jsonify({'msg': f"welcome: {current_user}"}), 200

@auth_blueprint.route("/api/revoke_api_key", methods=["DELETE"])
@jwt_required
async def logout():
    jti = get_raw_jwt()["jti"]
    revoked_store.set(jti, "true", ACCESS_EXPIRES * 1.2)
    return jsonify({"msg": "API key successfully revoked"}), 200
