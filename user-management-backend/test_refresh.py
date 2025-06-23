#!/usr/bin/env python3
"""
Quick test for token refresh endpoint
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test01@vscode.com",
    "password": "securepassword123"
}

async def test_token_refresh():
    """Test the token refresh endpoint specifically."""
    
    # First login to get tokens
    print("🔐 Logging in...")
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            f"{BASE_URL}/auth/login-json",
            json=TEST_USER
        )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    login_data = login_response.json()
    access_token = login_data.get("access_token")
    refresh_token = login_data.get("refresh_token")
    
    print(f"✅ Login successful")
    print(f"🎫 Access token: {'Present' if access_token else 'Missing'}")
    print(f"🔄 Refresh token: {'Present' if refresh_token else 'Missing'}")
    
    if not refresh_token:
        print("❌ No refresh token to test with")
        return False
    
    # Test token refresh
    print("\n🔄 Testing token refresh...")
    async with httpx.AsyncClient() as client:
        refresh_response = await client.post(
            f"{BASE_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
    
    print(f"📡 Refresh response status: {refresh_response.status_code}")
    
    if refresh_response.status_code == 200:
        refresh_data = refresh_response.json()
        new_access_token = refresh_data.get("access_token")
        new_refresh_token = refresh_data.get("refresh_token")
        
        print("✅ Token refresh successful!")
        print(f"🎫 New access token: {'Present' if new_access_token else 'Missing'}")
        print(f"🔄 New refresh token: {'Present' if new_refresh_token else 'Missing'}")
        return True
    else:
        print(f"❌ Token refresh failed: {refresh_response.text}")
        return False

async def main():
    success = await test_token_refresh()
    if success:
        print("\n✅ Token refresh test passed!")
    else:
        print("\n❌ Token refresh test failed!")

if __name__ == "__main__":
    asyncio.run(main())
