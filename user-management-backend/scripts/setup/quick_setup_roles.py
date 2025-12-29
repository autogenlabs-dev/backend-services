#!/usr/bin/env python3
"""
Quick Role Account Setup

Creates test accounts for all 4 roles with simple credentials.
Perfect for development and testing.
"""

import asyncio
from create_role_accounts import create_sample_accounts, list_users_by_role

async def quick_setup():
    """Quick setup with predefined accounts"""
    
    print("🚀 Quick Role Account Setup")
    print("=" * 50)
    print("Creating test accounts for all roles...")
    print()
    
    # Create sample accounts
    await create_sample_accounts()
    
    print("🔍 Listing all users...")
    print()
    
    # List all users
    await list_users_by_role()
    
    print("🎉 Quick setup complete!")
    print()
    print("🔗 Test your roles at: http://localhost:8000/docs")
    print()
    print("💡 Use these credentials to test different role access:")
    print("   👤 USER:       user@codemurf.com / userpass123")
    print("   💻 DEVELOPER:  developer@codemurf.com / devpass123") 
    print("   🛡️ ADMIN:      admin@codemurf.com / adminpass123")
    print("   👑 SUPERADMIN: superadmin@codemurf.com / superpass123")

if __name__ == "__main__":
    asyncio.run(quick_setup())