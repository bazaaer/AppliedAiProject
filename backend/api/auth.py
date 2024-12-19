# api/auth.py
from quart import Blueprint, request, jsonify
from quart_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    get_raw_jwt,
    get_jwt_claims
)
import bcrypt
from config import ACCESS_EXPIRES, revoked_store
from db import users_collection
from api.utils import jwt_role_required
import pytz
from datetime import timedelta
belgium_tz = pytz.timezone("Europe/Brussels")

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/api/login', methods=['POST'])
async def login():
    """
    Handle user login by validating credentials and generating an API token.
    This asynchronous function retrieves JSON data from the request, extracts the username and password,
    and validates them against the stored user data in the database. If the credentials are valid, an
    API token is generated and returned in the response.
    Returns:
        Response: A JSON response containing the API token if login is successful, or an error message
        if the credentials are invalid or missing.
    Raises:
        400: If the username or password is not provided in the request.
        401: If the username or password is incorrect.
    """

    data = await request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'msg': 'Username and password are required'}), 400

    user = await users_collection.find_one({"username": username})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'msg': 'Invalid username or password'}), 401

    role = user.get("role", "user")
    user_claims = {
        "role": role,
    }

    if role != "demo":
        api_token = create_access_token(
            identity=username,
            user_claims=user_claims
        )
    else:
        api_token = create_access_token(
            identity=username,
            user_claims=user_claims,
            expires_delta=timedelta(minutes=60),
        )

    return jsonify({'token': api_token, "role": role}), 200

@auth_blueprint.route("/api/logout", methods=["POST"])
@jwt_role_required(["admin", "user"])
async def logout():
    """
    Handle user logout by revoking the API token.
    This asynchronous function retrieves the JWT token identifier (jti) from the request and stores it in the
    revoked token store to invalidate the token.
    Returns:
        Response: A JSON response indicating the token was successfully revoked.
    """

    jti = get_raw_jwt()["jti"]
    revoked_store.set(jti, "true", ACCESS_EXPIRES * 1.2)
    return jsonify({"msg": "Token successfully revoked"}), 200

@auth_blueprint.route("/api/protected", methods=["GET"])
@jwt_role_required(["admin", "user", "demo"])
async def protected():
    """
    Protected route that requires a valid API token.
    This asynchronous function retrieves the current user from the JWT token and returns a welcome message.
    Returns:
        Response: A JSON response with a welcome message containing the current user's username
    """

    current_user = get_jwt_identity()
    claims = get_jwt_claims()
    role = claims.get("role")
    return jsonify({'msg': f"welcome: {current_user}", "role": role}), 200