"""Delete all templates from MongoDB."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin"

async def delete_templates():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.user_management_db
    result = await db.templates.delete_many({})
    print(f"Deleted {result.deleted_count} templates")
    client.close()

if __name__ == "__main__":
    asyncio.run(delete_templates())
