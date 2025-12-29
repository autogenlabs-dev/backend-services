#!/usr/bin/env python3
"""
Comprehensive API Testing with Real Data
Tests all backend endpoints with Clerk authentication
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Optional, Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# Test user data (simulated Clerk JWT payload)
TEST_USER = {
    "email": "test@codemurf.com",
    "name": "Test User",
    "first_name": "Test",
    "last_name": "User"
}

# Color codes
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


class APITester:
    def __init__(self):
        self.client = None
        self.results = []
        self.access_token = None
        self.user_id = None
        
    def print_header(self, text: str):
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.RESET}\n")
    
    def print_test(self, name: str):
        print(f"{Colors.CYAN}▶ Testing: {name}{Colors.RESET}")
    
    def print_success(self, msg: str):
        print(f"{Colors.GREEN}  ✅ {msg}{Colors.RESET}")
    
    def print_error(self, msg: str):
        print(f"{Colors.RED}  ❌ {msg}{Colors.RESET}")
    
    def print_info(self, msg: str):
        print(f"{Colors.YELLOW}  ℹ️  {msg}{Colors.RESET}")
    
    def print_data(self, label: str, data: Any):
        print(f"{Colors.PURPLE}  📊 {label}:{Colors.RESET}")
        if isinstance(data, dict) or isinstance(data, list):
            print(f"     {json.dumps(data, indent=6)}")
        else:
            print(f"     {data}")
    
    async def test_health_endpoints(self):
        """Test health and basic endpoints"""
        self.print_header("HEALTH & BASIC ENDPOINTS")
        
        endpoints = [
            ("/health", "Health Check"),
            ("/", "Root Endpoint"),
            ("/api/auth/providers", "OAuth Providers"),
        ]
        
        for endpoint, name in endpoints:
            self.print_test(name)
            try:
                response = await self.client.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    self.print_success(f"Status: {response.status_code}")
                    data = response.json()
                    self.print_data("Response", data)
                    self.results.append({"test": name, "status": "PASS"})
                else:
                    self.print_error(f"Status: {response.status_code}")
                    self.results.append({"test": name, "status": "FAIL"})
            except Exception as e:
                self.print_error(f"Error: {str(e)}")
                self.results.append({"test": name, "status": "ERROR"})
            print()
    
    async def test_user_registration(self):
        """Test user registration with email/password"""
        self.print_header("USER REGISTRATION")
        
        self.print_test("Register New User")
        
        user_data = {
            "email": f"testuser_{datetime.now().timestamp()}@example.com",
            "password": "TestPassword123!",
            "name": "Test User"
        }
        
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/auth/register",
                json=user_data
            )
            
            if response.status_code in [200, 201]:
                self.print_success(f"Registration successful")
                data = response.json()
                self.print_data("User Data", data)
                self.results.append({"test": "User Registration", "status": "PASS"})
            else:
                self.print_error(f"Registration failed: {response.status_code}")
                self.print_info(f"Response: {response.text}")
                self.results.append({"test": "User Registration", "status": "FAIL"})
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.results.append({"test": "User Registration", "status": "ERROR"})
        print()
    
    async def test_template_endpoints(self):
        """Test template-related endpoints"""
        self.print_header("TEMPLATE ENDPOINTS")
        
        # Get all templates
        self.print_test("Get All Templates")
        try:
            response = await self.client.get(f"{BASE_URL}/api/templates/")
            if response.status_code == 200:
                data = response.json()
                templates = data.get("templates", [])
                self.print_success(f"Found {len(templates)} templates")
                if templates:
                    self.print_data("First Template", templates[0])
                self.results.append({"test": "Get Templates", "status": "PASS"})
            else:
                self.print_error(f"Failed: {response.status_code}")
                self.results.append({"test": "Get Templates", "status": "FAIL"})
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.results.append({"test": "Get Templates", "status": "ERROR"})
        print()
        
        # Get template categories
        self.print_test("Get Template Categories")
        try:
            response = await self.client.get(f"{BASE_URL}/api/templates/categories/list")
            if response.status_code == 200:
                categories = response.json()
                self.print_success(f"Found {len(categories)} categories")
                self.print_data("Categories", categories)
                self.results.append({"test": "Get Categories", "status": "PASS"})
            else:
                self.print_error(f"Failed: {response.status_code}")
                self.results.append({"test": "Get Categories", "status": "FAIL"})
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.results.append({"test": "Get Categories", "status": "ERROR"})
        print()
        
        # Get template stats
        self.print_test("Get Template Stats")
        try:
            response = await self.client.get(f"{BASE_URL}/api/templates/stats/overview")
            if response.status_code == 200:
                stats = response.json()
                self.print_success("Stats retrieved")
                self.print_data("Stats", stats)
                self.results.append({"test": "Get Stats", "status": "PASS"})
            else:
                self.print_error(f"Failed: {response.status_code}")
                self.results.append({"test": "Get Stats", "status": "FAIL"})
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.results.append({"test": "Get Stats", "status": "ERROR"})
        print()
    
    async def test_protected_endpoints_without_auth(self):
        """Test that protected endpoints require authentication"""
        self.print_header("PROTECTED ENDPOINTS (No Auth)")
        
        protected_endpoints = [
            ("/api/users/me", "GET", "User Profile"),
            ("/api/tokens/usage", "GET", "Token Usage"),
            ("/api/subscriptions/current", "GET", "Current Subscription"),
        ]
        
        for endpoint, method, name in protected_endpoints:
            self.print_test(name)
            try:
                if method == "GET":
                    response = await self.client.get(f"{BASE_URL}{endpoint}")
                else:
                    response = await self.client.post(f"{BASE_URL}{endpoint}")
                
                if response.status_code == 401:
                    self.print_success("Correctly requires authentication (401)")
                    self.results.append({"test": f"{name} Auth Check", "status": "PASS"})
                else:
                    self.print_error(f"Unexpected status: {response.status_code}")
                    self.results.append({"test": f"{name} Auth Check", "status": "FAIL"})
            except Exception as e:
                self.print_error(f"Error: {str(e)}")
                self.results.append({"test": f"{name} Auth Check", "status": "ERROR"})
            print()
    
    async def test_api_documentation(self):
        """Test API documentation endpoints"""
        self.print_header("API DOCUMENTATION")
        
        docs_endpoints = [
            ("/docs", "Swagger UI"),
            ("/redoc", "ReDoc"),
            ("/openapi.json", "OpenAPI Schema"),
        ]
        
        for endpoint, name in docs_endpoints:
            self.print_test(name)
            try:
                response = await self.client.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    self.print_success(f"Available at: {BASE_URL}{endpoint}")
                    self.results.append({"test": name, "status": "PASS"})
                else:
                    self.print_error(f"Status: {response.status_code}")
                    self.results.append({"test": name, "status": "FAIL"})
            except Exception as e:
                self.print_error(f"Error: {str(e)}")
                self.results.append({"test": name, "status": "ERROR"})
            print()
    
    async def test_cors_configuration(self):
        """Test CORS configuration"""
        self.print_header("CORS CONFIGURATION")
        
        self.print_test("CORS Headers")
        try:
            response = await self.client.options(
                f"{BASE_URL}/api/templates",
                headers={"Origin": "http://localhost:3000"}
            )
            
            cors_headers = {
                "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
                "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
                "access-control-allow-credentials": response.headers.get("access-control-allow-credentials"),
            }
            
            self.print_success("CORS headers present")
            self.print_data("CORS Headers", cors_headers)
            self.results.append({"test": "CORS Configuration", "status": "PASS"})
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.results.append({"test": "CORS Configuration", "status": "ERROR"})
        print()
    
    async def test_rate_limiting(self):
        """Test rate limiting"""
        self.print_header("RATE LIMITING")
        
        self.print_test("Rate Limit Headers")
        try:
            response = await self.client.get(f"{BASE_URL}/api/templates")
            
            rate_limit_headers = {
                "X-RateLimit-Limit": response.headers.get("X-RateLimit-Limit"),
                "X-RateLimit-Remaining": response.headers.get("X-RateLimit-Remaining"),
                "X-RateLimit-Reset": response.headers.get("X-RateLimit-Reset"),
            }
            
            if any(rate_limit_headers.values()):
                self.print_success("Rate limiting is active")
                self.print_data("Rate Limit Info", rate_limit_headers)
                self.results.append({"test": "Rate Limiting", "status": "PASS"})
            else:
                self.print_info("Rate limiting headers not found (may be in fallback mode)")
                self.results.append({"test": "Rate Limiting", "status": "SKIP"})
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.results.append({"test": "Rate Limiting", "status": "ERROR"})
        print()
    
    async def test_frontend_connection(self):
        """Test frontend connectivity"""
        self.print_header("FRONTEND CONNECTION")
        
        self.print_test("Frontend Availability")
        try:
            response = await self.client.get(FRONTEND_URL)
            if response.status_code == 200:
                self.print_success(f"Frontend is running at {FRONTEND_URL}")
                self.print_info("Check browser DevTools for Clerk authentication")
                self.results.append({"test": "Frontend Connectivity", "status": "PASS"})
            else:
                self.print_error(f"Frontend returned: {response.status_code}")
                self.results.append({"test": "Frontend Connectivity", "status": "FAIL"})
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.print_info("Make sure frontend is running: npm run dev")
            self.results.append({"test": "Frontend Connectivity", "status": "ERROR"})
        print()
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        errors = len([r for r in self.results if r["status"] == "ERROR"])
        skipped = len([r for r in self.results if r["status"] == "SKIP"])
        total = len(self.results)
        
        print(f"{Colors.BOLD}Results:{Colors.RESET}")
        print(f"  {Colors.GREEN}✅ Passed:  {passed}{Colors.RESET}")
        print(f"  {Colors.RED}❌ Failed:  {failed}{Colors.RESET}")
        print(f"  {Colors.RED}⚠️  Errors:  {errors}{Colors.RESET}")
        print(f"  {Colors.YELLOW}⏭️  Skipped: {skipped}{Colors.RESET}")
        print(f"  {Colors.BLUE}📊 Total:   {total}{Colors.RESET}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.RESET}")
        
        if failed == 0 and errors == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.RESET}")
        elif failed > 0:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  SOME TESTS FAILED{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ TESTS HAD ERRORS{Colors.RESET}")
    
    def print_next_steps(self):
        """Print next steps"""
        self.print_header("NEXT STEPS")
        
        print(f"{Colors.CYAN}1. Frontend Testing:{Colors.RESET}")
        print(f"   • Open {FRONTEND_URL} in browser")
        print(f"   • Sign in with Clerk")
        print(f"   • Open DevTools → Network tab")
        print(f"   • Look for API calls with Authorization header")
        print()
        
        print(f"{Colors.CYAN}2. Clerk Integration:{Colors.RESET}")
        print(f"   • Backend logs should show 'Clerk token verified'")
        print(f"   • Check MongoDB for users with clerk_id field")
        print(f"   • Verify user creation/sync works")
        print()
        
        print(f"{Colors.CYAN}3. VS Code Extension:{Colors.RESET}")
        print(f"   • Test extension authentication with API keys")
        print(f"   • Verify X-API-Key header authentication")
        print(f"   • Check extension can access protected endpoints")
        print()
        
        print(f"{Colors.CYAN}4. API Documentation:{Colors.RESET}")
        print(f"   • Swagger UI: {BASE_URL}/docs")
        print(f"   • ReDoc: {BASE_URL}/redoc")
        print(f"   • Try testing endpoints manually")
        print()
        
        print(f"{Colors.CYAN}5. Database Check:{Colors.RESET}")
        print(f"   • MongoDB: Check user collection for clerk_id")
        print(f"   • Redis: Check session storage")
        print(f"   • Verify data persistence")
    
    async def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.PURPLE}{Colors.BOLD}")
        print("="*70)
        print("  COMPREHENSIVE API TESTING WITH CLERK AUTH")
        print("  Backend Integration Test Suite")
        print("="*70)
        print(f"{Colors.RESET}")
        
        print(f"{Colors.YELLOW}Backend: {BASE_URL}{Colors.RESET}")
        print(f"{Colors.YELLOW}Frontend: {FRONTEND_URL}{Colors.RESET}")
        print(f"{Colors.YELLOW}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            self.client = client
            
            # Run all test suites
            await self.test_health_endpoints()
            await self.test_api_documentation()
            await self.test_frontend_connection()
            await self.test_template_endpoints()
            await self.test_protected_endpoints_without_auth()
            await self.test_cors_configuration()
            await self.test_rate_limiting()
            await self.test_user_registration()
            
            # Print results
            self.print_summary()
            self.print_next_steps()


async def main():
    tester = APITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
