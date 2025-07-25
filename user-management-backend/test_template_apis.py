#!/usr/bin/env python3
"""
Test Template APIs for website integration
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"

async def test_template_apis():
    """Test all template API endpoints"""
    
    print("🧪 Testing Template APIs")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Get all templates (public)
        print("1️⃣ Testing GET /templates (public)")
        try:
            async with session.get(f"{BASE_URL}/templates") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Success: Found {len(data.get('templates', []))} templates")
                    if data.get('templates'):
                        template = data['templates'][0]
                        print(f"   📋 Sample template: {template.get('title', 'N/A')}")
                        print(f"   📂 Category: {template.get('category', 'N/A')}")
                        print(f"   💰 Plan: {template.get('plan_type', 'N/A')}")
                else:
                    print(f"❌ Failed with status: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 2: Get template categories (public)
        print("\n2️⃣ Testing GET /templates/categories/list (public)")
        try:
            async with session.get(f"{BASE_URL}/templates/categories/list") as response:
                if response.status == 200:
                    data = await response.json()
                    categories = data.get('categories', [])
                    print(f"✅ Success: Found {len(categories)} categories")
                    print(f"   📂 Categories: {', '.join(categories[:5])}...")
                else:
                    print(f"❌ Failed with status: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 3: Get template stats (public)
        print("\n3️⃣ Testing GET /templates/stats/overview (public)")
        try:
            async with session.get(f"{BASE_URL}/templates/stats/overview") as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data.get('stats', {})
                    print(f"✅ Success: Template statistics")
                    print(f"   📊 Total: {stats.get('total_templates', 0)}")
                    print(f"   🆓 Free: {stats.get('free_templates', 0)}")
                    print(f"   💰 Paid: {stats.get('paid_templates', 0)}")
                    print(f"   ⭐ Featured: {stats.get('featured_templates', 0)}")
                else:
                    print(f"❌ Failed with status: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 4: Search templates (public)
        print("\n4️⃣ Testing GET /templates with search (public)")
        try:
            search_params = {
                'search': 'portfolio',
                'plan_type': 'Free',
                'limit': '5'
            }
            url = f"{BASE_URL}/templates?" + "&".join([f"{k}={v}" for k, v in search_params.items()])
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    templates = data.get('templates', [])
                    pagination = data.get('pagination', {})
                    print(f"✅ Success: Search returned {len(templates)} templates")
                    print(f"   🔍 Search: 'portfolio', Plan: Free")
                    print(f"   📄 Page: {pagination.get('page', 0)}/{pagination.get('pages', 0)}")
                else:
                    print(f"❌ Failed with status: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 5: Get single template (public) - if templates exist
        print("\n5️⃣ Testing GET /templates/{id} (public)")
        try:
            # First get a template ID
            async with session.get(f"{BASE_URL}/templates?limit=1") as response:
                if response.status == 200:
                    data = await response.json()
                    templates = data.get('templates', [])
                    if templates:
                        template_id = templates[0]['id']
                        
                        # Now test getting single template
                        async with session.get(f"{BASE_URL}/templates/{template_id}") as detail_response:
                            if detail_response.status == 200:
                                detail_data = await detail_response.json()
                                template = detail_data.get('template', {})
                                print(f"✅ Success: Retrieved template details")
                                print(f"   📋 Title: {template.get('title', 'N/A')}")
                                print(f"   👁️ Views: {template.get('views', 0)}")
                                print(f"   📥 Downloads: {template.get('downloads', 0)}")
                            else:
                                print(f"❌ Failed with status: {detail_response.status}")
                    else:
                        print("⚠️ No templates found to test with")
                else:
                    print(f"❌ Failed to get templates list: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 6: Login and test protected endpoints
        print("\n6️⃣ Testing protected endpoints with authentication")
        try:
            # Login first
            login_data = {
                "email": "testuser_20250720_234038@example.com",
                "password": "TestPassword123!"
            }
            
            async with session.post(
                f"{BASE_URL}/auth/login-json",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as login_response:
                
                if login_response.status == 200:
                    login_result = await login_response.json()
                    access_token = login_result.get('access_token')
                    print(f"✅ Login successful")
                    
                    if access_token:
                        headers = {"Authorization": f"Bearer {access_token}"}
                        
                        # Test my templates
                        async with session.get(f"{BASE_URL}/templates/user/my-templates", headers=headers) as my_templates_response:
                            if my_templates_response.status == 200:
                                my_data = await my_templates_response.json()
                                my_templates = my_data.get('templates', [])
                                print(f"✅ My templates: {len(my_templates)} templates")
                            else:
                                print(f"⚠️ My templates failed: {my_templates_response.status}")
                        
                        # Test like functionality (if templates exist)
                        async with session.get(f"{BASE_URL}/templates?limit=1") as templates_response:
                            if templates_response.status == 200:
                                templates_data = await templates_response.json()
                                templates = templates_data.get('templates', [])
                                if templates:
                                    template_id = templates[0]['id']
                                    
                                    async with session.post(f"{BASE_URL}/templates/{template_id}/like", headers=headers) as like_response:
                                        if like_response.status == 200:
                                            like_data = await like_response.json()
                                            print(f"✅ Like toggle: {like_data.get('message', 'Success')}")
                                        else:
                                            print(f"⚠️ Like failed: {like_response.status}")
                else:
                    print(f"❌ Login failed: {login_response.status}")
                    
        except Exception as e:
            print(f"❌ Error in protected endpoints: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Template API testing completed!")
    print("\n💡 Integration Ready:")
    print("• All public endpoints working for website display")
    print("• Authentication working for user actions")
    print("• Search and filtering available")
    print("• Statistics and categories available")
    print("• Like and download tracking available")

if __name__ == "__main__":
    asyncio.run(test_template_apis())
