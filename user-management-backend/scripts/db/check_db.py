import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def check_database():
    try:
        client = AsyncIOMotorClient(settings.database_url)
        db = client.user_management_db
        
        # List all collections
        collections = await db.list_collection_names()
        print(f'Collections in database: {collections}')
        
        # Check user collection specifically
        if 'user' in collections:
            user_count = await db.user.count_documents({})
            print(f'User collection has {user_count} documents')
            
            # Sample user document
            sample_user = await db.user.find_one({})
            if sample_user:
                email = sample_user.get('email', 'N/A')
                role = sample_user.get('role', 'N/A')
                print(f'Sample user: {email} - {role}')
        
        client.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_database())
