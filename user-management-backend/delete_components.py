"""Delete all components and re-upload with fixed fields."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin"

async def delete_components():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.user_management_db
    result = await db.components.delete_many({})
    print(f"Deleted {result.deleted_count} components")
    client.close()

if __name__ == "__main__":
    asyncio.run(delete_components())
