#!/usr/bin/env python3
"""
Debug OAuth Callback Script
This script simulates the complete OAuth flow to identify issues
"""

import requests
import json
import time
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000/api"

def test_complete_oauth_flow():
    """Test the complete OAuth flow for Google"""
    print("🔍 Testing Complete OAuth Flow for Google")
    
    # Step 1: Initiate OAuth login
    print("\n1. Initiating OAuth login...")
    response = requests.get(f"{BASE_URL}/auth/google/login", allow_redirects=False)
    
    if response.status_code != 302:
        print(f"❌ Failed to initiate OAuth: {response.status_code}")
        return False
    
    redirect_url = response.headers.get('Location')
    print(f"✅ OAuth initiated. Redirect URL: {redirect_url[:100]}...")
    
    # Extract state from redirect URL for testing
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    state_list = query_params.get('state', [])
    state = state_list[0] if state_list else None
    
    if not state:
        print("❌ No state parameter found in OAuth URL")
        return False
    
    print(f"📋 State parameter: {state}")
    
    # Step 2: Simulate callback with mock authorization code
    print("\n2. Simulating OAuth callback...")
    
    # Note: This will fail because we don't have a real authorization code
    # But it will help us see the exact error
    callback_url = f"{BASE_URL}/auth/google/callback?code=mock_code&state={state}"
    
    try:
        callback_response = requests.get(callback_url, allow_redirects=False)
        print(f"Callback response status: {callback_response.status_code}")
        
        if callback_response.status_code == 302:
            final_redirect = callback_response.headers.get('Location')
            print(f"✅ Successful redirect to: {final_redirect}")
            
            # Check if tokens are in the redirect URL
            if final_redirect and 'access_token=' in final_redirect:
                print("✅ Access token found in redirect URL")
                return True
            else:
                print("❌ No access token found in redirect URL")
                return False
        else:
            print(f"❌ Callback failed with status: {callback_response.status_code}")
            try:
                error_detail = callback_response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Error response: {callback_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Callback request failed: {str(e)}")
        return False

def check_frontend_availability():
    """Check if frontend is running on port 3000"""
    print("\n🔍 Checking frontend availability...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        print(f"✅ Frontend is running on port 3000 (status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not running on port 3000")
        return False
    except Exception as e:
        print(f"❌ Error checking frontend: {str(e)}")
        return False

def main():
    """Main debugging function"""
    print("=" * 60)
    print("🔍 OAuth Debug Script")
    print("=" * 60)
    
    # Check frontend availability
    frontend_running = check_frontend_availability()
    
    # Test OAuth flow
    oauth_success = test_complete_oauth_flow()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEBUG SUMMARY")
    print("=" * 60)
    print(f"Frontend running (port 3000): {'✅ YES' if frontend_running else '❌ NO'}")
    print(f"OAuth flow test: {'✅ SUCCESS' if oauth_success else '❌ FAILED'}")
    
    if not frontend_running:
        print("\n💡 RECOMMENDATION:")
        print("The original error suggests a frontend is trying to connect.")
        print("Start the frontend application on port 3000 and try again.")
        print("The OAuth callback URL is configured for http://localhost:3000/auth/callback")
    
    if not oauth_success:
        print("\n💡 OAuth ISSUES FOUND:")
        print("Check server logs for detailed OAuth error information")
        print("Ensure OAuth providers are properly configured")
        print("Verify redirect URIs match in OAuth provider settings")

if __name__ == "__main__":
    main()
