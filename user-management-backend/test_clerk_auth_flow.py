#!/usr/bin/env python3
"""
Test script for Clerk authentication flow with the backend API.
This script helps diagnose authentication issues between frontend and backend.
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_CLERK_TOKEN = None  # You'll need to paste a real Clerk JWT token here for testing

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_header(message):
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{message}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

async def test_health_check():
    """Test if the backend is running"""
    print_header("Test 1: Backend Health Check")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                print_success(f"Backend is running at {BACKEND_URL}")
                print_info(f"Response: {response.json()}")
                return True
            else:
                print_error(f"Backend returned status {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Cannot connect to backend: {e}")
        print_warning("Make sure the backend is running with: docker-compose up -d")
        return False

async def test_clerk_jwks_endpoint():
    """Test if Clerk JWKS endpoint is accessible"""
    print_header("Test 2: Clerk JWKS Endpoint")
    jwks_url = "https://apt-clam-53.clerk.accounts.dev/.well-known/jwks.json"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            if response.status_code == 200:
                jwks_data = response.json()
                print_success("Clerk JWKS endpoint is accessible")
                print_info(f"Number of keys: {len(jwks_data.get('keys', []))}")
                if jwks_data.get('keys'):
                    print_info(f"First key ID: {jwks_data['keys'][0].get('kid')}")
                return True
            else:
                print_error(f"JWKS endpoint returned status {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Cannot access Clerk JWKS endpoint: {e}")
        return False

async def test_cors_headers():
    """Test CORS configuration"""
    print_header("Test 3: CORS Configuration")
    try:
        async with httpx.AsyncClient() as client:
            # Send OPTIONS request to check CORS
            response = await client.options(
                f"{BACKEND_URL}/api/auth/me",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Authorization,Content-Type"
                }
            )
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("access-control-allow-origin"),
                "Access-Control-Allow-Methods": response.headers.get("access-control-allow-methods"),
                "Access-Control-Allow-Headers": response.headers.get("access-control-allow-headers"),
                "Access-Control-Allow-Credentials": response.headers.get("access-control-allow-credentials"),
            }
            
            print_info("CORS Headers:")
            for key, value in cors_headers.items():
                if value:
                    print(f"  {key}: {value}")
            
            if cors_headers["Access-Control-Allow-Origin"]:
                print_success("CORS is properly configured")
                return True
            else:
                print_error("CORS headers missing")
                return False
                
    except Exception as e:
        print_error(f"CORS test failed: {e}")
        return False

async def test_auth_with_clerk_token():
    """Test authentication with a Clerk JWT token"""
    print_header("Test 4: Clerk Token Authentication")
    
    if not FRONTEND_CLERK_TOKEN:
        print_warning("No Clerk token provided")
        print_info("To test with a real token:")
        print_info("1. Sign in to your frontend (http://localhost:3000)")
        print_info("2. Open browser DevTools > Application > Cookies")
        print_info("3. Copy the __session cookie value")
        print_info("4. Set FRONTEND_CLERK_TOKEN variable in this script")
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/auth/me",
                headers={
                    "Authorization": f"Bearer {FRONTEND_CLERK_TOKEN}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print_success("Successfully authenticated with Clerk token")
                print_info(f"User: {user_data.get('email')}")
                print_info(f"User ID: {user_data.get('id')}")
                return True
            elif response.status_code == 401:
                print_error("Authentication failed (401 Unauthorized)")
                print_info(f"Response: {response.json()}")
                return False
            else:
                print_error(f"Unexpected status code: {response.status_code}")
                print_info(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print_error(f"Authentication test failed: {e}")
        return False

async def test_public_endpoints():
    """Test public endpoints"""
    print_header("Test 5: Public Endpoints")
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/docs", "API documentation"),
    ]
    
    all_pass = True
    async with httpx.AsyncClient() as client:
        for endpoint, description in endpoints:
            try:
                response = await client.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    print_success(f"{description}: {endpoint}")
                else:
                    print_warning(f"{description}: {endpoint} (Status: {response.status_code})")
                    all_pass = False
            except Exception as e:
                print_error(f"{description}: {endpoint} - {e}")
                all_pass = False
    
    return all_pass

async def test_register_endpoint():
    """Test user registration endpoint"""
    print_header("Test 6: Registration Endpoint (Simulated Clerk)")
    
    # Simulate what frontend sends after Clerk authentication
    test_user = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "clerk_id": f"user_test_{datetime.now().timestamp()}",
        "password": None  # Not needed with Clerk
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/auth/register",
                json=test_user
            )
            
            if response.status_code in [200, 201]:
                print_success("Registration endpoint is working")
                data = response.json()
                print_info(f"Created user: {data.get('email')}")
                print_info(f"Access token received: {'Yes' if data.get('access_token') else 'No'}")
                return True
            else:
                print_error(f"Registration failed with status {response.status_code}")
                print_info(f"Response: {response.json()}")
                return False
                
    except Exception as e:
        print_error(f"Registration test failed: {e}")
        return False

async def check_environment_variables():
    """Check if required environment variables are set"""
    print_header("Test 7: Environment Configuration")
    
    # Check if we can see the configuration through a debug endpoint
    # Note: This would need to be implemented in the backend
    print_info("Required environment variables:")
    required_vars = [
        "CLERK_SECRET_KEY",
        "CLERK_PUBLISHABLE_KEY", 
        "CLERK_FRONTEND_API",
        "CLERK_JWKS_URL",
        "DATABASE_URL",
        "REDIS_URL"
    ]
    
    for var in required_vars:
        print(f"  - {var}")
    
    print_warning("Verify these are set in docker-compose.yml or .env file")
    return True

async def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Clerk Authentication Diagnostic Tool{Colors.END}")
    print(f"{Colors.BOLD}Backend: {BACKEND_URL}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    tests = [
        ("Health Check", test_health_check),
        ("JWKS Endpoint", test_clerk_jwks_endpoint),
        ("CORS Configuration", test_cors_headers),
        ("Public Endpoints", test_public_endpoints),
        ("Registration", test_register_endpoint),
        ("Environment Check", check_environment_variables),
        ("Clerk Token Auth", test_auth_with_clerk_token),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for name, result in results:
        if result is True:
            print_success(f"{name}: PASSED")
        elif result is False:
            print_error(f"{name}: FAILED")
        else:
            print_warning(f"{name}: SKIPPED")
    
    print(f"\n{Colors.BOLD}Total: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}{Colors.END}\n")
    
    if failed > 0:
        print_header("Troubleshooting Tips")
        print_info("1. Ensure Docker containers are running: docker-compose ps")
        print_info("2. Check backend logs: docker-compose logs api")
        print_info("3. Verify environment variables in docker-compose.yml")
        print_info("4. Restart containers: docker-compose restart api")
        print_info("5. Check Clerk Dashboard for correct API keys")
        print_info("6. Ensure frontend is using the correct Clerk keys")

if __name__ == "__main__":
    asyncio.run(main())
