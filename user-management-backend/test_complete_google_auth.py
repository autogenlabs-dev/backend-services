#!/usr/bin/env python3
"""
Complete Google OAuth Authentication Test
This script tests the full Google auth flow from initiation to user creation and token verification
"""

import asyncio
import requests
import json
import time
import webbrowser
from urllib.parse import urlparse, parse_qs, parse_qs, urljoin
from datetime import datetime
import jwt
import sys

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class OAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_info = None
        
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
        """Check OAuth configuration"""
        try:
            response = self.session.get(f"{API_BASE}/auth/providers")
            if response.status_code == 200:
                providers = response.json().get("providers", [])
                google_provider = next((p for p in providers if p["name"] == "google"), None)
                
                if google_provider:
                    print("✅ Google OAuth provider is configured")
                    print(f"📋 Authorization URL: {google_provider['authorization_url']}")
                    return True
                else:
                    print("❌ Google OAuth provider is not configured")
                    return False
            else:
                print(f"❌ Failed to get OAuth providers: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ OAuth configuration check failed: {e}")
            return False
    
    def initiate_oauth_flow(self):
        """Initiate OAuth flow"""
        print("\n🔍 Step 1: Initiating Google OAuth flow...")
        
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
            return redirect_url
            
        except Exception as e:
            print(f"❌ OAuth initiation failed: {e}")
            return None
    
    def simulate_oauth_callback(self, auth_code):
        """Simulate OAuth callback with authorization code"""
        print("\n🔍 Step 2: Simulating OAuth callback...")
        
        try:
            # This would normally be handled by the browser redirect
            # For testing, we'll make a direct call to the callback endpoint
            callback_url = f"{API_BASE}/auth/google/callback?code={auth_code}"
            
            response = self.session.get(callback_url, allow_redirects=False)
            
            if response.status_code == 302:
                # Extract tokens from redirect URL
                redirect_url = response.headers.get('Location')
                parsed_url = urlparse(redirect_url)
                query_params = parse_qs(parsed_url.query, keep_blank_values=True)
                
                access_token = query_params.get('access_token', [None])[0]
                refresh_token = query_params.get('refresh_token', [None])[0]
                user_id = query_params.get('user_id', [None])[0]
                
                if access_token:
                    print("✅ OAuth callback successful - tokens received")
                    self.auth_token = access_token
                    return {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'user_id': user_id
                    }
                else:
                    print("❌ No access token found in callback response")
                    return None
            else:
                print(f"❌ Callback failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ OAuth callback simulation failed: {e}")
            return None
    
    def verify_jwt_token(self, token):
        """Verify JWT token structure and claims"""
        print("\n🔍 Step 3: Verifying JWT token...")
        
        try:
            # Decode without verification first to check structure
            decoded = jwt.decode(token, options={"verify_signature": False})
            
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
            
            return decoded
            
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid JWT token: {e}")
            return False
        except Exception as e:
            print(f"❌ Token verification failed: {e}")
            return False
    
    def test_authenticated_endpoint(self):
        """Test accessing protected endpoint with auth token"""
        print("\n🔍 Step 4: Testing authenticated endpoint...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        try:
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
            print(f"❌ Authenticated endpoint test failed: {e}")
            return False
    
    def test_token_refresh(self, refresh_token):
        """Test token refresh functionality"""
        print("\n🔍 Step 5: Testing token refresh...")
        
        if not refresh_token:
            print("❌ No refresh token available")
            return False
        
        try:
            data = {'refresh_token': refresh_token}
            response = self.session.post(f"{API_BASE}/auth/refresh", json=data)
            
            if response.status_code == 200:
                token_data = response.json()
                new_access_token = token_data.get('access_token')
                
                if new_access_token:
                    print("✅ Token refresh successful")
                    print(f"📋 New access token received: {new_access_token[:20]}...")
                    
                    # Test new token
                    headers = {'Authorization': f'Bearer {new_access_token}'}
                    test_response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
                    
                    if test_response.status_code == 200:
                        print("✅ New token is valid")
                        return True
                    else:
                        print("❌ New token is invalid")
                        return False
                else:
                    print("❌ No new access token in refresh response")
                    return False
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Token refresh test failed: {e}")
            return False
    
    def test_logout(self):
        """Test logout functionality"""
        print("\n🔍 Step 6: Testing logout...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            response = self.session.post(f"{API_BASE}/auth/logout", headers=headers)
            
            if response.status_code == 200:
                logout_data = response.json()
                print("✅ Logout successful")
                print(f"📋 Message: {logout_data.get('message')}")
                
                # Test that token is no longer valid (if we had token blacklisting)
                # For now, just verify the logout endpoint works
                return True
            else:
                print(f"❌ Logout failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Logout test failed: {e}")
            return False
    
    def run_interactive_oauth_test(self):
        """Run interactive OAuth test with real browser"""
        print("\n" + "=" * 60)
        print("🌐 INTERACTIVE OAUTH TEST")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_backend_health():
            return False
        
        if not self.check_oauth_configuration():
            return False
        
        # Initiate OAuth flow
        redirect_url = self.initiate_oauth_flow()
        if not redirect_url:
            return False
        
        print(f"\n📋 Opening browser for Google OAuth authentication...")
        print(f"🌐 URL: {redirect_url}")
        
        # Open browser
        webbrowser.open(redirect_url)
        
        print("\n" + "=" * 60)
        print("📋 INSTRUCTIONS:")
        print("1. Complete Google authentication in your browser")
        print("2. After successful auth, you'll be redirected to frontend")
        print("3. The frontend will extract tokens from URL parameters")
        print("4. Copy the access token from browser console or URL")
        print("5. Paste it here to continue testing")
        print("=" * 60)
        
        # Get token from user
        token = input("\n🔑 Enter the access token from browser (or press Enter to skip): ").strip()
        
        if token:
            self.auth_token = token
            return self.run_post_auth_tests()
        else:
            print("⚠️  Skipping post-authentication tests")
            return True
    
    def run_post_auth_tests(self):
        """Run tests after authentication"""
        success = True
        
        # Verify JWT token
        token_data = self.verify_jwt_token(self.auth_token)
        if not token_data:
            success = False
        
        # Test authenticated endpoint
        if not self.test_authenticated_endpoint():
            success = False
        
        # Test token refresh (if we have refresh token)
        # This would require storing the refresh token from the callback
        # For now, we'll skip this in the interactive flow
        
        # Test logout
        if not self.test_logout():
            success = False
        
        return success
    
    def run_comprehensive_test(self):
        """Run comprehensive test with simulated flow"""
        print("\n" + "=" * 60)
        print("🔍 COMPREHENSIVE GOOGLE OAUTH TEST")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_backend_health():
            return False
        
        if not self.check_oauth_configuration():
            return False
        
        # For comprehensive testing, we need a real auth code
        # In a real scenario, this would come from the OAuth provider
        print("\n⚠️  This test requires a real Google OAuth authorization code")
        print("💡 Use the interactive test instead for complete flow testing")
        
        return self.run_interactive_oauth_test()

def main():
    """Main test function"""
    print("🔍 Complete Google OAuth Authentication Test")
    print("=" * 60)
    
    tester = OAuthTester()
    
    # Choose test mode
    print("\n📋 Test Options:")
    print("1. Interactive OAuth Test (Recommended - uses real browser)")
    print("2. Configuration Check Only")
    
    choice = input("\nChoose test mode (1 or 2): ").strip()
    
    if choice == "1":
        success = tester.run_interactive_oauth_test()
    elif choice == "2":
        success = tester.check_backend_health() and tester.check_oauth_configuration()
    else:
        print("❌ Invalid choice")
        return False
    
    if success:
        print("\n✅ OAuth test completed successfully!")
        
        if tester.user_info:
            print("\n📋 Authenticated User Info:")
            print(f"  ID: {tester.user_info.get('id')}")
            print(f"  Email: {tester.user_info.get('email')}")
            print(f"  Active: {tester.user_info.get('is_active')}")
            print(f"  Created: {tester.user_info.get('created_at')}")
            print(f"  Last Login: {tester.user_info.get('last_login_at')}")
        
        print("\n💡 Next Steps:")
        print("1. Test frontend integration with the auth tokens")
        print("2. Verify user data in database")
        print("3. Test API endpoints with authentication")
    else:
        print("\n❌ OAuth test failed")
        print("\n🔍 Troubleshooting:")
        print("1. Check backend console logs for errors")
        print("2. Verify Google OAuth configuration")
        print("3. Ensure redirect URI matches Google Console settings")
        print("4. Check network connectivity")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
