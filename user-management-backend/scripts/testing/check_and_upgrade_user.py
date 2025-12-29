from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def check_users():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['user_management']
    
    count = await db.users.count_documents({})
    print(f"\nTotal users: {count}\n")
    
    users = await db.users.find().limit(10).to_list(10)
    for u in users:
        print(f"Email: {u.get('email'):<40} Role: {u.get('role', 'user'):<10} ID: {u.get('_id')}")
    
    # Find our test user
    test_user = await db.users.find_one({'email': 'dev@example.com'})
    if test_user:
        print(f"\nFound dev@example.com:")
        print(f"  ID: {test_user['_id']}")
        print(f"  Role: {test_user.get('role', 'user')}")
        
        # Upgrade to developer
        result = await db.users.update_one(
            {'_id': test_user['_id']},
            {'$set': {'role': 'developer'}}
        )
        print(f"  Updated: {result.modified_count} document(s)")
        
        # Verify
        updated = await db.users.find_one({'_id': test_user['_id']})
        print(f"  New role: {updated.get('role')}")
    else:
        print("\ndev@example.com not found!")
    
    client.close()

asyncio.run(check_users())
