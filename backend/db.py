# db.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_USER = os.getenv("MONGO_USER", "root")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "examplepassword")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")

client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/")
db = client['klopta-db']

users_collection = db['users']
token_blacklist_collection = db['token_blacklist']

# Create indexes
token_blacklist_collection.create_index('jti', unique=True)
token_blacklist_collection.create_index('exp', expireAfterSeconds=0)
