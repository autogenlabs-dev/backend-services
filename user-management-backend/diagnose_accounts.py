#!/usr/bin/env python3
"""
Diagnose why the created accounts are not working
Checks:
1. Database connection
2. User records exist
3. Password hashing matches
4. Account status (is_active, etc.)
"""
import asyncio
import hashlib
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from app.config import Settings
from typing import cast, Any

settings = Settings()

def hash_password(password: str) -> str:
    """Hash password using SHA-256 - same as reset script"""
    return hashlib.sha256(password.encode()).hexdigest()

async def diagnose():
    """Diagnose account issues"""
    print("\n" + "="*80)
    print("🔍 ACCOUNT DIAGNOSTICS")
    print("="*80)
    
    # Connect to database
    print("\n1️⃣ Testing Database Connection...")
    try:
        client = AsyncIOMotorClient(settings.database_url)
        database = client.get_database()
        await database.command('ping')
        print(f"✅ Connected to: {settings.database_url}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Initialize Beanie
    print("\n2️⃣ Initializing Beanie...")
    try:
        await init_beanie(
            database=cast(Any, database),
            document_models=[User]
        )
        print("✅ Beanie initialized")
    except Exception as e:
        print(f"❌ Beanie initialization failed: {e}")
        return
    
    # Check created accounts
    print("\n3️⃣ Checking Created Accounts...")
    test_accounts = [
        {"email": "superadmin@codemurf.com", "password": "SuperAdmin2025!@#", "expected_role": "superadmin"},
        {"email": "admin@codemurf.com", "password": "Admin2025!@#", "expected_role": "admin"},
        {"email": "dev1@codemurf.com", "password": "Dev1Pass2025!", "expected_role": "developer"},
        {"email": "dev2@codemurf.com", "password": "Dev2Pass2025!", "expected_role": "developer"},
    ]
    
    for idx, account in enumerate(test_accounts, 1):
        print(f"\n{'─'*80}")
        print(f"Account {idx}: {account['email']}")
        print(f"{'─'*80}")
        
        try:
            user = await User.find_one(User.email == account['email'])
            
            if not user:
                print(f"❌ User NOT FOUND in database")
                continue
            
            print(f"✅ User EXISTS in database")
            print(f"   📧 Email: {user.email}")
            print(f"   👤 Name: {user.name}")
            print(f"   🎭 Role: {user.role}")
            print(f"   🔓 Active: {user.is_active}")
            print(f"   🎟️  Tokens: {user.tokens_remaining}")
            
            # Check role
            if str(user.role) == account['expected_role']:
                print(f"   ✅ Role matches: {user.role}")
            else:
                print(f"   ⚠️  Role mismatch! Expected: {account['expected_role']}, Got: {user.role}")
            
            # Check password hash
            expected_hash = hash_password(account['password'])
            if user.password_hash == expected_hash:
                print(f"   ✅ Password hash matches")
                print(f"   🔑 Hash: {user.password_hash[:20]}...")
            else:
                print(f"   ❌ Password hash MISMATCH!")
                print(f"   Expected: {expected_hash[:20]}...")
                print(f"   Got:      {user.password_hash[:20] if user.password_hash else 'None'}...")
            
            # Check is_active
            if user.is_active:
                print(f"   ✅ Account is active")
            else:
                print(f"   ❌ Account is INACTIVE")
            
            # Check if password_hash is set
            if user.password_hash:
                print(f"   ✅ Password hash is set")
            else:
                print(f"   ❌ Password hash is MISSING")
                
        except Exception as e:
            print(f"❌ Error checking user: {e}")
    
    # Count total users
    print(f"\n{'='*80}")
    print("4️⃣ Database Summary")
    print(f"{'='*80}")
    try:
        total_users = await User.count()
        print(f"📊 Total users in database: {total_users}")
        
        # List all users
        all_users = await User.find_all().to_list()
        print(f"\n👥 All Users:")
        for user in all_users:
            print(f"   • {user.email} ({user.role}) - Active: {user.is_active}")
            
    except Exception as e:
        print(f"❌ Error counting users: {e}")
    
    # Check authentication method
    print(f"\n{'='*80}")
    print("5️⃣ Authentication Method Check")
    print(f"{'='*80}")
    print(f"🔐 Password hashing method: SHA-256")
    print(f"📝 Expected hash for 'SuperAdmin2025!@#':")
    print(f"   {hash_password('SuperAdmin2025!@#')}")
    
    client.close()
    
    print(f"\n{'='*80}")
    print("✅ DIAGNOSTICS COMPLETE")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    asyncio.run(diagnose())
