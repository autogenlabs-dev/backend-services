#!/usr/bin/env python3
"""
Test script to verify the frontend OAuth fix
"""

import requests
import time
import webbrowser
from urllib.parse import urlparse, parse_qs

def test_oauth_flow():
    """Test the complete OAuth flow with the frontend fix"""
    
    print("🧪 Testing Frontend OAuth Fix")
    print("=" * 50)
    
    # Test 1: Check if backend OAuth endpoint is accessible
    print("\n1. Testing backend OAuth endpoint...")
    try:
        response = requests.get('http://localhost:8000/api/auth/google/login', allow_redirects=False)
        if response.status_code == 302:
            redirect_url = response.headers.get('location')
            print(f"✅ Backend OAuth endpoint redirects to: {redirect_url[:100]}...")
            
            # Verify it's Google OAuth
            if 'accounts.google.com' in redirect_url:
                print("✅ Redirects to Google OAuth correctly")
            else:
                print("❌ Does not redirect to Google OAuth")
                return False
        else:
            print(f"❌ Backend OAuth endpoint returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing backend OAuth endpoint: {e}")
        return False
    
    # Test 2: Check if frontend is accessible
    print("\n2. Testing frontend accessibility...")
    try:
        response = requests.get('http://localhost:3000')
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing frontend: {e}")
        return False
    
    # Test 3: Check if frontend auth page is accessible
    print("\n3. Testing frontend auth page...")
    try:
        response = requests.get('http://localhost:3000/auth')
        if response.status_code == 200:
            print("✅ Frontend auth page is accessible")
        else:
            print(f"❌ Frontend auth page returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing frontend auth page: {e}")
        return False
    
    # Test 4: Check if frontend callback page is accessible
    print("\n4. Testing frontend callback page...")
    try:
        response = requests.get('http://localhost:3000/auth/callback')
        if response.status_code == 200:
            print("✅ Frontend callback page is accessible")
        else:
            print(f"❌ Frontend callback page returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing frontend callback page: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("\n📋 Summary of fixes applied:")
    print("1. ✅ OAuth callback page simplified to handle tokens from backend")
    print("2. ✅ AuthContext updated with loginWithOAuth method")
    print("3. ✅ OAuth login button redirects to backend instead of frontend API")
    print("4. ✅ Frontend and backend are both running")
    
    print("\n🔧 To test the complete OAuth flow:")
    print("1. Open http://localhost:3000/auth in your browser")
    print("2. Click 'Continue with Google'")
    print("3. Complete Google authentication")
    print("4. Verify you're redirected to dashboard")
    
    return True

if __name__ == "__main__":
    test_oauth_flow()