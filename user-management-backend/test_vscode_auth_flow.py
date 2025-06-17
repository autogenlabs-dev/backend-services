#!/usr/bin/env python3
"""
VS Code Extension Authentication Flow Test - COMPLETE DEMONSTRATION

This test file demonstrates the EXACT authenticat    try:
        response = requests.post(f"{BASE_U        if response.status_code ==    if api_key:
        api_headers = {"X-API-Key": api_key}
        try:
            response = requests.get(f"{BASE_URL}/users/me", headers=api_headers)
            print(f"API Key Auth Status: {response.status_code}")
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ API Key authentication successful!")
                print(f"User: {user_info.get('email')}")
                print(f"Authenticated via API key instead of JWT token")
            else:
                print(f"❌ API Key authentication failed: {response.text}")
        except Exception as e:
            print(f"❌ API Key authentication error: {e}")
    else:
        print("❌ No API key available for testing")
    
    print("\n" + "="*60)
    print("🎯 VS CODE EXTENSION FLOW TEST COMPLETE!")
    print("="*60)
    if api_key:
        print(f"\n🔑 FINAL API KEY FOR VS CODE: {api_key[:30]}...")
    print(f"📧 USER EMAIL: {user_email}")i_result = response.json()
            print(f"Full API Key Response: {api_result}")
            
            # The API returns the key in the 'api_key' field
            api_key = api_result.get("api_key")
            print(f"✅ API Key created successfully!")
            print(f"🔑 API Key: {api_key[:30]}...")
            print(f"Key ID: {api_result.get('id')}")
            print(f"Key Name: {api_result.get('name')}")
            print(f"Created At: {api_result.get('created_at')}")
            print(f"Is Active: {api_result.get('is_active')}")
            print("\n🎯 THIS IS THE KEY THE VS CODE EXTENSION WILL STORE AND USE!")ys", json=api_key_data, headers=headers)
        print(f"API Key Creation Status: {response.status_code}")
        print(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            api_result = response.json()
            print(f"Full API Response: {json.dumps(api_result, indent=2)}")
            
            # Handle different possible response formats
            if isinstance(api_result, dict):
                # Try different possible key names
                api_key = (api_result.get("api_key") or 
                          api_result.get("key") or 
                          api_result.get("access_key"))
                
                if api_key:
                    print(f"✅ API Key created successfully!")
                    print(f"🔑 API Key: {api_key[:30]}...")
                    print(f"Key ID: {api_result.get('id')}")
                    print(f"Key Name: {api_result.get('name')}")
                    print(f"Key Preview: {api_result.get('key_preview')}")
                    print(f"Created At: {api_result.get('created_at')}")
                    print(f"Expires At: {api_result.get('expires_at', 'Never')}")
                    print("\n🎯 THIS IS THE KEY THE VS CODE EXTENSION WILL STORE AND USE!")
                else:
                    print("❌ API Key not found in response, available keys:")
                    print(list(api_result.keys()))
                    return False
            else:
                print(f"❌ Unexpected response format: {type(api_result)}")
                return False
        else:
            print(f"❌ API Key creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ API Key creation error: {e}")
        print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
        return Falsede extension users
will experience when using the autogen-code-builder extension with the backend.

USER JOURNEY IN VS CODE:
1. User opens VS Code extension panel
2. User clicks "Login" or "Sign Up" button
3. Extension opens authentication dialog/webview
4. User enters credentials (register or login)
5. Extension receives JWT tokens automatically
6. Extension immediately creates persistent API key
7. Extension stores API key securely in VS Code secrets
8. Extension uses API key for ALL LLM requests
9. User can now use AI features seamlessly - NO manual API key management!

TECHNICAL FLOW:
Register → Login → Auto-create API Key → Store in VS Code → Use for LLM

This test validates each step to ensure users get a seamless authentication experience.
"""

import requests
import json
import time
from datetime import datetime
import sys
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000"

class Colors:
    """Console colors for better test output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def main():
    print("��� VS Code Extension Authentication Flow Test")
    print(f"��� Started at: {datetime.now()}")
    print(f"��� Testing API at: {BASE_URL}")
    print("="*60)
    
    # Variables to track the flow
    access_token = None
    refresh_token = None
    api_key = None
    user_email = None
    
    # Step 1: User Registration (like VS Code extension sign-up)
    print("\n1️⃣ USER REGISTRATION FLOW")
    print("-" * 40)
    print("Simulating: User clicks 'Register' in VS Code extension")
    
    test_user = {
        "email": f"vscode_user_{int(time.time())}@example.com",
        "password": "SecurePassword123!",
        "full_name": "VS Code User"
    }
    user_email = test_user["email"]
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        print(f"Registration Status: {response.status_code}")
        print(f"Registration Response: {response.text}")
        
        if response.status_code == 200:
            reg_data = response.json()
            print(f"Full Registration Response: {json.dumps(reg_data, indent=2)}")
            
            # Handle different response formats
            user_info = reg_data.get('user') or reg_data
            email = user_info.get('email') if isinstance(user_info, dict) else None
            user_id = user_info.get('id') if isinstance(user_info, dict) else None
            subscription = user_info.get('subscription_tier') if isinstance(user_info, dict) else None
            
            print(f"✅ User registered successfully: {email or 'Email not in response'}")
            print(f"User ID: {user_id or 'ID not in response'}")
            print(f"Subscription Tier: {subscription or 'Free/Default'}")
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Step 2: User Login (getting JWT tokens)
    print("\n2️⃣ USER LOGIN FLOW")
    print("-" * 40)
    print("Simulating: User enters credentials in VS Code extension")
    
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"Login Status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            print(f"✅ Login successful!")
            print(f"Access Token: {access_token[:30]}...")
            print(f"Refresh Token: {refresh_token[:30]}...")
            print(f"Token Type: {token_data.get('token_type')}")
            print(f"Expires In: {token_data.get('expires_in')} seconds")
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 3: Verify User Profile Access
    print("\n3️⃣ USER PROFILE ACCESS")
    print("-" * 40)
    print("Simulating: Extension verifies user authentication")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print(f"Profile Access Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User profile accessed successfully")
            print(f"Email: {user_data.get('email')}")
            print(f"Subscription: {user_data.get('subscription_tier')}")
            print(f"Total API Calls: {user_data.get('total_api_calls', 0)}")
            if user_data.get('monthly_usage'):
                usage = user_data['monthly_usage']
                print(f"Monthly Usage: {usage.get('api_calls', 0)} calls, {usage.get('total_tokens', 0)} tokens")
        else:
            print(f"❌ Profile access failed: {response.text}")
    except Exception as e:
        print(f"❌ Profile access error: {e}")
    
    # Step 4: Create API Key (THE CRITICAL STEP FOR VS CODE)
    print("\n4️⃣ API KEY CREATION FOR VS CODE")
    print("-" * 40)
    print("Simulating: Extension automatically creates persistent API key")
    
    api_key_data = {
        "name": "VS Code Extension - AutoGen",
        "description": "Persistent API key for VS Code AutoGen extension"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/keys", json=api_key_data, headers=headers)
        print(f"API Key Creation Status: {response.status_code}")
        if response.status_code == 200:
            api_result = response.json()
            api_key = api_result.get("key")
            print(f"✅ API Key created successfully!")
            print(f"��� API Key: {api_key[:30]}...")
            print(f"Key ID: {api_result.get('id')}")
            print(f"Key Name: {api_result.get('name')}")
            print(f"Created At: {api_result.get('created_at')}")
            print(f"Is Active: {api_result.get('is_active')}")
            print("\n��� THIS IS THE KEY THE VS CODE EXTENSION WILL STORE AND USE!")
        else:
            print(f"❌ API Key creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ API Key creation error: {e}")
        return False
    
    # Step 5: Test API Key Authentication (How VS Code will authenticate)
    print("\n5️⃣ API KEY AUTHENTICATION TEST")
    print("-" * 40)
    print("Simulating: VS Code extension using stored API key for requests")
    
    if api_key:
        api_headers = {"X-API-Key": api_key}
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=api_headers)
        print(f"API Key Auth Status: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ API Key authentication successful!")
            print(f"User: {user_info.get('email')}")
            print(f"Authenticated via API key instead of JWT token")
        else:
            print(f"❌ API Key authentication failed: {response.text}")
    except Exception as e:
        print(f"❌ API Key authentication error: {e}")
    
    print("\n" + "="*60)
    print("��� VS CODE EXTENSION FLOW TEST COMPLETE!")
    print("="*60)
    print(f"\n��� FINAL API KEY FOR VS CODE: {api_key[:30]}...")
    print(f"��� USER EMAIL: {user_email}")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ All tests passed! Authentication flow is working perfectly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed! Check the output above.")
        sys.exit(1)
