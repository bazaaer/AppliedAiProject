# api/users.py
from quart import Blueprint, request, jsonify
import bcrypt
from db import users_collection
from api.utils import jwt_role_required

users_bleuprint = Blueprint('users', __name__)

async def insert_user(username: str, password: str, role: str):
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        # Attempt to find and update the user, or insert if not found
        result = await users_collection.find_one_and_update(
            {"username": username},
            {
                "$setOnInsert": {
                    "username": username,
                    "password": hashed_password.decode('utf-8'),
                    "role": role
                }
            },
            upsert=True,
            return_document=False  # Ensures None is returned for insertion
        )
        
        # Check if a new user was created
        if result is None:
            print(f"{username} user created.")
        else:
            print(f"{username} user already exists.")
    except Exception as e:
        print(f"An error occurred while inserting the {username} user: {e}")

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