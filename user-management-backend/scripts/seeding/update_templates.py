import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def update_templates():
    client = AsyncIOMotorClient('mongodb://localhost:27017/')
    db = client['user_management_db']
    templates = db['templates']
    
    # Update all templates to Free
    result = await templates.update_many(
        {'plan_type': {'$in': ['Paid', 'Premium']}},
        {'$set': {'plan_type': 'Free'}}
    )
    
    print(f'Updated {result.modified_count} templates to Free plan')
    
    # Verify the update
    count = await templates.count_documents({'plan_type': 'Free'})
    print(f'Total Free templates now: {count}')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_templates())
