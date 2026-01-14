import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.models.api_key_pool import ApiKeyPool
from beanie import init_beanie

async def check_pool():
    client = AsyncIOMotorClient(settings.database_url)
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[ApiKeyPool])
    
    keys = await ApiKeyPool.find(ApiKeyPool.key_type == "glm").to_list()
    print(f"Found {len(keys)} GLM keys in pool")
    for k in keys:
        print(f"Key: {k.key_preview}, Active: {k.is_active}, Users: {len(k.assigned_user_ids) if k.assigned_user_ids else 0}/{k.max_users}")

if __name__ == "__main__":
    asyncio.run(check_pool())
