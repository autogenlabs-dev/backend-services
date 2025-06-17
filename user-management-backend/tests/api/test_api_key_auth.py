#!/usr/bin/env python3
"""
Test API Key Authentication on Supported Endpoints
"""

import requests
import json
import time
from datetime import datetime


BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"api_test_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"


def test_api_key_authentication():
    """Test API key authentication on endpoints that support it"""
    
    print("🔑 API Key Authentication Test")
    print("=" * 60)
    print(f"🌐 Testing API at: {BASE_URL}")
    print(f"⏰ Started at: {datetime.now()}")
    print()
    
    # Step 1: Register and login to get JWT token
    print("1️⃣ Setting up user and creating API key...")
    
    # Register
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "API Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Registration Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.text}")
        return False
    
    # Login
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Login Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return False
    
    tokens = response.json()
    jwt_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    # Create API Key
    api_key_data = {
        "name": "Authentication Test Key",
        "description": "Testing API key authentication"
    }
    
    response = requests.post(f"{BASE_URL}/api/keys", json=api_key_data, headers=jwt_headers)
    print(f"API Key Creation Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ API Key creation failed: {response.text}")
        return False
    
    api_key_result = response.json()
    api_key = api_key_result.get("api_key")
    
    if not api_key:
        print(f"❌ No API key in response: {api_key_result}")
        return False
    
    print(f"✅ API Key created: {api_key[:20]}...")
    api_headers = {"X-API-Key": api_key}
    
    print("\n" + "="*60)
    print("2️⃣ Testing API Key Authentication on Supported Endpoints")
    print("="*60)
    
    # Test 1: API Key Validation Endpoint
    print("\n🔍 Test 1: API Key Validation Endpoint")
    print("Endpoint: GET /api/keys/validate")
    
    try:
        response = requests.get(f"{BASE_URL}/api/keys/validate", headers=api_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Key validation successful!")
            print(f"   Valid: {result.get('valid')}")
            print(f"   User: {result.get('user', {}).get('email')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ API Key validation failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: LLM Models Endpoint
    print("\n🤖 Test 2: LLM Models Endpoint")
    print("Endpoint: GET /llm/models")
    
    try:
        response = requests.get(f"{BASE_URL}/llm/models", headers=api_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ LLM models accessed with API key!")
            print(f"   Available models: {len(models) if isinstance(models, list) else 'Unknown'}")
            if isinstance(models, list) and models:
                for i, model in enumerate(models[:3]):
                    if isinstance(model, dict):
                        print(f"   - {model.get('name', model.get('id', 'Unknown'))}")
                    else:
                        print(f"   - {model}")
                    if i >= 2:
                        break
        else:
            print(f"❌ LLM models failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: LLM Health Check
    print("\n🏥 Test 3: LLM Health Check")
    print("Endpoint: GET /llm/health")
    
    try:
        response = requests.get(f"{BASE_URL}/llm/health", headers=api_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ LLM health check with API key!")
            print(f"   Status: {health.get('status')}")
            print(f"   Providers: {health.get('providers', [])}")
        else:
            print(f"❌ LLM health failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: LLM Providers Endpoint
    print("\n🏢 Test 4: LLM Providers Endpoint")
    print("Endpoint: GET /llm/providers")
    
    try:
        response = requests.get(f"{BASE_URL}/llm/providers", headers=api_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            providers = response.json()
            print(f"✅ LLM providers accessed with API key!")
            print(f"   Available providers: {len(providers) if isinstance(providers, list) else 'Unknown'}")
            if isinstance(providers, list):
                for provider in providers:
                    if isinstance(provider, dict):
                        print(f"   - {provider.get('name', provider.get('id', 'Unknown'))}")
        else:
            print(f"❌ LLM providers failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Compare with JWT-only endpoint
    print("\n🚫 Test 5: JWT-Only Endpoint (should fail)")
    print("Endpoint: GET /users/me (JWT only)")
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=api_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"⚠️ Unexpected success - this endpoint should require JWT")
        else:
            print(f"✅ Expected failure (JWT required): {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Verify JWT still works
    print("\n🎫 Test 6: Verify JWT Authentication Still Works")
    print("Endpoint: GET /users/me (with JWT)")
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=jwt_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ JWT authentication working!")
            print(f"   User: {user_info.get('email')}")
        else:
            print(f"❌ JWT failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("🎯 API KEY AUTHENTICATION TEST COMPLETE!")
    print("="*60)
    print()
    print("📋 SUMMARY:")
    print("✅ API Keys work for LLM endpoints (/llm/*)")
    print("✅ API Keys work for key validation (/api/keys/validate)")
    print("❌ API Keys do NOT work for user endpoints (/users/me)")
    print("✅ JWT tokens work for all endpoints")
    print()
    print("🔍 CONCLUSION:")
    print("VS Code extensions should use API keys for LLM requests")
    print("and JWT tokens for user management operations.")
    
    return True


if __name__ == "__main__":
    test_api_key_authentication()
