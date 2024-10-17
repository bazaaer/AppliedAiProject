import datetime
import bcrypt
import jwt
from flask import Blueprint, request, jsonify, current_app
from pymongo import MongoClient
from functools import wraps
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_USER = os.getenv("MONGO_USER", "root")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "examplepassword")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminpassword")

# MongoDB setup
client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/")
db = client.your_database_name
users_collection = db.users

# Insert admin user if not exists
if not users_collection.find_one({"username": ADMIN_USERNAME}):
    hashed_password = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({"username": ADMIN_USERNAME, "password": hashed_password, "role": "admin"})

# Auth Blueprint
auth_blueprint = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users_collection.find_one({"username": data["username"]})
            if not current_user:
                raise ValueError('User not found')
        except Exception as e:
            return jsonify({'message': f'Token is invalid: {str(e)}'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@auth_blueprint.route('/create_user', methods=['POST'])
@token_required
def create_user(current_user):
    if current_user.get("role") != "admin":
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if users_collection.find_one({"username": username}):
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({"username": username, "password": hashed_password})

    return jsonify({'message': 'User created successfully'}), 201

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = users_collection.find_one({"username": username})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'message': 'Invalid username or password'}), 401

    token = jwt.encode({
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token}), 200

@auth_blueprint.route('/protected', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({'message': f'Welcome {current_user["username"]}, this is a protected route!'}), 200
