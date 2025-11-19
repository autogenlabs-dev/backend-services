"""
Migration script to merge developer role into user role
This script updates all users with 'developer' role to 'user' role
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def migrate_developer_to_user():
    """Migrate all developer users to user role"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.database_name]
        users_collection = db.users
        
        # Find all users with developer role
        developer_users = await users_collection.count_documents({"role": "developer"})
        print(f"Found {developer_users} users with developer role")
        
        if developer_users == 0:
            print("No developer users found to migrate")
            return
        
        # Update all developer users to user role
        result = await users_collection.update_many(
            {"role": "developer"},
            {"$set": {"role": "user"}}
        )
        
        print(f"Successfully migrated {result.modified_count} developer users to user role")
        
        # Verify migration
        remaining_developers = await users_collection.count_documents({"role": "developer"})
        print(f"Remaining developer users: {remaining_developers}")
        
        # Show updated user counts
        user_count = await users_collection.count_documents({"role": "user"})
        admin_count = await users_collection.count_documents({"role": "admin"})
        superadmin_count = await users_collection.count_documents({"role": "superadmin"})
        
        print("\nUpdated role distribution:")
        print(f"  Users: {user_count}")
        print(f"  Admins: {admin_count}")
        print(f"  Superadmins: {superadmin_count}")
        
        client.close()
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        raise

if __name__ == "__main__":
    print("Starting developer to user role migration...")
    asyncio.run(migrate_developer_to_user())
    print("\nMigration complete!")
