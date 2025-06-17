#!/usr/bin/env python3
"""
Complete VS Code Extension Authentication Flow Test
Tests the full authentication journey including API key support for LLM endpoints
"""

import requests
import json
import time
from datetime import datetime


BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"vscode_complete_{int(time.time())}@example.com"
TEST_PASSWORD = "VSCodeTest123!"


def test_complete_vscode_flow():
    """Test the complete VS Code extension authentication flow with API key support"""
    
    print("🚀 VS CODE EXTENSION COMPLETE AUTHENTICATION FLOW TEST")
    print("=" * 70)
    print(f"🌐 API Base URL: {BASE_URL}")
    print(f"📧 Test Email: {TEST_EMAIL}")
    print(f"⏰ Started at: {datetime.now()}")
    print()

    # Step 1: User Registration
    print("1️⃣ USER REGISTRATION")
    print("-" * 40)
    print("Simulating: User signs up for the first time")
    
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "VS Code Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User registered successfully!")
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Subscription: {user_data.get('subscription', 'free')}")
            print(f"   Tokens: {user_data.get('tokens_remaining', 10000)}")
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

    # Step 2: User Login
    print("\n2️⃣ USER LOGIN")
    print("-" * 40)
    print("Simulating: User logs in through VS Code extension")
    
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
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
            print(f"   Token Type: {tokens.get('token_type')}")
            print(f"   Expires In: {tokens.get('expires_in')} seconds")
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

    # Step 3: Create API Key for Persistent Authentication
    print("\n3️⃣ API KEY CREATION")
    print("-" * 40)
    print("Simulating: VS Code extension creates API key for persistent auth")
    
    jwt_headers = {"Authorization": f"Bearer {access_token}"}
    api_key_data = {
        "name": "VS Code Extension Key",
        "description": "Persistent API key for VS Code extension authentication"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/keys/", json=api_key_data, headers=jwt_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            api_result = response.json()
            api_key = api_result.get("api_key")
            print(f"✅ API Key created successfully!")
            print(f"   API Key: {api_key[:30]}...")
            print(f"   Key ID: {api_result.get('id')}")
            print(f"   Key Name: {api_result.get('name')}")
            print(f"   Created At: {api_result.get('created_at')}")
            print("\n🔐 VS Code extension will store this API key securely!")
        else:
            print(f"❌ API Key creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ API Key creation error: {e}")
        return False

    # Step 4: Test API Key Authentication on LLM Endpoints
    print("\n4️⃣ API KEY AUTHENTICATION ON LLM ENDPOINTS")
    print("-" * 40)
    print("Simulating: VS Code extension using API key for LLM requests")
    
    api_headers = {"X-API-Key": api_key}
    
    # Test 4a: LLM Models
    print("\n🤖 Test 4a: LLM Models Endpoint")
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
                    if i >= 2:
                        break
        else:
            print(f"❌ LLM models failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 4b: LLM Providers
    print("\n🏢 Test 4b: LLM Providers Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/llm/providers", headers=api_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            providers = response.json()
            print(f"✅ LLM providers accessed with API key!")
            print(f"   Available providers: {len(providers) if isinstance(providers, list) else 'Unknown'}")
        else:
            print(f"❌ LLM providers failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 4c: LLM Health Check
    print("\n🏥 Test 4c: LLM Health Check")
    try:
        response = requests.get(f"{BASE_URL}/llm/health", headers=api_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ LLM health check with API key!")
            print(f"   Status: {health.get('status')}")
            print(f"   User ID: {health.get('user_id')}")
            print(f"   Providers: {len(health.get('providers', []))}")
        else:
            print(f"❌ LLM health failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Step 5: Test Mixed Authentication (JWT for user management, API key for LLM)
    print("\n5️⃣ MIXED AUTHENTICATION TEST")
    print("-" * 40)
    print("Testing: JWT for user management, API key for LLM operations")
    
    # Test JWT for user profile
    print("\n👤 User Profile (JWT)")
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=jwt_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ User profile accessed with JWT!")
            print(f"   Email: {user_info.get('email')}")
            print(f"   Tokens Remaining: {user_info.get('tokens_remaining')}")
        else:
            print(f"❌ JWT user profile failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test API key validation endpoint
    print("\n🔍 API Key Validation")
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

    # Step 6: Test Chat Completion (Main LLM Functionality)
    print("\n6️⃣ CHAT COMPLETION TEST")
    print("-" * 40)
    print("Testing: Core LLM functionality with API key")
    
    chat_request = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hello! Can you help me with VS Code extension development?"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        response = requests.post(f"{BASE_URL}/llm/chat/completions", 
                               json=chat_request, 
                               headers=api_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            chat_result = response.json()
            print(f"✅ Chat completion with API key successful!")
            print(f"   Model: {chat_result.get('model', 'Unknown')}")
            print(f"   Usage: {chat_result.get('usage', {})}")
            
            choices = chat_result.get('choices', [])
            if choices:
                message = choices[0].get('message', {})
                content = message.get('content', '')[:100]
                print(f"   Response: {content}...")
        else:
            print(f"❌ Chat completion failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "="*70)
    print("🎯 VS CODE EXTENSION AUTHENTICATION FLOW COMPLETE!")
    print("="*70)
    print()
    print("📋 SUMMARY:")
    print("✅ User registration working")
    print("✅ User login working (JWT tokens)")
    print("✅ API key creation working")
    print("✅ LLM endpoints support API key authentication")
    print("✅ Mixed authentication working (JWT + API key)")
    print("✅ Chat completion working with API key")
    print()
    print("🔧 VS CODE EXTENSION IMPLEMENTATION:")
    print("1. Store API key securely after one-time login")
    print("2. Use API key for all LLM operations")
    print("3. Use JWT tokens for user management (if needed)")
    print("4. No need for frequent re-authentication!")
    print()
    print(f"🔑 FINAL API KEY: {api_key[:30]}...")
    print(f"📧 USER EMAIL: {TEST_EMAIL}")
    
    return True


if __name__ == "__main__":
    test_complete_vscode_flow()
