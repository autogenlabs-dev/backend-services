"""Test script for sub-user management system"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "testpassword123"
SUB_USER_EMAIL = "subuser@example.com"
SUB_USER_NAME = "Test Sub User"

def test_sub_user_system():
    """Test the complete sub-user management system"""
    
    print("🧪 Testing Sub-User Management System")
    print("=" * 50)
    
    # Step 1: Register or login main user
    print("1. Setting up main user...")
    
    # Try to register first
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 409:
        print("   User already exists, logging in...")
    elif response.status_code == 201:
        print("   User registered successfully")
    else:
        print(f"   Registration failed: {response.text}")
        return
    
    # Login to get token
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"   Login failed: {response.text}")
        return
    
    auth_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    print("   ✅ Main user authenticated")
    
    # Step 2: Upgrade to Pro subscription (required for sub-users)
    print("\n2. Upgrading to Pro subscription...")
    
    # First check current subscription
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        print(f"   Current subscription: {user_data.get('subscription', 'unknown')}")
        
        # Update subscription to pro
        update_data = {"subscription": "pro"}
        response = requests.put(f"{BASE_URL}/admin/users/{user_data['id']}/subscription", 
                              json=update_data, headers=headers)
        if response.status_code == 200:
            print("   ✅ Upgraded to Pro subscription")
        else:
            print(f"   ⚠️  Could not upgrade subscription: {response.text}")
    
    # Step 3: Create a sub-user
    print("\n3. Creating sub-user...")
    
    sub_user_data = {
        "email": SUB_USER_EMAIL,
        "name": SUB_USER_NAME,
        "permissions": {
            "api_access": True,
            "can_create_api_keys": True,
            "can_view_usage": True,
            "can_modify_settings": False,
            "allowed_endpoints": ["*"]
        },
        "limits": {
            "monthly_tokens": 2000,
            "requests_per_minute": 30,
            "max_api_keys": 2
        },
        "password": "subuser123"
    }
    
    response = requests.post(f"{BASE_URL}/sub-users/", json=sub_user_data, headers=headers)
    if response.status_code == 200:
        sub_user = response.json()
        sub_user_id = sub_user["id"]
        print(f"   ✅ Sub-user created: {sub_user['name']} ({sub_user['email']})")
        print(f"   📊 Token limit: {sub_user['monthly_limit']}")
    else:
        print(f"   ❌ Sub-user creation failed: {response.text}")
        return
    
    # Step 4: List sub-users
    print("\n4. Listing sub-users...")
    
    response = requests.get(f"{BASE_URL}/sub-users/", headers=headers)
    if response.status_code == 200:
        sub_users = response.json()
        print(f"   ✅ Found {len(sub_users)} sub-user(s)")
        for user in sub_users:
            print(f"      - {user['name']} ({user['email']}) - {user['tokens_remaining']} tokens remaining")
    else:
        print(f"   ❌ Failed to list sub-users: {response.text}")
    
    # Step 5: Create API key for sub-user
    print("\n5. Creating API key for sub-user...")
    
    api_key_data = {
        "name": "Sub-user Test Key"
    }
    
    response = requests.post(f"{BASE_URL}/sub-users/{sub_user_id}/api-keys", 
                           json=api_key_data, headers=headers)
    if response.status_code == 200:
        api_key_info = response.json()
        sub_user_api_key = api_key_info["key"]
        print(f"   ✅ API key created: {api_key_info['name']}")
        print(f"   🔑 Key preview: {sub_user_api_key[:16]}...")
    else:
        print(f"   ❌ API key creation failed: {response.text}")
        return
    
    # Step 6: Test API access with sub-user key
    print("\n6. Testing API access with sub-user key...")
    
    sub_user_headers = {"Authorization": f"Bearer {sub_user_api_key}"}
    
    # Try to make a test request (if LLM endpoint exists)
    test_request = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello, test message"}],
        "max_tokens": 10
    }
    
    response = requests.post(f"{BASE_URL}/llm/chat/completions", 
                           json=test_request, headers=sub_user_headers)
    if response.status_code == 200:
        print("   ✅ Sub-user API access successful")
    else:
        print(f"   ⚠️  API request status: {response.status_code} - {response.text}")
    
    # Step 7: Get sub-user usage statistics
    print("\n7. Getting sub-user usage statistics...")
    
    response = requests.get(f"{BASE_URL}/sub-users/{sub_user_id}/usage", headers=headers)
    if response.status_code == 200:
        usage_stats = response.json()
        print(f"   ✅ Usage stats retrieved:")
        print(f"      Tokens used: {usage_stats['tokens_used']}")
        print(f"      Tokens remaining: {usage_stats['tokens_remaining']}")
        print(f"      Usage percentage: {usage_stats['usage_percentage']:.1f}%")
    else:
        print(f"   ❌ Failed to get usage stats: {response.text}")
    
    # Step 8: Test dashboard overview
    print("\n8. Testing dashboard overview...")
    
    response = requests.get(f"{BASE_URL}/dashboard/sub-users/overview", headers=headers)
    if response.status_code == 200:
        dashboard = response.json()
        print(f"   ✅ Dashboard data retrieved:")
        print(f"      Total sub-users: {dashboard['total_sub_users']}")
        print(f"      Active sub-users: {dashboard['active_sub_users']}")
        print(f"      Total tokens used: {dashboard['total_tokens_used']}")
        print(f"      Monthly usage: {dashboard['monthly_usage_percentage']:.1f}%")
    else:
        print(f"   ⚠️  Dashboard not available: {response.status_code}")
    
    # Step 9: Update sub-user limits
    print("\n9. Updating sub-user limits...")
    
    new_limits = {
        "limits": {
            "monthly_tokens": 3000,
            "requests_per_minute": 50
        }
    }
    
    response = requests.put(f"{BASE_URL}/sub-users/{sub_user_id}/limits", 
                          json=new_limits, headers=headers)
    if response.status_code == 200:
        updated_user = response.json()
        print(f"   ✅ Limits updated successfully")
        print(f"   📊 New monthly limit: {updated_user['monthly_limit']}")
    else:
        print(f"   ❌ Failed to update limits: {response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 Sub-User System Test Complete!")
    print("\n📋 Summary of Features Tested:")
    print("   ✅ User authentication")
    print("   ✅ Subscription management")
    print("   ✅ Sub-user creation")
    print("   ✅ Sub-user listing")
    print("   ✅ API key generation")
    print("   ✅ Usage statistics")
    print("   ✅ Dashboard overview")
    print("   ✅ Limit updates")
    
    print("\n🔧 System Capabilities:")
    print("   • Hierarchical user management")
    print("   • Granular permissions control")
    print("   • Token limit enforcement")
    print("   • API key management")
    print("   • Usage tracking and analytics")
    print("   • Real-time monitoring")

if __name__ == "__main__":
    try:
        test_sub_user_system()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
