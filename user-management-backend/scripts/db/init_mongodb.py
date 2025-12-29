#!/usr/bin/env python3
"""
MongoDB Database Initialization Script
Creates necessary collections and indexes for the user management system.
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.user import User
from app.models.organization import Organization
from app.config import settings

async def init_database():
    """Initialize MongoDB database with collections and indexes."""
    
    print("🔄 Initializing MongoDB database...")
    print(f"📡 Connecting to: {settings.database_url}")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.database_url)
    db = client.user_management_db
    
    try:
        # Test connection first
        server_info = await client.server_info()
        print(f"✅ Connected to MongoDB {server_info['version']}")
        
        # Initialize Beanie with document models
        await init_beanie(database=db, document_models=[User, Organization])
        print("✅ Beanie initialized successfully")
          # Create indexes
        print("🔧 Creating indexes...")
        try:
            await User.create_indexes()
            print("   ✅ User indexes created")
        except Exception as e:
            print(f"   ⚠️  User indexes: {e}")
        
        try:
            await Organization.create_indexes()
            print("   ✅ Organization indexes created")
        except Exception as e:
            print(f"   ⚠️  Organization indexes: {e}")
        
        print("✅ Database indexes creation completed")
        
        # List collections
        collections = await db.list_collection_names()
        print(f"📁 Collections: {collections}")
        
        # Collection stats
        for collection_name in collections:
            count = await db[collection_name].count_documents({})
            print(f"   📊 {collection_name}: {count} documents")
            
        print("\n🎉 Database initialization completed successfully!")
        return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    finally:
        client.close()
        print("🔌 Database connection closed")

async def create_test_user():
    """Create a test user for authentication testing."""
    
    print("\n🧪 Creating test user...")
    
    client = AsyncIOMotorClient(settings.database_url)
    db = client.user_management_db
    
    try:
        await init_beanie(database=db, document_models=[User, Organization])
        
        # Check if test user already exists
        existing_user = await User.find_one(User.email == "test@vscode.com")
        if existing_user:
            print("⚠️  Test user already exists")
            print(f"   📧 Email: {existing_user.email}")
            print(f"   🆔 ID: {existing_user.id}")
            return existing_user
        
        # Create test user
        from app.utils.password import hash_password
        
        test_user = User(
            email="test@vscode.com",
            password_hash=hash_password("securepassword123"),
            name="Test User",
            full_name="Test User for VS Code",
            subscription="free",
            tokens_remaining=10000,
            tokens_used=0,
            monthly_limit=10000,
            is_active=True,
            role="user"
        )
        
        await test_user.create()
        print("✅ Test user created successfully")
        print(f"   📧 Email: {test_user.email}")
        print(f"   🆔 ID: {test_user.id}")
        print(f"   🔑 Password: securepassword123")
        
        return test_user
        
    except Exception as e:
        print(f"❌ Test user creation failed: {e}")
        return None
    
    finally:
        client.close()

if __name__ == "__main__":
    print("🚀 Starting MongoDB setup...")
    
    # Initialize database
    success = asyncio.run(init_database())
    
    if success:
        # Create test user
        asyncio.run(create_test_user())
        print("\n✅ Setup completed! You can now run authentication tests.")
    else:
        print("\n❌ Setup failed! Please check your MongoDB connection.")
