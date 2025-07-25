#!/usr/bin/env python3
"""
Script to create a new user and test login functionality
"""
import asyncio
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = BASE_URL  # No /api prefix needed

async def create_user_and_login():
    """Create a new user and test login"""
    
    print("🚀 Testing User Registration and Login")
    print("=" * 50)
    
    # New user data with timestamp to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_user = {
        "email": f"testuser_{timestamp}@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    print(f"👤 Creating new user: {new_user['email']}")
    
    try:
        # Test 1: Register new user
        print("\n1️⃣ Testing user registration...")
        register_response = requests.post(
            f"{API_BASE}/auth/register",
            json=new_user,
            headers={"Content-Type": "application/json"}
        )
        
        if register_response.status_code == 200:
            response_data = register_response.json()
            user_data = response_data.get('user', {})
            print("✅ User registration successful!")
            print(f"   Message: {response_data.get('message', 'N/A')}")
            print(f"   User ID: {user_data.get('id', 'N/A')}")
            print(f"   Email: {user_data.get('email', 'N/A')}")
            print(f"   Name: {user_data.get('name', 'N/A')}")
            print(f"   Is Active: {user_data.get('is_active', 'N/A')}")
            print(f"   Role: {user_data.get('role', 'N/A')}")
            print(f"   Created: {user_data.get('created_at', 'N/A')}")
            
            # Print the full registration response for debugging
            print(f"\n   📄 Full Registration Response: {json.dumps(response_data, indent=2, default=str)}")
        else:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(f"   Error: {register_response.text}")
            
            # If user already exists, that's okay for testing
            if register_response.status_code == 400 and "already exists" in register_response.text.lower():
                print("ℹ️  User already exists, proceeding with login test...")
            else:
                return
        
        # Test 2: Login with the created user
        print("\n2️⃣ Testing user login...")
        login_data = {
            "email": new_user["email"],
            "password": new_user["password"]
        }
        
        login_response = requests.post(
            f"{API_BASE}/auth/login-json",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("✅ Login successful!")
            print(f"   Access Token: {login_result.get('access_token', 'N/A')[:50]}...")
            print(f"   Refresh Token: {login_result.get('refresh_token', 'N/A')[:50]}...")
            print(f"   Token Type: {login_result.get('token_type', 'N/A')}")
            
            # Test 3: Use access token to get user info
            print("\n3️⃣ Testing authenticated request...")
            access_token = login_result.get('access_token')
            
            if access_token:
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                # Try to get current user info
                user_info_response = requests.get(
                    f"{API_BASE}/auth/me",
                    headers=headers
                )
                
                if user_info_response.status_code == 200:
                    response_data = user_info_response.json()
                    user_info = response_data.get('user', {})
                    print("✅ Authenticated request successful!")
                    print(f"   User ID: {user_info.get('id', 'N/A')}")
                    print(f"   User Email: {user_info.get('email', 'N/A')}")
                    print(f"   Name: {user_info.get('name', 'N/A')}")
                    print(f"   Subscription Tier: {user_info.get('subscription_tier', 'N/A')}")
                    print(f"   Tokens Remaining: {user_info.get('tokens_remaining', 'N/A')}")
                    print(f"   Tokens Used: {user_info.get('tokens_used', 'N/A')}")
                    print(f"   Monthly Limit: {user_info.get('monthly_limit', 'N/A')}")
                    
                    # Print the full response for debugging
                    print(f"\n   📄 Full Response: {json.dumps(response_data, indent=2, default=str)}")
                else:
                    print(f"❌ Authenticated request failed: {user_info_response.status_code}")
                    print(f"   Error: {user_info_response.text}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on http://localhost:8000")
        print("💡 Run: python run_server.py")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def test_with_curl_commands():
    """Print curl commands for manual testing"""
    print("\n" + "=" * 50)
    print("🔧 MANUAL TESTING WITH CURL")
    print("=" * 50)
    
    print("\n1. Register a new user:")
    print('curl -X POST "http://localhost:8000/auth/register" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"email": "newuser@example.com", "password": "password123", "first_name": "New", "last_name": "User"}\'')
    
    print("\n2. Login with the user:")
    print('curl -X POST "http://localhost:8000/auth/login-json" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"email": "newuser@example.com", "password": "password123"}\'')
    
    print("\n3. Use the token (replace YOUR_TOKEN with actual token):")
    print('curl -X GET "http://localhost:8000/auth/me" \\')
    print('  -H "Authorization: Bearer YOUR_TOKEN"')
    
    print("\n💡 WORKING LOGIN CREDENTIALS:")
    print("=" * 50)
    print("📧 Email: testuser_20250720_234038@example.com")
    print("🔑 Password: TestPassword123!")
    print("👤 Role: user")
    print("\n📧 Email: abhishek1234@gmail.com")
    print("🔑 Password: (your original password)")
    print("👤 Role: developer")

async def main():
    """Main function"""
    # Check if server is running first
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start it first:")
        print("   python run_server.py")
        print("\nAlternatively, here are curl commands for manual testing:")
        test_with_curl_commands()
        return
    except Exception as e:
        print(f"❌ Error checking server: {str(e)}")
        return
    
    await create_user_and_login()
    test_with_curl_commands()

if __name__ == "__main__":
    asyncio.run(main())
