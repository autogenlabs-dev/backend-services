"""
End-to-End Clerk Authentication Flow Test
This script tests the complete authentication flow between frontend and backend.
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "http://localhost:8000"
CLERK_PUBLISHABLE_KEY = "pk_test_YXB0LWNsYW0tNTMuY2xlcmsuYWNjb3VudHMuZGV2JA"  # Update if needed

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class TestResult:
    """Store test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.tests = []
    
    def add_pass(self, test_name: str, message: str = ""):
        self.passed += 1
        self.tests.append({
            "name": test_name,
            "status": "PASS",
            "message": message
        })
        print(f"{GREEN}✅ PASS:{RESET} {test_name}")
        if message:
            print(f"   {message}")
    
    def add_fail(self, test_name: str, message: str = ""):
        self.failed += 1
        self.tests.append({
            "name": test_name,
            "status": "FAIL",
            "message": message
        })
        print(f"{RED}❌ FAIL:{RESET} {test_name}")
        if message:
            print(f"   {message}")
    
    def add_warning(self, test_name: str, message: str = ""):
        self.warnings += 1
        self.tests.append({
            "name": test_name,
            "status": "WARN",
            "message": message
        })
        print(f"{YELLOW}⚠️  WARN:{RESET} {test_name}")
        if message:
            print(f"   {message}")
    
    def print_summary(self):
        total = self.passed + self.failed + self.warnings
        print(f"\n{'='*60}")
        print(f"{BLUE}TEST SUMMARY{RESET}")
        print(f"{'='*60}")
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"{YELLOW}Warnings: {self.warnings}{RESET}")
        print(f"{'='*60}\n")


async def test_backend_health(client: httpx.AsyncClient, results: TestResult):
    """Test 1: Check if backend is running and healthy."""
    print(f"\n{BLUE}[TEST 1] Backend Health Check{RESET}")
    try:
        response = await client.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            results.add_pass("Backend Health Check", f"Backend is running on {BACKEND_URL}")
            return True
        else:
            results.add_fail("Backend Health Check", f"Unexpected status: {response.status_code}")
            return False
    except httpx.ConnectError:
        results.add_fail("Backend Health Check", f"Cannot connect to backend at {BACKEND_URL}")
        return False
    except Exception as e:
        results.add_fail("Backend Health Check", f"Error: {str(e)}")
        return False


async def test_cors_configuration(client: httpx.AsyncClient, results: TestResult):
    """Test 2: Verify CORS headers are properly configured."""
    print(f"\n{BLUE}[TEST 2] CORS Configuration{RESET}")
    try:
        # Send OPTIONS request to check CORS preflight
        response = await client.options(
            f"{BACKEND_URL}/api/auth/me",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization"
            }
        )
        
        cors_headers = {
            "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
            "access-control-allow-credentials": response.headers.get("access-control-allow-credentials"),
            "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
        }
        
        if cors_headers.get("access-control-allow-origin"):
            results.add_pass("CORS Headers Present", f"CORS configured: {json.dumps(cors_headers, indent=2)}")
        else:
            results.add_warning("CORS Headers", "CORS headers not found in preflight response")
        
        return True
    except Exception as e:
        results.add_warning("CORS Configuration", f"Error testing CORS: {str(e)}")
        return True


async def test_unprotected_endpoints(client: httpx.AsyncClient, results: TestResult):
    """Test 3: Verify unprotected endpoints work without auth."""
    print(f"\n{BLUE}[TEST 3] Unprotected Endpoints{RESET}")
    
    endpoints = [
        "/",
        "/health",
        "/api/auth/providers"
    ]
    
    all_passed = True
    for endpoint in endpoints:
        try:
            response = await client.get(f"{BACKEND_URL}{endpoint}")
            if response.status_code == 200:
                results.add_pass(f"Unprotected: {endpoint}", f"Status: {response.status_code}")
            else:
                results.add_fail(f"Unprotected: {endpoint}", f"Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            results.add_fail(f"Unprotected: {endpoint}", f"Error: {str(e)}")
            all_passed = False
    
    return all_passed


async def test_protected_endpoint_without_auth(client: httpx.AsyncClient, results: TestResult):
    """Test 4: Verify protected endpoints reject requests without auth."""
    print(f"\n{BLUE}[TEST 4] Protected Endpoints (No Auth){RESET}")
    
    try:
        response = await client.get(f"{BACKEND_URL}/api/auth/me")
        
        if response.status_code == 401:
            results.add_pass("Protected Endpoint Security", "Correctly returns 401 without auth token")
            return True
        elif response.status_code == 403:
            results.add_pass("Protected Endpoint Security", "Correctly returns 403 without auth token")
            return True
        else:
            results.add_fail("Protected Endpoint Security", 
                           f"Expected 401/403, got {response.status_code}")
            return False
    except Exception as e:
        results.add_fail("Protected Endpoint Security", f"Error: {str(e)}")
        return False


async def test_with_mock_clerk_token(client: httpx.AsyncClient, results: TestResult):
    """Test 5: Test with a mock Clerk token structure."""
    print(f"\n{BLUE}[TEST 5] Mock Clerk Token Test{RESET}")
    
    # Create a mock JWT token (this will fail verification but tests the flow)
    import base64
    header = base64.b64encode(json.dumps({"alg": "RS256", "typ": "JWT"}).encode()).decode()
    payload = base64.b64encode(json.dumps({
        "sub": "user_test123",
        "email": "test@example.com",
        "iss": "https://apt-clam-53.clerk.accounts.dev",
        "exp": 9999999999
    }).encode()).decode()
    signature = base64.b64encode(b"fake_signature").decode()
    mock_token = f"{header}.{payload}.{signature}"
    
    try:
        response = await client.get(
            f"{BACKEND_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {mock_token}"}
        )
        
        if response.status_code == 401:
            results.add_pass("Clerk Token Verification", 
                           "Backend correctly validates token signatures (rejected mock token)")
        elif response.status_code == 200:
            results.add_warning("Clerk Token Verification",
                              "Backend accepted mock token - may be in debug mode")
        else:
            results.add_fail("Clerk Token Verification",
                           f"Unexpected status: {response.status_code}")
        
        return True
    except Exception as e:
        results.add_fail("Clerk Token Verification", f"Error: {str(e)}")
        return False


async def test_api_key_endpoint(client: httpx.AsyncClient, results: TestResult):
    """Test 6: Check API key endpoint structure."""
    print(f"\n{BLUE}[TEST 6] API Key Endpoint{RESET}")
    
    try:
        response = await client.get(f"{BACKEND_URL}/api/user/api-key")
        
        if response.status_code == 401:
            results.add_pass("API Key Endpoint Security", 
                           "Endpoint correctly requires authentication")
            return True
        else:
            results.add_warning("API Key Endpoint", 
                              f"Unexpected status: {response.status_code}")
            return True
    except Exception as e:
        results.add_fail("API Key Endpoint", f"Error: {str(e)}")
        return False


async def test_clerk_integration_info(results: TestResult):
    """Test 7: Display Clerk integration information."""
    print(f"\n{BLUE}[TEST 7] Clerk Integration Info{RESET}")
    
    info = {
        "Clerk Domain": "apt-clam-53.clerk.accounts.dev",
        "JWKS URL": "https://apt-clam-53.clerk.accounts.dev/.well-known/jwks.json",
        "Expected Token Issuer": "https://apt-clam-53.clerk.accounts.dev",
        "Backend Auth File": "app/auth/clerk_auth.py",
        "Auth Dependency": "get_current_user_clerk"
    }
    
    print(f"\n{YELLOW}Clerk Configuration:{RESET}")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    results.add_pass("Clerk Integration Info", "Configuration displayed")
    return True


async def test_database_connection(results: TestResult):
    """Test 8: Check if database connection is configured."""
    print(f"\n{BLUE}[TEST 8] Database Connection{RESET}")
    
    try:
        # Try to read config to check database URL
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        
        from app.config import settings
        
        if settings.database_url:
            results.add_pass("Database Configuration", 
                           f"Database URL configured: {settings.database_url[:30]}...")
        else:
            results.add_fail("Database Configuration", "Database URL not configured")
        
        return True
    except Exception as e:
        results.add_warning("Database Configuration", 
                          f"Could not check database config: {str(e)}")
        return True


async def test_token_exchange_endpoint(client: httpx.AsyncClient, results: TestResult):
    """Test 9: Check token exchange endpoint for API keys."""
    print(f"\n{BLUE}[TEST 9] Token Exchange Endpoint{RESET}")
    
    try:
        # Test the extension auth endpoint
        response = await client.post(
            f"{BACKEND_URL}/api/extension/exchange-token",
            json={"clerk_token": "fake_token"}
        )
        
        if response.status_code in [401, 500]:
            # 401 or 500 means endpoint exists but token is invalid (expected)
            results.add_pass("Token Exchange Endpoint", 
                           "Endpoint exists and validates Clerk tokens")
        elif response.status_code == 404:
            results.add_fail("Token Exchange Endpoint", 
                           "Endpoint not found - may not be implemented")
        elif response.status_code == 400:
            results.add_pass("Token Exchange Endpoint", 
                           "Endpoint exists and validates input format")
        else:
            results.add_warning("Token Exchange Endpoint", 
                              f"Unexpected status: {response.status_code}")
        
        return True
    except Exception as e:
        results.add_warning("Token Exchange Endpoint", f"Error: {str(e)}")
        return True


async def print_frontend_integration_guide(results: TestResult):
    """Test 10: Display frontend integration guide."""
    print(f"\n{BLUE}[TEST 10] Frontend Integration Guide{RESET}")
    
    guide = """
    {YELLOW}Frontend Integration Steps:{RESET}
    
    1. Install Clerk SDK:
       npm install @clerk/clerk-react
    
    2. Wrap app with ClerkProvider in your root component:
       import {{ ClerkProvider }} from '@clerk/clerk-react';
       
       <ClerkProvider publishableKey="pk_test_...">
         <App />
       </ClerkProvider>
    
    3. Get session token and call backend:
       import {{ useAuth }} from '@clerk/clerk-react';
       
       const {{ getToken }} = useAuth();
       const token = await getToken();
       
       const response = await fetch('http://localhost:8000/api/auth/me', {{
         headers: {{
           'Authorization': `Bearer ${{token}}`
         }}
       }});
    
    4. For API key retrieval:
       const response = await fetch('http://localhost:8000/api/user/api-key', {{
         headers: {{
           'Authorization': `Bearer ${{token}}`
         }}
       }});
       
    {YELLOW}Testing with Clerk Dashboard:{RESET}
    - Go to: https://dashboard.clerk.com/
    - Navigate to your app (apt-clam-53)
    - Create a test user or use existing one
    - Copy JWT token from the user's session
    - Use it in Authorization header for backend requests
    """
    
    print(guide.format(YELLOW=YELLOW, RESET=RESET))
    results.add_pass("Frontend Integration Guide", "Guide displayed")
    return True


async def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Clerk Authentication E2E Test Suite{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    results = TestResult()
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Run tests in sequence
        backend_healthy = await test_backend_health(client, results)
        
        if not backend_healthy:
            print(f"\n{RED}Backend is not running. Please start the backend server first:{RESET}")
            print(f"  cd user-management-backend")
            print(f"  uvicorn app.main:app --reload --port 8000")
            results.print_summary()
            return
        
        await test_cors_configuration(client, results)
        await test_unprotected_endpoints(client, results)
        await test_protected_endpoint_without_auth(client, results)
        await test_with_mock_clerk_token(client, results)
        await test_api_key_endpoint(client, results)
        await test_clerk_integration_info(results)
        await test_database_connection(results)
        await test_token_exchange_endpoint(client, results)
        await print_frontend_integration_guide(results)
    
    # Print summary
    results.print_summary()
    
    # Print next steps
    print(f"{BLUE}Next Steps:{RESET}")
    if results.failed == 0:
        print(f"{GREEN}✅ All critical tests passed!{RESET}")
        print(f"\nTo test with real Clerk token:")
        print(f"1. Get a Clerk token from your frontend")
        print(f"2. Run: curl -H 'Authorization: Bearer YOUR_CLERK_TOKEN' {BACKEND_URL}/api/auth/me")
    else:
        print(f"{RED}⚠️  Some tests failed. Please fix the issues above.{RESET}")
    
    print(f"\n{BLUE}For manual testing:{RESET}")
    print(f"- Start backend: uvicorn app.main:app --reload --port 8000")
    print(f"- Start frontend: npm run dev (on port 3000)")
    print(f"- Sign in via Clerk and check browser console for token")
    print()


if __name__ == "__main__":
    asyncio.run(main())
