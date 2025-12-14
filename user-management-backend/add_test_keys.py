"""
Script to add fake API keys to the key pool for testing.
Run this inside the Docker container:
docker exec -it user-management-backend-api-1 python add_test_keys.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from datetime import datetime, timezone

# Import models
import sys
sys.path.insert(0, '/app')
from app.config import settings
from app.models.api_key_pool import ApiKeyPool
from app.models.user import User

async def add_test_keys():
    """Add fake API keys to the pool for testing."""
    
    # Connect to database
    client = AsyncIOMotorClient(settings.database_url)
    database = client.get_default_database()
    
    await init_beanie(
        database=database,
        document_models=[ApiKeyPool, User]
    )
    
    print("Connected to database...")
    
    # Define fake test keys
    test_keys = [
        # GLM keys (for Pro users)
        {
            "key_type": "glm",
            "key_value": "glm-test-key-001-abcdef123456",
            "key_preview": "glm-test-key-001-***",
            "label": "Test GLM Key 1",
            "max_users": 10,
            "is_active": True,
        },
        {
            "key_type": "glm",
            "key_value": "glm-test-key-002-ghijkl789012",
            "key_preview": "glm-test-key-002-***",
            "label": "Test GLM Key 2",
            "max_users": 10,
            "is_active": True,
        },
        {
            "key_type": "glm",
            "key_value": "glm-test-key-003-mnopqr345678",
            "key_preview": "glm-test-key-003-***",
            "label": "Test GLM Key 3",
            "max_users": 10,
            "is_active": True,
        },
        # Bytez keys (for Ultra users)
        {
            "key_type": "bytez",
            "key_value": "bytez-test-key-001-stuvwx901234",
            "key_preview": "bytez-test-key-001-***",
            "label": "Test Bytez Key 1",
            "max_users": 5,
            "is_active": True,
        },
        {
            "key_type": "bytez",
            "key_value": "bytez-test-key-002-yzabcd567890",
            "key_preview": "bytez-test-key-002-***",
            "label": "Test Bytez Key 2",
            "max_users": 5,
            "is_active": True,
        },
    ]
    
    added_count = 0
    for key_data in test_keys:
        # Check if key already exists
        existing = await ApiKeyPool.find_one({"key_value": key_data["key_value"]})
        if existing:
            print(f"Key already exists: {key_data['label']}")
            continue
        
        # Create new key
        new_key = ApiKeyPool(
            key_type=key_data["key_type"],
            key_value=key_data["key_value"],
            key_preview=key_data["key_preview"],
            label=key_data["label"],
            max_users=key_data["max_users"],
            is_active=key_data["is_active"],
            assigned_user_ids=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        await new_key.insert()
        print(f"✅ Added: {key_data['label']} ({key_data['key_type']})")
        added_count += 1
    
    print(f"\n✅ Added {added_count} new test keys to the pool!")
    
    # Show current pool status
    glm_count = await ApiKeyPool.find({"key_type": "glm"}).count()
    bytez_count = await ApiKeyPool.find({"key_type": "bytez"}).count()
    print(f"\nCurrent pool status:")
    print(f"  GLM keys: {glm_count}")
    print(f"  Bytez keys: {bytez_count}")

if __name__ == "__main__":
    asyncio.run(add_test_keys())
