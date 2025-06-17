#!/usr/bin/env python3
"""
Simple API Key Authentication Test
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"simple_test_{int(time.time())}@example.com"
TEST_PASSWORD = "SimpleTest123!"

def main():
    print("🔑 Simple API Key Authentication Test")
    print("=" * 50)
    
    # 1. Register
    print("1. Registering user...")
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Simple Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data, timeout=10)
        print(f"   Registration status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Registration failed: {e}")
        return False
    
    # 2. Login
    print("2. Logging in...")
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        print(f"   Login status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return False
        
        tokens = response.json()
        access_token = tokens.get("access_token")
        print(f"   Got access token: {access_token[:20]}...")
        print(f"   Complete login response: {json.dumps(tokens, indent=2)}")
        
    except Exception as e:
        print(f"   Login failed: {e}")
        return False
    
    # 3. Create API Key
    print("3. Creating API key...")
    jwt_headers = {"Authorization": f"Bearer {access_token}"}
    api_key_data = {
        "name": "Simple Test Key",
        "description": "Testing API key creation"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/keys/", json=api_key_data, headers=jwt_headers, timeout=10)
        print(f"   API key creation status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return False
        
        api_result = response.json()
        api_key = api_result.get("api_key")
        print(f"   Got API key: {api_key[:20]}...")
        
    except Exception as e:
        print(f"   API key creation failed: {e}")
        return False
    
    # 4. Test API Key on LLM endpoint
    print("4. Testing API key on LLM models endpoint...")
    api_headers = {"X-API-Key": api_key}
    
    try:
        response = requests.get(f"{BASE_URL}/llm/models", headers=api_headers, timeout=10)
        print(f"   LLM models status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API Key works on LLM endpoints!")
            models = response.json()
            print(f"   Found {len(models) if isinstance(models, list) else 'unknown'} models")
        else:
            print(f"   ❌ LLM models failed: {response.text}")
            return False
    except Exception as e:
        print(f"   LLM models test failed: {e}")
        return False
    
    # 5. Test API Key Validation
    print("5. Testing API key validation...")
    try:
        response = requests.get(f"{BASE_URL}/api/keys/validate", headers=api_headers, timeout=10)
        print(f"   API key validation status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("   ✅ API Key validation works!")
            print(f"   User: {result.get('user', {}).get('email')}")
        else:
            print(f"   ❌ API key validation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   API key validation test failed: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("VS Code extension authentication flow is working!")
    return True

if __name__ == "__main__":
    main()
