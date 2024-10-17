# extensions.py
from flask_jwt_extended import JWTManager

# Initialize JWTManager without the app
jwt = JWTManager()

# In-memory token blacklist (use persistent storage in production)
blacklist = set()
