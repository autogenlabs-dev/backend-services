#!/usr/bin/env python3
"""
Real OAuth Flow Test Script
This script tests the actual OAuth flow by opening the browser for real authentication
"""

import webbrowser
import time
import requests
import json
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000/api"

def test_real_oauth_flow():
    """Test the real OAuth flow by opening browser"""
    print("🔍 Testing Real OAuth Flow for Google")
    print("=" * 60)
    
    # Step 1: Initiate OAuth login
    print("\n1. Initiating OAuth login...")
    response = requests.get(f"{BASE_URL}/auth/google/login", allow_redirects=False)
    
    if response.status_code != 302:
        print(f"❌ Failed to initiate OAuth: {response.status_code}")
        return False
    
    redirect_url = response.headers.get('Location')
    print(f"✅ OAuth initiated.")
    print(f"🌐 Opening browser for authentication...")
    print(f"📋 Login URL: {redirect_url[:100]}...")
    
    # Open browser for real OAuth authentication
    if redirect_url:
        webbrowser.open(redirect_url)
    else:
        print("❌ No redirect URL found in OAuth response")
        return False
    
    print("\n" + "=" * 60)
    print("📋 INSTRUCTIONS:")
    print("1. Complete the Google OAuth authentication in your browser")
    print("2. After successful authentication, you'll be redirected to the frontend")
    print("3. The frontend callback should extract tokens and log you in")
    print("4. Check the browser console for token extraction logs")
    print("\n💡 Expected flow:")
    print("- Google login → Backend callback → Frontend redirect → Token extraction")
    print("=" * 60)
    
    # Monitor backend for callback processing
    print("\n🔍 Monitoring for OAuth callback...")
    print("The backend will show debug logs when the callback is processed.")
    print("Look for messages like:")
    print("  🔍 OAuth callback for google")
    print("  🔍 Authorization code received: ...")
    print("  🔍 Token exchange successful!")
    print("  🔍 User identified: user@example.com")
    print("  🔍 JWT tokens created for user...")
    print("  🔍 Redirecting to: http://localhost:3000/auth/callback...")
    
    return True

def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(BASE_URL.replace('/api', '/health'), timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            return True
    except:
        pass
    
    print("❌ Backend is not running or not healthy")
    return False

def main():
    """Main testing function"""
    print("🔍 Real OAuth Flow Test")
    print("=" * 60)
    
    # Check backend health
    if not check_backend_health():
        print("\n💡 Please start the backend server first:")
        print("   cd /home/cis/Downloads/backend-services/user-management-backend")
        print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        return False
    
    # Test real OAuth flow
    success = test_real_oauth_flow()
    
    if success:
        print("\n✅ OAuth flow test initiated successfully!")
        print("📋 Complete the authentication in your browser to test the full flow")
        print("\n🔍 If you encounter issues:")
        print("1. Check backend console for debug messages")
        print("2. Check browser console for token extraction errors")
        print("3. Verify frontend callback page exists at /auth/callback")
        print("4. Ensure redirect URI matches Google OAuth configuration")
    else:
        print("\n❌ OAuth flow test failed")
    
    return success

if __name__ == "__main__":
    main()
