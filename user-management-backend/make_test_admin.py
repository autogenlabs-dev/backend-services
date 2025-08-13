import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def make_test_admin():
    try:
        client = AsyncIOMotorClient(settings.database_url)
        db = client.user_management_db
        
        # Update the test admin user to admin role
        result = await db.users.update_one(
            {'email': 'admin@test.com'},
            {'$set': {'role': 'admin'}}
        )
        
        print(f'Updated {result.modified_count} user to admin role')
        
        client.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(make_test_admin())
