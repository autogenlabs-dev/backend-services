#!/usr/bin/env python3
"""
Check which database the LIVE API is actually using by querying it
This will show us which MongoDB the API connects to when it runs
"""
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from typing import cast, Any

async def test_api_database():
    """Test which database the API is actually connected to"""
    print("\n" + "="*80)
    print("🔍 CHECKING WHICH DATABASE THE LIVE API IS USING")
    print("="*80)
    
    # Read the .env file that the container uses
    print("\n1️⃣ Reading Container .env Configuration...")
    try:
        with open('.env', 'r') as f:
            for line in f:
                if 'DATABASE' in line or 'MONGO' in line:
                    print(f"   {line.strip()}")
    except Exception as e:
        print(f"   ⚠️  Could not read .env: {e}")
    
    # Import settings the same way the API does
    print("\n2️⃣ Loading Settings (same as API)...")
    from app.config import Settings
    settings = Settings()
    
    api_db_url = settings.database_url
    print(f"   📍 API Database URL: {api_db_url}")
    print(f"   🌍 Environment: {settings.environment}")
    
    # Now connect to the SAME database the API uses
    print(f"\n3️⃣ Connecting to API's Database...")
    print(f"   URL: {api_db_url}")
    
    try:
        client = AsyncIOMotorClient(api_db_url, serverSelectionTimeoutMS=10000)
        database = client.get_database()
        
        # Test connection
        await database.command('ping')
        print(f"   ✅ Connected successfully!")
        
        # Get database name
        db_name = database.name
        print(f"   📂 Database Name: {db_name}")
        
        # Initialize Beanie
        await init_beanie(
            database=cast(Any, database),
            document_models=[User]
        )
        
        # Check users
        print(f"\n4️⃣ Checking Users in API's Database...")
        user_count = await User.count()
        print(f"   📊 Total users: {user_count}")
        
        users = []
        if user_count > 0:
            users = await User.find_all().to_list()
            print(f"\n   👥 User List:")
            for idx, user in enumerate(users, 1):
                hash_preview = user.password_hash[:20] if user.password_hash else "None"
                hash_len = len(user.password_hash) if user.password_hash else 0
                print(f"   {idx}. {user.email}")
                print(f"      Role: {user.role}")
                print(f"      Active: {user.is_active}")
                print(f"      Password Hash: {hash_preview}... (length: {hash_len})")
                
                # Detect hash type
                if hash_len == 64:
                    print(f"      Hash Type: ✅ SHA-256 (correct)")
                elif hash_len == 60 and user.password_hash and user.password_hash.startswith('$2b$'):
                    print(f"      Hash Type: ❌ BCRYPT (causes 'Invalid salt' error!)")
                else:
                    print(f"      Hash Type: ❓ Unknown")
                print()
        else:
            print(f"   ⚠️  No users found - database is empty!")
        
        # Check server info
        print(f"\n5️⃣ MongoDB Server Information...")
        server_info = await database.command('serverStatus')
        print(f"   🖥️  Host: {server_info.get('host', 'Unknown')}")
        print(f"   📦 Version: {server_info.get('version', 'Unknown')}")
        
        # Check if this is Atlas or local
        connection_str = api_db_url.lower()
        if 'mongodb.net' in connection_str or 'atlas' in connection_str:
            print(f"   ☁️  Type: MongoDB Atlas (Cloud)")
        elif 'localhost' in connection_str or '127.0.0.1' in connection_str:
            print(f"   💻 Type: Local MongoDB (Host)")
        elif 'mongodb:' in connection_str:
            print(f"   🐳 Type: Docker Container MongoDB")
        else:
            print(f"   ❓ Type: Unknown")
        
        client.close()
        
        print(f"\n{'='*80}")
        print("📝 CONCLUSION")
        print(f"{'='*80}")
        
        if user_count == 0:
            print("❌ API database is EMPTY!")
            print("   Solution: Run reset_docker_db.sh or reset_live_db.py")
        elif user_count == 4 and any(u.email == 'superadmin@codemurf.com' for u in users):
            print("✅ API database has the NEW accounts we created!")
            print("   If login still fails, the issue is NOT the database.")
            print("   Check:")
            print("   • Frontend API endpoint URL")
            print("   • API container is running and healthy")
            print("   • CORS settings")
            print("   • Network connectivity")
        else:
            print("⚠️  API database has DIFFERENT users than expected!")
            print("   This might be an old database or wrong MongoDB instance.")
            print("   Solution: Run reset_docker_db.sh to reset THIS database")
        
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        print(f"\n   This means the API CANNOT connect to its configured database!")
        print(f"   Check:")
        print(f"   • MongoDB container is running")
        print(f"   • Network configuration")
        print(f"   • Database URL in .env file")

if __name__ == "__main__":
    asyncio.run(test_api_database())
