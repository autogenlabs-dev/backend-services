import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from app.models.api_key_pool import ApiKeyPool

async def assign_glm_key():
    client = AsyncIOMotorClient("mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin")
    await init_beanie(database=client.get_default_database(), document_models=[User, ApiKeyPool])
    
    # Find the Ultra user
    user = await User.find_one({"email": "abhishek.r@cisinlabs.com"})
    if not user:
        print("User not found")
        return
    
    print(f"Found user: {user.name} ({user.email})")
    print(f"Current GLM key: {user.glm_api_key}")
    
    if user.glm_api_key:
        print("User already has GLM key assigned.")
        return
    
    # Find an available GLM key with capacity
    glm_pool = await ApiKeyPool.find({"key_type": "glm", "is_active": True}).to_list()
    print(f"Found {len(glm_pool)} GLM keys in pool")
    
    for key in glm_pool:
        current_users = len(key.assigned_user_ids) if key.assigned_user_ids else 0
        print(f"Key: {key.label} - {current_users}/{key.max_users} users")
        if current_users < key.max_users:
            print(f"Assigning key: {key.label}")
            
            # Add user to key pool
            if not key.assigned_user_ids:
                key.assigned_user_ids = []
            key.assigned_user_ids.append(str(user.id))
            key.updated_at = datetime.now(timezone.utc)
            await key.save()
            
            # Set user's glm_api_key
            user.glm_api_key = key.key_value
            await user.save()
            
            print(f"SUCCESS: Assigned GLM key to {user.email}")
            print(f"Key: {key.key_value[:20]}...")
            return
    
    print("ERROR: No GLM keys with available capacity found.")

if __name__ == "__main__":
    asyncio.run(assign_glm_key())
