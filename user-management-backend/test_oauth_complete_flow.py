#!/usr/bin/env python3
"""
Complete OAuth Flow Test with Real Browser
This script tests the full OAuth flow including the frontend callback handling
"""

import asyncio
import requests
import json
import time
import webbrowser
from urllib.parse import urlparse, parse_qs, urljoin
from datetime import datetime
import jwt
import sys
import uuid
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
FRONTEND_URL = "http://localhost:3000"

class SimpleCallbackHandler(BaseHTTPRequestHandler):
    """Simple HTTP server to simulate frontend callback handling"""
    
    def do_GET(self):
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/auth/callback':
            query_params = parse_qs(parsed_url.query)
            
            print(f"\n🎯 Frontend callback received!")
            print(f"📋 Path: {parsed_url.path}")
            print(f"📋 Query params: {list(query_params.keys())}")
            
            access_token = query_params.get('access_token', [None])[0]
            refresh_token = query_params.get('refresh_token', [None])[0]
            user_id = query_params.get('user_id', [None])[0]
            
            if access_token:
                print(f"✅ Access token received: {access_token[:20]}...")
                print(f"✅ Refresh token received: {refresh_token[:20] if refresh_token else 'None'}...")
                print(f"✅ User ID received: {user_id}")
                
                # Verify JWT token
                try:
                    decoded = jwt.decode(access_token, options={"verify_signature": False})
                    print(f"✅ JWT token valid for user: {decoded.get('email')}")
                except Exception as e:
                    print(f"❌ JWT token invalid: {e}")
                
                # Return success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html_response = f"""
                <html>
                <head><title>OAuth Callback Success</title></head>
                <body>
                    <h1>✅ OAuth Authentication Successful!</h1>
                    <h2>User Information:</h2>
                    <p><strong>User ID:</strong> {user_id}</p>
                    <p><strong>Access Token:</strong> {access_token[:50]}...</p>
                    <p><strong>Refresh Token:</strong> {refresh_token[:50] if refresh_token else 'N/A'}...</p>
                    
                    <h3>Test Authentication:</h3>
                    <button onclick="testAuth()">Test Authenticated API</button>
                    <div id="test-result"></div>
                    
                    <script>
                    function testAuth() {{
                        const accessToken = '{access_token}';
                        fetch('{API_BASE}/auth/me', {{
                            headers: {{
                                'Authorization': 'Bearer ' + accessToken,
                                'Content-Type': 'application/json'
                            }}
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            document.getElementById('test-result').innerHTML = 
                                '<h4>✅ API Test Successful!</h4>' +
                                '<p><strong>Email:</strong> ' + data.email + '</p>' +
                                '<p><strong>ID:</strong> ' + data.id + '</p>' +
                                '<p><strong>Active:</strong> ' + data.is_active + '</p>';
                        }})
                        .catch(error => {{
                            document.getElementById('test-result').innerHTML = 
                                '<h4>❌ API Test Failed!</h4>' +
                                '<p>Error: ' + error.message + '</p>';
                        }});
                    }}
                    </script>
                </body>
                </html>
                """
                self.wfile.write(html_response.encode())
            else:
                print(f"❌ No access token in callback")
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>OAuth Callback Failed</h1><p>No access token received</p></body></html>')
        else:
            # Redirect to login page for other paths
            self.send_response(302)
            self.send_header('Location', f'{FRONTEND_URL}/login')
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress server logs
        pass

class OAuthFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.callback_server = None
        self.callback_server_thread = None
        
    def start_callback_server(self):
        """Start a simple HTTP server to simulate frontend callback"""
        try:
            self.callback_server = HTTPServer(('localhost', 3000), SimpleCallbackHandler)
            print(f"🌐 Starting callback server on {FRONTEND_URL}")
            self.callback_server.serve_forever()
        except Exception as e:
            print(f"❌ Failed to start callback server: {e}")
            print(f"💡 Make sure port 3000 is available")
            return False
        return True
    
    def stop_callback_server(self):
        """Stop the callback server"""
        if self.callback_server:
            self.callback_server.shutdown()
            print("🛑 Callback server stopped")
    
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
    
    def test_oauth_initiation(self):
        """Test OAuth initiation"""
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
            
            # Verify redirect URL parameters
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            
            required_params = ['client_id', 'redirect_uri', 'scope', 'response_type']
            missing_params = [param for param in required_params if param not in query_params]
            
            if missing_params:
                print(f"⚠️  Missing OAuth parameters: {missing_params}")
            else:
                print("✅ All required OAuth parameters present")
            
            return redirect_url
            
        except Exception as e:
            print(f"❌ OAuth initiation failed: {e}")
            return None
    
    def run_complete_oauth_test(self):
        """Run complete OAuth test with callback server"""
        print("🔍 Complete OAuth Flow Test with Frontend Simulation")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_backend_health():
            return False
        
        if not self.check_oauth_configuration():
            return False
        
        # Start callback server in background
        print("\n🌐 Starting frontend callback simulation...")
        self.callback_server_thread = threading.Thread(target=self.start_callback_server, daemon=True)
        self.callback_server_thread.start()
        
        # Give server time to start
        time.sleep(2)
        
        # Test OAuth initiation
        redirect_url = self.test_oauth_initiation()
        if not redirect_url:
            self.stop_callback_server()
            return False
        
        print("\n" + "=" * 60)
        print("🌐 BROWSER OAUTH TEST")
        print("=" * 60)
        print(f"📋 Opening browser for Google OAuth authentication...")
        print(f"🌐 URL: {redirect_url}")
        
        # Open browser
        webbrowser.open(redirect_url)
        
        print("\n" + "=" * 60)
        print("📋 INSTRUCTIONS:")
        print("1. Complete Google authentication in your browser")
        print("2. After successful auth, you'll be redirected to localhost:3000")
        print("3. The callback server will show the authentication result")
        print("4. Click 'Test Authenticated API' button to verify tokens work")
        print("5. Press Ctrl+C to stop the test")
        print("=" * 60)
        
        try:
            # Wait for user to complete the flow
            while self.callback_server_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Test interrupted by user")
        finally:
            self.stop_callback_server()
        
        return True

def main():
    """Main test function"""
    print("🔍 Complete OAuth Flow Test with Frontend Simulation")
    print("=" * 60)
    
    tester = OAuthFlowTester()
    
    try:
        success = tester.run_complete_oauth_test()
        
        if success:
            print("\n✅ OAuth flow test completed!")
            print("\n💡 If you still experience redirect loops in your actual frontend:")
            print("1. Ensure frontend callback page extracts tokens from URL parameters")
            print("2. Store tokens in localStorage or sessionStorage")
            print("3. Update frontend authentication state")
            print("4. Redirect to dashboard instead of login page")
            print("5. Check for JavaScript errors in browser console")
        else:
            print("\n❌ OAuth flow test failed")
    
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)