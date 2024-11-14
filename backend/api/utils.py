# api/utils.py
from db import users_collection, api_keys_collection
import hashlib
from functools import wraps
from quart import jsonify, request
from quart_jwt_extended import (
    verify_jwt_in_request, get_jwt_claims, exceptions as jwt_exceptions, jwt_required
)
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
    hashed_key = hashlib.sha256(api_key.encode('utf-8')).hexdigest()
    
    key_record = await api_keys_collection.find_one({
        "status": "active",
        "api_key": hashed_key
    })
    
    if key_record:
        expires_at = key_record["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) > expires_at:
            return {"expired": True, "expires_at": expires_at}

        user = await users_collection.find_one({"_id": key_record["user_id"]})
        return {"user": user}

    return None

def jwt_or_api_key_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            # Try to verify JWT
            try:
                await verify_jwt_in_request()
                # If JWT is valid, get the claims
                claims = get_jwt_claims()
                role = claims.get("role")
                if role not in allowed_roles:
                    return jsonify({"msg": "Access denied"}), 403
                # Proceed with the request
                return await fn(*args, **kwargs)
            except jwt_exceptions.NoAuthorizationError:
                # No JWT found, check for API key
                api_key = request.headers.get("X-API-Key")
                if not api_key:
                    return jsonify({"msg": "Authorization required"}), 401

                # Validate the API key
                validation_result = await validate_api_key(api_key)
                if not validation_result:
                    return jsonify({"msg": "Invalid or revoked API key"}), 403

                # Check if the key is expired
                if validation_result.get("expired"):
                    expires_at = validation_result["expires_at"].astimezone(belgium_tz).strftime("%Y-%m-%d %H:%M:%S")
                    return jsonify({"msg": f"API key expired on {expires_at}"}), 403

                # Get the user's role from the validation result
                user = validation_result["user"]
                role = user.get("role")
                if role not in allowed_roles:
                    return jsonify({"msg": "Access denied"}), 403

                # Optionally, set the user in the request context
                request.current_user = user

                # Proceed with the request if the API key is valid
                return await fn(*args, **kwargs)
            except jwt_exceptions.JWTDecodeError:
                # JWT is present but invalid
                return jsonify({"msg": "Invalid JWT token"}), 401
            except Exception as e:
                # Other exceptions
                return jsonify({"msg": str(e)}), 400

        return wrapper
    return decorator