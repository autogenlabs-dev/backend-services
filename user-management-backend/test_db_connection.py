#!/usr/bin/env python3
"""
Test script to check MongoDB connection
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        # Get DATABASE_URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False
            
        print(f"🔗 Connecting to: {database_url}")
        
        # Create MongoDB client
        client = AsyncIOMotorClient(database_url)
        
        # Test connection by pinging the server
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Get database name from URL or use default
        if "/user_management_db" in database_url:
            db_name = "user_management_db"
        else:
            # Extract database name from URL
            db_name = database_url.split("/")[-1].split("?")[0] if "/" in database_url else "user_management_db"
        
        db = client[db_name]
        print(f"📁 Using database: {db_name}")
        
        # List collections to verify database access
        collections = await db.list_collection_names()
        print(f"📋 Collections in database: {collections if collections else 'No collections found'}")
        
        # Test basic operations
        test_collection = db.test_connection
        
        # Insert a test document
        test_doc = {"test": True, "message": "Connection test successful"}
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Read the test document
        found_doc = await test_collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print(f"✅ Test document retrieved: {found_doc}")
        
        # Clean up - delete the test document
        await test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test document cleaned up")
        
        # Close the connection
        client.close()
        print("✅ Database connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        return False

async def test_redis_connection():
    """Test Redis connection"""
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        print(f"🔗 Connecting to Redis: {redis_url}")
        
        redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Test Redis connection
        redis_client.ping()
        print("✅ Redis connection successful!")
        
        # Test basic operations
        redis_client.set("test_key", "test_value")
        value = redis_client.get("test_key")
        print(f"✅ Redis test operation successful: {value}")
        
        # Clean up
        redis_client.delete("test_key")
        print("🧹 Redis test key cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting database connection tests...\n")
    
    # Test MongoDB
    print("=" * 50)
    print("TESTING MONGODB CONNECTION")
    print("=" * 50)
    mongodb_success = await test_mongodb_connection()
    
    print("\n" + "=" * 50)
    print("TESTING REDIS CONNECTION")
    print("=" * 50)
    redis_success = test_redis_connection()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"MongoDB: {'✅ Success' if mongodb_success else '❌ Failed'}")
    print(f"Redis: {'✅ Success' if redis_success else '❌ Failed'}")
    
    if mongodb_success and redis_success:
        print("\n🎉 All database connections are working correctly!")
    else:
        print("\n⚠️ Some database connections failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
