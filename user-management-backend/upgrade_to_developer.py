# Run this to upgrade user to developer
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def upgrade():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['user_management']
    result = await db.users.update_one(
        {'email': 'dev@example.com'},
        {'$set': {'role': 'developer'}}
    )
    print(f'Updated {result.modified_count} user(s)')
    user = await db.users.find_one({'email': 'dev@example.com'})
    print(f'Role is now: {user.get("role", "user")}')
    client.close()

asyncio.run(upgrade())
