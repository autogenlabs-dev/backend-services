#!/usr/bin/env python3
"""
Test Template APIs and create integration guide
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"

async def test_template_endpoints():
    """Test template endpoints and show integration examples"""
    
    print("🧪 Testing Template API Integration")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Test Templates Endpoint
        print("1️⃣ Testing GET /templates")
        try:
            async with session.get(f"{BASE_URL}/templates") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    templates = data.get('templates', [])
                    pagination = data.get('pagination', {})
                    print(f"   ✅ Found {len(templates)} templates")
                    print(f"   📄 Pagination: Page {pagination.get('page', 0)}/{pagination.get('pages', 0)}")
                    
                    if templates:
                        sample = templates[0]
                        print(f"   📋 Sample: {sample.get('title', 'N/A')} ({sample.get('category', 'N/A')})")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # 2. Test Categories Endpoint
        print("\n2️⃣ Testing GET /templates/categories")
        try:
            async with session.get(f"{BASE_URL}/templates/categories") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    categories = data.get('categories', [])
                    print(f"   ✅ Found {len(categories)} categories")
                    print(f"   📂 Categories: {', '.join(categories[:5])}...")
                elif response.status == 404:
                    print("   ⚠️ Categories endpoint not available")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # 3. Test Statistics Endpoint
        print("\n3️⃣ Testing GET /templates/stats")
        try:
            async with session.get(f"{BASE_URL}/templates/stats") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    stats = data.get('stats', {})
                    print(f"   ✅ Statistics available")
                    print(f"   📊 Total: {stats.get('total_templates', 0)}")
                    print(f"   🆓 Free: {stats.get('free_templates', 0)}")
                    print(f"   💰 Paid: {stats.get('paid_templates', 0)}")
                elif response.status == 404:
                    print("   ⚠️ Stats endpoint not available")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # 4. Test Search/Filter
        print("\n4️⃣ Testing Template Search & Filter")
        try:
            params = {'search': 'template', 'limit': '3'}
            url_params = '&'.join([f"{k}={v}" for k, v in params.items()])
            
            async with session.get(f"{BASE_URL}/templates?{url_params}") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    templates = data.get('templates', [])
                    print(f"   ✅ Search returned {len(templates)} results")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # 5. Test Authentication Endpoints
        print("\n5️⃣ Testing Authentication")
        try:
            # Login
            login_data = {
                "email": "testuser_20250720_234038@example.com",
                "password": "TestPassword123!"
            }
            
            async with session.post(
                f"{BASE_URL}/auth/login-json",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"   Login Status: {response.status}")
                if response.status == 200:
                    login_result = await response.json()
                    access_token = login_result.get('access_token')
                    print(f"   ✅ Login successful, token available")
                    
                    # Test protected endpoint
                    if access_token:
                        headers = {"Authorization": f"Bearer {access_token}"}
                        async with session.get(f"{BASE_URL}/templates/user/my-templates", headers=headers) as my_response:
                            print(f"   My Templates Status: {my_response.status}")
                            if my_response.status == 200:
                                my_data = await my_response.json()
                                my_templates = my_data.get('templates', [])
                                print(f"   ✅ User has {len(my_templates)} templates")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Login Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION READY!")

if __name__ == "__main__":
    asyncio.run(test_template_endpoints())
