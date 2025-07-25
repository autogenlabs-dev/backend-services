#!/usr/bin/env python3
"""
Test script for user registration and login
"""
import asyncio
import aiohttp
import json
from datetime import datetime

# Test server URL (adjust if your server runs on different port)
BASE_URL = "http://localhost:8000"
API_BASE = BASE_URL  # No /api prefix in this application

async def test_user_registration_and_login():
    """Test user registration and login flow"""
    
    # Test user data
    test_user = {
        "email": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    print("🚀 Starting User Registration and Login Tests")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Check if server is running
        print("🔍 Testing server connection...")
        try:
            async with session.get(f"{BASE_URL}/") as response:
                if response.status == 200:
                    print("✅ Server is running and accessible")
                else:
                    print(f"⚠️ Server responded with status: {response.status}")
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("💡 Make sure your server is running on http://localhost:8000")
            return
        
        # Test 2: List OAuth providers (optional test)
        print("\n🔍 Testing OAuth providers endpoint...")
        try:
            async with session.get(f"{API_BASE}/auth/providers") as response:
                if response.status == 200:
                    providers = await response.json()
                    print(f"✅ OAuth providers: {providers}")
                else:
                    print(f"⚠️ OAuth providers endpoint status: {response.status}")
        except Exception as e:
            print(f"⚠️ OAuth providers test failed: {e}")
        
        # Test 3: User Registration
        print(f"\n👤 Testing user registration...")
        print(f"📧 Email: {test_user['email']}")
        
        try:
            registration_data = {
                "email": test_user["email"],
                "password": test_user["password"],
                "first_name": test_user["first_name"],
                "last_name": test_user["last_name"]
            }
            
            async with session.post(
                f"{API_BASE}/auth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                response_text = await response.text()
                print(f"📊 Registration response status: {response.status}")
                
                if response.status == 200:
                    user_data = await response.json()
                    print("✅ User registration successful!")
                    print(f"📋 User ID: {user_data.get('id', 'N/A')}")
                    print(f"📧 Email: {user_data.get('email', 'N/A')}")
                    print(f"✅ Active: {user_data.get('is_active', 'N/A')}")
                    print(f"📅 Created: {user_data.get('created_at', 'N/A')}")
                    
                elif response.status == 400:
                    error_data = await response.json()
                    print(f"⚠️ Registration failed: {error_data.get('detail', 'Unknown error')}")
                    
                    # If user already exists, we can still test login
                    if "already exists" in error_data.get('detail', '').lower():
                        print("💡 User already exists, proceeding to login test...")
                    else:
                        print("❌ Registration failed with validation error")
                        return
                        
                else:
                    print(f"❌ Registration failed with status {response.status}")
                    print(f"📄 Response: {response_text}")
                    return
                    
        except Exception as e:
            print(f"❌ Registration request failed: {e}")
            return
        
        # Test 4: User Login (JSON)
        print(f"\n🔐 Testing user login (JSON)...")
        
        try:
            json_login_data = {
                "email": test_user["email"],
                "password": test_user["password"]
            }
            
            async with session.post(
                f"{API_BASE}/auth/login-json",
                json=json_login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                response_text = await response.text()
                print(f"📊 Login response status: {response.status}")
                
                if response.status == 200:
                    token_data = await response.json()
                    print("✅ User login successful!")
                    print(f"🔑 Access Token: {token_data.get('access_token', 'N/A')[:50]}...")
                    print(f"🔄 Refresh Token: {token_data.get('refresh_token', 'N/A')[:50]}...")
                    print(f"📝 Token Type: {token_data.get('token_type', 'N/A')}")
                    
                    user_info = token_data.get('user', {})
                    if user_info:
                        print(f"👤 User Info:")
                        print(f"   📧 Email: {user_info.get('email', 'N/A')}")
                        print(f"   🆔 ID: {user_info.get('id', 'N/A')}")
                        print(f"   ✅ Active: {user_info.get('is_active', 'N/A')}")
                        print(f"   🕐 Last Login: {user_info.get('last_login_at', 'N/A')}")
                    
                    # Store tokens for further testing
                    access_token = token_data.get('access_token')
                    
                elif response.status == 401:
                    error_data = await response.json()
                    print(f"❌ Login failed: {error_data.get('detail', 'Unauthorized')}")
                    return
                    
                else:
                    print(f"❌ Login failed with status {response.status}")
                    print(f"📄 Response: {response_text}")
                    return
                    
        except Exception as e:
            print(f"❌ Login request failed: {e}")
            return
        
        # Test 5: Test user info endpoint
        # Test 5: Test user info endpoint
        print(f"\n� Testing user info endpoint...")
        
        if 'access_token' in locals():
            try:
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                async with session.get(
                    f"{API_BASE}/auth/me",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        user_data = await response.json()
                        print("✅ User info endpoint access successful!")
                        print(f"� Current user: {user_data.get('email', 'N/A')}")
                        
                    else:
                        print(f"⚠️ User info endpoint failed with status {response.status}")
                        
            except Exception as e:
                print(f"⚠️ User info endpoint test failed: {e}")
        else:
            print("⚠️ No access token available for testing user info endpoint")
        
        # Test 6: Test protected endpoint with token
        if 'access_token' in locals():
            print(f"\n🔒 Testing protected endpoint...")
            
            try:
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                async with session.get(
                    f"{API_BASE}/users/me",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        user_data = await response.json()
                        print("✅ Protected endpoint access successful!")
                        print(f"👤 Current user: {user_data.get('email', 'N/A')}")
                        
                    elif response.status == 404:
                        print("⚠️ Protected endpoint not available")
                        
                    else:
                        print(f"⚠️ Protected endpoint failed with status {response.status}")
                        
            except Exception as e:
                print(f"⚠️ Protected endpoint test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 User registration and login tests completed!")
    print("💡 Check the results above for any issues")

async def check_existing_users():
    """Check how many users exist in database"""
    print("\n🔍 Checking existing users in database...")
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.config import settings
        
        client = AsyncIOMotorClient(settings.database_url)
        db = client.user_management_db
        users_collection = db.users
        
        total_users = await users_collection.count_documents({})
        print(f"👥 Total users in database: {total_users}")
        
        if total_users > 0:
            print("📋 Recent users:")
            async for user in users_collection.find({}).sort("created_at", -1).limit(3):
                print(f"  • {user.get('email', 'N/A')} (Created: {user.get('created_at', 'N/A')})")
        
        client.close()
        
    except Exception as e:
        print(f"⚠️ Could not check database: {e}")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(check_existing_users())
    asyncio.run(test_user_registration_and_login())
