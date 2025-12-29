#!/usr/bin/env python3
"""
Check which MongoDB is being used on the live server and inspect password hashing
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from app.config import Settings
from typing import cast, Any

async def check_mongodb_sources():
    """Check both potential MongoDB sources"""
    print("\n" + "="*80)
    print("🔍 CHECKING LIVE MONGODB SOURCES")
    print("="*80)
    
    # Get settings from .env
    settings = Settings()
    print(f"\n📋 Current Settings:")
    print(f"   DATABASE_URL from config: {settings.database_url}")
    print(f"   Environment: {settings.environment}")
    
    # Check environment variable
    env_db_url = os.environ.get("DATABASE_URL", "Not set in environment")
    print(f"\n🌍 Environment Variables:")
    print(f"   DATABASE_URL: {env_db_url}")
    
    # Test connections to different MongoDB sources
    sources_to_test = [
        ("Docker Container MongoDB", "mongodb://mongodb:27017/user_management_db"),
        ("Localhost MongoDB", "mongodb://localhost:27017/user_management_db"),
        ("Settings Config", settings.database_url),
    ]
    
    print(f"\n{'='*80}")
    print("🧪 TESTING MONGODB CONNECTIONS")
    print(f"{'='*80}")
    
    for name, db_url in sources_to_test:
        print(f"\n📡 Testing: {name}")
        print(f"   URL: {db_url}")
        
        try:
            client = AsyncIOMotorClient(db_url, serverSelectionTimeoutMS=5000)
            database = client.get_database()
            
            # Try to ping
            await database.command('ping')
            print(f"   ✅ Connection successful!")
            
            # Initialize Beanie
            await init_beanie(
                database=cast(Any, database),
                document_models=[User]
            )
            
            # Count users
            user_count = await User.count()
            print(f"   📊 Users found: {user_count}")
            
            # List users
            if user_count > 0:
                users = await User.find_all().to_list()
                print(f"   👥 User emails:")
                for user in users:
                    print(f"      • {user.email} ({user.role})")
                    
                # Check first user's password hash format
                if users:
                    first_user = users[0]
                    if first_user.password_hash:
                        hash_len = len(first_user.password_hash)
                        print(f"\n   🔐 Password Hash Analysis:")
                        print(f"      Length: {hash_len} characters")
                        print(f"      Format: {first_user.password_hash[:20]}...")
                        
                        # Detect hash type
                        if hash_len == 64:
                            print(f"      Type: ✅ SHA-256 (64 chars) - CORRECT")
                        elif hash_len == 60 and first_user.password_hash.startswith('$2b$'):
                            print(f"      Type: ⚠️  BCRYPT (60 chars) - MISMATCH!")
                            print(f"      ❌ This is causing the 'Invalid salt' error!")
                        else:
                            print(f"      Type: ❓ Unknown format")
            else:
                print(f"   ⚠️  No users in this database")
            
            client.close()
            print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
        except Exception as e:
            print(f"   ❌ Connection failed: {str(e)[:100]}")
            print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    print(f"\n{'='*80}")
    print("📝 DIAGNOSIS")
    print(f"{'='*80}")
    print("""
    The 'Invalid salt' error occurs when:
    
    1. ❌ Password hashes are stored in BCRYPT format ($2b$...)
    2. ✅ But authentication code expects SHA-256 (64-char hex)
    
    Solutions:
    • If wrong database: Point to correct MongoDB
    • If wrong format: Re-run reset_live_db.py to recreate users with SHA-256
    """)

if __name__ == "__main__":
    asyncio.run(check_mongodb_sources())
