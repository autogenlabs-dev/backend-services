"""
Manual Clerk Token Test Script
Use this to test with a real Clerk token from your frontend.
"""

import asyncio
import httpx
import sys

BACKEND_URL = "http://localhost:8000"

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


async def test_with_clerk_token(token: str):
    """Test backend endpoints with a real Clerk token."""
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Testing Backend with Real Clerk Token{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Get current user info
        print(f"{BLUE}[1] Testing /api/auth/me endpoint...{RESET}")
        try:
            response = await client.get(
                f"{BACKEND_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"{GREEN}✅ SUCCESS{RESET}")
                print(f"User ID: {data.get('id')}")
                print(f"Email: {data.get('email')}")
                print(f"Is Active: {data.get('is_active')}")
                print(f"Last Login: {data.get('last_login_at')}")
            else:
                print(f"{RED}❌ FAILED{RESET}")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"{RED}❌ ERROR: {e}{RESET}")
        
        print()
        
        # Test 2: Get API key
        print(f"{BLUE}[2] Testing /api/user/api-key endpoint...{RESET}")
        try:
            response = await client.get(
                f"{BACKEND_URL}/api/user/api-key",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"{GREEN}✅ SUCCESS{RESET}")
                api_key = data.get('api_key', '')
                if api_key:
                    # Mask most of the API key for security
                    masked = api_key[:8] + '*' * (len(api_key) - 12) + api_key[-4:]
                    print(f"API Key: {masked}")
                print(f"Created At: {data.get('created_at')}")
            else:
                print(f"{RED}❌ FAILED{RESET}")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"{RED}❌ ERROR: {e}{RESET}")
        
        print()
        
        # Test 3: Exchange token
        print(f"{BLUE}[3] Testing /api/extension/exchange-token endpoint...{RESET}")
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/extension/exchange-token",
                json={"clerk_token": token}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"{GREEN}✅ SUCCESS{RESET}")
                print(f"Got backend access token")
                api_key = data.get('api_key', '')
                if api_key:
                    masked = api_key[:8] + '*' * (len(api_key) - 12) + api_key[-4:]
                    print(f"API Key: {masked}")
                print(f"Token Type: {data.get('token_type')}")
                print(f"Expires In: {data.get('expires_in')} seconds")
            else:
                print(f"{RED}❌ FAILED{RESET}")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"{RED}❌ ERROR: {e}{RESET}")
        
        print()
        
        # Test 4: Get user subscription info
        print(f"{BLUE}[4] Testing /api/users/me/subscription endpoint...{RESET}")
        try:
            response = await client.get(
                f"{BACKEND_URL}/api/users/me/subscription",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"{GREEN}✅ SUCCESS{RESET}")
                print(f"Plan: {data.get('plan', 'N/A')}")
                print(f"Status: {data.get('status', 'N/A')}")
                print(f"Tokens Remaining: {data.get('tokens_remaining', 'N/A')}")
            else:
                print(f"{YELLOW}⚠️  INFO{RESET}")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
        except Exception as e:
            print(f"{YELLOW}⚠️  ERROR: {e}{RESET}")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{GREEN}Testing Complete!{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def main():
    """Main function to run tests."""
    
    if len(sys.argv) < 2:
        print(f"\n{YELLOW}Usage:{RESET}")
        print(f"  python test_with_clerk_token.py YOUR_CLERK_TOKEN")
        print(f"\n{YELLOW}How to get your Clerk token:{RESET}")
        print(f"  1. Sign in to your app via Clerk")
        print(f"  2. Open browser console (F12)")
        print(f"  3. Run: await window.Clerk.session.getToken()")
        print(f"  4. Copy the token and pass it as argument")
        print(f"\n{YELLOW}Example:{RESET}")
        print(f"  python test_with_clerk_token.py eyJhbGciOiJSUzI1NiIs...")
        print()
        sys.exit(1)
    
    token = sys.argv[1]
    
    # Validate token format (should be JWT)
    if not token or len(token) < 20 or token.count('.') < 2:
        print(f"{RED}Error: Invalid token format. Token should be a JWT (xxx.yyy.zzz){RESET}")
        sys.exit(1)
    
    asyncio.run(test_with_clerk_token(token))


if __name__ == "__main__":
    main()
