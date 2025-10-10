#!/usr/bin/env python3
"""
Comprehensive API Testing Script - Token Management APIs
Tests all token-related endpoints systematically
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = f"tokentest_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
TEST_PASSWORD = "TokenTest123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title: str):
    print(f"\n{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^80}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*80}{Colors.RESET}\n")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.RESET}")

def print_response(response: requests.Response):
    print(f"\n{Colors.CYAN}Status Code:{Colors.RESET} {response.status_code}")
    print(f"{Colors.CYAN}Headers:{Colors.RESET} {dict(response.headers)}")
    try:
        body = response.json()
        print(f"{Colors.CYAN}Body:{Colors.RESET} {json.dumps(body, indent=2)}")
    except:
        print(f"{Colors.CYAN}Body:{Colors.RESET} {response.text}")

# Test counters
tests_passed = 0
tests_failed = 0
test_results = []

def register_and_login() -> str:
    """Register a new user and return access token"""
    print_header("Setup: Register and Login")
    
    # Register
    register_data = {
        "email": TEST_USER_EMAIL,
        "username": TEST_USER_EMAIL.split('@')[0],
        "password": TEST_PASSWORD,
        "name": "Token Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code != 200:
        print_error(f"Registration failed: {response.text}")
        return None
    
    print_success("User registered successfully")
    
    # Login
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code != 200:
        print_error(f"Login failed: {response.text}")
        return None
    
    token = response.json()["access_token"]
    print_success("Login successful")
    print_info(f"Access Token: {token[:50]}...")
    
    return token

def test_token_balance(token: str):
    """Test GET /tokens/balance"""
    global tests_passed, tests_failed
    
    print_header("Test: Get Token Balance")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tokens/balance", headers=headers)
    
    print_response(response)
    
    if response.status_code == 200:
        print_success("Token balance retrieved successfully!")
        test_results.append(("Get Token Balance", "PASSED"))
        tests_passed += 1
    else:
        print_error(f"Failed to get token balance: {response.status_code}")
        test_results.append(("Get Token Balance", "FAILED"))
        tests_failed += 1

def test_token_limits(token: str):
    """Test GET /tokens/limits"""
    global tests_passed, tests_failed
    
    print_header("Test: Get Token Limits")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tokens/limits", headers=headers)
    
    print_response(response)
    
    if response.status_code == 200:
        print_success("Token limits retrieved successfully!")
        test_results.append(("Get Token Limits", "PASSED"))
        tests_passed += 1
    else:
        print_error(f"Failed to get token limits: {response.status_code}")
        test_results.append(("Get Token Limits", "FAILED"))
        tests_failed += 1

def test_token_usage(token: str):
    """Test GET /tokens/usage"""
    global tests_passed, tests_failed
    
    print_header("Test: Get Token Usage History")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": 10, "offset": 0}
    response = requests.get(f"{BASE_URL}/tokens/usage", headers=headers, params=params)
    
    print_response(response)
    
    if response.status_code == 200:
        print_success("Token usage history retrieved successfully!")
        test_results.append(("Get Token Usage", "PASSED"))
        tests_passed += 1
    else:
        print_error(f"Failed to get token usage: {response.status_code}")
        test_results.append(("Get Token Usage", "FAILED"))
        tests_failed += 1

def test_token_stats(token: str):
    """Test GET /tokens/stats"""
    global tests_passed, tests_failed
    
    print_header("Test: Get Token Usage Stats")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"days": 30}
    response = requests.get(f"{BASE_URL}/tokens/stats", headers=headers, params=params)
    
    print_response(response)
    
    if response.status_code == 200:
        print_success("Token usage stats retrieved successfully!")
        test_results.append(("Get Token Stats", "PASSED"))
        tests_passed += 1
    else:
        print_error(f"Failed to get token stats: {response.status_code}")
        test_results.append(("Get Token Stats", "FAILED"))
        tests_failed += 1

def test_token_reserve(token: str):
    """Test POST /tokens/reserve"""
    global tests_passed, tests_failed
    
    print_header("Test: Reserve Tokens")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "amount": 1000,
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "request_type": "chat"
    }
    response = requests.post(f"{BASE_URL}/tokens/reserve", headers=headers, params=params)
    
    print_response(response)
    
    if response.status_code == 200:
        print_success("Tokens reserved successfully!")
        test_results.append(("Reserve Tokens", "PASSED"))
        tests_passed += 1
        return True
    else:
        print_error(f"Failed to reserve tokens: {response.status_code}")
        test_results.append(("Reserve Tokens", "FAILED"))
        tests_failed += 1
        return False

def test_token_consume(token: str):
    """Test POST /tokens/consume"""
    global tests_passed, tests_failed
    
    print_header("Test: Consume Tokens")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "amount": 500,
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "request_type": "chat",
        "input_tokens": 300,
        "output_tokens": 200
    }
    
    metadata = {
        "request_id": "test_request_001",
        "endpoint": "chat/completions",
        "model": "gpt-3.5-turbo"
    }
    
    response = requests.post(
        f"{BASE_URL}/tokens/consume",
        headers=headers,
        params=params,
        json=metadata
    )
    
    print_response(response)
    
    if response.status_code == 200:
        print_success("Tokens consumed successfully!")
        test_results.append(("Consume Tokens", "PASSED"))
        tests_passed += 1
    else:
        print_error(f"Failed to consume tokens: {response.status_code}")
        test_results.append(("Consume Tokens", "FAILED"))
        tests_failed += 1

def print_summary():
    """Print test summary"""
    print_header("📊 Test Summary")
    
    for test_name, status in test_results:
        if status == "PASSED":
            print_success(f"PASSED - {test_name}")
        else:
            print_error(f"FAILED - {test_name}")
    
    total = tests_passed + tests_failed
    print(f"\n{Colors.BOLD}Total: {tests_passed}/{total} tests passed{Colors.RESET}")
    
    if tests_failed == 0:
        print(f"{Colors.GREEN}✅ 🎉 All tests passed!{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ {tests_failed} test(s) failed{Colors.RESET}")

def main():
    print_header("🚀 Starting Token Management API Tests")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test User: {TEST_USER_EMAIL}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup
    token = register_and_login()
    if not token:
        print_error("Setup failed. Cannot continue tests.")
        return
    
    # Run all tests
    test_token_balance(token)
    test_token_limits(token)
    test_token_usage(token)
    test_token_stats(token)
    test_token_reserve(token)
    test_token_consume(token)
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()
