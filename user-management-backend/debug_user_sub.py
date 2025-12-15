
import asyncio
import os
from datetime import datetime, timezone
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.user import User

async def check_user():
    # Connect to DB
    client = AsyncIOMotorClient("mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin")
    await init_beanie(database=client.get_default_database(), document_models=[User])

    # Find user
    users = await User.find({"$or": [{"email": {"$regex": "abhishek", "$options": "i"}}, {"name": {"$regex": "abhishek", "$options": "i"}}]}).to_list()
    
    print(f"Found {len(users)} users.")
    for user in users:
        print(f"User: {user.name} ({user.email})")
        print(f"Subscription: {user.subscription}")
        print(f"End Date: {user.subscription_end_date}")
        
        days_left = 0
        if user.subscription_end_date:
            now = datetime.now(timezone.utc)
            # Ensure aware datetime
            if user.subscription_end_date.tzinfo is None:
                 user.subscription_end_date = user.subscription_end_date.replace(tzinfo=timezone.utc)
            
            print(f"Now: {now}")
            print(f"End Date (Aware): {user.subscription_end_date}")
            
            if user.subscription_end_date > now:
                delta = user.subscription_end_date - now
                days_left = delta.days
        
        print(f"Calculated Days Left: {days_left}")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(check_user())
