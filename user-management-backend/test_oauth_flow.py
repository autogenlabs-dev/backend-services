#!/usr/bin/env python3
"""
OAuth Flow Testing Script for User Management Backend
Tests Google and GitHub OAuth authentication flows
"""

import requests
import json
import webbrowser
import urllib.parse
from typing import Optional, Dict, Any
import sys
import time

# Configuration
BASE_URL = "http://localhost:8000/api"  # Updated to match the running server port with API prefix

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
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body: {response.text}")

def test_oauth_providers():
    """Test OAuth providers listing"""
    print_header("Testing OAuth Providers List")
    try:
        response = requests.get(f"{BASE_URL}/auth/providers")
        if response.status_code == 200:
            providers = response.json()
            print_success(f"OAuth providers retrieved: {json.dumps(providers, indent=2)}")
            return providers
        else:
            print_error(f"Failed to get OAuth providers: {response.status_code}")
            print_response(response)
            return None
    except Exception as e:
        print_error(f"OAuth providers error: {str(e)}")
        return None

def test_oauth_login_initiation(provider: str):
    """Test OAuth login initiation"""
    print_header(f"Testing {provider.upper()} OAuth Login Initiation")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/{provider}/login", allow_redirects=False)
        
        if response.status_code in [302, 303]:
            redirect_url = response.headers.get('Location')
            if redirect_url:
                print_success(f"OAuth login initiated successfully!")
                print_info(f"Redirect URL: {redirect_url}")
                print_info(f"You can manually visit this URL to test OAuth flow")
                return redirect_url
            else:
                print_error("No redirect URL found in response")
                return None
        else:
            print_error(f"OAuth login initiation failed with status {response.status_code}")
            print_response(response)
            return None
    except Exception as e:
        print_error(f"OAuth login initiation error: {str(e)}")
        return None

def test_oauth_callback_simulation(provider: str):
    """Simulate OAuth callback (this would normally be handled by the OAuth provider)"""
    print_header(f"Testing {provider.upper()} OAuth Callback Simulation")
    
    print_warning("Note: This is a simulation. In a real scenario:")
    print_info("1. User would be redirected to OAuth provider")
    print_info("2. User would authenticate and authorize the application")
    print_info("3. Provider would redirect back to our callback URL")
    print_info("4. Our callback endpoint would process the response")
    
    # Check if callback endpoint exists
    try:
        response = requests.get(f"{BASE_URL}/auth/{provider}/callback")
        if response.status_code == 422:  # Expected for missing OAuth parameters
            print_success(f"OAuth callback endpoint exists and is properly configured")
            return True
        else:
            print_warning(f"Unexpected response from callback endpoint: {response.status_code}")
            print_response(response)
            return False
    except Exception as e:
        print_error(f"OAuth callback test error: {str(e)}")
        return False

def test_oauth_endpoints():
    """Test all OAuth-related endpoints"""
    print_header("Testing OAuth Endpoints")
    
    # Test providers list
    providers = test_oauth_providers()
    if not providers:
        return False
    
    # Get available providers
    available_providers = [p['name'] for p in providers.get('providers', [])]
    
    if not available_providers:
        print_error("No OAuth providers are configured")
        return False
    
    print_info(f"Available OAuth providers: {available_providers}")
    
    # Test each provider
    results = {}
    for provider in available_providers:
        print_info(f"\n--- Testing {provider.upper()} ---")
        
        # Test login initiation
        redirect_url = test_oauth_login_initiation(provider)
        results[f"{provider}_login"] = redirect_url is not None
        
        # Test callback endpoint
        results[f"{provider}_callback"] = test_oauth_callback_simulation(provider)
        
        # Small delay between tests
        time.sleep(1)
    
    return results

def test_manual_oauth_flow():
    """Guide user through manual OAuth flow testing"""
    print_header("Manual OAuth Flow Testing Guide")
    
    providers = test_oauth_providers()
    if not providers:
        return False
    
    available_providers = [p['name'] for p in providers.get('providers', [])]
    
    print_info("To manually test OAuth flow:")
    print("1. Open your browser")
    print("2. Visit one of these URLs:")
    
    for provider in available_providers:
        url = f"{BASE_URL}/auth/{provider}/login"
        print(f"   - {provider.upper()}: {url}")
    
    print("\n3. Complete the authentication in your browser")
    print("4. You should be redirected back with a token")
    print("5. Check the server logs for any errors")
    
    return True

def main():
    """Main test function"""
    print_header("🔐 OAuth Flow Testing")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test OAuth endpoints
    results = test_oauth_endpoints()
    
    # Provide manual testing guide
    test_manual_oauth_flow()
    
    # Print summary
    print_header("📊 OAuth Test Summary")
    
    if results:
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            color = Colors.OKGREEN if result else Colors.FAIL
            print(f"{color}{status}{Colors.ENDC} - {test_name}")
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        print(f"\n{Colors.BOLD}OAuth Tests: {passed}/{total} passed{Colors.ENDC}")
    else:
        print_warning("OAuth tests could not be completed")
    
    print_info("\n📝 Manual Testing Required:")
    print_info("OAuth flows require browser interaction for complete testing")
    print_info("Use the URLs provided above to test the full flow")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_warning("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\n💥 Fatal error: {str(e)}")
        sys.exit(1)
