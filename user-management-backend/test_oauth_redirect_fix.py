#!/usr/bin/env python3
"""
Comprehensive OAuth Redirect Fix Test
This script tests the complete OAuth flow and identifies the redirect loop issue
"""

import asyncio
import requests
import json
import time
import webbrowser
from urllib.parse import urlparse, parse_qs, urljoin, urlencode
from datetime import datetime
import jwt
import sys
import uuid

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class OAuthRedirectTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.refresh_token = None
        self.user_info = None
        self.test_user_email = f"test-{uuid.uuid4().hex[:8]}@example.com"
        
    def check_backend_health(self):
        """Check if backend is running"""
        try:
            response = self.session.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is running and healthy")
                return True
        except Exception as e:
            print(f"❌ Backend health check failed: {e}")
        
        print("❌ Backend is not running or not healthy")
        return False
    
    def check_oauth_configuration(self):
        """Check OAuth configuration and debug info"""
        try:
            # Check providers
            response = self.session.get(f"{API_BASE}/auth/providers")
            if response.status_code == 200:
                providers = response.json().get("providers", [])
                google_provider = next((p for p in providers if p["name"] == "google"), None)
                
                if google_provider:
                    print("✅ Google OAuth provider is configured")
                    print(f"📋 Authorization URL: {google_provider['authorization_url']}")
                else:
                    print("❌ Google OAuth provider is not configured")
                    return False
            else:
                print(f"❌ Failed to get OAuth providers: {response.status_code}")
                return False
            
            # Check debug endpoint
            response = self.session.get(f"{API_BASE}/auth/debug/oauth")
            if response.status_code == 200:
                debug_info = response.json()
                print("🔍 OAuth Debug Info:")
                print(f"  Google configured: {debug_info['oauth_providers'].get('google', {}).get('configured', False)}")
                print(f"  Client ID set: {debug_info['oauth_providers'].get('google', {}).get('client_id_set', False)}")
                print(f"  Client secret set: {debug_info['oauth_providers'].get('google', {}).get('client_secret_set', False)}")
                
                if not debug_info['oauth_providers'].get('google', {}).get('configured'):
                    print("❌ Google OAuth is not properly configured")
                    return False
            else:
                print(f"❌ Failed to get OAuth debug info: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"❌ OAuth configuration check failed: {e}")
            return False
    
    def test_oauth_initiation(self):
        """Test OAuth initiation and capture redirect URL"""
        print("\n🔍 Step 1: Testing OAuth initiation...")
        
        try:
            response = self.session.get(f"{API_BASE}/auth/google/login", allow_redirects=False)
            
            if response.status_code != 302:
                print(f"❌ Failed to initiate OAuth: {response.status_code}")
                print(f"Response: {response.text}")
                return None
            
            redirect_url = response.headers.get('Location')
            if not redirect_url:
                print("❌ No redirect URL found in OAuth response")
                return None
            
            print(f"✅ OAuth flow initiated successfully")
            print(f"🌐 Redirect URL: {redirect_url[:100]}...")
            
            # Parse redirect URL to verify it contains required parameters
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            
            required_params = ['client_id', 'redirect_uri', 'scope', 'response_type']
            missing_params = [param for param in required_params if param not in query_params]
            
            if missing_params:
                print(f"⚠️  Missing OAuth parameters: {missing_params}")
            else:
                print("✅ All required OAuth parameters present")
            
            # Check redirect URI
            redirect_uri = query_params.get('redirect_uri', [None])[0]
            if redirect_uri:
                print(f"📋 OAuth Redirect URI: {redirect_uri}")
                if 'localhost:8000' in redirect_uri:
                    print("✅ Using development redirect URI")
                elif 'api.codemurf.com' in redirect_uri:
                    print("✅ Using production redirect URI")
                else:
                    print(f"⚠️  Unexpected redirect URI: {redirect_uri}")
            
            return redirect_url
            
        except Exception as e:
            print(f"❌ OAuth initiation test failed: {e}")
            return None
    
    def simulate_oauth_callback_with_code(self, auth_code):
        """Simulate OAuth callback with a real authorization code"""
        print("\n🔍 Step 2: Testing OAuth callback with authorization code...")
        
        try:
            callback_url = f"{API_BASE}/auth/google/callback?code={auth_code}"
            
            # Follow redirects to see the complete flow
            response = self.session.get(callback_url, allow_redirects=False)
            
            print(f"📋 Callback response status: {response.status_code}")
            
            if response.status_code == 302:
                # Extract tokens from redirect URL
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    print(f"📋 Redirect URL: {redirect_url[:100]}...")
                    
                    parsed_url = urlparse(redirect_url)
                    query_params = parse_qs(parsed_url.query, keep_blank_values=True)
                    
                    access_token = query_params.get('access_token', [None])[0] if query_params else None
                    refresh_token = query_params.get('refresh_token', [None])[0] if query_params else None
                    user_id = query_params.get('user_id', [None])[0] if query_params else None
                else:
                    access_token = None
                    refresh_token = None
                    user_id = None
                
                if access_token:
                    print("✅ OAuth callback successful - tokens received")
                    print(f"📋 Access token: {access_token[:20]}...")
                    print(f"📋 User ID: {user_id}")
                    
                    self.auth_token = access_token
                    self.refresh_token = refresh_token
                    
                    return {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'user_id': user_id,
                        'redirect_url': redirect_url
                    }
                else:
                    print("❌ No access token found in callback response")
                    print("📋 Check if tokens are being properly passed in redirect URL")
                    return None
            else:
                print(f"❌ Callback failed: {response.status_code}")
                print(f"Response: {response.text[:500]}...")
                return None
                
        except Exception as e:
            print(f"❌ OAuth callback simulation failed: {e}")
            return None
    
    def test_token_verification(self):
        """Test JWT token verification and user info"""
        print("\n🔍 Step 3: Testing token verification...")
        
        if not self.auth_token:
            print("❌ No access token available")
            return False
        
        try:
            # Decode token without verification first
            decoded = jwt.decode(self.auth_token, options={"verify_signature": False})
            print("✅ JWT token structure is valid")
            print(f"📋 Token claims: {list(decoded.keys())}")
            
            # Check required claims
            required_claims = ['sub', 'email', 'exp', 'iat']
            missing_claims = [claim for claim in required_claims if claim not in decoded]
            
            if missing_claims:
                print(f"⚠️  Missing claims: {missing_claims}")
            else:
                print("✅ All required claims present")
            
            # Check expiration
            if 'exp' in decoded:
                exp_time = datetime.fromtimestamp(decoded['exp'])
                if exp_time > datetime.now():
                    print(f"✅ Token is valid until: {exp_time}")
                else:
                    print("❌ Token has expired")
                    return False
            
            # Test authenticated endpoint
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print("✅ Authenticated endpoint access successful")
                print(f"📋 User ID: {user_data.get('id')}")
                print(f"📋 Email: {user_data.get('email')}")
                print(f"📋 Active: {user_data.get('is_active')}")
                
                self.user_info = user_data
                return True
            else:
                print(f"❌ Authenticated endpoint access failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Token verification failed: {e}")
            return False
    
    def test_redirect_loop_detection(self):
        """Test for potential redirect loops in the OAuth flow"""
        print("\n🔍 Step 4: Testing for redirect loops...")
        
        # Test 1: Check if callback redirects to login page
        print("📋 Testing callback redirect behavior...")
        
        # Simulate a callback without proper authorization
        callback_url = f"{API_BASE}/auth/google/callback?error=access_denied"
        response = self.session.get(callback_url, allow_redirects=False)
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location')
            print(f"📋 Error callback redirects to: {redirect_url}")
            
            # Check if it redirects back to login (which could cause a loop)
            if redirect_url and 'login' in redirect_url.lower():
                print("⚠️  Error callback redirects to login page - potential loop issue")
            else:
                print("✅ Error callback redirects appropriately")
        
        # Test 2: Check session handling
        print("📋 Testing session handling...")
        response = self.session.get(f"{API_BASE}/auth/debug/cleanup")
        if response.status_code == 200:
            print("✅ Session cleanup endpoint works")
        
        return True
    
    def test_complete_flow_simulation(self):
        """Test complete OAuth flow with simulated browser behavior"""
        print("\n🔍 Step 5: Testing complete flow simulation...")
        
        # Clear any existing session
        self.session.get(f"{API_BASE}/auth/debug/cleanup")
        
        # Step 1: Initiate OAuth
        redirect_url = self.test_oauth_initiation()
        if not redirect_url:
            return False
        
        # Step 2: Extract OAuth parameters for manual testing
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        
        state = query_params.get('state', [None])[0]
        redirect_uri = query_params.get('redirect_uri', [None])[0]
        
        print(f"📋 OAuth State: {state}")
        print(f"📋 Expected Redirect URI: {redirect_uri}")
        
        print("\n" + "=" * 60)
        print("🌐 MANUAL OAUTH TEST INSTRUCTIONS")
        print("=" * 60)
        print(f"1. Open this URL in your browser:")
        print(f"   {redirect_url}")
        print(f"2. Complete Google authentication")
        print(f"3. After authentication, copy the authorization code from the browser URL")
        print(f"4. The URL will look like: {redirect_uri}?code=...&state=...")
        print(f"5. Copy the 'code' parameter value")
        print("=" * 60)
        
        # Get authorization code from user
        auth_code = input("\n🔑 Enter the authorization code from browser (or press Enter to skip): ").strip()
        
        if auth_code:
            # Test the callback with the real authorization code
            result = self.simulate_oauth_callback_with_code(auth_code)
            if result:
                # Test token verification
                if self.test_token_verification():
                    print("✅ Complete OAuth flow test successful!")
                    return True
                else:
                    print("❌ Token verification failed")
                    return False
            else:
                print("❌ OAuth callback failed")
                return False
        else:
            print("⚠️  Skipping manual OAuth test")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive OAuth redirect test"""
        print("🔍 Comprehensive OAuth Redirect Fix Test")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_backend_health():
            return False
        
        if not self.check_oauth_configuration():
            return False
        
        success = True
        
        # Test OAuth initiation
        redirect_url = self.test_oauth_initiation()
        if not redirect_url:
            success = False
        
        # Test redirect loop detection
        if not self.test_redirect_loop_detection():
            success = False
        
        # Test complete flow simulation
        if not self.test_complete_flow_simulation():
            success = False
        
        return success

def main():
    """Main test function"""
    print("🔍 OAuth Redirect Loop Detection and Fix Test")
    print("=" * 60)
    
    tester = OAuthRedirectTester()
    
    # Run comprehensive test
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ OAuth redirect test completed successfully!")
        
        if tester.user_info:
            print("\n📋 Authenticated User Info:")
            print(f"  ID: {tester.user_info.get('id')}")
            print(f"  Email: {tester.user_info.get('email')}")
            print(f"  Active: {tester.user_info.get('is_active')}")
            print(f"  Created: {tester.user_info.get('created_at')}")
            print(f"  Last Login: {tester.user_info.get('last_login_at')}")
        
        print("\n💡 If you still experience redirect loops:")
        print("1. Check frontend callback page implementation")
        print("2. Verify token extraction and storage in frontend")
        print("3. Ensure frontend properly handles authentication state")
        print("4. Check for CORS issues between frontend and backend")
    else:
        print("\n❌ OAuth redirect test failed")
        print("\n🔍 Common redirect loop causes:")
        print("1. Frontend callback page not extracting tokens properly")
        print("2. Frontend not storing tokens in localStorage/sessionStorage")
        print("3. Frontend redirecting back to login after successful auth")
        print("4. CORS issues preventing token access")
        print("5. Frontend authentication state not updated correctly")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)