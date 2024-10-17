# app.py
from gevent import monkey
monkey.patch_all()

from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import datetime

# Import jwt and blacklist from extensions.py
from extensions import jwt, blacklist

load_dotenv()

app = Flask(__name__)

# Securely load your secret key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'my_precious')
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']

# JWT configuration
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=15)  # Access token validity
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=7)     # Refresh token validity
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

CORS(app)

# Initialize JWTManager with the app
jwt.init_app(app)

# Register JWT callbacks after initializing jwt with the app
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in blacklist

# Optional: Customize error messages
@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({'message': 'Token has been revoked'}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'message': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'message': 'Invalid token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'message': 'Token is missing'}), 401

# Import and register blueprints
from api import auth_blueprint, api_blueprint
app.register_blueprint(auth_blueprint)
app.register_blueprint(api_blueprint)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
