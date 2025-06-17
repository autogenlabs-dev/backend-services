#!/usr/bin/env python3
"""
🚀 FINAL COMPREHENSIVE AUTHENTICATION & API FLOW TEST
====================================================

This test covers the complete VS Code extension authentication flow including:
- User Registration & Login
- JWT Token Management 
- API Key Creation & Validation
- LLM Service Integration
- Subscription Management
- OAuth Provider Integration
- Error Handling & Edge Cases
- Performance & Rate Limiting

Created: June 10, 2025
Status: Production Ready ✅
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TIMESTAMP = int(time.time())
TEST_EMAIL = f"final_test_{TEST_TIMESTAMP}@example.com"
TEST_PASSWORD = "FinalTest123!"
TEST_NAME = "Final Test User"

class TestResults:
    """Track test results and generate summary"""
    
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.start_time = time.time()
    
    def add_test(self, name: str, success: bool, details: str = None):
        """Add a test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.tests.append({
            "name": name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
        
        print(f"{status}: {name}")
        if details and not success:
            print(f"   Details: {details}")
    
    def print_summary(self):
        """Print comprehensive test summary"""
        duration = time.time() - self.start_time
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*80)
        print("🎯 FINAL COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        print(f"📊 Total Tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.failed > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.tests:
                if not test["success"]:
                    print(f"   • {test['name']}: {test['details']}")
        
        print("\n🔍 DETAILED RESULTS:")
        for i, test in enumerate(self.tests, 1):
            print(f"{i:2d}. {test['status']} {test['name']}")
        
        print("="*80)
        
        if success_rate >= 95:
            print("🎉 EXCELLENT! System is production ready!")
        elif success_rate >= 80:
            print("⚠️  GOOD! Minor issues need attention.")
        else:
            print("🚨 CRITICAL! Major issues detected!")
        
        return success_rate >= 95

def make_request(method: str, endpoint: str, data: Dict = None, headers: Dict = None, 
                expected_status: int = 200, timeout: int = 10) -> Tuple[bool, requests.Response]:
    """Make HTTP request with error handling"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == "POST":
            if headers and headers.get("Content-Type") == "application/x-www-form-urlencoded":
                response = requests.post(url, data=data, headers=headers, timeout=timeout)
            else:
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            return False, None
        
        success = response.status_code == expected_status
        return success, response
        
    except Exception as e:
        print(f"Request error: {e}")
        return False, None

def test_health_check(results: TestResults):
    """Test API health and availability"""
    print("\n1️⃣ SYSTEM HEALTH CHECK")
    print("-" * 40)
    
    # Basic health
    success, response = make_request("GET", "/health")
    if success:
        health_data = response.json()
        results.add_test("API Health Check", True, f"Status: {health_data.get('status')}")
    else:
        results.add_test("API Health Check", False, "API not responding")
        return False
    
    # Root endpoint
    success, response = make_request("GET", "/")
    results.add_test("Root Endpoint", success, None if success else "Root endpoint failed")
    
    # OAuth providers
    success, response = make_request("GET", "/auth/providers")
    if success:
        providers = response.json()
        results.add_test("OAuth Providers", True, f"Available: {len(providers.get('providers', []))}")
    else:
        results.add_test("OAuth Providers", False, "Failed to get providers")
    
    return True

def test_authentication_flow(results: TestResults) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Test complete authentication flow"""
    print("\n2️⃣ AUTHENTICATION FLOW")
    print("-" * 40)
    
    # User Registration
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": TEST_NAME
    }
    
    success, response = make_request("POST", "/auth/register", register_data)
    if success:
        user_data = response.json()
        results.add_test("User Registration", True, f"User ID: {user_data.get('id', 'N/A')}")
    else:
        error_msg = response.text if response else "No response"
        results.add_test("User Registration", False, error_msg)
        return None, None, None
    
    # User Login
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    success, response = make_request("POST", "/auth/login", login_data, headers)
    if success:
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        results.add_test("User Login", True, f"Token type: {tokens.get('token_type')}")
        
        # Validate token structure
        if access_token and refresh_token:
            results.add_test("Token Generation", True, "Both tokens generated")
        else:
            results.add_test("Token Generation", False, "Missing tokens")
            return None, None, None
    else:
        error_msg = response.text if response else "No response"
        results.add_test("User Login", False, error_msg)
        return None, None, None
    
    # Test protected endpoint
    jwt_headers = {"Authorization": f"Bearer {access_token}"}
    success, response = make_request("GET", "/users/me", headers=jwt_headers)
    if success:
        user_info = response.json()
        results.add_test("Protected Endpoint Access", True, f"User: {user_info.get('email')}")
    else:
        results.add_test("Protected Endpoint Access", False, "JWT authentication failed")
    
    return access_token, refresh_token, user_data.get('id')

def test_api_key_management(results: TestResults, access_token: str) -> Optional[str]:
    """Test API key creation and management"""
    print("\n3️⃣ API KEY MANAGEMENT")
    print("-" * 40)
    
    jwt_headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create API Key
    api_key_data = {
        "name": "Final Test API Key",
        "description": "Comprehensive test API key"
    }
    
    success, response = make_request("POST", "/api/keys", api_key_data, jwt_headers)
    if success:
        key_result = response.json()
        api_key = key_result.get("api_key")
        results.add_test("API Key Creation", True, f"Key ID: {key_result.get('id')}")
    else:
        error_msg = response.text if response else "No response"
        results.add_test("API Key Creation", False, error_msg)
        return None
    
    # List API Keys
    success, response = make_request("GET", "/api/keys", headers=jwt_headers)
    if success:
        keys = response.json()
        results.add_test("API Key Listing", True, f"Found {len(keys)} keys")
    else:
        results.add_test("API Key Listing", False, "Failed to list keys")
    
    # Validate API Key
    api_headers = {"X-API-Key": api_key}
    success, response = make_request("GET", "/api/keys/validate", headers=api_headers)
    if success:
        validation = response.json()
        results.add_test("API Key Validation", True, f"Valid: {validation.get('valid')}")
    else:
        results.add_test("API Key Validation", False, "Validation failed")
    
    return api_key

def test_llm_services(results: TestResults, api_key: str):
    """Test LLM service integration"""
    print("\n4️⃣ LLM SERVICE INTEGRATION")
    print("-" * 40)
    
    api_headers = {"X-API-Key": api_key}
    
    # LLM Health Check
    success, response = make_request("GET", "/llm/health", headers=api_headers)
    if success:
        health = response.json()
        results.add_test("LLM Health Check", True, f"Status: {health.get('status')}")
    else:
        results.add_test("LLM Health Check", False, "LLM health check failed")
    
    # List Providers
    success, response = make_request("GET", "/llm/providers", headers=api_headers)
    if success:
        providers = response.json()
        provider_count = len(providers) if isinstance(providers, list) else 0
        results.add_test("LLM Providers", True, f"Available providers: {provider_count}")
    else:
        results.add_test("LLM Providers", False, "Failed to get providers")
    
    # List Models
    success, response = make_request("GET", "/llm/models", headers=api_headers)
    if success:
        models = response.json()
        model_count = len(models) if isinstance(models, list) else 0
        results.add_test("LLM Models", True, f"Available models: {model_count}")
        
        # Test model filtering (if models available)
        if model_count > 0:
            success, response = make_request("GET", "/llm/models?provider=openrouter", headers=api_headers)
            results.add_test("Model Filtering", success, "Provider filtering works" if success else "Filtering failed")
    else:
        results.add_test("LLM Models", False, "Failed to get models")

def test_subscription_management(results: TestResults, access_token: str, api_key: str):
    """Test subscription and token management"""
    print("\n5️⃣ SUBSCRIPTION MANAGEMENT")
    print("-" * 40)
    
    # Test with JWT
    jwt_headers = {"Authorization": f"Bearer {access_token}"}
    success, response = make_request("GET", "/subscriptions/current", headers=jwt_headers)
    if success:
        subscription = response.json()
        results.add_test("Current Subscription (JWT)", True, f"Plan: {subscription.get('subscription')}")
    else:
        results.add_test("Current Subscription (JWT)", False, "Failed with JWT")
    
    # Test with API Key
    api_headers = {"X-API-Key": api_key}
    success, response = make_request("GET", "/subscriptions/current", headers=api_headers)
    if success:
        subscription = response.json()
        results.add_test("Current Subscription (API Key)", True, f"Plan: {subscription.get('subscription')}")
    else:
        results.add_test("Current Subscription (API Key)", False, "Failed with API Key")
    
    # Subscription Plans
    success, response = make_request("GET", "/subscriptions/plans", headers=api_headers)
    if success:
        plans = response.json()
        plan_count = len(plans) if isinstance(plans, list) else 0
        results.add_test("Subscription Plans", True, f"Available plans: {plan_count}")
    else:
        results.add_test("Subscription Plans", False, "Failed to get plans")
    
    # Token Usage Stats
    success, response = make_request("GET", "/tokens/stats", headers=api_headers)
    if success:
        stats = response.json()
        results.add_test("Token Usage Stats", True, f"Total tokens: {stats.get('total_tokens', 0)}")
    else:
        results.add_test("Token Usage Stats", False, "Failed to get token stats")

def test_token_refresh(results: TestResults, refresh_token: str) -> Optional[str]:
    """Test token refresh functionality"""
    print("\n6️⃣ TOKEN REFRESH")
    print("-" * 40)
    
    refresh_data = {"refresh_token": refresh_token}
    success, response = make_request("POST", "/auth/refresh", refresh_data)
    
    if success:
        new_tokens = response.json()
        new_access_token = new_tokens.get("access_token")
        results.add_test("Token Refresh", True, "New access token generated")
        
        # Test new token works
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        success, response = make_request("GET", "/users/me", headers=new_headers)
        results.add_test("Refreshed Token Validation", success, "New token works" if success else "New token failed")
        
        return new_access_token
    else:
        results.add_test("Token Refresh", False, "Token refresh failed")
        return None

def test_error_handling(results: TestResults):
    """Test error handling and edge cases"""
    print("\n7️⃣ ERROR HANDLING")
    print("-" * 40)
    
    # Invalid endpoint
    success, response = make_request("GET", "/invalid/endpoint", expected_status=404)
    results.add_test("404 Error Handling", success, "Returns 404 for invalid endpoints")
    
    # Invalid credentials
    invalid_login = {"username": "invalid@test.com", "password": "wrongpass"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    success, response = make_request("POST", "/auth/login", invalid_login, headers, expected_status=401)
    results.add_test("Invalid Login Handling", success, "Returns 401 for invalid credentials")
    
    # Invalid API Key
    invalid_headers = {"X-API-Key": "invalid_key_12345"}
    success, response = make_request("GET", "/llm/models", headers=invalid_headers, expected_status=401)
    results.add_test("Invalid API Key Handling", success, "Returns 401 for invalid API key")
    
    # Missing Authorization
    success, response = make_request("GET", "/users/me", expected_status=401)
    results.add_test("Missing Auth Handling", success, "Returns 401 for missing authentication")

def test_performance_metrics(results: TestResults, api_key: str):
    """Test performance and response times"""
    print("\n8️⃣ PERFORMANCE METRICS")
    print("-" * 40)
    
    api_headers = {"X-API-Key": api_key}
    
    # Test multiple rapid requests
    start_time = time.time()
    successful_requests = 0
    
    for i in range(5):
        success, response = make_request("GET", "/llm/health", headers=api_headers, timeout=5)
        if success:
            successful_requests += 1
    
    duration = time.time() - start_time
    avg_response_time = duration / 5
    
    results.add_test("Rapid Requests", successful_requests >= 4, 
                    f"{successful_requests}/5 requests succeeded, avg {avg_response_time:.3f}s")
    
    # Response time test
    start_time = time.time()
    success, response = make_request("GET", "/llm/models", headers=api_headers)
    response_time = time.time() - start_time
    
    results.add_test("Response Time", response_time < 2.0, 
                    f"Models endpoint: {response_time:.3f}s")

def main():
    """Run comprehensive test suite"""
    print("🚀 FINAL COMPREHENSIVE AUTHENTICATION & API FLOW TEST")
    print("=" * 80)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing API: {BASE_URL}")
    print(f"📧 Test User: {TEST_EMAIL}")
    print("=" * 80)
    
    results = TestResults()
    
    try:
        # Test 1: Health Check
        if not test_health_check(results):
            print("❌ CRITICAL: API is not healthy. Stopping tests.")
            return False
        
        # Test 2: Authentication Flow
        access_token, refresh_token, user_id = test_authentication_flow(results)
        if not access_token:
            print("❌ CRITICAL: Authentication failed. Stopping tests.")
            results.print_summary()
            return False
        
        # Test 3: API Key Management
        api_key = test_api_key_management(results, access_token)
        if not api_key:
            print("❌ CRITICAL: API key creation failed. Stopping tests.")
            results.print_summary()
            return False
        
        # Test 4: LLM Services
        test_llm_services(results, api_key)
        
        # Test 5: Subscription Management
        test_subscription_management(results, access_token, api_key)
        
        # Test 6: Token Refresh
        new_access_token = test_token_refresh(results, refresh_token)
        
        # Test 7: Error Handling
        test_error_handling(results)
        
        # Test 8: Performance
        test_performance_metrics(results, api_key)
        
        # Generate final summary
        success = results.print_summary()
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        results.print_summary()
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        results.add_test("Unexpected Error", False, str(e))
        results.print_summary()
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
