#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE AUTHENTICATION & API FLOW TEST
===================================================

This test covers the complete VS Code extension authentication flow.
Created: June 10, 2025
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TIMESTAMP = int(time.time())
TEST_EMAIL = f"final_test_{TEST_TIMESTAMP}@example.com"
TEST_PASSWORD = "FinalTest123!"

def test_complete_flow():
    """Run complete authentication and API test flow"""
    print("=" * 60)
    print("FINAL COMPREHENSIVE API TEST")
    print("=" * 60)
    print(f"Started: {datetime.now()}")
    print(f"Test Email: {TEST_EMAIL}")
    print()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health Check
    print("1. Testing API Health...")
    tests_total += 1
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ API Health: {health.get('status')}")
            tests_passed += 1
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: User Registration
    print("\n2. Testing User Registration...")
    tests_total += 1
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Final Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ User registered: {user_data.get('email')}")
            tests_passed += 1
        else:
            print(f"   ❌ Registration failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return False
    
    # Test 3: User Login
    print("\n3. Testing User Login...")
    tests_total += 1
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data, headers=headers, timeout=5)
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
            print(f"   ✅ Login successful, token type: {tokens.get('token_type')}")
            tests_passed += 1
        else:
            print(f"   ❌ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    # Test 4: Create API Key
    print("\n4. Testing API Key Creation...")
    tests_total += 1
    jwt_headers = {"Authorization": f"Bearer {access_token}"}
    api_key_data = {
        "name": "Final Test API Key",
        "description": "Comprehensive test key"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/keys", json=api_key_data, headers=jwt_headers, timeout=5)
        if response.status_code == 200:
            key_result = response.json()
            api_key = key_result.get("api_key")
            print(f"   ✅ API Key created: {api_key[:20]}...")
            tests_passed += 1
        else:
            print(f"   ❌ API Key creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ API Key creation error: {e}")
        return False
    
    # Test 5: API Key Validation
    print("\n5. Testing API Key Validation...")
    tests_total += 1
    api_headers = {"X-API-Key": api_key}
    
    try:
        response = requests.get(f"{BASE_URL}/api/keys/validate", headers=api_headers, timeout=5)
        if response.status_code == 200:
            validation = response.json()
            print(f"   ✅ API Key valid: {validation.get('valid')}")
            tests_passed += 1
        else:
            print(f"   ❌ API Key validation failed: {response.text}")
    except Exception as e:
        print(f"   ❌ API Key validation error: {e}")
    
    # Test 6: LLM Models Access
    print("\n6. Testing LLM Models Access...")
    tests_total += 1
    
    try:
        response = requests.get(f"{BASE_URL}/llm/models", headers=api_headers, timeout=10)
        if response.status_code == 200:
            models = response.json()
            model_count = len(models) if isinstance(models, list) else 0
            print(f"   ✅ LLM Models accessible: {model_count} models")
            tests_passed += 1
        else:
            print(f"   ❌ LLM Models access failed: {response.text}")
    except Exception as e:
        print(f"   ❌ LLM Models access error: {e}")
    
    # Test 7: LLM Health Check
    print("\n7. Testing LLM Health...")
    tests_total += 1
    
    try:
        response = requests.get(f"{BASE_URL}/llm/health", headers=api_headers, timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ LLM Health: {health.get('status')}")
            tests_passed += 1
        else:
            print(f"   ❌ LLM Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ LLM Health check error: {e}")
    
    # Test 8: Subscription Info
    print("\n8. Testing Subscription Info...")
    tests_total += 1
    
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/current", headers=api_headers, timeout=5)
        if response.status_code == 200:
            subscription = response.json()
            print(f"   ✅ Subscription: {subscription.get('subscription')}")
            tests_passed += 1
        else:
            print(f"   ❌ Subscription info failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Subscription info error: {e}")
    
    # Test 9: Token Refresh
    print("\n9. Testing Token Refresh...")
    tests_total += 1
    refresh_data = {"refresh_token": refresh_token}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data, timeout=5)
        if response.status_code == 200:
            new_tokens = response.json()
            print(f"   ✅ Token refresh successful")
            tests_passed += 1
        else:
            print(f"   ❌ Token refresh failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Token refresh error: {e}")
    
    # Test 10: Error Handling
    print("\n10. Testing Error Handling...")
    tests_total += 1
    
    try:
        # Test invalid API key
        invalid_headers = {"X-API-Key": "invalid_key_12345"}
        response = requests.get(f"{BASE_URL}/llm/models", headers=invalid_headers, timeout=5)
        if response.status_code == 401:
            print(f"   ✅ Error handling works (401 for invalid key)")
            tests_passed += 1
        else:
            print(f"   ❌ Error handling failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error handling test error: {e}")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {tests_total}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_total - tests_passed}")
    success_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Completed: {datetime.now()}")
    
    if success_rate >= 90:
        print("\n🎉 EXCELLENT! System is production ready!")
        return True
    elif success_rate >= 70:
        print("\n⚠️  GOOD! Minor issues need attention.")
        return True
    else:
        print("\n🚨 CRITICAL! Major issues detected!")
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)
