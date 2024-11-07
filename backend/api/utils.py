# api/utils.py
from db import users_collection, api_keys_collection
import bcrypt
from functools import wraps
from quart import jsonify, request
from quart_jwt_extended import jwt_required, get_jwt_claims
from datetime import datetime, timezone
import pytz
belgium_tz = pytz.timezone("Europe/Brussels")

def jwt_role_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required
        async def wrapper(*args, **kwargs):
            claims = get_jwt_claims()
            role = claims.get("role")

            if role not in allowed_roles:
                return jsonify({"msg": "Access denied"}), 403
            
            return await fn(*args, **kwargs)
        return wrapper
    return decorator

async def validate_api_key(api_key):
    # Search for an active API key in the api_keys collection
    async for key_record in api_keys_collection.find({"status": "active"}):
        if bcrypt.checkpw(api_key.encode('utf-8'), key_record["api_key"]):
            # Ensure expires_at is timezone-aware
            expires_at = key_record["expires_at"]
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            # Check if the API key has expired
            if datetime.now(timezone.utc) > expires_at:
                return {"expired": True, "expires_at": expires_at}

            # If the key is valid and not expired, retrieve and return the user
            user = await users_collection.find_one({"_id": key_record["user_id"]})
            return {"user": user}
    
    # If no valid key is found, return None
    return None

def api_key_required(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify({"msg": "API key required"}), 401

        # Validate the API key
        validation_result = await validate_api_key(api_key)
        if not validation_result:
            return jsonify({"msg": "Invalid or revoked API key"}), 403

        # Check if the key is expired
        if validation_result.get("expired"):
            expires_at = validation_result["expires_at"].astimezone(belgium_tz).strftime("%Y-%m-%d %H:%M:%S")
            return jsonify({"msg": f"API key expired on {expires_at}"}), 403

        # Proceed with the request if the API key is valid
        return await fn(*args, **kwargs)

    return wrapper