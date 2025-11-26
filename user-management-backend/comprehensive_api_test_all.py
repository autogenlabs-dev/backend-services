#!/usr/bin/env python3
"""
Comprehensive API Test Script
Tests all endpoints in the backend API one by one
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import sys

# Base URL
BASE_URL = "http://localhost:8000"

# Test results storage
test_results = []

# Global variables for authentication
access_token = None
api_key = None
test_user_email = f"test_user_{datetime.now().timestamp()}@example.com"
test_user_password = "TestPassword123!"


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")


def print_test(name: str, status: str, details: str = ""):
    """Print test result"""
    color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    print(f"{color}[{status}]{Colors.RESET} {name}")
    if details:
        print(f"       {details}")


def test_endpoint(
    name: str,
    method: str,
    endpoint: str,
    headers: Optional[Dict] = None,
    data: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    params: Optional[Dict] = None,
    expected_status: int = 200,
    auth_required: bool = False,
    skip: bool = False,
    skip_reason: str = ""
) -> Dict:
    """
    Test an API endpoint
    
    Args:
        name: Test name
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint path
        headers: Additional headers
        data: Form data
        json_data: JSON data
        params: Query parameters
        expected_status: Expected HTTP status code
        auth_required: Whether authentication is required
        skip: Whether to skip this test
        skip_reason: Reason for skipping
    
    Returns:
        Dict with test results
    """
    global access_token
    
    if skip:
        print_test(name, "SKIP", skip_reason)
        return {"name": name, "status": "SKIP", "reason": skip_reason}
    
    url = f"{BASE_URL}{endpoint}"
    
    # Prepare headers
    req_headers = headers or {}
    if auth_required and access_token:
        req_headers["Authorization"] = f"Bearer {access_token}"
    
    try:
        # Make request
        if method == "GET":
            response = requests.get(url, headers=req_headers, params=params)
        elif method == "POST":
            if data:
                response = requests.post(url, headers=req_headers, data=data, params=params)
            else:
                response = requests.post(url, headers=req_headers, json=json_data, params=params)
        elif method == "PUT":
            response = requests.put(url, headers=req_headers, json=json_data, params=params)
        elif method == "DELETE":
            response = requests.delete(url, headers=req_headers, params=params)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        # Check status
        status = "PASS" if response.status_code == expected_status else "FAIL"
        
        # Prepare details
        details = f"Status: {response.status_code}"
        if response.status_code != expected_status:
            details += f" (Expected: {expected_status})"
        
        try:
            response_data = response.json()
            if status == "FAIL":
                details += f" | Response: {json.dumps(response_data)[:100]}"
        except:
            if status == "FAIL":
                details += f" | Response: {response.text[:100]}"
        
        print_test(name, status, details)
        
        return {
            "name": name,
            "status": status,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "response": response.text[:500] if status == "FAIL" else "OK"
        }
        
    except Exception as e:
        print_test(name, "ERROR", str(e))
        return {
            "name": name,
            "status": "ERROR",
            "error": str(e)
        }


def test_health_endpoints():
    """Test health and root endpoints"""
    print_header("HEALTH & ROOT ENDPOINTS")
    
    test_results.append(test_endpoint(
        "Root Endpoint",
        "GET",
        "/",
        expected_status=200
    ))
    
    test_results.append(test_endpoint(
        "Health Check",
        "GET",
        "/health",
        expected_status=200
    ))


def test_authentication():
    """Test authentication endpoints"""
    global access_token, test_user_email, test_user_password
    
    print_header("AUTHENTICATION ENDPOINTS")
    
    # List OAuth providers
    test_results.append(test_endpoint(
        "List OAuth Providers",
        "GET",
        "/api/auth/providers",
        expected_status=200
    ))
    
    # Register user
    result = test_endpoint(
        "Register User",
        "POST",
        "/api/auth/register",
        json_data={
            "email": test_user_email,
            "password": test_user_password,
            "name": "Test User"
        },
        expected_status=200
    )
    test_results.append(result)
    
    # Login user (JSON)
    response = requests.post(
        f"{BASE_URL}/api/auth/login-json",
        json={"email": test_user_email, "password": test_user_password}
    )
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        print_test("Login User (JSON)", "PASS", f"Token obtained: {access_token[:20]}...")
        test_results.append({"name": "Login User (JSON)", "status": "PASS"})
    else:
        print_test("Login User (JSON)", "FAIL", f"Status: {response.status_code}")
        test_results.append({"name": "Login User (JSON)", "status": "FAIL"})
    
    # Login user (Form)
    test_results.append(test_endpoint(
        "Login User (Form)",
        "POST",
        "/api/auth/login",
        data={"username": test_user_email, "password": test_user_password},
        expected_status=200
    ))
    
    # Get current user info
    test_results.append(test_endpoint(
        "Get Current User Info",
        "GET",
        "/api/auth/me",
        auth_required=True,
        expected_status=200
    ))
    
    # Get VS Code config
    test_results.append(test_endpoint(
        "Get VS Code Configuration",
        "GET",
        "/api/auth/vscode-config",
        auth_required=True,
        expected_status=200
    ))


def test_user_management():
    """Test user management endpoints"""
    print_header("USER MANAGEMENT ENDPOINTS")
    
    # Get my profile
    test_results.append(test_endpoint(
        "Get My Profile",
        "GET",
        "/api/users/me",
        auth_required=True,
        expected_status=200
    ))
    
    # Update my profile
    test_results.append(test_endpoint(
        "Update My Profile",
        "PUT",
        "/api/users/me",
        json_data={"name": "Updated Test User"},
        auth_required=True,
        expected_status=200
    ))
    
    # Get my API keys
    test_results.append(test_endpoint(
        "Get My API Keys",
        "GET",
        "/api/users/me/api-keys",
        auth_required=True,
        expected_status=200
    ))
    
    # Create API key
    response = requests.post(
        f"{BASE_URL}/api/users/me/api-keys",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "Test API Key"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_test("Create My API Key", "PASS", f"Key created: {data.get('key_preview', 'N/A')}")
        test_results.append({"name": "Create My API Key", "status": "PASS"})
    else:
        print_test("Create My API Key", "FAIL", f"Status: {response.status_code}")
        test_results.append({"name": "Create My API Key", "status": "FAIL"})


def test_subscriptions():
    """Test subscription endpoints"""
    print_header("SUBSCRIPTION ENDPOINTS")
    
    # List plans
    test_results.append(test_endpoint(
        "List Subscription Plans",
        "GET",
        "/api/subscriptions/plans",
        expected_status=200
    ))
    
    # Compare plans
    test_results.append(test_endpoint(
        "Compare Plans",
        "GET",
        "/api/subscriptions/plans/compare",
        expected_status=200
    ))
    
    # Get current subscription
    test_results.append(test_endpoint(
        "Get Current Subscription",
        "GET",
        "/api/subscriptions/current",
        auth_required=True,
        expected_status=200
    ))
    
    # Get usage stats
    test_results.append(test_endpoint(
        "Get Usage Stats",
        "GET",
        "/api/subscriptions/usage",
        auth_required=True,
        expected_status=200
    ))
    
    # Get upgrade options
    test_results.append(test_endpoint(
        "Get Upgrade Options",
        "GET",
        "/api/subscriptions/upgrade-options",
        auth_required=True,
        expected_status=200
    ))
    
    # Get payment methods
    test_results.append(test_endpoint(
        "Get Payment Methods",
        "GET",
        "/api/subscriptions/payment-methods",
        auth_required=True,
        expected_status=200
    ))


def test_tokens():
    """Test token management endpoints"""
    print_header("TOKEN MANAGEMENT ENDPOINTS")
    
    # Get token balance
    test_results.append(test_endpoint(
        "Get Token Balance",
        "GET",
        "/api/tokens/balance",
        auth_required=True,
        expected_status=200
    ))
    
    # Get token usage
    test_results.append(test_endpoint(
        "Get Token Usage",
        "GET",
        "/api/tokens/usage",
        auth_required=True,
        expected_status=200
    ))
    
    # Get token limits
    test_results.append(test_endpoint(
        "Get Token Limits",
        "GET",
        "/api/tokens/limits",
        auth_required=True,
        expected_status=200
    ))
    
    # Get usage stats
    test_results.append(test_endpoint(
        "Get Token Usage Stats",
        "GET",
        "/api/tokens/stats",
        auth_required=True,
        expected_status=200
    ))
    
    # Reserve tokens
    test_results.append(test_endpoint(
        "Reserve Tokens",
        "POST",
        "/api/tokens/reserve",
        params={
            "amount": 100,
            "provider": "openrouter",
            "model_name": "gpt-3.5-turbo",
            "request_type": "chat"
        },
        auth_required=True,
        expected_status=200
    ))
    
    # Get model pricing
    test_results.append(test_endpoint(
        "Get Model Pricing",
        "GET",
        "/api/tokens/pricing/openrouter/gpt-3.5-turbo",
        expected_status=200
    ))


def test_llm_proxy():
    """Test LLM proxy endpoints"""
    print_header("LLM PROXY ENDPOINTS")
    
    # List providers
    test_results.append(test_endpoint(
        "List LLM Providers",
        "GET",
        "/api/llm/providers",
        auth_required=True,
        expected_status=200
    ))
    
    # List models
    test_results.append(test_endpoint(
        "List LLM Models",
        "GET",
        "/api/llm/models",
        auth_required=True,
        expected_status=200
    ))
    
    # LLM health check
    test_results.append(test_endpoint(
        "LLM Health Check",
        "GET",
        "/api/llm/health",
        auth_required=True,
        expected_status=200
    ))


def test_templates():
    """Test template endpoints"""
    print_header("TEMPLATE ENDPOINTS")
    
    # Get all templates
    test_results.append(test_endpoint(
        "Get All Templates",
        "GET",
        "/api/templates/",
        expected_status=200
    ))
    
    # Get template categories
    test_results.append(test_endpoint(
        "Get Template Categories",
        "GET",
        "/api/templates/categories",
        expected_status=200
    ))
    
    # Get template stats
    test_results.append(test_endpoint(
        "Get Template Stats",
        "GET",
        "/api/templates/stats/overview",
        expected_status=200
    ))
    
    # Get my templates
    test_results.append(test_endpoint(
        "Get My Templates",
        "GET",
        "/api/templates/my",
        auth_required=True,
        expected_status=200
    ))
    
    # Get favorite templates
    test_results.append(test_endpoint(
        "Get Favorite Templates",
        "GET",
        "/api/templates/favorites",
        auth_required=True,
        expected_status=200
    ))


def test_payments():
    """Test payment endpoints"""
    print_header("PAYMENT ENDPOINTS")
    
    # Get payment config
    test_results.append(test_endpoint(
        "Get Payment Config",
        "GET",
        "/api/payments/config",
        expected_status=200
    ))
    
    # Get user orders
    test_results.append(test_endpoint(
        "Get User Orders",
        "GET",
        "/api/payments/orders",
        auth_required=True,
        expected_status=200
    ))


def test_api_keys():
    """Test API key management endpoints"""
    print_header("API KEY MANAGEMENT ENDPOINTS")
    
    # List API keys
    test_results.append(test_endpoint(
        "List API Keys",
        "GET",
        "/api/keys/",
        auth_required=True,
        expected_status=200
    ))
    
    # Validate current key
    test_results.append(test_endpoint(
        "Validate Current Key",
        "GET",
        "/api/keys/validate",
        auth_required=True,
        expected_status=200
    ))


def generate_report():
    """Generate and print test report"""
    print_header("TEST REPORT")
    
    total = len(test_results)
    passed = sum(1 for r in test_results if r.get("status") == "PASS")
    failed = sum(1 for r in test_results if r.get("status") == "FAIL")
    errors = sum(1 for r in test_results if r.get("status") == "ERROR")
    skipped = sum(1 for r in test_results if r.get("status") == "SKIP")
    
    print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  Total Tests:   {total}")
    print(f"  {Colors.GREEN}Passed:        {passed}{Colors.RESET}")
    print(f"  {Colors.RED}Failed:        {failed}{Colors.RESET}")
    print(f"  {Colors.RED}Errors:        {errors}{Colors.RESET}")
    print(f"  {Colors.YELLOW}Skipped:       {skipped}{Colors.RESET}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n  {Colors.BOLD}Success Rate:  {success_rate:.1f}%{Colors.RESET}\n")
    
    # Save detailed report
    report_file = f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "success_rate": success_rate
            },
            "results": test_results
        }, f, indent=2)
    
    print(f"{Colors.BLUE}Detailed report saved to: {report_file}{Colors.RESET}\n")
    
    # Print failed tests
    if failed > 0 or errors > 0:
        print(f"\n{Colors.BOLD}{Colors.RED}Failed/Error Tests:{Colors.RESET}")
        for result in test_results:
            if result.get("status") in ["FAIL", "ERROR"]:
                print(f"  - {result['name']}")
                if "error" in result:
                    print(f"    Error: {result['error']}")
                elif "response" in result:
                    print(f"    Response: {result['response'][:100]}")


def main():
    """Main test runner"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                   COMPREHENSIVE BACKEND API TEST SUITE                        ║")
    print("║                                                                               ║")
    print(f"║  Base URL: {BASE_URL:<66} ║")
    print(f"║  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<70} ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    try:
        # Run all test suites
        test_health_endpoints()
        test_authentication()
        test_user_management()
        test_subscriptions()
        test_tokens()
        test_llm_proxy()
        test_templates()
        test_payments()
        test_api_keys()
        
        # Generate report
        generate_report()
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}\n")
        generate_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Fatal error: {e}{Colors.RESET}\n")
        generate_report()
        sys.exit(1)


if __name__ == "__main__":
    main()
