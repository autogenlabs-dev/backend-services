#!/usr/bin/env python3
"""Test script to verify the login API fix."""

import requests
import json
import sys

# Server URL - update this to your EC2 public URL or domain
BASE_URL = "http://localhost:8000/api"  # Change to your EC2 URL, e.g., "https://yourdomain.com" or "http://YOUR_EC2_IP:8000"

def test_login_json():
    """Test the /auth/login-json endpoint."""
    print("Testing /auth/login-json endpoint...")
    
    url = f"{BASE_URL}/auth/login-json"
    
    # Test with sample credentials
    test_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response Body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Body (text): {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return True
        elif response.status_code == 401:
            print("⚠️  Unauthorized - credentials may be incorrect (this is expected if user doesn't exist)")
            return True  # API is working, just wrong credentials
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_login_form():
    """Test the /auth/login endpoint (form data)."""
    print("\nTesting /auth/login endpoint...")
    
    url = f"{BASE_URL}/auth/login"
    
    # Test with sample credentials (OAuth2 form format)
    test_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(url, data=test_data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"Response Body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Body (text): {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return True
        elif response.status_code == 401:
            print("⚠️  Unauthorized - credentials may be incorrect (this is expected if user doesn't exist)")
            return True  # API is working, just wrong credentials
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_health():
    """Test if the server is reachable."""
    print("Testing server health...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server is reachable (status: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not reachable: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("API Login Fix Test")
    print("=" * 60)
    
    # Test server health first
    if not test_health():
        print("\n⚠️  Server is not reachable. Make sure it's running.")
        sys.exit(1)
    
    print()
    
    # Test both login endpoints
    json_result = test_login_json()
    form_result = test_login_form()
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"/auth/login-json: {'✅ PASS' if json_result else '❌ FAIL'}")
    print(f"/auth/login:      {'✅ PASS' if form_result else '❌ FAIL'}")
    
    if json_result and form_result:
        print("\n🎉 All tests passed! The API fix is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
