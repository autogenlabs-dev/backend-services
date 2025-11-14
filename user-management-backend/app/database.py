from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

# MongoDB setup
client = AsyncIOMotorClient(settings.database_url)
db = client.user_management_db # This will be the database name from the URL or a default

def get_db_client():
    """Dependency to get MongoDB client"""
    return client

def get_database():
    """Dependency to get MongoDB database"""
    return db

# Redis setup (assuming it remains the same)
import redis
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

def get_redis():
    """Dependency to get Redis client"""
    return redis_client
