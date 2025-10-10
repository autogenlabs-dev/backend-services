#!/usr/bin/env python3
"""
Live Database Reset & Account Creation

This script CLEARS the live production database and creates essential accounts.
⚠️  WARNING: This will DELETE ALL DATA in the production database!

Usage:
    python3 reset_live_db.py --confirm

Required accounts to create:
- 1 SuperAdmin
- 1 Admin  
- 2 Developers
"""

import asyncio
import argparse
import hashlib
import sys
from datetime import datetime, UTC
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User, UserRole
from app.config import Settings
from typing import cast, Any

# Load settings (will use production .env)
settings = Settings()

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

async def clear_database():
    """⚠️ DANGER: Clear ALL collections in the database"""
    
    print("🚨 CLEARING LIVE DATABASE...")
    print("=" * 60)
    
    # Connect to database
    client = AsyncIOMotorClient(settings.database_url)
    db_name = settings.database_url.split('/')[-1].split('?')[0]
    db = client[db_name]
    
    try:
        # Get all collections
        collections = await db.list_collection_names()
        
        print(f"📍 Database: {db_name}")
        print(f"🗂️  Found {len(collections)} collections:")
        for collection in collections:
            print(f"   - {collection}")
        print()
        
        # Clear each collection
        for collection_name in collections:
            collection = db[collection_name]
            result = await collection.delete_many({})
            print(f"🗑️  Cleared {collection_name}: {result.deleted_count} documents")
        
        print()
        print("✅ Database cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        raise e
    finally:
        client.close()

async def create_production_accounts():
    """Create essential accounts for production"""
    
    print("🏭 CREATING PRODUCTION ACCOUNTS...")
    print("=" * 60)
    
    # Production accounts with strong passwords
    accounts = [
        {
            "email": "superadmin@codemurf.com",
            "password": "SuperAdmin2025!@#",  # Strong password
            "role": UserRole.SUPERADMIN,
            "name": "System SuperAdmin"
        },
        {
            "email": "admin@codemurf.com", 
            "password": "Admin2025!@#",     # Strong password
            "role": UserRole.ADMIN,
            "name": "Platform Administrator"
        },
        {
            "email": "dev1@codemurf.com",
            "password": "Dev1Pass2025!",    # Strong password
            "role": UserRole.DEVELOPER,
            "name": "Lead Developer"
        },
        {
            "email": "dev2@codemurf.com",
            "password": "Dev2Pass2025!",    # Strong password
            "role": UserRole.DEVELOPER, 
            "name": "Senior Developer"
        }
    ]
    
    # Connect to database
    client = AsyncIOMotorClient(settings.database_url)
    # Use consistent database naming as in main app
    database = client.user_management_db
    
    try:
        # Initialize Beanie (cast to satisfy type checker)
        await init_beanie(database=cast(Any, database), document_models=[User])
        
        created_accounts = []
        
        for account in accounts:
            # Create user
            user = User(
                email=account["email"],
                password_hash=hash_password(account["password"]),
                name=account["name"],
                role=account["role"],
                subscription="free",
                tokens_remaining=50000,  # More tokens for production
                tokens_used=0,
                monthly_limit=50000,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                is_active=True
            )
            
            # Save user
            await user.insert()
            
            emoji = {
                "superadmin": "👑",
                "admin": "🛡️",
                "developer": "💻"
            }
            
            print(f"✅ Created {emoji[account['role'].value]} {account['role'].value.upper()}:")
            print(f"   📧 Email: {account['email']}")
            print(f"   👤 Name: {account['name']}")
            print(f"   🔑 Password: {account['password']}")
            print(f"   🎟️  Tokens: {user.tokens_remaining}")
            print()
            
            created_accounts.append(account)
        
        return created_accounts
        
    except Exception as e:
        print(f"❌ Error creating accounts: {e}")
        raise e
    finally:
        client.close()

async def verify_accounts():
    """Verify all accounts were created successfully"""
    
    print("🔍 VERIFYING ACCOUNTS...")
    print("=" * 60)
    
    # Connect to database
    client = AsyncIOMotorClient(settings.database_url)
    # Use consistent database naming as in main app
    database = client.user_management_db
    
    try:
        # Initialize Beanie (cast to satisfy type checker)
        await init_beanie(database=cast(Any, database), document_models=[User])
        
        # Get all users
        users = await User.find_all().to_list()
        
        print(f"📊 Total users created: {len(users)}")
        print()
        
        # Group by role
        by_role = {}
        for user in users:
            role = user.role.value
            if role not in by_role:
                by_role[role] = []
            by_role[role].append(user)
        
        # Display by role
        emoji_map = {
            "superadmin": "👑",
            "admin": "🛡️", 
            "developer": "💻",
            "user": "👤"
        }
        
        for role, users_in_role in by_role.items():
            emoji = emoji_map.get(role, "❓")
            print(f"{emoji} {role.upper()} ({len(users_in_role)} accounts):")
            
            for user in users_in_role:
                status = "🟢" if user.is_active else "🔴"
                print(f"   {status} {user.email} - {user.name}")
            print()
        
        return len(users)
        
    except Exception as e:
        print(f"❌ Error verifying accounts: {e}")
        raise e
    finally:
        client.close()

def print_connection_info():
    """Print database connection information"""
    
    print("🔗 DATABASE CONNECTION INFO:")
    print("=" * 60)
    
    # Parse database URL safely
    db_url = settings.database_url
    
    if "mongodb+srv://" in db_url:
        print("🌐 Type: MongoDB Atlas (Cloud)")
        
        # Extract database name
        if '/' in db_url:
            db_name = db_url.split('/')[-1].split('?')[0]
            print(f"📍 Database: {db_name}")
        
        # Check if it contains production indicators
        if any(keyword in db_url.lower() for keyword in ['prod', 'production', 'live']):
            print("🏭 Environment: PRODUCTION")
        else:
            print("🧪 Environment: Development/Staging")
            
    elif "mongodb://" in db_url:
        print("🐳 Type: MongoDB (Local/Docker)")
        print("🧪 Environment: Development")
    
    print()

def confirm_destruction():
    """Get user confirmation for database destruction"""
    
    print("⚠️  DANGER ZONE ⚠️")
    print("=" * 60)
    print("🚨 This will PERMANENTLY DELETE ALL DATA in the database!")
    print("🚨 This action CANNOT be undone!")
    print()
    print("This includes:")
    print("• All user accounts")
    print("• All templates and components") 
    print("• All usage logs and analytics")
    print("• All subscription data")
    print("• All API keys and tokens")
    print()
    
    response1 = input("Type 'DELETE ALL DATA' to confirm: ").strip()
    if response1 != "DELETE ALL DATA":
        print("❌ Confirmation failed. Aborting.")
        return False
    
    response2 = input("Are you absolutely sure? Type 'YES': ").strip()
    if response2 != "YES":
        print("❌ Final confirmation failed. Aborting.")
        return False
    
    return True

async def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description="Reset live database and create production accounts")
    parser.add_argument("--confirm", action="store_true", 
                       help="Skip interactive confirmation (use with caution)")
    parser.add_argument("--create-only", action="store_true",
                       help="Only create accounts, don't clear database")
    parser.add_argument("--verify-only", action="store_true", 
                       help="Only verify existing accounts")
    
    args = parser.parse_args()
    
    print("🏭 LIVE DATABASE RESET & ACCOUNT CREATION")
    print("=" * 80)
    print()
    
    # Show connection info
    print_connection_info()
    
    if args.verify_only:
        # Only verify accounts
        await verify_accounts()
        return
    
    if not args.create_only:
        # Get confirmation for database clearing
        if not args.confirm:
            if not confirm_destruction():
                print("Operation cancelled by user.")
                return
        else:
            print("⚡ Running with --confirm flag (skipping interactive confirmation)")
        
        print()
        print("🚀 Starting database reset...")
        print()
        
        # Clear database
        await clear_database()
        print()
    
    # Create accounts
    accounts = await create_production_accounts()
    print()
    
    # Verify creation
    total_users = await verify_accounts()
    
    print("🎉 SETUP COMPLETE!")
    print("=" * 80)
    print()
    print("📋 PRODUCTION LOGIN CREDENTIALS:")
    print("-" * 80)
    print("👑 SUPERADMIN: superadmin@codemurf.com / SuperAdmin2025!@#")
    print("🛡️ ADMIN:      admin@codemurf.com / Admin2025!@#")
    print("💻 DEV1:       dev1@codemurf.com / Dev1Pass2025!")
    print("💻 DEV2:       dev2@codemurf.com / Dev2Pass2025!")
    print()
    print("🔒 SECURITY REMINDERS:")
    print("• Change these passwords after first login")
    print("• Enable 2FA if available")
    print("• Restrict admin access by IP if possible")
    print("• Monitor login activity regularly")
    print()
    print(f"✅ Total accounts created: {total_users}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)