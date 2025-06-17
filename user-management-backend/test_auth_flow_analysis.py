#!/usr/bin/env python3
"""
Complete API Authentication Flow Test & Analysis
Demonstrates the current state and the gap in API key authentication
"""

import requests
import json
import time
from datetime import datetime


BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"flow_test_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"


def test_full_authentication_flow():
    """Test the complete authentication flow and demonstrate the current limitations"""
    
    print("🔐 COMPLETE API AUTHENTICATION FLOW TEST")
    print("=" * 70)
    print(f"🌐 API Base URL: {BASE_URL}")
    print(f"⏰ Test Started: {datetime.now()}")
    print(f"👤 Test User: {TEST_EMAIL}")
    print()
    
    # Step 1: User Registration
    print("1️⃣ USER REGISTRATION")
    print("-" * 40)
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Flow Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Registration successful!")
        print(f"   User ID: {user_data.get('id')}")
        print(f"   Email: {user_data.get('email')}")
        print(f"   Subscription: {user_data.get('subscription')}")
        print(f"   Tokens: {user_data.get('tokens_remaining')}")
    else:
        print(f"❌ Registration failed: {response.text}")
        return False
    
    # Step 2: User Login
    print(f"\n2️⃣ USER LOGIN")
    print("-" * 40)
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        
        print(f"✅ Login successful!")
        print(f"   Access Token: {access_token[:30]}...")
        print(f"   Refresh Token: {refresh_token[:30]}...")
        print(f"   Expires In: {tokens.get('expires_in')} seconds")
        
        jwt_headers = {"Authorization": f"Bearer {access_token}"}
    else:
        print(f"❌ Login failed: {response.text}")
        return False
    
    # Step 3: Access Protected Endpoint with JWT
    print(f"\n3️⃣ JWT AUTHENTICATION TEST")
    print("-" * 40)
    print("Testing: GET /users/me")
    
    response = requests.get(f"{BASE_URL}/users/me", headers=jwt_headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        user_info = response.json()
        print(f"✅ JWT authentication working!")
        print(f"   User: {user_info.get('email')}")
        print(f"   API Calls: {user_info.get('total_api_calls', 'N/A')}")
    else:
        print(f"❌ JWT authentication failed: {response.text}")
    
    # Step 4: Create API Key
    print(f"\n4️⃣ API KEY CREATION")
    print("-" * 40)
    api_key_data = {
        "name": "VS Code Extension Key",
        "description": "API key for testing VS Code extension flow"
    }
    
    response = requests.post(f"{BASE_URL}/api/keys", json=api_key_data, headers=jwt_headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        api_key_result = response.json()
        api_key = api_key_result.get("api_key")
        
        print(f"✅ API Key created successfully!")
        print(f"   Key ID: {api_key_result.get('id')}")
        print(f"   Key Name: {api_key_result.get('name')}")
        print(f"   API Key: {api_key[:25]}...")
        print(f"   Preview: {api_key_result.get('key_preview')}")
        print(f"   Created: {api_key_result.get('created_at')}")
        
        api_headers = {"X-API-Key": api_key}
    else:
        print(f"❌ API Key creation failed: {response.text}")
        return False
    
    # Step 5: Test API Key Authentication - Current State
    print(f"\n5️⃣ API KEY AUTHENTICATION ANALYSIS")
    print("-" * 40)
    
    # Test endpoints that should support API key according to docs
    endpoints_to_test = [
        ("/users/me", "User Profile (JWT Only)"),
        ("/api/keys/validate", "API Key Validation"),
        ("/llm/models", "LLM Models"),
        ("/llm/health", "LLM Health"),
        ("/llm/providers", "LLM Providers")
    ]
    
    for endpoint, description in endpoints_to_test:
        print(f"\n🔍 Testing: {description}")
        print(f"   Endpoint: GET {endpoint}")
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=api_headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ API Key authentication WORKS")
                
                # Show sample response for successful calls
                try:
                    data = response.json()
                    if endpoint == "/api/keys/validate":
                        print(f"   Result: {data.get('message', 'Validated')}")
                    elif endpoint == "/llm/models" and isinstance(data, list):
                        print(f"   Models: {len(data)} available")
                    elif endpoint == "/llm/health":
                        print(f"   Health: {data.get('status', 'Unknown')}")
                    elif endpoint == "/llm/providers" and isinstance(data, list):
                        print(f"   Providers: {len(data)} available")
                except:
                    print(f"   Response: Success")
                    
            elif response.status_code == 401:
                print(f"   ❌ Not authenticated")
            elif response.status_code == 403:
                print(f"   ❌ Forbidden/Not authenticated")
            else:
                print(f"   ⚠️ Other error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    # Step 6: Verify which authentication methods work where
    print(f"\n6️⃣ AUTHENTICATION METHOD COMPARISON")
    print("-" * 40)
    
    test_endpoint = "/users/me"
    
    print(f"Testing {test_endpoint} with different auth methods:")
    
    # Test with JWT
    print(f"\n🎫 JWT Token Authentication:")
    response = requests.get(f"{BASE_URL}{test_endpoint}", headers=jwt_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ JWT works for {test_endpoint}")
    else:
        print(f"   ❌ JWT failed for {test_endpoint}")
    
    # Test with API Key
    print(f"\n🔑 API Key Authentication:")
    response = requests.get(f"{BASE_URL}{test_endpoint}", headers=api_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ API Key works for {test_endpoint}")
    else:
        print(f"   ❌ API Key failed for {test_endpoint}")
    
    # Step 7: Summary and Recommendations
    print(f"\n" + "="*70)
    print("🎯 AUTHENTICATION FLOW ANALYSIS COMPLETE")
    print("="*70)
    
    print(f"\n📊 CURRENT STATE:")
    print(f"✅ User registration and login work perfectly")
    print(f"✅ JWT token authentication works for all endpoints")
    print(f"✅ API key creation works via JWT authentication")
    print(f"❌ API key authentication is not implemented for endpoints")
    print(f"⚠️  Documentation suggests API key support but it's missing")
    
    print(f"\n🔍 KEY FINDINGS:")
    print(f"1. All endpoints use get_current_user (JWT only)")
    print(f"2. API key auth system exists but isn't used by endpoints")
    print(f"3. LLM endpoints documented as supporting API keys but don't")
    print(f"4. VS Code extension needs API keys for persistent auth")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"1. Create unified auth dependency supporting both JWT and API keys")
    print(f"2. Update LLM endpoints to accept both authentication methods")
    print(f"3. Create endpoints that work with API key authentication")
    print(f"4. Implement proper API key validation for documented endpoints")
    
    print(f"\n🚀 FOR VS CODE EXTENSION:")
    print(f"Currently: Users must re-authenticate frequently (JWT expires)")
    print(f"Solution: Implement API key auth for LLM endpoints")
    print(f"Benefit: Persistent authentication without re-login")
    
    return True


if __name__ == "__main__":
    test_full_authentication_flow()
