# db.py
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_USER = os.getenv("MONGO_USER", "root")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "examplepassword")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")

client = AsyncIOMotorClient(f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/")
db = client['klopta-db']

# Define collections
users_collection = db['users']
api_keys_collection = db['api_keys']

async def create_indexes():
    await users_collection.create_index("username", unique=True)
    await api_keys_collection.create_index([("user_id", 1), ("name", 1)], unique=True)