#!/usr/bin/env python3
"""
Simple admin API test script to diagnose issues
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_admin_apis():
    """Test admin APIs with proper authentication"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Login as admin
        print("1. Testing admin login...")
        login_data = {
            "email": "amit123@gmail.com", 
            "password": "1234567890"
        }
        
        try:
            async with session.post(f"{base_url}/auth/login-json", json=login_data) as resp:
                print(f"   Login status: {resp.status}")
                if resp.status == 200:
                    login_result = await resp.json()
                    token = login_result.get("access_token")
                    user_info = login_result.get("user", {})
                    print(f"   Login successful! Role: {user_info.get('role', 'unknown')}")
                    print(f"   Token: {token[:50]}...")
                else:
                    error_text = await resp.text()
                    print(f"   Login failed: {error_text}")
                    return
        except Exception as e:
            print(f"   Login error: {e}")
            return

        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Test analytics API
        print("\n2. Testing admin analytics API...")
        try:
            async with session.get(f"{base_url}/admin/analytics", headers=headers) as resp:
                print(f"   Analytics status: {resp.status}")
                if resp.status == 200:
                    analytics = await resp.json()
                    users = analytics.get("users", {})
                    content = analytics.get("content", {})
                    print(f"   Total users: {users.get('total', 0)}")
                    print(f"   Total content: {content.get('totals', {}).get('all_content', 0)}")
                    print(f"   Pending approvals: {content.get('totals', {}).get('pending_content', 0)}")
                else:
                    error_text = await resp.text()
                    print(f"   Analytics error: {error_text}")
        except Exception as e:
            print(f"   Analytics exception: {e}")
        
        # Step 3: Test content API
        print("\n3. Testing admin content API...")
        try:
            async with session.get(f"{base_url}/admin/content", headers=headers) as resp:
                print(f"   Content status: {resp.status}")
                if resp.status == 200:
                    content_data = await resp.json()
                    content_list = content_data.get("content", [])
                    print(f"   Total content items: {len(content_list)}")
                    
                    # Show status breakdown
                    status_counts = {}
                    for item in content_list:
                        status = item.get("status", "unknown")
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    print(f"   Status breakdown: {status_counts}")
                    
                    # Show first few items
                    print("\n   First 3 content items:")
                    for i, item in enumerate(content_list[:3]):
                        print(f"     {i+1}. {item.get('title', 'No title')} ({item.get('content_type', 'unknown')}) - {item.get('status', 'No status')}")
                else:
                    error_text = await resp.text()
                    print(f"   Content error: {error_text}")
        except Exception as e:
            print(f"   Content exception: {e}")
        
        # Step 4: Test users API
        print("\n4. Testing admin users API...")
        try:
            async with session.get(f"{base_url}/admin/users", headers=headers) as resp:
                print(f"   Users status: {resp.status}")
                if resp.status == 200:
                    users_data = await resp.json()
                    users_list = users_data.get("users", [])
                    print(f"   Total users: {len(users_list)}")
                    
                    # Show role breakdown
                    role_counts = {}
                    for user in users_list:
                        role = user.get("role", "unknown")
                        role_counts[role] = role_counts.get(role, 0) + 1
                    
                    print(f"   Role breakdown: {role_counts}")
                else:
                    error_text = await resp.text()
                    print(f"   Users error: {error_text}")
        except Exception as e:
            print(f"   Users exception: {e}")

if __name__ == "__main__":
    print("Admin API Test Script")
    print("=" * 50)
    asyncio.run(test_admin_apis())
    print("\nTest completed.")
