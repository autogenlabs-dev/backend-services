#!/usr/bin/env python3
"""
Simple Login Response Test
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"login_test_{int(time.time())}@example.com"
TEST_PASSWORD = "LoginTest123!"

def main():
    print("🔐 Login Response Test")
    print("=" * 40)
    
    # 1. Register
    print("1. Registering user...")
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Login Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data, timeout=5)
        print(f"   Registration status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"   Registration failed: {e}")
        return
    
    # 2. Login and show complete response
    print("\n2. Logging in...")
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            tokens = response.json()
            print("\n📋 COMPLETE LOGIN RESPONSE:")
            print("=" * 50)
            print(json.dumps(tokens, indent=2))
            print("=" * 50)
            
            print("\n🔍 RESPONSE FIELDS:")
            for key, value in tokens.items():
                if key == "access_token":
                    print(f"   {key}: {str(value)[:50]}...")
                elif key == "refresh_token":
                    print(f"   {key}: {str(value)[:50]}...")
                else:
                    print(f"   {key}: {value}")
        else:
            print(f"   Login failed: {response.text}")
            
    except Exception as e:
        print(f"   Login failed: {e}")

if __name__ == "__main__":
    main()
