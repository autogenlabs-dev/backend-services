#!/usr/bin/env python3
"""
Get existing user credentials for login testing
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def get_user_credentials():
    """Get existing user credentials from database"""
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.database_url)
        db = client.user_management_db
        users_collection = db.users
        
        print("🔍 Available User Credentials:")
        print("=" * 50)
        
        # Get all users
        async for user in users_collection.find({}):
            email = user.get('email', 'N/A')
            role = user.get('role', 'N/A')
            created = user.get('created_at', 'N/A')
            user_id = str(user.get('_id', 'N/A'))
            
            print(f"📧 Email: {email}")
            print(f"👤 Role: {role}")
            print(f"🆔 ID: {user_id}")
            print(f"📅 Created: {created}")
            print(f"🔑 Password: (hashed - use test password if you created it)")
            print("-" * 30)
        
        print("\n💡 Login Instructions:")
        print("For testing, use these credentials:")
        print("📧 Email: abhishek1234@gmail.com")
        print("🔑 Password: (original password used when created)")
        print("\nOr for test users:")
        print("📧 Email: testuser_TIMESTAMP@example.com")
        print("🔑 Password: TestPassword123!")
        
        print("\n🌐 Working Endpoints:")
        print("• Registration: POST http://localhost:8000/auth/register")
        print("• Login: POST http://localhost:8000/auth/login-json")
        print("• User Info: GET http://localhost:8000/auth/me")
        print("• User Profile: GET http://localhost:8000/users/me")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error getting user credentials: {e}")

if __name__ == "__main__":
    asyncio.run(get_user_credentials())
