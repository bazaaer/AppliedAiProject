# config.py
import os
from datetime import timedelta
import redis

# Define expiration time for access tokens
ACCESS_EXPIRES = timedelta(days=7)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

# Define Redis store for revoked tokens
revoked_store = redis.StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
)

llm_cache_store = redis.StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True 
)

REDIS_CACHE_TTL = 3600

# Load admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "pwd")
