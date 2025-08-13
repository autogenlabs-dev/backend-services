import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def check_users():
    try:
        client = AsyncIOMotorClient(settings.database_url)
        db = client.user_management_db
        
        # Find all users
        users = await db.user.find({}).to_list(length=10)
        
        print(f'Found {len(users)} users:')
        for user in users:
            email = user.get('email', 'N/A')
            role = user.get('role', 'N/A')
            print(f'  Email: {email}, Role: {role}')
        
        client.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_users())
