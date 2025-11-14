#!/usr/bin/env python3
"""
Frontend-Backend Integration Test Script
Tests that the frontend can properly connect to the backend
"""

import asyncio
import json
import os
import time
import requests
import sys
import webbrowser
from typing import Dict, Any, Optional

class FrontendBackendIntegrationTester:
    def __init__(self, backend_url: str = "http://localhost:8000", frontend_path: str = "/home/cis/Music/Autogenlabs-Web-App"):
        self.backend_url = backend_url
        self.frontend_path = frontend_path
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
            url = f"{self.backend_url}{endpoint}"
            response = requests.request(method, url, timeout=10, **kwargs)
            
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
    
    def test_backend_connectivity(self):
        """Test backend connectivity"""
        print("\n=== Testing Backend Connectivity ===")
        
        result = self.make_request("GET", "/health")
        self.log_test(
            "Backend Health Check", 
            result["success"],
            f"Status: {result['status']}"
        )
        
        result = self.make_request("GET", "/")
        self.log_test(
            "Backend Root Endpoint", 
            result["success"],
            f"Status: {result['status']}"
        )
        
        return result["success"]
    
    def test_frontend_backend_compatibility(self):
        """Test frontend-backend compatibility"""
        print("\n=== Testing Frontend-Backend Compatibility ===")
        
        # Test CORS preflight
        result = self.make_request("OPTIONS", "/api/auth/providers")
        has_cors = any(
            header.lower() in [h.lower() for h in result.get("headers", {})]
            for header in ["Access-Control-Allow-Origin", "Access-Control-Allow-Methods", "Access-Control-Allow-Headers"]
        )
        
        self.log_test(
            "CORS Preflight", 
            has_cors,
            f"CORS headers present: {has_cors}"
        )
        
        # Test API endpoints that frontend would use
        endpoints_to_test = [
            "/api/auth/providers",
            "/api/auth/register",
            "/api/auth/login-json",
            "/api/users/me",
            "/api/keys/",
            "/api/templates/"
        ]
        
        all_passed = True
        for endpoint in endpoints_to_test:
            result = self.make_request("GET", endpoint)
            passed = result["success"] or result["status"] in [401, 422]  # 401 for protected, 422 for validation
            self.log_test(
                f"Endpoint {endpoint}", 
                passed,
                f"Status: {result['status']}"
            )
            if not passed:
                all_passed = False
        
        return all_passed
    
    def test_oauth_integration(self):
        """Test OAuth integration"""
        print("\n=== Testing OAuth Integration ===")
        
        providers = ["google", "github", "openrouter"]
        all_passed = True
        
        for provider in providers:
            result = self.make_request("GET", f"/api/auth/{provider}/login", allow_redirects=False)
            is_redirect = result["status"] in [302, 307]
            self.log_test(
                f"OAuth {provider.title()} Login", 
                is_redirect,
                f"Status: {result['status']} (redirect expected)"
            )
            
            if is_redirect and "location" in result.get("headers", {}):
                redirect_url = result["headers"]["location"]
                print(f"    Redirect URL: {redirect_url}")
            
            if not is_redirect:
                all_passed = False
        
        return all_passed
    
    def test_complete_auth_flow(self):
        """Test complete authentication flow"""
        print("\n=== Testing Complete Auth Flow ===")
        
        # Test user registration
        test_user = {
            "email": f"integration{int(time.time())}@example.com",
            "password": "testpassword123",
            "name": "Integration Test User"
        }
        
        result = self.make_request(
            "POST", 
            "/api/auth/register",
            json=test_user
        )
        
        if not result["success"]:
            self.log_test("User Registration", False, f"Failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test user login
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        result = self.make_request(
            "POST", 
            "/api/auth/login-json",
            json=login_data
        )
        
        if not result["success"] or "access_token" not in result.get("data", {}):
            self.log_test("User Login", False, f"Failed: {result.get('error', 'Invalid credentials')}")
            return False
        
        auth_token = result["data"]["access_token"]
        
        # Test protected endpoint with token
        headers = {"Authorization": f"Bearer {auth_token}"}
        result = self.make_request("GET", "/api/users/me", headers=headers)
        
        if not result["success"]:
            self.log_test("Protected Access", False, f"Failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test logout
        result = self.make_request("POST", "/api/auth/logout", headers=headers)
        
        if not result["success"]:
            self.log_test("Logout", False, f"Failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test protected access after logout
        result = self.make_request("GET", "/api/users/me")
        is_protected = not result["success"] and result["status"] == 401
        
        self.log_test(
            "Protected Access After Logout", 
            is_protected,
            f"Status: {result['status']} (401 expected after logout)"
        )
        
        return True
    
    def test_frontend_files_exist(self):
        """Test that frontend files exist"""
        print("\n=== Testing Frontend Files ===")
        
        import os
        frontend_files = [
            "package.json",
            "next.config.js",
            ".env.local",
            "src/app/layout.tsx",
            "src/app/page.tsx"
        ]
        
        all_exist = True
        for file_path in frontend_files:
            full_path = os.path.join(self.frontend_path, file_path)
            exists = os.path.exists(full_path)
            self.log_test(
                f"Frontend File {file_path}", 
                exists,
                f"Path: {full_path}"
            )
            if not exists:
                all_exist = False
        
        return all_exist
    
    def test_frontend_backend_connection(self):
        """Test that frontend can connect to backend"""
        print("\n=== Testing Frontend-Backend Connection ===")
        
        # Simulate frontend API calls
        try:
            # Test registration from frontend perspective
            frontend_registration = {
                "email": f"frontend{int(time.time())}@example.com",
                "password": "testpassword123",
                "name": "Frontend Test User"
            }
            
            result = self.make_request(
                "POST", 
                "/api/auth/register",
                json=frontend_registration
            )
            
            self.log_test(
                "Frontend Registration Call", 
                result["success"],
                f"Status: {result['status']}"
            )
            
            if result["success"]:
                # Test login from frontend perspective
                frontend_login = {
                    "email": frontend_registration["email"],
                    "password": frontend_registration["password"]
                }
                
                result = self.make_request(
                    "POST", 
                    "/api/auth/login-json",
                    json=frontend_login
                )
                
                self.log_test(
                    "Frontend Login Call", 
                    result["success"],
                    f"Status: {result['status']}"
                )
                
                if result["success"] and "access_token" in result.get("data", {}):
                    # Test API calls with frontend token
                    token = result["data"]["access_token"]
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # Test user profile
                    profile_result = self.make_request("GET", "/api/users/me", headers=headers)
                    self.log_test(
                        "Frontend Profile Call", 
                        profile_result["success"],
                        f"Status: {profile_result['status']}"
                    )
                    
                    # Test API keys
                    api_keys_result = self.make_request("GET", "/api/keys/", headers=headers)
                    self.log_test(
                        "Frontend API Keys Call", 
                        api_keys_result["success"],
                        f"Status: {api_keys_result['status']}"
                    )
                    
                    return True
                else:
                    self.log_test("Frontend Token Handling", False, "Failed to get access token")
                    return False
            else:
                self.log_test("Frontend Login", False, "Failed to authenticate")
                return False
                
        except Exception as e:
            self.log_test("Frontend-Backend Connection", False, f"Error: {e}")
            return False
    
    def open_frontend_dashboard(self):
        """Open frontend dashboard"""
        print("\n=== Opening Frontend Dashboard ===")
        
        try:
            # Check if it's a Next.js app
            next_config = os.path.join(self.frontend_path, "next.config.js")
            if os.path.exists(next_config):
                # It's a Next.js app, try to start it
                print(f"    Next.js app detected at {self.frontend_path}")
                print("    To start frontend: cd /home/cis/Music/Autogenlabs-Web-App && npm run dev")
                print("    Frontend will be available at http://localhost:3000")
                return True
            
            # Check if it's a React app
            package_json = os.path.join(self.frontend_path, "package.json")
            if os.path.exists(package_json):
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                    if "scripts" in package_data:
                        print(f"    React/Vue app detected at {self.frontend_path}")
                        print("    To start frontend: cd /home/cis/Music/Autogenlabs-Web-App && npm start")
                        print("    Frontend will be available at http://localhost:3000")
                        return True
            
            print(f"    Frontend directory found: {self.frontend_path}")
            print("    Could not determine frontend type")
            return False
            
        except Exception as e:
            self.log_test("Frontend Dashboard", False, f"Error: {e}")
            return False
    
    def run_integration_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Frontend-Backend Integration Tests")
        print("=" * 60)
        
        start_time = time.time()
        passed_tests = 0
        total_tests = 0
        
        # Test sequence
        test_sequence = [
            ("Backend Connectivity", self.test_backend_connectivity),
            ("Frontend-Backend Compatibility", self.test_frontend_backend_compatibility),
            ("OAuth Integration", self.test_oauth_integration),
            ("Complete Auth Flow", self.test_complete_auth_flow),
            ("Frontend Files Exist", self.test_frontend_files_exist),
            ("Frontend-Backend Connection", self.test_frontend_backend_connection),
            ("Frontend Dashboard", self.open_frontend_dashboard)
        ]
        
        for test_name, test_func in test_sequence:
            total_tests += 1
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"    ⚠️ Test failed with exception: {e}")
        
        end_time = time.time()
        
        # Print summary
        self.print_summary(passed_tests, total_tests, end_time - start_time)
        
        return passed_tests == total_tests
    
    def print_summary(self, passed: int, total: int, duration: float):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 FRONTEND-BACKEND INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
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
        
        print("\n🔐 Integration Status:")
        integration_steps = [
            "Backend Connectivity",
            "Frontend-Backend Compatibility", 
            "OAuth Integration",
            "Complete Auth Flow",
            "Frontend Files Exist",
            "Frontend-Backend Connection",
            "Frontend Dashboard"
        ]
        
        for step in integration_steps:
            step_passed = any(
                result["passed"] and result["test"] == step
                for result in self.test_results
            )
            status = "✅" if step_passed else "❌"
            print(f"    {status} {step}")
        
        print("\n🌐 Access Information:")
        print(f"    Backend API: {self.backend_url}")
        print(f"    Frontend Path: {self.frontend_path}")
        print(f"    API Documentation: {self.backend_url}/docs")
        print(f"    Health Check: {self.backend_url}/health")
        
        print("\n💡 Integration Instructions:")
        print("    • Frontend should make API calls to http://localhost:8000")
        print("    • Use CORS-enabled requests for cross-origin requests")
        print("    • Implement JWT token storage and refresh")
        print("    • Handle OAuth redirects properly")
        print("    • Test all authentication flows before production")
        
        print("\n🚀 Frontend Start Commands:")
        print("    # Next.js App:")
        print("    cd /home/cis/Music/Autogenlabs-Web-App && npm run dev")
        print("    # React/Vue App:")
        print("    cd /home/cis/Music/Autogenlabs-Web-App && npm start")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Frontend-Backend Integration Testing")
    parser.add_argument(
        "--backend-url", 
        default="http://localhost:8000",
        help="Backend URL to test (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--frontend-path", 
        default="/home/cis/Music/Autogenlabs-Web-App",
        help="Frontend path to test (default: /home/cis/Music/Autogenlabs-Web-App)"
    )
    parser.add_argument(
        "--open-frontend",
        action="store_true",
        help="Open frontend dashboard after testing"
    )
    
    args = parser.parse_args()
    
    tester = FrontendBackendIntegrationTester(args.backend_url, args.frontend_path)
    success = tester.run_integration_tests()
    
    # Open frontend if requested
    if args.open_frontend:
        try:
            webbrowser.open(f"file://{args.frontend_path}")
        except:
            pass
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()