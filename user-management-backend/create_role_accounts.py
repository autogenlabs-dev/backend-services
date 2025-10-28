#!/usr/bin/env python3
"""
Create User Accounts with Different Roles

This script allows you to create users with specific roles:
- USER (default)
- DEVELOPER  
- ADMIN
- SUPERADMIN

Usage:
    python3 create_role_accounts.py
    
Or use command line arguments:
    python3 create_role_accounts.py --email user@example.com --role admin --password mypassword
"""

import asyncio
import argparse
import hashlib
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User, UserRole
from app.config import Settings
from typing import cast, Any

settings = Settings()

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

async def create_user_with_role(email: str, password: str, role: UserRole, name: str | None = None):
    """Create a new user with specified role"""
    
    # Connect to database
    client = AsyncIOMotorClient(settings.database_url)
    db = client.user_management_db
    
    try:
        # Initialize Beanie (cast to satisfy type checker)
        await init_beanie(database=cast(Any, db), document_models=[User])
        
        # Check if user already exists
        existing_user = await User.find_one({"email": email})
        if existing_user:
            print(f"❌ User {email} already exists with role: {existing_user.role}")
            return None
        
        # Create new user
        user = User(
            email=email,
            password_hash=hash_password(password),
            name=name or email.split('@')[0].title(),
            role=role,
            subscription="free",
            tokens_remaining=10000,
            tokens_used=0,
            monthly_limit=10000,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )
        
        # Save user
        await user.insert()
        
        print(f"✅ Created {role.value} account:")
        print(f"   📧 Email: {email}")
        print(f"   👤 Name: {user.name}")
        print(f"   🎭 Role: {role.value}")
        print(f"   🔑 Password: {password}")
        print(f"   🎟️  Tokens: {user.tokens_remaining}")
        print()
        
        return user
        
    except Exception as e:
        print(f"❌ Error creating user {email}: {e}")
        return None
    finally:
        client.close()

async def create_sample_accounts():
    """Create sample accounts for testing"""
    
    accounts = [
        {
            "email": "user@codemurf.com",
            "password": "userpass123",
            "role": UserRole.USER,
            "name": "Regular User"
        },
        {
            "email": "developer@codemurf.com", 
            "password": "devpass123",
            "role": UserRole.DEVELOPER,
            "name": "Content Developer"
        },
        {
            "email": "admin@codemurf.com",
            "password": "adminpass123", 
            "role": UserRole.ADMIN,
            "name": "Platform Admin"
        },
        {
            "email": "superadmin@codemurf.com",
            "password": "superpass123",
            "role": UserRole.SUPERADMIN,
            "name": "System Owner"
        }
    ]
    
    print("🚀 Creating sample accounts...")
    print("=" * 60)
    
    for account in accounts:
        await create_user_with_role(
            email=account["email"],
            password=account["password"],
            role=account["role"],
            name=account["name"]
        )
    
    print("=" * 60)
    print("✅ Account creation complete!")
    print()
    print("📋 Login Credentials:")
    print("=" * 60)
    for account in accounts:
        emoji = {
            "user": "👤",
            "developer": "💻", 
            "admin": "🛡️",
            "superadmin": "👑"
        }
        print(f"{emoji[account['role'].value]} {account['role'].value.upper()}: {account['email']} / {account['password']}")

async def update_existing_user_role(email: str, new_role: UserRole):
    """Update role of existing user"""
    
    # Connect to database
    client = AsyncIOMotorClient(settings.database_url)
    db = client.user_management_db
    
    try:
        # Initialize Beanie (cast to satisfy type checker)
        await init_beanie(database=cast(Any, db), document_models=[User])
        
        # Find the user
        user = await User.find_one({"email": email})
        
        if not user:
            print(f"❌ User {email} not found!")
            return None
        
        old_role = user.role
        user.role = new_role
        user.updated_at = datetime.utcnow()
        await user.save()
        
        print(f"✅ Updated user role:")
        print(f"   📧 Email: {email}")
        print(f"   👤 Name: {user.name}")
        print(f"   🎭 Role: {old_role.value} → {new_role.value}")
        print()
        
        return user
        
    except Exception as e:
        print(f"❌ Error updating user {email}: {e}")
        return None
    finally:
        client.close()

async def list_users_by_role():
    """List all users grouped by role"""
    
    # Connect to database
    client = AsyncIOMotorClient(settings.database_url)
    db = client.user_management_db
    
    try:
        # Initialize Beanie (cast to satisfy type checker)
        await init_beanie(database=cast(Any, db), document_models=[User])
        
        print("📊 Users by Role:")
        print("=" * 60)
        
        for role in UserRole:
            users = await User.find({"role": role.value}).to_list()
            emoji = {
                "user": "👤",
                "developer": "💻",
                "admin": "🛡️", 
                "superadmin": "👑"
            }
            
            print(f"{emoji[role.value]} {role.value.upper()} ({len(users)} users):")
            
            if users:
                for user in users:
                    status = "🟢" if user.is_active else "🔴"
                    print(f"   {status} {user.email} - {user.name}")
            else:
                print("   (no users)")
            print()
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")
    finally:
        client.close()

def main():
    """Main function with command line argument support"""
    
    parser = argparse.ArgumentParser(description="Create user accounts with different roles")
    parser.add_argument("--email", help="User email address")
    parser.add_argument("--password", help="User password")
    parser.add_argument("--role", choices=["user", "developer", "admin", "superadmin"], 
                       help="User role")
    parser.add_argument("--name", help="User display name")
    parser.add_argument("--update", action="store_true", 
                       help="Update existing user role instead of creating new")
    parser.add_argument("--list", action="store_true", 
                       help="List all users by role")
    parser.add_argument("--create-samples", action="store_true",
                       help="Create sample accounts for all roles")
    
    args = parser.parse_args()
    
    if args.list:
        asyncio.run(list_users_by_role())
    elif args.create_samples:
        asyncio.run(create_sample_accounts())
    elif args.email and args.role:
        role = UserRole(args.role)
        
        if args.update:
            asyncio.run(update_existing_user_role(args.email, role))
        else:
            password = args.password or "defaultpass123"
            asyncio.run(create_user_with_role(args.email, password, role, args.name))
    else:
        print("🎭 User Account Manager")
        print("=" * 60)
        print()
        print("Available options:")
        print("1. Create sample accounts for all roles")
        print("2. List existing users by role")
        print("3. Create custom account")
        print("4. Update user role")
        print()
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == "1":
            asyncio.run(create_sample_accounts())
        elif choice == "2":
            asyncio.run(list_users_by_role())
        elif choice == "3":
            email = input("Enter email: ").strip()
            password = input("Enter password: ").strip()
            print("\nRoles: user, developer, admin, superadmin")
            role_str = input("Enter role: ").strip().lower()
            name_input = input("Enter name (optional): ").strip()
            name = name_input if name_input else None
            
            try:
                role = UserRole(role_str)
                asyncio.run(create_user_with_role(email, password, role, name))
            except ValueError:
                print("❌ Invalid role. Use: user, developer, admin, or superadmin")
        elif choice == "4":
            email = input("Enter user email: ").strip()
            print("\nRoles: user, developer, admin, superadmin")
            role_str = input("Enter new role: ").strip().lower()
            
            try:
                role = UserRole(role_str)
                asyncio.run(update_existing_user_role(email, role))
            except ValueError:
                print("❌ Invalid role. Use: user, developer, admin, or superadmin")
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()