#!/usr/bin/env python3
"""Test API Keys Management"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = f"apikey_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
TEST_PASSWORD = "ApiKey123"

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
    print_header("Setup: Register and Login")
    
    register_data = {
        "email": TEST_USER_EMAIL,
        "username": TEST_USER_EMAIL.split('@')[0],
        "password": TEST_PASSWORD,
        "name": "API Key Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code != 200:
        print_error("Registration failed")
        return ""
    
    print_success("Registered")
    
    login_data = {"username": TEST_USER_EMAIL, "password": TEST_PASSWORD}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if response.status_code != 200:
        print_error("Login failed")
        return ""
    
    token = response.json()["access_token"]
    print_success("Logged in")
    return token

def test_list_api_keys(token: str):
    global tests_passed, tests_failed
    print_header("Test: List API Keys")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/keys/", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        print_success("API Keys list retrieved!")
        test_results.append(("List API Keys", "PASSED"))
        tests_passed += 1
        return response.json()
    else:
        print_error(f"Failed: {response.status_code}")
        test_results.append(("List API Keys", "FAILED"))
        tests_failed += 1
        return []

def test_create_api_key(token: str):
    global tests_passed, tests_failed
    print_header("Test: Create API Key")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": "Test API Key", "description": "Testing API key creation"}
    response = requests.post(f"{BASE_URL}/api/keys/", headers=headers, json=data)
    print_response(response)
    
    if response.status_code == 200:
        print_success("API Key created!")
        test_results.append(("Create API Key", "PASSED"))
        tests_passed += 1
        return response.json()
    else:
        print_error(f"Failed: {response.status_code}")
        test_results.append(("Create API Key", "FAILED"))
        tests_failed += 1
        return None

def test_validate_api_key(api_key: str):
    global tests_passed, tests_failed
    print_header("Test: Validate API Key")
    
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(f"{BASE_URL}/api/keys/validate", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        print_success("API Key validated!")
        test_results.append(("Validate API Key", "PASSED"))
        tests_passed += 1
    else:
        print_error(f"Failed: {response.status_code}")
        test_results.append(("Validate API Key", "FAILED"))
        tests_failed += 1

def test_revoke_api_key(token: str, key_id: str):
    global tests_passed, tests_failed
    print_header("Test: Revoke API Key")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/api/keys/{key_id}", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        print_success("API Key revoked!")
        test_results.append(("Revoke API Key", "PASSED"))
        tests_passed += 1
    else:
        print_error(f"Failed: {response.status_code}")
        test_results.append(("Revoke API Key", "FAILED"))
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
    print_header("🚀 Starting API Keys Management Tests")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test User: {TEST_USER_EMAIL}")
    
    token = register_and_login()
    if not token:
        print_error("Setup failed")
        return
    
    # Test list (should be empty initially)
    test_list_api_keys(token)
    
    # Create new API key
    key_response = test_create_api_key(token)
    
    if key_response and "api_key" in key_response:
        api_key = key_response["api_key"]
        key_id = key_response.get("id", "")
        
        # Validate the newly created key
        test_validate_api_key(api_key)
        
        # Revoke the key
        if key_id:
            test_revoke_api_key(token, key_id)
    
    print_summary()

if __name__ == "__main__":
    main()
