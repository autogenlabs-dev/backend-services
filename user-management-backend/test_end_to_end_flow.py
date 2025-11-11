#!/usr/bin/env python3
"""
End-to-End Authentication Flow Test Script
Tests complete user journey from registration to API usage
"""

import asyncio
import json
import time
import requests
import sys
import webbrowser
from typing import Dict, Any, Optional

class EndToEndFlowTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
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
    
    def test_1_user_registration(self):
        """Test Step 1: User Registration"""
        print("\n=== Step 1: User Registration ===")
        
        test_user = {
            "email": f"e2e{int(time.time())}@example.com",
            "password": "testpassword123",
            "name": "End-to-End Test User"
        }
        
        result = self.make_request(
            "POST", 
            "/api/auth/register",
            json=test_user
        )
        
        if result["success"]:
            self.user_data = result["data"]
            self.log_test("User Registration", True, "User created successfully")
            return True
        else:
            self.log_test(
                "User Registration", 
                False, 
                f"Failed: {result.get('error', 'Unknown error')}"
            )
            return False
    
    def test_2_user_login(self):
        """Test Step 2: User Login"""
        print("\n=== Step 2: User Login ===")
        
        if not self.user_data:
            self.log_test("User Login", False, "No registered user available")
            return False
        
        login_data = {
            "email": self.user_data["email"],
            "password": "testpassword123"
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
            return True
        else:
            self.log_test(
                "User Login", 
                False, 
                f"Failed: {result.get('error', 'Invalid credentials')}"
            )
            return False
    
    def test_3_user_profile(self):
        """Test Step 3: Get User Profile"""
        print("\n=== Step 3: Get User Profile ===")
        
        if not self.auth_token:
            self.log_test("User Profile", False, "No auth token available")
            return False
        
        result = self.make_request("GET", "/api/users/me")
        
        if result["success"]:
            self.log_test("User Profile", True, "Profile retrieved successfully")
            return True
        else:
            self.log_test(
                "User Profile", 
                False, 
                f"Failed: {result.get('error', 'Unknown error')}"
            )
            return False
    
    def test_4_api_key_creation(self):
        """Test Step 4: Create API Key"""
        print("\n=== Step 4: Create API Key ===")
        
        if not self.auth_token:
            self.log_test("API Key Creation", False, "No auth token available")
            return False
        
        api_key_data = {
            "name": "End-to-End Test API Key",
            "description": "API key for testing complete flow",
            "expires_in_days": 30
        }
        
        result = self.make_request(
            "POST",
            "/api/keys/",
            json=api_key_data
        )
        
        if result["success"]:
            self.log_test("API Key Creation", True, "API key created successfully")
            return True
        else:
            self.log_test(
                "API Key Creation", 
                False, 
                f"Failed: {result.get('error', 'Unknown error')}"
            )
            return False
    
    def test_5_token_usage_logging(self):
        """Test Step 5: Log Token Usage"""
        print("\n=== Step 5: Log Token Usage ===")
        
        if not self.auth_token:
            self.log_test("Token Usage Logging", False, "No auth token available")
            return False
        
        usage_data = {
            "provider": "test",
            "model_name": "test-model",
            "tokens_used": 100,
            "request_type": "test",
            "request_metadata": {"test": True, "flow": "end-to-end"}
        }
        
        result = self.make_request(
            "POST", 
            "/api/users/me/token-usage",
            json=usage_data
        )
        
        if result["success"]:
            self.log_test("Token Usage Logging", True, "Usage logged successfully")
            return True
        else:
            self.log_test(
                "Token Usage Logging", 
                False, 
                f"Failed: {result.get('error', 'Unknown error')}"
            )
            return False
    
    def test_6_vscode_config(self):
        """Test Step 6: Get VS Code Configuration"""
        print("\n=== Step 6: Get VS Code Configuration ===")
        
        if not self.auth_token:
            self.log_test("VS Code Config", False, "No auth token available")
            return False
        
        result = self.make_request("GET", "/api/auth/vscode-config")
        
        if result["success"]:
            self.log_test("VS Code Config", True, "Configuration retrieved successfully")
            return True
        else:
            self.log_test(
                "VS Code Config", 
                False, 
                f"Failed: {result.get('error', 'Unknown error')}"
            )
            return False
    
    def test_7_logout(self):
        """Test Step 7: Logout"""
        print("\n=== Step 7: Logout ===")
        
        if not self.auth_token:
            self.log_test("Logout", False, "No auth token available")
            return False
        
        result = self.make_request("POST", "/api/auth/logout")
        
        if result["success"]:
            # Clear token
            self.auth_token = None
            if "Authorization" in self.session.headers:
                del self.session.headers["Authorization"]
            
            self.log_test("Logout", True, "Logout successful")
            return True
        else:
            self.log_test(
                "Logout", 
                False, 
                f"Failed: {result.get('error', 'Unknown error')}"
            )
            return False
    
    def test_8_protected_access_after_logout(self):
        """Test Step 8: Verify Protected Access After Logout"""
        print("\n=== Step 8: Verify Protected Access After Logout ===")
        
        result = self.make_request("GET", "/api/users/me")
        
        # Should fail with 401 after logout
        is_protected = not result["success"] and result["status"] == 401
        self.log_test(
            "Protected Access After Logout", 
            is_protected,
            f"Status: {result['status']} (401 expected after logout)"
        )
        return is_protected
    
    def test_9_oauth_flow(self, provider: str):
        """Test Step 9: OAuth Flow"""
        print(f"\n=== Step 9: OAuth Flow ({provider}) ===")
        
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
        
        return is_redirect
    
    def test_10_open_dashboard(self):
        """Test Step 10: Open Dashboard"""
        print("\n=== Step 10: Open Dashboard ===")
        
        try:
            # Open API documentation in browser
            dashboard_url = f"{self.base_url}/docs"
            print(f"    Opening dashboard: {dashboard_url}")
            webbrowser.open(dashboard_url)
            
            self.log_test("Open Dashboard", True, f"Opened {dashboard_url}")
            return True
        except Exception as e:
            self.log_test("Open Dashboard", False, f"Failed to open browser: {e}")
            return False
    
    def run_complete_flow_test(self):
        """Run complete end-to-end flow test"""
        print("🚀 Starting Complete End-to-End Flow Test")
        print("=" * 60)
        
        start_time = time.time()
        passed_tests = 0
        total_tests = 0
        
        # Test sequence
        test_sequence = [
            ("User Registration", self.test_1_user_registration),
            ("User Login", self.test_2_user_login),
            ("User Profile", self.test_3_user_profile),
            ("API Key Creation", self.test_4_api_key_creation),
            ("Token Usage Logging", self.test_5_token_usage_logging),
            ("VS Code Config", self.test_6_vscode_config),
            ("Logout", self.test_7_logout),
            ("Protected Access After Logout", self.test_8_protected_access_after_logout),
            ("Google OAuth", lambda: self.test_9_oauth_flow("google")),
            ("GitHub OAuth", lambda: self.test_9_oauth_flow("github")),
            ("Open Dashboard", self.test_10_open_dashboard)
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
        print("📊 END-TO-END FLOW TEST SUMMARY")
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
        
        print("\n🔐 Authentication Flow Status:")
        flow_steps = [
            "User Registration",
            "User Login", 
            "User Profile",
            "API Key Creation",
            "Token Usage Logging",
            "VS Code Config",
            "Logout",
            "Protected Access Verification",
            "OAuth Integration",
            "Dashboard Access"
        ]
        
        for step in flow_steps:
            step_passed = any(
                result["passed"] and result["test"] == step
                for result in self.test_results
            )
            status = "✅" if step_passed else "❌"
            print(f"    {status} {step}")
        
        print("\n🌐 Access Information:")
        print(f"    Backend API: {self.base_url}")
        print(f"    API Documentation: {self.base_url}/docs")
        print(f"    Health Check: {self.base_url}/health")
        
        print("\n💡 Recommendations:")
        if passed == total:
            print("    • All end-to-end tests passed! System is ready for production.")
            print("    • Frontend can safely integrate with this backend.")
            print("    • Complete user workflow is functional.")
        else:
            print("    • Some end-to-end tests failed.")
            print("    • Check backend logs for detailed error information.")
            print("    • Verify database connectivity and OAuth configuration.")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="End-to-End Authentication Flow Testing")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="Backend URL to test (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--open-dashboard",
        action="store_true",
        help="Open dashboard in browser after testing"
    )
    
    args = parser.parse_args()
    
    tester = EndToEndFlowTester(args.url)
    success = tester.run_complete_flow_test()
    
    # Open dashboard if requested
    if args.open_dashboard:
        try:
            webbrowser.open(f"{args.url}/docs")
        except:
            pass
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()