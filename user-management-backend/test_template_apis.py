#!/usr/bin/env python3
"""Test Template APIs"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
TEST_PASSWORD = "Template123"

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
        print(f"{Colors.CYAN}Body:{Colors.RESET} {json.dumps(body, indent=2)[:1000]}")
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
        "name": "Template Test User"
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

def test_get_categories(token: str):
    global tests_passed, tests_failed
    print_header("Test: Get Template Categories")
    
    response = requests.get(f"{BASE_URL}/templates/categories")
    print_response(response)
    
    if response.status_code == 200:
        print_success("Categories retrieved!")
        test_results.append(("Get Categories", "PASSED"))
        tests_passed += 1
    else:
        print_error(f"Failed: {response.status_code}")
        test_results.append(("Get Categories", "FAILED"))
        tests_failed += 1

def test_list_all_templates(token: str):
    global tests_passed, tests_failed
    print_header("Test: List All Templates")
    
    response = requests.get(f"{BASE_URL}/templates/")
    print_response(response)
    
    if response.status_code == 200:
        print_success("Templates list retrieved!")
        test_results.append(("List All Templates", "PASSED"))
        tests_passed += 1
        return response.json()
    else:
        print_error(f"Failed: {response.status_code}")
        test_results.append(("List All Templates", "FAILED"))
        tests_failed += 1
        return None

def test_get_my_templates(token: str):
    global tests_passed, tests_failed
    print_header("Test: Get My Templates")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/templates/my", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        print_success("My templates retrieved!")
        test_results.append(("Get My Templates", "PASSED"))
        tests_passed += 1
    else:
        print_error(f"Failed: {response.status_code}")
        test_results.append(("Get My Templates", "FAILED"))
        tests_failed += 1

def test_create_template(token: str):
    global tests_passed, tests_failed
    print_header("Test: Create Template")
    
    headers = {"Authorization": f"Bearer {token}"}
    template_data = {
        "title": "Test Template",
        "description": "A test template created via API",
        "category": "Test",
        "plan_type": "Free",
        "difficulty_level": "Beginner",
        "config": {"test": "data"},
        "version": "1.0.0"
    }
    
    response = requests.post(f"{BASE_URL}/templates/", headers=headers, json=template_data)
    print_response(response)
    
    if response.status_code == 200:
        print_success("Template created!")
        test_results.append(("Create Template", "PASSED"))
        tests_passed += 1
        return response.json()
    else:
        print_error(f"Failed: {response.status_code}")
        test_results.append(("Create Template", "FAILED"))
        tests_failed += 1
        return None

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
    print_header("🚀 Starting Template API Tests")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test User: {TEST_USER_EMAIL}")
    
    token = register_and_login()
    if not token:
        print_error("Setup failed")
        return
    
    test_get_categories(token)
    test_list_all_templates(token)
    test_get_my_templates(token)
    test_create_template(token)
    
    print_summary()

if __name__ == "__main__":
    main()
