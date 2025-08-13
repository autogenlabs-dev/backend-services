#!/usr/bin/env python3
"""
Comprehensive test script for Admin Dashboard System - Phase 2
Tests all admin endpoints and role-based access control features.
"""

import asyncio
import sys
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, Optional


class AdminDashboardTester:
    """Test suite for admin dashboard functionality."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.admin_token = None
        self.developer_token = None
        self.user_token = None
        
    async def create_test_users(self) -> Dict[str, str]:
        """Create test users for different roles."""
        print("🔧 Creating test users...")
        
        async with aiohttp.ClientSession() as session:
            users = {
                "admin": {
                    "email": "admin@autogenlabs.com",
                    "password": "admin123",
                    "first_name": "Admin",
                    "last_name": "User"
                },
                "developer": {
                    "email": "dev@autogenlabs.com", 
                    "password": "dev123",
                    "first_name": "Developer",
                    "last_name": "User"
                },
                "user": {
                    "email": "user@autogenlabs.com",
                    "password": "user123", 
                    "first_name": "Regular",
                    "last_name": "User"
                }
            }
            
            tokens = {}
            
            for role, user_data in users.items():
                # Try to register user
                try:
                    async with session.post(f"{self.base_url}/register", json=user_data) as resp:
                        if resp.status in [200, 201]:
                            print(f"✅ Registered {role} user")
                        elif resp.status == 400:
                            print(f"ℹ️  {role} user already exists")
                        else:
                            print(f"❌ Failed to register {role} user: {resp.status}")
                except Exception as e:
                    print(f"⚠️  Registration error for {role}: {e}")
                
                # Login to get token
                try:
                    login_data = {"email": user_data["email"], "password": user_data["password"]}
                    async with session.post(f"{self.base_url}/login", json=login_data) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            tokens[role] = result["access_token"]
                            print(f"✅ Logged in {role} user")
                        else:
                            print(f"❌ Failed to login {role} user: {resp.status}")
                except Exception as e:
                    print(f"⚠️  Login error for {role}: {e}")
            
            self.admin_token = tokens.get("admin")
            self.developer_token = tokens.get("developer") 
            self.user_token = tokens.get("user")
            
            return tokens
    
    async def test_admin_users_endpoint(self) -> bool:
        """Test admin users management endpoint."""
        print("\n🧪 Testing Admin Users Endpoint...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
            
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            try:
                # Test basic users list
                async with session.get(f"{self.base_url}/admin/users", headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        print(f"✅ Retrieved {result.get('total', 0)} users")
                        return True
                    else:
                        print(f"❌ Failed to get users: {resp.status}")
                        return False
            except Exception as e:
                print(f"❌ Users endpoint error: {e}")
                return False
    
    async def test_admin_developers_endpoint(self) -> bool:
        """Test admin developers management endpoint."""
        print("\n🧪 Testing Admin Developers Endpoint...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
            
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            try:
                async with session.get(f"{self.base_url}/admin/developers", headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        print(f"✅ Retrieved {result.get('total', 0)} developers")
                        return True
                    else:
                        print(f"❌ Failed to get developers: {resp.status}")
                        return False
            except Exception as e:
                print(f"❌ Developers endpoint error: {e}")
                return False
    
    async def test_admin_pending_content_endpoint(self) -> bool:
        """Test admin pending content endpoint."""
        print("\n🧪 Testing Admin Pending Content Endpoint...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
            
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            try:
                async with session.get(f"{self.base_url}/admin/content/pending", headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        print(f"✅ Retrieved {result.get('total', 0)} pending content items")
                        return True
                    else:
                        print(f"❌ Failed to get pending content: {resp.status}")
                        return False
            except Exception as e:
                print(f"❌ Pending content endpoint error: {e}")
                return False
    
    async def test_admin_analytics_endpoint(self) -> bool:
        """Test admin analytics endpoint."""
        print("\n🧪 Testing Admin Analytics Endpoint...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
            
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            try:
                async with session.get(f"{self.base_url}/admin/analytics", headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        print(f"✅ Retrieved analytics: {result.get('users', {}).get('total', 0)} users, {result.get('content', {}).get('totals', {}).get('all_content', 0)} content items")
                        return True
                    else:
                        print(f"❌ Failed to get analytics: {resp.status}")
                        return False
            except Exception as e:
                print(f"❌ Analytics endpoint error: {e}")
                return False
    
    async def test_admin_audit_logs_endpoint(self) -> bool:
        """Test admin audit logs endpoint."""
        print("\n🧪 Testing Admin Audit Logs Endpoint...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
            
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            try:
                async with session.get(f"{self.base_url}/admin/audit-logs", headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        print(f"✅ Retrieved {result.get('total', 0)} audit log entries")
                        return True
                    else:
                        print(f"❌ Failed to get audit logs: {resp.status}")
                        return False
            except Exception as e:
                print(f"❌ Audit logs endpoint error: {e}")
                return False
    
    async def test_content_creation_with_approval(self) -> bool:
        """Test content creation with approval workflow."""
        print("\n🧪 Testing Content Creation with Approval Workflow...")
        
        if not self.developer_token:
            print("❌ No developer token available")
            return False
            
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.developer_token}"}
            
            # Create test template
            template_data = {
                "title": "Test Admin Template",
                "category": "Web Development",
                "type": "Frontend",
                "language": "JavaScript",
                "difficulty_level": "Beginner",
                "plan_type": "free",
                "pricing_inr": 0,
                "pricing_usd": 0,
                "short_description": "Test template for admin approval",
                "full_description": "This is a test template to verify the admin approval workflow",
                "preview_images": [],
                "dependencies": ["react"],
                "tags": ["test", "admin"],
                "developer_name": "Test Developer",
                "developer_experience": "5 years",
                "is_available_for_dev": True,
                "featured": False,
                "popular": False
            }
            
            try:
                async with session.post(f"{self.base_url}/templates", json=template_data, headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        template_id = result.get("id")
                        status = result.get("status", "unknown")
                        print(f"✅ Created template with status: {status}")
                        
                        if status == "pending_approval":
                            print("✅ Template correctly set to pending approval")
                            return True
                        else:
                            print(f"⚠️  Expected pending_approval, got {status}")
                            return False
                    else:
                        print(f"❌ Failed to create template: {resp.status}")
                        return False
            except Exception as e:
                print(f"❌ Template creation error: {e}")
                return False
    
    async def test_role_based_access_control(self) -> bool:
        """Test role-based access control."""
        print("\n🧪 Testing Role-Based Access Control...")
        
        success = True
        
        # Test user access to admin endpoints (should fail)
        if self.user_token:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                
                try:
                    async with session.get(f"{self.base_url}/admin/users", headers=headers) as resp:
                        if resp.status == 403:
                            print("✅ Regular user correctly denied admin access")
                        else:
                            print(f"❌ Regular user should not access admin endpoint: {resp.status}")
                            success = False
                except Exception as e:
                    print(f"⚠️  Access control test error: {e}")
        
        # Test developer creating content (should work)
        if self.developer_token:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.developer_token}"}
                
                component_data = {
                    "title": "Test Component",
                    "category": "UI",
                    "type": "Component",
                    "language": "React",
                    "difficulty_level": "Beginner",
                    "plan_type": "free",
                    "pricing_inr": 0,
                    "pricing_usd": 0,
                    "short_description": "Test component",
                    "full_description": "Test component description",
                    "preview_images": [],
                    "dependencies": [],
                    "tags": ["test"],
                    "developer_name": "Test Dev",
                    "developer_experience": "2 years",
                    "is_available_for_dev": True,
                    "featured": False,
                    "popular": False
                }
                
                try:
                    async with session.post(f"{self.base_url}/components", json=component_data, headers=headers) as resp:
                        if resp.status == 200:
                            print("✅ Developer can create components")
                        else:
                            print(f"❌ Developer should be able to create components: {resp.status}")
                            success = False
                except Exception as e:
                    print(f"⚠️  Component creation test error: {e}")
        
        return success
    
    async def test_content_visibility(self) -> bool:
        """Test content visibility based on approval status."""
        print("\n🧪 Testing Content Visibility Based on Approval Status...")
        
        # Test anonymous user access (should only see approved content)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/templates") as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        templates = result.get("templates", [])
                        
                        # Check if any pending templates are visible
                        pending_visible = any(t.get("status") == "pending_approval" for t in templates)
                        
                        if not pending_visible:
                            print("✅ Anonymous users only see approved content")
                            return True
                        else:
                            print("❌ Anonymous users should not see pending content")
                            return False
                    else:
                        print(f"❌ Failed to get templates: {resp.status}")
                        return False
            except Exception as e:
                print(f"❌ Content visibility test error: {e}")
                return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all admin dashboard tests."""
        print("🚀 Starting Admin Dashboard Test Suite")
        print("=" * 50)
        
        # Setup
        await self.create_test_users()
        
        # Run tests
        test_results = {}
        
        test_results["admin_users"] = await self.test_admin_users_endpoint()
        test_results["admin_developers"] = await self.test_admin_developers_endpoint()
        test_results["admin_pending_content"] = await self.test_admin_pending_content_endpoint()
        test_results["admin_analytics"] = await self.test_admin_analytics_endpoint()
        test_results["admin_audit_logs"] = await self.test_admin_audit_logs_endpoint()
        test_results["content_creation"] = await self.test_content_creation_with_approval()
        test_results["role_based_access"] = await self.test_role_based_access_control()
        test_results["content_visibility"] = await self.test_content_visibility()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print("=" * 50)
        
        passed = sum(test_results.values())
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Admin dashboard is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
        
        return test_results


async def main():
    """Main test runner."""
    tester = AdminDashboardTester()
    
    try:
        results = await tester.run_all_tests()
        return results
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return {}
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        return {}


if __name__ == "__main__":
    print("🧪 Admin Dashboard Test Suite")
    print("Make sure the server is running on http://localhost:8000")
    print()
    
    # Run tests
    results = asyncio.run(main())
    
    # Exit with appropriate code
    if results and all(results.values()):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
