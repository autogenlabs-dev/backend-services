#!/usr/bin/env python3
"""
Comprehensive API Testing Script for User Management Backend
Tests authentication, user management, and other API endpoints
"""

import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
TEST_USER_PASSWORD = "Password123"  # Now works with SHA-256 hashing
TEST_USER_USERNAME = f"testuser_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# Global variables to store tokens
access_token: Optional[str] = None
refresh_token: Optional[str] = None
user_id: Optional[str] = None


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}")
    print(f"{text.center(80)}")
    print(f"{'=' * 80}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_response(response: requests.Response, title: str = "Response"):
    """Pretty print response details"""
    print(f"\n{Colors.BOLD}{title}:{Colors.ENDC}")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body: {response.text}")


def test_health_check():
    """Test health check endpoint"""
    print_header("Testing Health Check Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success(f"Health check passed: {response.json()}")
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            print_response(response)
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False


def test_list_oauth_providers():
    """Test OAuth providers listing"""
    print_header("Testing OAuth Providers List")
    try:
        response = requests.get(f"{BASE_URL}/auth/providers")
        if response.status_code == 200:
            providers = response.json()
            print_success(f"OAuth providers retrieved: {providers}")
            return True
        else:
            print_error(f"Failed to get OAuth providers: {response.status_code}")
            print_response(response)
            return False
    except Exception as e:
        print_error(f"OAuth providers error: {str(e)}")
        return False


def test_signup():
    """Test user registration"""
    global user_id
    print_header("Testing User Registration (Signup)")
    
    payload = {
        "email": TEST_USER_EMAIL,
        "username": TEST_USER_USERNAME,
        "password": TEST_USER_PASSWORD,
        "name": "Test User",
        "full_name": "Test User Full Name",
        "first_name": "Test",
        "last_name": "User"
    }
    
    print_info(f"Registering user: {TEST_USER_EMAIL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            user_id = data.get("user", {}).get("id")
            print_success("User registration successful!")
            print_response(response, "Registration Response")
            return True
        else:
            print_error(f"Registration failed with status {response.status_code}")
            print_response(response)
            return False
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return False


def test_login():
    """Test user login"""
    global access_token, refresh_token
    print_header("Testing User Login")
    
    # Use JSON login endpoint instead of form-based login
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    print_info(f"Logging in as: {TEST_USER_EMAIL}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login-json",
            json=payload,  # Use json= for JSON data
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            print_success("Login successful!")
            print_info(f"Access Token: {access_token[:20]}..." if access_token else "No token")
            print_response(response, "Login Response")
            return True
        else:
            print_error(f"Login failed with status {response.status_code}")
            print_response(response)
            return False
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return False


def test_get_profile():
    """Test get user profile"""
    print_header("Testing Get User Profile")
    
    if not access_token:
        print_error("No access token available. Login first.")
        return False
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",  # Changed from /auth/profile to /auth/me
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("Profile retrieved successfully!")
            print_response(response, "Profile Response")
            return True
        else:
            print_error(f"Failed to get profile: {response.status_code}")
            print_response(response)
            return False
    except Exception as e:
        print_error(f"Profile error: {str(e)}")
        return False


def test_update_profile():
    """Test update user profile"""
    print_header("Testing Update User Profile")
    
    if not access_token:
        print_error("No access token available. Login first.")
        return False
    
    payload = {
        "name": "Updated Test User",
        "full_name": "Updated Test User Full Name"
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/users/me",  # Changed from /auth/profile to /users/me
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("Profile updated successfully!")
            print_response(response, "Update Response")
            return True
        else:
            print_error(f"Failed to update profile: {response.status_code}")
            print_response(response)
            return False
    except Exception as e:
        print_error(f"Update profile error: {str(e)}")
        return False


def test_token_refresh():
    """Test token refresh"""
    global access_token
    print_header("Testing Token Refresh")
    
    if not refresh_token:
        print_error("No refresh token available. Login first.")
        return False
    
    payload = {
        "refresh_token": refresh_token
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/refresh",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            new_access_token = data.get("access_token")
            if new_access_token:
                access_token = new_access_token
            print_success("Token refresh successful!")
            print_response(response, "Refresh Response")
            return True
        else:
            print_error(f"Token refresh failed: {response.status_code}")
            print_response(response)
            return False
    except Exception as e:
        print_error(f"Token refresh error: {str(e)}")
        return False


def test_logout():
    """Test logout"""
    print_header("Testing Logout")
    
    if not access_token:
        print_error("No access token available. Login first.")
        return False
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/logout",
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("Logout successful!")
            print_response(response, "Logout Response")
            return True
        else:
            print_error(f"Logout failed: {response.status_code}")
            print_response(response)
            return False
    except Exception as e:
        print_error(f"Logout error: {str(e)}")
        return False


def test_subscription_plans():
    """Test get subscription plans"""
    print_header("Testing Get Subscription Plans")
    
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/plans")
        
        if response.status_code == 200:
            print_success("Subscription plans retrieved!")
            print_response(response, "Subscription Plans")
            return True
        else:
            print_error(f"Failed to get plans: {response.status_code}")
            print_response(response)
            return False
    except Exception as e:
        print_error(f"Subscription plans error: {str(e)}")
        return False


def run_all_tests():
    """Run all API tests"""
    print_header("🚀 Starting Comprehensive API Tests")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test User: {TEST_USER_EMAIL}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test sequence
    tests = [
        ("Health Check", test_health_check),
        ("OAuth Providers", test_list_oauth_providers),
        ("User Registration", test_signup),
        ("User Login", test_login),
        ("Get Profile", test_get_profile),
        ("Update Profile", test_update_profile),
        ("Token Refresh", test_token_refresh),
        ("Subscription Plans", test_subscription_plans),
        ("Logout", test_logout),
    ]
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {str(e)}")
            results[test_name] = False
    
    # Print summary
    print_header("📊 Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        color = Colors.OKGREEN if result else Colors.FAIL
        print(f"{color}{status}{Colors.ENDC} - {test_name}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print_success("🎉 All tests passed!")
        return 0
    else:
        print_error(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_warning("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\n💥 Fatal error: {str(e)}")
        sys.exit(1)
