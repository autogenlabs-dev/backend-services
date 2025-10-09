#!/usr/bin/env python3
"""
Test LLM Proxy APIs
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = f"llmtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
TEST_PASSWORD = "LLMTest123"

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
    try:
        body = response.json()
        print(f"{Colors.CYAN}Body:{Colors.RESET} {json.dumps(body, indent=2)}")
    except:
        print(f"{Colors.CYAN}Body:{Colors.RESET} {response.text[:500]}")

tests_passed = 0
tests_failed = 0
test_results = []

def register_and_login() -> str:
    """Register and login"""
    print_header("Setup: Register and Login")
    
    register_data = {
        "email": TEST_USER_EMAIL,
        "username": TEST_USER_EMAIL.split('@')[0],
        "password": TEST_PASSWORD,
        "name": "LLM Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code != 200:
        print_error(f"Registration failed")
        return ""
    
    print_success("Registered")
    
    login_data = {"username": TEST_USER_EMAIL, "password": TEST_PASSWORD}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if response.status_code != 200:
        print_error(f"Login failed")
        return ""
    
    token = response.json()["access_token"]
    print_success("Logged in")
    return token

def test_llm_health(token: str):
    global tests_passed, tests_failed
    print_header("Test: LLM Health Check")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/llm/health", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        print_success("LLM Health check passed!")
        test_results.append(("LLM Health", "PASSED"))
        tests_passed += 1
    else:
        print_error(f"LLM Health check failed: {response.status_code}")
        test_results.append(("LLM Health", "FAILED"))
        tests_failed += 1

def test_llm_providers(token: str):
    global tests_passed, tests_failed
    print_header("Test: List LLM Providers")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/llm/providers", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        print_success("LLM Providers retrieved!")
        test_results.append(("LLM Providers", "PASSED"))
        tests_passed += 1
    else:
        print_error(f"LLM Providers failed: {response.status_code}")
        test_results.append(("LLM Providers", "FAILED"))
        tests_failed += 1

def test_llm_models(token: str):
    global tests_passed, tests_failed
    print_header("Test: List LLM Models")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/llm/models", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        print_success("LLM Models retrieved!")
        test_results.append(("LLM Models", "PASSED"))
        tests_passed += 1
    else:
        print_error(f"LLM Models failed: {response.status_code}")
        test_results.append(("LLM Models", "FAILED"))
        tests_failed += 1

def print_summary():
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
    print_header("🚀 Starting LLM Proxy API Tests")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test User: {TEST_USER_EMAIL}")
    
    token = register_and_login()
    if not token:
        print_error("Setup failed")
        return
    
    test_llm_health(token)
    test_llm_providers(token)
    test_llm_models(token)
    
    print_summary()

if __name__ == "__main__":
    main()
