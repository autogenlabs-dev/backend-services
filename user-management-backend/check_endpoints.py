#!/usr/bin/env python3
"""
Simple script to check what endpoints are available
"""
import asyncio
import aiohttp

BASE_URL = "http://localhost:8000"

async def check_endpoints():
    """Check what endpoints are available"""
    
    endpoints_to_test = [
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/auth/register",
        "/auth/login", 
        "/auth/providers",
        "/register",
        "/login",
        "/token",
        "/providers"
    ]
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Checking available endpoints...")
        print("=" * 50)
        
        for endpoint in endpoints_to_test:
            try:
                async with session.get(f"{BASE_URL}{endpoint}") as response:
                    status = response.status
                    if status == 200:
                        print(f"✅ {endpoint} - Status: {status}")
                    elif status == 405:  # Method not allowed (GET on POST endpoint)
                        print(f"📝 {endpoint} - Status: {status} (POST endpoint)")
                    elif status == 404:
                        print(f"❌ {endpoint} - Status: {status} (Not Found)")
                    else:
                        print(f"⚠️ {endpoint} - Status: {status}")
                        
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_endpoints())
