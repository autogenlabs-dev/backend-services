#!/usr/bin/env python3
"""
Direct A4F API test to diagnose the models list issue
"""
import asyncio
import httpx
import json

A4F_API_KEY = "ddc-a4f-a480842d898b49d4a15e14800c2f3c72"
A4F_BASE_URL = "https://api.a4f.co/v1"

async def test_a4f_api():
    """Test A4F API directly."""
    print("🔍 DIRECT A4F API TEST")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Basic models endpoint
        print("1️⃣ Testing A4F Models Endpoint")
        try:
            response = await client.get(
                f"{A4F_BASE_URL}/models",
                headers={
                    "Authorization": f"Bearer {A4F_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS: Found {len(data.get('data', []))} models")
                if data.get('data'):
                    print(f"   📝 First model: {data['data'][0]}")
                else:
                    print("   ⚠️  No models in response")
            else:
                print(f"   ❌ FAILED: {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
        
        # Test 2: Alternative API key format
        print("\n2️⃣ Testing Alternative Authorization Format")
        try:
            response = await client.get(
                f"{A4F_BASE_URL}/models",
                headers={
                    "Authorization": f"Api-Key {A4F_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS with Api-Key format: Found {len(data.get('data', []))} models")
            else:
                print(f"   ❌ FAILED with Api-Key format: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ ERROR with Api-Key format: {str(e)}")
        
        # Test 3: Check if endpoint exists
        print("\n3️⃣ Testing Base URL Connectivity")
        try:
            response = await client.get(f"{A4F_BASE_URL}/", timeout=5.0)
            print(f"   Base URL Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Base URL ERROR: {str(e)}")
        
        # Test 4: Test chat completions endpoint (just to verify API key works)
        print("\n4️⃣ Testing Chat Completions Endpoint")
        try:
            test_payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
            
            response = await client.post(
                f"{A4F_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {A4F_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=test_payload,
                timeout=10.0
            )
            print(f"   Chat Status Code: {response.status_code}")
            
            if response.status_code in [200, 400, 401]:
                print(f"   Chat Response: {response.text[:300]}")
            
        except Exception as e:
            print(f"   ❌ Chat ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_a4f_api())
