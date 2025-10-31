#!/usr/bin/env python3
"""
OAuth State Fix Script
This script identifies and fixes OAuth state management issues
"""

import requests
import json
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000/api"

def test_oauth_with_session():
    """Test OAuth flow with proper session handling"""
    print("🔍 Testing OAuth with Session Management")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Initiate OAuth login with session
    print("\n1. Initiating OAuth login with session...")
    response = session.get(f"{BASE_URL}/auth/google/login", allow_redirects=False)
    
    if response.status_code != 302:
        print(f"❌ Failed to initiate OAuth: {response.status_code}")
        return False, None, None
    
    redirect_url = response.headers.get('Location')
    print(f"✅ OAuth initiated. Redirect URL: {redirect_url[:100]}...")
    
    # Check if session cookies were set
    cookies = session.cookies.get_dict()
    print(f"🍪 Session cookies: {cookies}")
    
    # Extract state from redirect URL
    if redirect_url:
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        state_list = query_params.get('state', [])
        state = state_list[0] if state_list else None
    else:
        state = None
    
    if not state:
        print("❌ No state parameter found in OAuth URL")
        return False, None, None
    
    print(f"📋 State parameter: {state}")
    
    # Step 2: Test callback with same session
    print("\n2. Testing callback with same session...")
    callback_url = f"{BASE_URL}/auth/google/callback?code=mock_code&state={state}"
    
    callback_response = session.get(callback_url, allow_redirects=False)
    print(f"Callback response status: {callback_response.status_code}")
    
    if callback_response.status_code == 302:
        final_redirect = callback_response.headers.get('Location')
        print(f"✅ Successful redirect to: {final_redirect}")
        return True, state, session
    else:
        print(f"❌ Callback failed with status: {callback_response.status_code}")
        try:
            error_detail = callback_response.json()
            print(f"Error details: {json.dumps(error_detail, indent=2)}")
        except:
            print(f"Error response: {callback_response.text}")
        return False, state, session

def check_server_logs():
    """Check server logs for OAuth errors"""
    print("\n🔍 Checking for common OAuth issues...")
    
    issues = []
    
    # Check if OpenRouter has placeholder credentials
    with open('.env', 'r') as f:
        env_content = f.read()
        if 'your_openrouter_client_id' in env_content:
            issues.append("OpenRouter OAuth has placeholder credentials")
    
    # Check session middleware configuration
    try:
        with open('app/main.py', 'r') as f:
            main_content = f.read()
            if 'SessionMiddleware' in main_content:
                print("✅ SessionMiddleware is configured")
            else:
                issues.append("SessionMiddleware not found in main.py")
    except FileNotFoundError:
        issues.append("Could not read app/main.py")
    
    return issues

def main():
    """Main function to diagnose and suggest fixes"""
    print("=" * 60)
    print("🔍 OAuth State Management Fix")
    print("=" * 60)
    
    # Test OAuth with session
    success, state, session = test_oauth_with_session()
    
    # Check for common issues
    issues = check_server_logs()
    
    # Summary and recommendations
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS SUMMARY")
    print("=" * 60)
    print(f"OAuth with session: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"State parameter extracted: {'✅ YES' if state else '❌ NO'}")
    
    if issues:
        print("\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"❌ {issue}")
    
    if not success:
        print("\n💡 RECOMMENDED FIXES:")
        print("1. Ensure SessionMiddleware is properly configured")
        print("2. Check that cookies are being set and maintained")
        print("3. Verify OAuth state storage in session")
        print("4. Update OpenRouter OAuth credentials")
        print("5. Check CORS configuration for frontend-backend communication")
        
        print("\n🔧 IMMEDIATE ACTIONS:")
        print("- Fix OpenRouter OAuth credentials in .env file")
        print("- Test OAuth flow manually in browser")
        print("- Monitor server logs during OAuth attempts")

if __name__ == "__main__":
    main()
