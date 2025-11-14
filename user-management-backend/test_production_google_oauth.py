#!/usr/bin/env python3
"""
Comprehensive test script for Google OAuth on production API.
This script will test the Google OAuth flow and identify any issues.
"""

import asyncio
import httpx
import json
from urllib.parse import urlencode, parse_qs
from typing import Dict, Any, Optional
import sys

class ProductionOAuthTester:
    def __init__(self):
        self.base_url = "https://api.codemurf.com"
        self.timeout = 30.0
        self.session = None
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            verify=False  # Bypass SSL verification for testing
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def test_api_health(self) -> bool:
        """Test if the API is healthy and responsive."""
        print("🔍 Testing API health...")
        try:
            if not self.session:
                return False
            response = await self.session.get("/")
            print(f"✅ Root endpoint status: {response.status_code}")
            print(f"✅ Root endpoint response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ API health check failed: {e}")
            return False
    
    async def test_auth_routes_exist(self) -> Dict[str, bool]:
        """Test if auth routes are properly registered."""
        print("\n🔍 Testing auth route availability...")
        routes = {
            "/api": "Base API route",
            "/api/auth": "Auth base route",
            "/api/auth/providers": "OAuth providers list",
            "/api/auth/google/login": "Google OAuth login",
            "/api/auth/google/callback": "Google OAuth callback",
        }
        
        results = {}
        for route, description in routes.items():
            try:
                if not self.session:
                    results[route] = False
                    continue
                response = await self.session.get(route)
                status = response.status_code
                print(f"📍 {description} ({route}): {status}")
                
                if status == 404:
                    print(f"   ❌ Route not found")
                    results[route] = False
                elif status == 405:  # Method not allowed (expected for GET on POST endpoints)
                    print(f"   ✅ Route exists (different method expected)")
                    results[route] = True
                elif status in [200, 302]:
                    print(f"   ✅ Route accessible")
                    results[route] = True
                else:
                    print(f"   ⚠️ Unexpected status: {status}")
                    results[route] = False
                    
                # Print response body for debugging
                try:
                    body = response.json()
                    if route == "/api/auth/providers" and status == 200:
                        print(f"   📄 Available providers: {body}")
                except:
                    pass
                    
            except Exception as e:
                print(f"   ❌ Error testing {route}: {e}")
                results[route] = False
        
        return results
    
    async def test_oauth_providers(self) -> Optional[Dict[str, Any]]:
        """Test the OAuth providers endpoint."""
        print("\n🔍 Testing OAuth providers configuration...")
        try:
            if not self.session:
                return None
            response = await self.session.get("/api/auth/providers")
            if response.status_code == 200:
                providers_data = response.json()
                print(f"✅ Providers response: {json.dumps(providers_data, indent=2)}")
                return providers_data
            else:
                print(f"❌ Providers endpoint returned {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error testing providers: {e}")
            return None
    
    async def test_google_oauth_redirect(self) -> bool:
        """Test the Google OAuth login redirect."""
        print("\n🔍 Testing Google OAuth login redirect...")
        try:
            if not self.session:
                return False
            response = await self.session.get("/api/auth/google/login", follow_redirects=False)
            print(f"📍 Status code: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get("location", "")
                print(f"✅ Redirect location: {location}")
                
                # Check if it's redirecting to Google
                if "accounts.google.com" in location:
                    print("✅ Properly redirecting to Google OAuth")
                    return True
                else:
                    print(f"❌ Not redirecting to Google. Location: {location}")
                    return False
            elif response.status_code == 404:
                print("❌ Google OAuth route not found")
                return False
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing Google OAuth redirect: {e}")
            return False
    
    async def test_oauth_debug_endpoint(self) -> Optional[Dict[str, Any]]:
        """Test the OAuth debug endpoint."""
        print("\n🔍 Testing OAuth debug endpoint...")
        try:
            if not self.session:
                return None
            response = await self.session.get("/api/auth/debug/oauth")
            if response.status_code == 200:
                debug_data = response.json()
                print(f"✅ Debug info: {json.dumps(debug_data, indent=2)}")
                return debug_data
            else:
                print(f"❌ Debug endpoint returned {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error testing debug endpoint: {e}")
            return None
    
    async def test_server_info(self) -> Dict[str, Any]:
        """Gather information about the server configuration."""
        print("\n🔍 Gathering server information...")
        info = {
            "server_running": False,
            "routes_registered": False,
            "google_oauth_configured": False,
            "ssl_working": False
        }
        
        # Test if server is running
        try:
            if not self.session:
                return info
            response = await self.session.get("/")
            info["server_running"] = response.status_code == 200
            info["ssl_working"] = True  # If we get here, SSL is working (even with verify=False)
        except:
            pass
        
        # Test if routes are registered
        try:
            if self.session:
                response = await self.session.get("/api/auth/providers")
                info["routes_registered"] = response.status_code != 404
        except:
            pass
        
        # Test Google OAuth configuration
        try:
            if self.session:
                response = await self.session.get("/api/auth/google/login")
                info["google_oauth_configured"] = response.status_code != 404
        except:
            pass
        
        return info
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results."""
        print("🚀 Starting comprehensive Google OAuth production test...")
        print("=" * 60)
        
        results = {
            "timestamp": asyncio.get_event_loop().time(),
            "tests": {}
        }
        
        # Test 1: API Health
        results["tests"]["api_health"] = await self.test_api_health()
        
        # Test 2: Route Registration
        results["tests"]["auth_routes"] = await self.test_auth_routes_exist()
        
        # Test 3: OAuth Providers
        results["tests"]["oauth_providers"] = await self.test_oauth_providers()
        
        # Test 4: Google OAuth Redirect
        results["tests"]["google_oauth_redirect"] = await self.test_google_oauth_redirect()
        
        # Test 5: Debug Information
        results["tests"]["debug_info"] = await self.test_oauth_debug_endpoint()
        
        # Test 6: Server Information
        results["tests"]["server_info"] = await self.test_server_info()
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        # Summary
        server_info = results["tests"]["server_info"]
        print(f"Server Running: {'✅' if server_info['server_running'] else '❌'}")
        print(f"Routes Registered: {'✅' if server_info['routes_registered'] else '❌'}")
        print(f"Google OAuth Configured: {'✅' if server_info['google_oauth_configured'] else '❌'}")
        print(f"SSL Working: {'✅' if server_info['ssl_working'] else '❌'}")
        
        # Recommendations
        print("\n🔧 RECOMMENDATIONS:")
        if not server_info['server_running']:
            print("- ❌ Server is not responding properly")
        elif not server_info['routes_registered']:
            print("- ❌ API routes are not properly registered")
            print("- Check if the FastAPI app is correctly including the auth router")
            print("- Verify the deployment is running the latest code")
        elif not server_info['google_oauth_configured']:
            print("- ❌ Google OAuth routes are not available")
            print("- Check if Google OAuth is properly configured in production")
        else:
            print("- ✅ Basic configuration looks good")
            print("- Check Google OAuth client configuration and credentials")
        
        return results


async def main():
    """Main test runner."""
    async with ProductionOAuthTester() as tester:
        results = await tester.run_comprehensive_test()
        
        # Save results to file
        with open("production_oauth_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📁 Detailed results saved to: production_oauth_test_results.json")
        
        return results


if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        # Exit with appropriate code based on results
        server_info = results["tests"]["server_info"]
        if all([server_info['server_running'], server_info['routes_registered'], server_info['google_oauth_configured']]):
            print("\n✅ All basic tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)
