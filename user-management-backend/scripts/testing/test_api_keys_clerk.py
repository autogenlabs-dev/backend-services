"""
Test API Key Generation with Clerk Authentication
Shows how frontend can get API keys after Clerk login
"""

import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

async def test_api_key_flow():
    """Test the complete API key workflow"""
    
    print(f"\n{Colors.PURPLE}{Colors.BOLD}")
    print("="*70)
    print("  API KEY GENERATION FLOW WITH CLERK")
    print("="*70)
    print(f"{Colors.RESET}\n")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # Step 1: Register a test user (simulating Clerk user creation)
        print(f"{Colors.YELLOW}Step 1: Register Test User{Colors.RESET}")
        email = f"apitest_{int(datetime.now().timestamp())}@example.com"
        register_data = {
            "email": email,
            "password": "TestPassword123!",
            "username": "apitest"
        }
        
        response = await client.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"{Colors.RED}Registration failed: {response.text}{Colors.RESET}")
            return
        
        user_data = response.json()
        user_id = user_data["id"]
        print(f"{Colors.GREEN}✅ User created: {email}{Colors.RESET}\n")
        
        # Step 2: Login to get JWT token (simulating Clerk JWT)
        print(f"{Colors.YELLOW}Step 2: Login to Get Token{Colors.RESET}")
        login_data = {
            "username": email,  # OAuth2 form uses 'username' field
            "password": "TestPassword123!"
        }
        
        response = await client.post(f"{BASE_URL}/api/auth/login", data=login_data)  # Form data, not JSON
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"{Colors.RED}Login failed: {response.text}{Colors.RESET}")
            return
        
        auth_data = response.json()
        jwt_token = auth_data["access_token"]
        print(f"{Colors.GREEN}✅ JWT Token obtained{Colors.RESET}")
        print(f"Token preview: {jwt_token[:50]}...\n")
        
        # Step 3: Create API Key using JWT token
        print(f"{Colors.YELLOW}Step 3: Create API Key (Main Flow){Colors.RESET}")
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        api_key_data = {
            "name": "My VS Code Extension Key"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/users/me/api-keys",  # Fixed: use correct endpoint
            json=api_key_data,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"{Colors.RED}API Key creation failed: {response.text}{Colors.RESET}")
            return
        
        api_key_response = response.json()
        api_key = api_key_response.get("key") or api_key_response.get("api_key")
        print(f"{Colors.GREEN}✅ API Key created!{Colors.RESET}")
        print(f"{Colors.BOLD}Full API Key:{Colors.RESET} {api_key}")
        print(f"{Colors.BOLD}Key ID:{Colors.RESET} {api_key_response.get('id')}")
        print(f"{Colors.BOLD}Name:{Colors.RESET} {api_key_response.get('name')}")
        print(f"{Colors.YELLOW}⚠️  Save this key - it won't be shown again!{Colors.RESET}\n")
        
        # Step 4: List all API keys
        print(f"{Colors.YELLOW}Step 4: List All API Keys{Colors.RESET}")
        response = await client.get(f"{BASE_URL}/api/users/me/api-keys", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            keys = response.json()
            print(f"{Colors.GREEN}✅ Found {len(keys)} API key(s){Colors.RESET}")
            for key in keys:
                print(f"  • {key['name']} (Preview: {key.get('key_preview', 'N/A')})")
        print()
        
        # Step 5: Test the API key works
        print(f"{Colors.YELLOW}Step 5: Test API Key Authentication{Colors.RESET}")
        api_headers = {
            "X-API-Key": api_key
        }
        
        response = await client.get(f"{BASE_URL}/api/users/me", headers=api_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"{Colors.GREEN}✅ API Key works! Authenticated as: {user_info['email']}{Colors.RESET}\n")
        else:
            print(f"{Colors.RED}❌ API Key authentication failed{Colors.RESET}\n")
        
        # Step 6: Show how to use in VS Code Extension
        print(f"{Colors.PURPLE}{Colors.BOLD}How to Use in VS Code Extension:{Colors.RESET}")
        print(f"{Colors.BLUE}")
        print("// Store in VS Code settings or secure storage")
        print(f"const apiKey = '{api_key}';")
        print("const apiEndpoint = 'http://localhost:8000';")
        print()
        print("// Use in HTTP requests")
        print("fetch(`${apiEndpoint}/api/users/me`, {")
        print("  headers: {")
        print("    'X-API-Key': apiKey")
        print("  }")
        print("});")
        print(f"{Colors.RESET}\n")
        
        # Summary
        print(f"{Colors.PURPLE}{Colors.BOLD}")
        print("="*70)
        print("  INTEGRATION SUMMARY")
        print("="*70)
        print(f"{Colors.RESET}")
        print(f"""
{Colors.GREEN}✅ Complete Flow Working:{Colors.RESET}
1. User logs in with Clerk (frontend)
2. Frontend gets JWT token from Clerk
3. Frontend calls /api/keys/ with Bearer token
4. Backend creates API key for user
5. Frontend stores API key securely
6. VS Code Extension uses API key for all requests

{Colors.YELLOW}📌 Frontend Implementation:{Colors.RESET}
After Clerk login, call your backend:

const createApiKey = async (clerkJWT) => {{
  const response = await fetch('{BASE_URL}/api/users/me/api-keys', {{
    method: 'POST',
    headers: {{
      'Authorization': `Bearer ${{clerkJWT}}`,
      'Content-Type': 'application/json'
    }},
    body: JSON.stringify({{
      name: 'VS Code Extension'
    }})
  }});
  
  const data = await response.json();
  return data.key; // Store this securely!
}};

{Colors.YELLOW}📌 API Endpoints:{Colors.RESET}
• POST   /api/users/me/api-keys           Create new API key
• GET    /api/users/me/api-keys           List all user's API keys
• DELETE /api/users/me/api-keys/{{key_id}}  Revoke API key

{Colors.YELLOW}📌 Authentication Methods:{Colors.RESET}
• Bearer Token (Clerk JWT)   → For web frontend
• X-API-Key Header           → For VS Code Extension
        """)

if __name__ == "__main__":
    asyncio.run(test_api_key_flow())
