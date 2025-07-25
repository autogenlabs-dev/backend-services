import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def check_users():
    """Check how many users are in the database"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.database_url)
        db = client.user_management_db
        
        print("🔍 Checking users in database...")
        print(f"📊 Database: {db.name}")
        
        # Get users collection
        users_collection = db.users
        
        # Count total users
        total_users = await users_collection.count_documents({})
        print(f"👥 Total users: {total_users}")
        
        if total_users > 0:
            # Get some sample users (first 5)
            print("\n📋 Sample users:")
            async for user in users_collection.find({}).limit(5):
                user_info = {
                    "id": str(user.get("_id", "N/A")),
                    "email": user.get("email", "N/A"),
                    "username": user.get("username", "N/A"),
                    "role": user.get("role", "N/A"),
                    "is_verified": user.get("is_verified", False),
                    "created_at": user.get("created_at", "N/A")
                }
                print(f"  • {user_info}")
            
            if total_users > 5:
                print(f"  ... and {total_users - 5} more users")
        
        # Get users by role if role field exists
        print("\n📊 Users by role:")
        pipeline = [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        async for role_count in users_collection.aggregate(pipeline):
            role = role_count.get("_id", "Unknown")
            count = role_count.get("count", 0)
            print(f"  • {role}: {count} users")
        
        # Check verification status
        verified_count = await users_collection.count_documents({"is_verified": True})
        unverified_count = await users_collection.count_documents({"is_verified": False})
        
        print(f"\n✅ Verified users: {verified_count}")
        print(f"❌ Unverified users: {unverified_count}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error checking users: {e}")

if __name__ == "__main__":
    asyncio.run(check_users())
