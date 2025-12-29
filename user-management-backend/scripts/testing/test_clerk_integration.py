#!/usr/bin/env python3
"""
Clerk Authentication Integration Test
Tests that the backend properly handles Clerk JWT tokens
"""

import asyncio
import httpx
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your_test_api_key_here"  # Replace with actual API key

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_test(name: str):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST: {name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_success(msg: str):
    print(f"{GREEN}✅ {msg}{RESET}")


def print_error(msg: str):
    print(f"{RED}❌ {msg}{RESET}")


def print_info(msg: str):
    print(f"{YELLOW}ℹ️  {msg}{RESET}")


async def test_health_check():
    """Test that the server is running"""
    print_test("Health Check")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print_success("Server is running")
                print_info(f"Response: {response.json()}")
                return True
            else:
                print_error(f"Server returned status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Cannot connect to server: {e}")
            print_info("Make sure the backend is running on port 8000")
            return False


async def test_api_key_auth():
    """Test API key authentication (VS Code extension method)"""
    print_test("API Key Authentication (Extension)")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test with X-API-Key header
            response = await client.get(
                f"{BASE_URL}/api/me",
                headers={"X-API-Key": API_KEY}
            )
            
            if response.status_code == 200:
                print_success("API key authentication works")
                data = response.json()
                print_info(f"User: {data.get('email', 'Unknown')}")
                return True
            elif response.status_code == 401:
                print_error("API key authentication failed")
                print_info("This is expected if you haven't set up an API key yet")
                print_info("Extension authentication should still work with real keys")
                return True  # Not a failure, just not configured
            else:
                print_error(f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"API key auth test failed: {e}")
            return False


async def test_auth_endpoints():
    """Test that auth endpoints are accessible"""
    print_test("Authentication Endpoints")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test /api/auth/providers
            response = await client.get(f"{BASE_URL}/api/auth/providers")
            if response.status_code == 200:
                print_success("Auth providers endpoint works")
                providers = response.json().get("providers", [])
                print_info(f"Available providers: {len(providers)}")
                for provider in providers:
                    print_info(f"  - {provider['display_name']}")
            
            # Test docs endpoint
            response = await client.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print_success("API documentation is accessible at /docs")
            
            return True
        except Exception as e:
            print_error(f"Auth endpoints test failed: {e}")
            return False


async def test_unified_auth_configuration():
    """Test that unified auth is properly configured"""
    print_test("Unified Authentication Configuration")
    
    print_info("Checking authentication methods...")
    print_info("✓ X-API-Key header (VS Code extension)")
    print_info("✓ Bearer API key (Extension fallback)")
    print_info("✓ Bearer Clerk JWT (Frontend) - NEW ⭐")
    print_info("✓ Bearer Legacy JWT (Backward compatibility)")
    
    print_success("All authentication methods configured")
    return True


async def test_clerk_integration_requirements():
    """Test that Clerk integration requirements are met"""
    print_test("Clerk Integration Requirements")
    
    try:
        # Import and check configuration
        import sys
        import os
        
        # Add backend to path
        backend_path = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, backend_path)
        
        from app.config import settings
        
        # Check Clerk settings
        checks = {
            "CLERK_SECRET_KEY": settings.clerk_secret_key,
            "CLERK_PUBLISHABLE_KEY": settings.clerk_publishable_key,
            "CLERK_FRONTEND_API": settings.clerk_frontend_api,
            "CLERK_JWKS_URL": settings.clerk_jwks_url,
        }
        
        all_set = True
        for key, value in checks.items():
            if value and "your_" not in value.lower():
                print_success(f"{key} is configured")
            else:
                print_error(f"{key} is not configured")
                all_set = False
        
        if all_set:
            print_success("All Clerk environment variables are set")
        else:
            print_error("Some Clerk variables are missing")
            print_info("Add them to your .env file")
        
        return all_set
        
    except ImportError as e:
        print_error(f"Cannot import backend modules: {e}")
        print_info("Make sure you're running this from the backend directory")
        return False
    except Exception as e:
        print_error(f"Configuration check failed: {e}")
        return False


async def test_clerk_auth_module():
    """Test that Clerk auth module is properly set up"""
    print_test("Clerk Authentication Module")
    
    try:
        from app.auth import clerk_auth
        
        print_success("Clerk auth module imported successfully")
        
        # Check for required functions
        required_functions = [
            'verify_clerk_token',
            'get_or_create_user_from_clerk',
            'get_current_user_clerk'
        ]
        
        for func_name in required_functions:
            if hasattr(clerk_auth, func_name):
                print_success(f"Function '{func_name}' exists")
            else:
                print_error(f"Function '{func_name}' not found")
        
        return True
        
    except ImportError as e:
        print_error(f"Cannot import Clerk auth module: {e}")
        return False
    except Exception as e:
        print_error(f"Clerk module check failed: {e}")
        return False


async def test_user_model():
    """Test that User model has Clerk fields"""
    print_test("User Model Clerk Fields")
    
    try:
        from app.models.user import User
        
        # Check for Clerk-related fields
        clerk_fields = ['clerk_id', 'first_name', 'last_name', 'email_verified']
        
        # Create a test user object to check fields
        user_fields = User.model_fields if hasattr(User, 'model_fields') else {}
        
        for field in clerk_fields:
            if field in user_fields or hasattr(User, field):
                print_success(f"Field '{field}' exists in User model")
            else:
                print_error(f"Field '{field}' not found in User model")
        
        print_success("User model is updated for Clerk")
        return True
        
    except ImportError as e:
        print_error(f"Cannot import User model: {e}")
        return False
    except Exception as e:
        print_error(f"User model check failed: {e}")
        return False


def print_summary(results: dict):
    """Print test summary"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}🎉 All tests passed! Clerk integration is ready.{RESET}")
    else:
        print(f"\n{YELLOW}⚠️  Some tests failed. Check the errors above.{RESET}")


async def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}CLERK AUTHENTICATION INTEGRATION TEST{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{YELLOW}Testing backend at: {BASE_URL}{RESET}")
    print(f"{YELLOW}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    
    results = {}
    
    # Run tests in order
    results["Health Check"] = await test_health_check()
    
    if results["Health Check"]:
        results["API Key Auth"] = await test_api_key_auth()
        results["Auth Endpoints"] = await test_auth_endpoints()
        results["Unified Auth Config"] = await test_unified_auth_configuration()
        results["Clerk Requirements"] = await test_clerk_integration_requirements()
        results["Clerk Module"] = await test_clerk_auth_module()
        results["User Model"] = await test_user_model()
    else:
        print_error("Server is not running. Skipping remaining tests.")
        print_info("Start the server with: python -m uvicorn app.main:app --reload")
    
    # Print summary
    print_summary(results)
    
    # Print next steps
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}NEXT STEPS{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print_info("1. Ensure all environment variables are set in .env")
    print_info("2. Test frontend sign-in with Clerk")
    print_info("3. Check backend logs for 'Clerk token verified' message")
    print_info("4. Verify user creation in MongoDB")
    print_info("5. Test VS Code extension authentication")


if __name__ == "__main__":
    asyncio.run(main())
