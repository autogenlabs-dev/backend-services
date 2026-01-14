import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.models.api_key_pool import ApiKeyPool
from beanie import init_beanie

async def seed_keys():
    client = AsyncIOMotorClient(settings.database_url)
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[ApiKeyPool])
    
    # Check if exists
    existing = await ApiKeyPool.find(ApiKeyPool.key_type == "glm").count()
    if existing == 0:
        print("Seeding test GLM key...")
        key = ApiKeyPool(
            key_type="glm",
            key_value="glm-test-key-1234567890abcdef",
            label="Test GLM Key 1",
            is_active=True,
            max_users=100
        )
        await key.save()
        print("Key added successfully.")
    else:
        print("Keys already exist.")

if __name__ == "__main__":
    asyncio.run(seed_keys())
