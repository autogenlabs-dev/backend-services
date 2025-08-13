#!/usr/bin/env python3
"""
Test existing user logins
"""
import asyncio
import aiohttp
import json

async def test_logins():
    """Test different admin email/password combinations"""
    
    base_url = "http://localhost:8000"
    
    # Different admin combinations to try
    admin_combinations = [
        {"email": "admin@marketplace.com", "password": "admin123"},
        {"email": "admin@autogenlabs.com", "password": "admin123"},
        {"email": "admin@example.com", "password": "admin123"},
        {"email": "admin@marketplace.com", "password": "password"},
        {"email": "admin@marketplace.com", "password": "marketplace123"},
    ]
    
    async with aiohttp.ClientSession() as session:
        for combo in admin_combinations:
            print(f"Testing: {combo['email']} / {combo['password']}")
            
            try:
                async with session.post(f"{base_url}/auth/login-json", json=combo) as resp:
                    print(f"   Status: {resp.status}")
                    if resp.status == 200:
                        result = await resp.json()
                        user_info = result.get("user", {})
                        print(f"   SUCCESS! Role: {user_info.get('role', 'unknown')}")
                        print(f"   User: {user_info}")
                        return result.get("access_token")
                    else:
                        error_text = await resp.text()
                        print(f"   Failed: {error_text}")
            except Exception as e:
                print(f"   Error: {e}")
            
            print()
    
    return None

if __name__ == "__main__":
    print("Testing Admin Login Combinations")
    print("=" * 50)
    asyncio.run(test_logins())
