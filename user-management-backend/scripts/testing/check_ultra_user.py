import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User

async def check_user():
    client = AsyncIOMotorClient("mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin")
    await init_beanie(database=client.get_default_database(), document_models=[User])
    
    # Find the Ultra user
    user = await User.find_one({"email": "abhishek.r@cisinlabs.com"})
    if not user:
        print("User not found")
        return
    
    print(f"User: {user.name} ({user.email})")
    print(f"Subscription: {user.subscription}")
    print(f"Subscription End Date: {user.subscription_end_date}")
    print(f"OpenRouter Key: {user.openrouter_api_key[:20] if user.openrouter_api_key else 'None'}...")
    print(f"GLM Key: {user.glm_api_key[:20] if user.glm_api_key else 'None'}...")
    print(f"Bytez Key: {user.bytez_api_key[:20] if user.bytez_api_key else 'None'}...")
    
    # Calculate days left
    if user.subscription_end_date:
        now = datetime.now(timezone.utc)
        end = user.subscription_end_date
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        if end > now:
            days_left = (end - now).days
            print(f"Days Left: {days_left}")
        else:
            print("Subscription EXPIRED")
    else:
        print("No subscription end date set")

if __name__ == "__main__":
    asyncio.run(check_user())
