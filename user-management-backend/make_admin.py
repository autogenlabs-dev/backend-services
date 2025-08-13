import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def make_user_admin():
    try:
        client = AsyncIOMotorClient(settings.database_url)
        db = client.user_management_db
        
        # Update the user role to admin
        result = await db.user.update_one(
            {'email': 'admin@test.com'},
            {'$set': {'role': 'admin'}}
        )
        
        print('Updated user to admin role')
        print(f'Modified count: {result.modified_count}')
        
        # Verify the update
        user = await db.user.find_one({'email': 'admin@test.com'})
        if user:
            print(f'User role is now: {user.get("role", "not set")}')
        
        client.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(make_user_admin())
