import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def make_admin():
    try:
        client = AsyncIOMotorClient(settings.database_url)
        db = client.user_management_db
        
        # Update the first user to admin role
        result = await db.users.update_one(
            {'email': 'autogencodelabs@gmail.com'},
            {'$set': {'role': 'admin'}}
        )
        
        print(f'Updated {result.modified_count} user to admin role')
        
        # Verify
        user = await db.users.find_one({'email': 'autogencodelabs@gmail.com'})
        if user:
            role = user.get('role', 'N/A')
            print(f'User role is now: {role}')
        
        client.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(make_admin())
