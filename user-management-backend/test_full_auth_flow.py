#!/usr/bin/env python3
"""
Full Authentication Flow Test Script
Tests complete authentication flow including registration, login, OAuth, and token management
"""

import asyncio
import json
import time
import requests
import sys
import webbrowser
from typing import Dict, Any, Optional
from urllib.parse import urlencode

class FullAuthFlowTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_user = {
            "email": f"fulltest{int(time.time())}@example.com",
            "password": "testpassword123",
            "name": "Full Flow Test User"
        }
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.request(method, url, timeout=10, **kwargs)
            
            try:
                data = response.json()
            except:
                data = response.text
            
            return {
                "success": response.ok,
                "status": response.status_code,
                "data": data,
                "headers": dict(response.headers)
            }
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_backend_health(self):
        """Test backend health before authentication tests"""
        print("\n=== Testing Backend Health ===")
        
        # Test root endpoint
        result = self.make_request("GET", "/")
        self.log_test(
            "Backend Root Endpoint", 
            result["success"],
            f"Status: {result['status']}"
        )
        
        # Test health endpoint
        result = self.make_request("GET", "/health")
        self.log_test(
            "Backend Health Check", 
            result["success"],
            f"Status: {result['status']}"
        )
        
        # Test API docs
        result = self.make_request("GET", "/docs")
        self.log_test(
            "API Documentation", 
            result["success"],
            f"Status: {result['status']}"
        )
    
    def test_user_registration(self):
        """Test user registration flow"""
        print("\n=== Testing User Registration ===")
        
        # Test registration with valid data
        result = self.make_request(
            "POST", 
            "/api/auth/register",
            json=self.test_user
        )
        
        if result["success"]:
            self.log_test("User Registration", True, "User created successfully")
            # Store registered user credentials for login test
            self.registered_user = self.test_user
        else:
            self.log_test(
                "User Registration", 
                False, 
                f"Failed: {result.get('error', 'Unknown error')}"
            )
    
    def test_user_login(self):
        """Test user login flow"""
        print("\n=== Testing User Login ===")
        
        if not hasattr(self, 'registered_user'):
            self.log_test("User Login", False, "No registered user available")
            return
        
        # Test login with registered credentials
        login_data = {
            "email": self.registered_user["email"],
            "password": self.registered_user["password"]
        }
        
        result = self.make_request(
            "POST", 
            "/api/auth/login-json",
            json=login_data
        )
        
        if result["success"] and "access_token" in result.get("data", {}):
            self.auth_token = result["data"]["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.auth_token}"
            })
            self.log_test("User Login", True, "Login successful, token obtained")
            
            # Test token validation
            self.test_token_validation()
        else:
            self.log_test(
                "User Login", 
                False, 
                f"Failed: {result.get('error', 'Invalid credentials')}"
            )
    
    def test_token_validation(self):
        """Test JWT token validation"""
        print("\n=== Testing Token Validation ===")
        
        # Test protected endpoint with valid token
        result = self.make_request("GET", "/api/users/me")
        self.log_test(
            "Token Validation", 
            result["success"],
            f"Status: {result['status']}"
        )
        
        # Test token refresh
        if self.auth_token:
            refresh_result = self.make_request(
                "POST",
                "/api/auth/refresh",
                json={"refresh_token": "dummy_refresh_token"}  # This will fail but test endpoint
            )
            self.log_test(
                "Token Refresh Endpoint", 
                refresh_result["status"] in [200, 401, 422],  # Expected responses
                f"Status: {refresh_result['status']}"
            )
    
    def test_oauth_providers(self):
        """Test OAuth provider endpoints"""
        print("\n=== Testing OAuth Providers ===")
        
        # Test OAuth providers list
        result = self.make_request("GET", "/api/auth/providers")
        if result["success"]:
            providers = result["data"].get("providers", [])
            self.log_test(
                "OAuth Providers List", 
                True, 
                f"Found {len(providers)} providers"
            )
            
            # Test each OAuth provider login endpoint
            for provider in providers:
                provider_name = provider["name"]
                self.test_oauth_provider_login(provider_name)
        else:
            self.log_test(
                "OAuth Providers List", 
                False, 
                f"Failed: {result.get('error', 'Unknown error')}"
            )
    
    def test_oauth_provider_login(self, provider: str):
        """Test specific OAuth provider login"""
        result = self.make_request(
            "GET", 
            f"/api/auth/{provider}/login",
            allow_redirects=False
        )
        
        # OAuth should return 302/307 redirect
        is_redirect = result["status"] in [302, 307]
        self.log_test(
            f"OAuth {provider.title()} Login", 
            is_redirect,
            f"Status: {result['status']} (redirect expected)"
        )
        
        if is_redirect and "location" in result.get("headers", {}):
            redirect_url = result["headers"]["location"]
            print(f"    Redirect URL: {redirect_url}")
    
    def test_protected_endpoints(self):
        """Test protected endpoints with authentication"""
        print("\n=== Testing Protected Endpoints ===")
        
        if not self.auth_token:
            self.log_test("Protected Endpoints", False, "No auth token available")
            return
        
        # Test user profile
        result = self.make_request("GET", "/api/users/me")
        self.log_test(
            "Get User Profile", 
            result["success"],
            f"Status: {result['status']}"
        )
        
        # Test API keys endpoint
        result = self.make_request("GET", "/api/api-keys/")
        self.log_test(
            "List API Keys", 
            result["success"],
            f"Status: {result['status']}"
        )
        
        # Test token usage logging
        usage_data = {
            "provider": "test",
            "model_name": "test-model",
            "tokens_used": 100,
            "request_type": "test",
            "request_metadata": {"test": True}
        }
        result = self.make_request(
            "POST", 
            "/api/users/me/token-usage",
            json=usage_data
        )
        self.log_test(
            "Log Token Usage", 
            result["success"],
            f"Status: {result['status']}"
        )
    
    def test_logout_flow(self):
        """Test logout functionality"""
        print("\n=== Testing Logout Flow ===")
        
        if not self.auth_token:
            self.log_test("Logout", False, "No auth token to logout")
            return
        
        # Test logout
        result = self.make_request("POST", "/api/auth/logout")
        self.log_test(
            "Logout", 
            result["success"],
            f"Status: {result['status']}"
        )
        
        # Clear token
        self.auth_token = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        
        # Test that token is no longer valid
        result = self.make_request("GET", "/api/users/me")
        is_protected = not result["success"] and result["status"] == 401
        self.log_test(
            "Token Invalidation", 
            is_protected,
            f"Status: {result['status']} (401 expected)"
        )
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n=== Testing Error Handling ===")
        
        # Test invalid login
        result = self.make_request(
            "POST", 
            "/api/auth/login-json",
            json={"email": "invalid@example.com", "password": "wrongpassword"}
        )
        is_auth_error = not result["success"] and result["status"] in [401, 422]
        self.log_test(
            "Invalid Login Handling", 
            is_auth_error,
            f"Status: {result['status']} (auth error expected)"
        )
        
        # Test protected endpoint without token
        session_backup = dict(self.session.headers)
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        
        result = self.make_request("GET", "/api/users/me")
        is_unauthorized = not result["success"] and result["status"] == 401
        self.log_test(
            "Unauthorized Access Handling", 
            is_unauthorized,
            f"Status: {result['status']} (401 expected)"
        )
        
        # Restore session
        self.session.headers = session_backup
    
    def test_frontend_integration(self):
        """Test frontend integration points"""
        print("\n=== Testing Frontend Integration ===")
        
        # Test CORS preflight
        result = self.make_request("OPTIONS", "/api/auth/providers")
        has_cors = any(
            header.lower() in [h.lower() for h in result.get("headers", {})]
            for header in ["Access-Control-Allow-Origin", "Access-Control-Allow-Methods"]
        )
        self.log_test(
            "CORS Preflight", 
            has_cors,
            "CORS headers present for frontend integration"
        )
        
        # Test VS Code configuration endpoint
        if self.auth_token:
            result = self.make_request("GET", "/api/auth/vscode-config")
            self.log_test(
                "VS Code Configuration", 
                result["success"],
                f"Status: {result['status']}"
            )
    
    def run_full_auth_test(self):
        """Run complete authentication flow test"""
        print("🚀 Starting Full Authentication Flow Test")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Run all test suites in order
            self.test_backend_health()
            self.test_user_registration()
            self.test_user_login()
            self.test_oauth_providers()
            self.test_protected_endpoints()
            self.test_logout_flow()
            self.test_error_handling()
            self.test_frontend_integration()
            
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
        
        end_time = time.time()
        
        # Print summary
        self.print_summary(end_time - start_time)
    
    def print_summary(self, duration: float):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 FULL AUTHENTICATION FLOW TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["passed"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"    • {result['test']}: {result['details']}")
        
        print("\n🔐 Authentication Flow Status:")
        auth_steps = [
            "Backend Health",
            "User Registration", 
            "User Login",
            "Token Validation",
            "OAuth Providers",
            "Protected Endpoints",
            "Logout Flow",
            "Error Handling",
            "Frontend Integration"
        ]
        
        for step in auth_steps:
            step_passed = any(
                result["passed"] and result["test"] == step
                for result in self.test_results
            )
            status = "✅" if step_passed else "❌"
            print(f"    {status} {step}")
        
        print("\n🌐 Access Information:")
        print(f"    Backend API: {self.base_url}")
        print(f"    API Documentation: {self.base_url}/docs")
        print(f"    Frontend Test: file:///home/cis/Downloads/backend-services/user-management-backend/frontend_test.html")
        
        print("\n💡 Recommendations:")
        if passed == total:
            print("    • All authentication tests passed! System is ready for production.")
            print("    • Frontend can safely integrate with this backend.")
            print("    • OAuth flows are working correctly.")
        else:
            print("    • Some authentication tests failed.")
            print("    • Check backend logs for detailed error information.")
            print("    • Verify database connectivity and OAuth configuration.")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Full Authentication Flow Testing")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="Backend URL to test (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--open-frontend",
        action="store_true",
        help="Open frontend test in browser after testing"
    )
    
    args = parser.parse_args()
    
    tester = FullAuthFlowTester(args.url)
    tester.run_full_auth_test()
    
    # Open frontend in browser if requested
    if args.open_frontend:
        frontend_path = "file:///home/cis/Downloads/backend-services/user-management-backend/frontend_test.html"
        print(f"\n🌐 Opening frontend test in browser: {frontend_path}")
        webbrowser.open(frontend_path)
    
    # Exit with appropriate code
    failed = sum(1 for result in tester.test_results if not result["passed"])
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()