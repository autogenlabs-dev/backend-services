#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_full_auth_flow():
    print("� Testing Full Authentication Flow")
    print("=" * 50)
    
    # 1. Register user
    print("\n1. � Registering new user...")
    user_data = {
        "email": f"test_{int(time.time())}@example.com",
        "password": "Password123!",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Registration Status: {response.status_code}")
        if response.status_code == 200:
            reg_result = response.json()
            print(f"✅ User registered: {reg_result.get('user', {}).get('email')}")
        else:
            print(f"❌ Registration failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    # 2. Login
    print("\n2. � Logging in...")
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"Login Status: {response.status_code}")
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get("access_token")
            print(f"✅ Login successful! Token: {access_token[:20]}...")
        else:
            print(f"❌ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # 3. Test protected endpoint
    print("\n3. �️ Testing protected endpoint...")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print(f"Protected endpoint Status: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ User info: {user_info.get('email')}")
        else:
            print(f"❌ Protected endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Protected endpoint error: {e}")
    
    # 4. Create API Key
    print("\n4. � Creating API key...")
    api_key_data = {
        "name": "VS Code Extension Key",
        "description": "API key for VS Code extension testing"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/keys", json=api_key_data, headers=headers)
        print(f"API Key Creation Status: {response.status_code}")
        if response.status_code == 200:
            api_result = response.json()
            api_key = api_result.get("key")
            print(f"✅ API Key created: {api_key[:20]}...")
            print(f"Key ID: {api_result.get('id')}")
            print(f"Key Name: {api_result.get('name')}")
        else:
            print(f"❌ API Key creation failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ API Key creation error: {e}")
        return
    
    # 5. Test API Key Authentication
    print("\n5. �️ Testing API key authentication...")
    api_headers = {"X-API-Key": api_key}
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=api_headers)
        print(f"API Key Auth Status: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ API Key auth works! User: {user_info.get('email')}")
        else:
            print(f"❌ API Key auth failed: {response.text}")
    except Exception as e:
        print(f"❌ API Key auth error: {e}")
    
    # 6. Test LLM endpoints with API key
    print("\n6. � Testing LLM endpoints with API key...")
    try:
        response = requests.get(f"{BASE_URL}/llm/models", headers=api_headers)
        print(f"LLM Models Status: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Available models: {len(models)}")
            for model in models[:3]:
                print(f"  - {model.get('name', 'Unknown')}")
        else:
            print(f"❌ LLM models failed: {response.text}")
    except Exception as e:
        print(f"❌ LLM models error: {e}")
    
    print("\n� AUTHENTICATION FLOW TEST COMPLETE!")
    print("\nThis demonstrates the VS Code extension flow:")
    print("1. User registers/logs in")
    print("2. Extension gets JWT tokens")
    print("3. Extension creates persistent API key")
    print("4. Extension uses API key for all LLM requests")
    print("5. API key allows access without re-authentication")

if __name__ == "__main__":
    test_full_auth_flow()
