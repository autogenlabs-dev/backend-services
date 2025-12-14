"""
Script to assign GLM key to Pro user who doesn't have one.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from datetime import datetime, timezone

import sys
sys.path.insert(0, '/app')
from app.config import settings
from app.models.api_key_pool import ApiKeyPool
from app.models.user import User

async def assign_glm_to_pro_users():
    """Assign GLM keys to Pro users who don't have one."""
    
    client = AsyncIOMotorClient(settings.database_url)
    database = client.get_default_database()
    
    await init_beanie(
        database=database,
        document_models=[ApiKeyPool, User]
    )
    
    print("Connected to database...")
    
    # Find Pro users without GLM key
    pro_users = await User.find({
        "subscription": "pro",
        "$or": [
            {"glm_api_key": None},
            {"glm_api_key": ""},
            {"glm_api_key": {"$exists": False}}
        ]
    }).to_list()
    
    print(f"Found {len(pro_users)} Pro users without GLM key")
    
    for user in pro_users:
        print(f"\nProcessing user: {user.email}")
        
        # Find available GLM key
        available_keys = await ApiKeyPool.find({
            "key_type": "glm",
            "is_active": True
        }).to_list()
        
        assigned = False
        for key in available_keys:
            current_users = len(key.assigned_user_ids or [])
            if current_users < key.max_users:
                # Assign this key
                if key.assigned_user_ids is None:
                    key.assigned_user_ids = []
                key.assigned_user_ids.append(user.id)
                await key.save()
                
                user.glm_api_key = key.key_value
                user.updated_at = datetime.now(timezone.utc)
                await user.save()
                
                print(f"  ✅ Assigned GLM key: {key.label} ({key.key_value[:8]}...)")
                assigned = True
                break
        
        if not assigned:
            print(f"  ❌ No available GLM key for user")
    
    print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(assign_glm_to_pro_users())
