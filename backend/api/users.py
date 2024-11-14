# api/users.py
from quart import Blueprint, request, jsonify
import bcrypt
from db import users_collection
from api.utils import jwt_role_required
from pymongo.errors import DuplicateKeyError

users_bleuprint = Blueprint('users', __name__)

# Define async function to insert admin user if not exists
async def insert_admin_user(admin_username: str, admin_password: str):
    existing_admin = await users_collection.find_one({"username": admin_username})
    if not existing_admin:
        try:
            hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
            await users_collection.insert_one({
                "username": admin_username,
                "password": hashed_password,
                "role": "admin"
            })
            print("Admin user created.")
        except DuplicateKeyError:
            print("Admin user already exists.")
        except Exception as e:
            print(f"An error occurred while inserting the admin user: {e}")
    else:
        print("Admin user already exists, skipping creation.")

@users_bleuprint.route("/api/users", methods=["POST"])
@jwt_role_required(["admin"])
async def create_user():
    """
    Create a new user with the provided username, password, and role.
    This function expects a JSON payload with the following fields:
    - username: The username of the new user (required).
    - password: The password of the new user (required).
    - role: The role of the new user (optional, defaults to "user").
    Returns:
        201: A JSON response with a success message if the user is created successfully.
        400: A JSON response with an error message if the username or password is missing.
    """


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

@users_bleuprint.route("/api/users", methods=["GET"])
@jwt_role_required(["admin"])
async def get_users():
    """
    Retrieve a list of all users in the database.
    This function queries the users collection in the database and returns a JSON response
    with a list of all users and their roles.
    Returns:
        200: A JSON response with a list of users and their roles.
    """

    users = []
    async for user in users_collection.find():
        users.append({
            "username": user["username"],
            "role": user.get("role", "user")
        })

    return jsonify({"users": users}), 200

@users_bleuprint.route("/api/users", methods=["DELETE"])
@jwt_role_required(["admin"])
async def delete_user():
    """
    Delete a user with the provided username.
    This function expects a JSON payload with the following field:
    - username: The username of the user to delete (required).
    Returns:
        200: A JSON response with a success message if the user is deleted successfully.
        400: A JSON response with an error message if the username is missing
    """

    data = await request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"msg": "Username is required"}), 400

    await users_collection.delete_one({"username": username})
    return jsonify({"msg": f"User '{username}' deleted successfully"}), 200

@users_bleuprint.route("/api/users", methods=["PUT"])
@jwt_role_required(["admin"])
async def update_user():
    """
    Update a user's password and/or role.
    This function expects a JSON payload with the following fields:
    - username: The username of the user to update (required).
    - password: The new password for the user (optional).
    - role: The new role for the user (optional).
    Returns:
        200: A JSON response with a success message if the user is updated successfully.
        400: A JSON response with an error message if the username is missing
    """

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