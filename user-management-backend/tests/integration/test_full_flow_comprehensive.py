#!/usr/bin/env python3
"""
Comprehensive test script for the full marketplace backend flow.
Tests authentication, rate limiting, API keys, subscriptions, LLM endpoints, and admin analytics.
"""

import requests
import json
import time
from datetime import datetime
import sys

# Base URL for the API
BASE_URL = "http://localhost:8000"

class TestResults:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
    
    def add_test(self, name, passed, details=None):
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            self.tests_failed += 1
            self.failures.append(f"{name}: {details}")
            print(f"❌ {name}: {details}")
    
    def print_summary(self):
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failures:
            print("\n❌ FAILURES:")
            for failure in self.failures:
                print(f"  - {failure}")

def test_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Helper function to test API endpoints"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        
        return response.status_code == expected_status, response
    except Exception as e:
        return False, str(e)

def main():
    results = TestResults()
    
    print("🚀 Starting Comprehensive Backend Test Suite")
    print(f"📅 Started at: {datetime.now()}")
    print(f"🌐 Testing API at: {BASE_URL}")
    print("="*60)
    
    # Store tokens and user data
    access_token = None
    refresh_token = None
    user_id = None
    api_key = None
    
    # 1. Health Check Tests
    print("\n1️⃣ HEALTH CHECK TESTS")
    print("-" * 30)
    
    # Test root endpoint
    success, response = test_endpoint("GET", "/")
    results.add_test("Root endpoint", success, None if success else response)
    
    # Test health endpoint
    success, response = test_endpoint("GET", "/health")
    results.add_test("Health endpoint", success, None if success else response)
    
    # 2. Authentication Flow Tests
    print("\n2️⃣ AUTHENTICATION FLOW TESTS")
    print("-" * 30)
    
    # Test user registration
    test_user = {
        "email": f"testuser_{int(time.time())}@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    }
    
    success, response = test_endpoint("POST", "/auth/register", test_user)
    if success:
        user_data = response.json()
        user_id = user_data.get("user", {}).get("id")
    results.add_test("User registration", success, None if success else response.text)
    
    # Test user login
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            success = True
        else:
            success = False
    except Exception as e:
        success = False
        response = str(e)
    
    results.add_test("User login", success, None if success else response.text if hasattr(response, 'text') else response)
    
    # Test protected endpoint access
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        success, response = test_endpoint("GET", "/users/me", headers=headers)
        results.add_test("Protected endpoint access", success, None if success else response.text)
    
    # 3. Rate Limiting Tests
    print("\n3️⃣ RATE LIMITING TESTS")
    print("-" * 30)
    
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
          # Test multiple requests to check rate limiting headers
        success, response = test_endpoint("GET", "/users/me", headers=headers)
        if success and hasattr(response, 'headers'):
            has_rate_limit_headers = any(header.lower().startswith('x-ratelimit') for header in response.headers)
            results.add_test("Rate limit headers present", has_rate_limit_headers, 
                           "No rate limit headers found" if not has_rate_limit_headers else None)
        else:
            results.add_test("Rate limit headers present", False, "Could not check headers")
    
    # 4. API Key Management Tests
    print("\n4️⃣ API KEY MANAGEMENT TESTS")
    print("-" * 30)
    
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Create API key
        api_key_data = {
            "name": "Test API Key",
            "description": "For testing purposes"
        }
        success, response = test_endpoint("POST", "/api/keys", api_key_data, headers)
        if success:
            api_key_response = response.json()
            api_key = api_key_response.get("key")
        results.add_test("API key creation", success, None if success else response.text)
        
        # List API keys
        success, response = test_endpoint("GET", "/api/keys", headers=headers)
        results.add_test("List API keys", success, None if success else response.text)
    
    # 5. Subscription Management Tests
    print("\n5️⃣ SUBSCRIPTION MANAGEMENT TESTS")
    print("-" * 30)
    
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Get current subscription
        success, response = test_endpoint("GET", "/subscriptions/current", headers=headers)
        results.add_test("Get current subscription", success, None if success else response.text)
        
        # List available plans
        success, response = test_endpoint("GET", "/subscriptions/plans", headers=headers)
        results.add_test("List subscription plans", success, None if success else response.text)
    
    # 6. LLM Endpoint Tests
    print("\n6️⃣ LLM ENDPOINT TESTS")
    print("-" * 30)
    
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test LLM health check
        success, response = test_endpoint("GET", "/llm/health", headers=headers)
        results.add_test("LLM health check", success, None if success else response.text)
        
        # Test list providers
        success, response = test_endpoint("GET", "/llm/providers", headers=headers)
        results.add_test("List LLM providers", success, None if success else response.text)
        
        # Test list models
        success, response = test_endpoint("GET", "/llm/models", headers=headers)
        results.add_test("List LLM models", success, None if success else response.text)
    
    # 7. Token Management Tests
    print("\n7️⃣ TOKEN MANAGEMENT TESTS")
    print("-" * 30)
    
    if refresh_token:
        # Test token refresh
        refresh_data = {"refresh_token": refresh_token}
        success, response = test_endpoint("POST", "/auth/refresh", refresh_data)
        if success:
            new_token_data = response.json()
            new_access_token = new_token_data.get("access_token")
            if new_access_token:
                access_token = new_access_token  # Update for further tests
        results.add_test("Token refresh", success, None if success else response.text)
    
    # 8. API Key Authentication Tests
    print("\n8️⃣ API KEY AUTHENTICATION TESTS")
    print("-" * 30)
    
    if api_key:
        api_headers = {"X-API-Key": api_key}
        
        # Test API key authentication
        success, response = test_endpoint("GET", "/users/me", headers=api_headers)
        results.add_test("API key authentication", success, None if success else response.text)
    
    # 9. Error Handling Tests
    print("\n9️⃣ ERROR HANDLING TESTS")
    print("-" * 30)
    
    # Test invalid endpoint
    success, response = test_endpoint("GET", "/invalid/endpoint", expected_status=404)
    results.add_test("404 for invalid endpoint", success, None if success else "Did not return 404")    # Test unauthorized access
    success, response = test_endpoint("GET", "/users/me")
    # Accept both 401 (Unauthorized) and 403 (Forbidden) as valid responses for unauthenticated access
    if hasattr(response, 'status_code'):
        unauthorized_success = response.status_code in [401, 403]
        error_msg = None if unauthorized_success else f"Expected 401/403, got {response.status_code}"
    else:
        unauthorized_success = False
        error_msg = f"Request failed: {response}"
    results.add_test("401 for unauthorized access", unauthorized_success, error_msg)
    
    # Test invalid login
    invalid_login = {
        "username": "invalid@email.com",
        "password": "wrongpassword"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=invalid_login)
        success = response.status_code in [401, 422]  # Either unauthorized or validation error
    except Exception:
        success = False
    results.add_test("Invalid login rejection", success, None if success else "Did not reject invalid login")
    
    # 10. Performance Tests
    print("\n🔟 BASIC PERFORMANCE TESTS")
    print("-" * 30)
    
    # Test response time
    start_time = time.time()
    success, response = test_endpoint("GET", "/health")
    end_time = time.time()
    response_time = end_time - start_time
    
    fast_response = response_time < 1.0  # Should respond within 1 second
    results.add_test("Fast response time", fast_response, 
                   f"Response took {response_time:.2f}s" if not fast_response else None)
    
    # Test concurrent requests
    import threading
    
    def make_request():
        return test_endpoint("GET", "/health")
    
    threads = []
    concurrent_results = []
    
    for i in range(5):
        thread = threading.Thread(target=lambda: concurrent_results.append(make_request()))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    concurrent_success = all(result[0] for result in concurrent_results)
    results.add_test("Concurrent requests handling", concurrent_success, 
                   "Some concurrent requests failed" if not concurrent_success else None)
    
    # Print final results
    results.print_summary()
    
    # Return appropriate exit code
    return 0 if results.tests_failed == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)