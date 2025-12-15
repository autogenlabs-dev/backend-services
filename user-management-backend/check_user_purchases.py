import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from app.models.item_purchase import ItemPurchase

async def check_purchases():
    client = AsyncIOMotorClient("mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin")
    await init_beanie(database=client.get_default_database(), document_models=[User, ItemPurchase])
    
    # Find the Ultra user
    user = await User.find_one({"email": "abhishek.r@cisinlabs.com"})
    if not user:
        print("User not found")
        return
    
    print(f"User: {user.name} ({user.email})")
    print(f"Subscription: {user.subscription}")
    
    # Check purchases
    purchases = await ItemPurchase.find({"user_id": user.id}).to_list()
    print(f"\nTotal purchases in database: {len(purchases)}")
    
    completed = [p for p in purchases if p.status == "completed"]
    print(f"Completed purchases: {len(completed)}")
    
    if completed:
        for p in completed:
            print(f"  - {p.item_title} ({p.item_type}) - ₹{p.paid_amount_inr}")
    else:
        print("\n✗ No completed purchases found")
        print("  → Ultra plan provides API access, NOT marketplace items")
        print("  → Templates/Components must be purchased separately from the marketplace")

if __name__ == "__main__":
    asyncio.run(check_purchases())
