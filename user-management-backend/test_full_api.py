#!/usr/bin/env python3
"""
Full API Test Script
Tests both the minimal auth server and attempts to test the full API endpoints.
"""

import asyncio
import json
import sys
from datetime import datetime
import httpx

# Test configuration
MINIMAL_SERVER_URL = "http://localhost:8000"  # Minimal auth server
FULL_API_URL = "http://localhost:8001"        # Full API server (if available)

TEST_USER = {
    "email": "test01@vscode.com",
    "password": "securepassword123",
    "first_name": "Test",
    "last_name": "User"
}

class FullAPITester:
    def __init__(self):
        self.minimal_server_url = MINIMAL_SERVER_URL
        self.full_api_url = FULL_API_URL
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        
    async def test_server_availability(self, url: str, server_name: str):
        """Test if a server is available."""
        print(f"🔍 Testing {server_name} availability at {url}...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5.0)
                
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {server_name} is available: {data}")
                return True
            else:
                print(f"❌ {server_name} health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ {server_name} connection failed: {e}")
            return False

    async def login_and_get_token(self, base_url: str):
        """Login and get access token from either server."""
        print(f"\n🔐 Attempting login at {base_url}...")
        
        try:
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/auth/login-json",
                    json=login_data
                )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login request failed: {e}")
            return False

    async def test_endpoint(self, base_url: str, endpoint: str, method: str = "GET", description: str = ""):
        """Test a specific endpoint."""
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(f"{base_url}{endpoint}", headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(f"{base_url}{endpoint}", headers=headers, json={})
                else:
                    print(f"❌ Unsupported method: {method}")
                    return False
            
            print(f"📡 {method} {endpoint} -> {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ {description}: Success")
                    return True
                except:
                    print(f"✅ {description}: Success (non-JSON response)")
                    return True
            elif response.status_code == 404:
                print(f"⚠️  {description}: Not implemented")
                return False
            elif response.status_code == 401:
                print(f"❌ {description}: Authentication failed")
                return False
            else:
                print(f"❌ {description}: Failed ({response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ {description}: Request failed - {e}")
            return False

    async def test_comprehensive_endpoints(self, base_url: str, server_name: str):
        """Test comprehensive list of API endpoints."""
        print(f"\n🚀 Testing {server_name} endpoints...")
        print("-" * 60)
        
        # Authentication endpoints
        auth_endpoints = [
            ("/auth/me", "GET", "Current User Info"),
            ("/auth/vscode-config", "GET", "VS Code Configuration"),
            ("/auth/providers", "GET", "OAuth Providers"),
            ("/auth/refresh", "POST", "Token Refresh"),
        ]
        
        # User management endpoints
        user_endpoints = [
            ("/users/me", "GET", "User Profile"),
            ("/users/preferences", "GET", "User Preferences"),
            ("/users/usage", "GET", "User Usage Stats"),
        ]
        
        # Subscription endpoints
        subscription_endpoints = [
            ("/subscriptions/current", "GET", "Current Subscription"),
            ("/subscriptions/plans", "GET", "Available Plans"),
            ("/subscriptions/usage", "GET", "Subscription Usage"),
        ]
        
        # API Key endpoints
        api_key_endpoints = [
            ("/api-keys", "GET", "List API Keys"),
            ("/api-keys/generate", "POST", "Generate API Key"),
        ]
        
        # Organization endpoints
        organization_endpoints = [
            ("/organizations", "GET", "List Organizations"),
            ("/organizations/current", "GET", "Current Organization"),
        ]
        
        # Sub-user endpoints
        sub_user_endpoints = [
            ("/sub-users", "GET", "List Sub-users"),
            ("/sub-users/dashboard", "GET", "Sub-user Dashboard"),
        ]
        
        # LLM endpoints
        llm_endpoints = [
            ("/llm/models", "GET", "Available Models"),
            ("/llm/providers", "GET", "LLM Providers"),
        ]
        
        # Token endpoints
        token_endpoints = [
            ("/tokens/usage", "GET", "Token Usage"),
            ("/tokens/reset", "POST", "Reset Token Usage"),
        ]
        
        # Admin endpoints
        admin_endpoints = [
            ("/admin/users", "GET", "Admin User List"),
            ("/admin/stats", "GET", "Admin Statistics"),
        ]
        
        all_endpoint_groups = [
            ("Authentication", auth_endpoints),
            ("User Management", user_endpoints),
            ("Subscriptions", subscription_endpoints),
            ("API Keys", api_key_endpoints),
            ("Organizations", organization_endpoints),
            ("Sub-users", sub_user_endpoints),
            ("LLM Services", llm_endpoints),
            ("Token Management", token_endpoints),
            ("Admin", admin_endpoints),
        ]
        
        results = {}
        
        for group_name, endpoints in all_endpoint_groups:
            print(f"\n📂 {group_name} Endpoints:")
            group_results = []
            
            for endpoint, method, description in endpoints:
                result = await self.test_endpoint(base_url, endpoint, method, description)
                group_results.append((endpoint, result, description))
            
            results[group_name] = group_results
        
        return results

    async def generate_test_report(self, results: dict, server_name: str):
        """Generate a comprehensive test report."""
        print(f"\n" + "=" * 80)
        print(f"📊 {server_name} API TEST REPORT")
        print("=" * 80)
        
        total_tests = 0
        total_passed = 0
        
        for group_name, group_results in results.items():
            passed = sum(1 for _, result, _ in group_results if result)
            total = len(group_results)
            total_tests += total
            total_passed += passed
            
            print(f"\n📂 {group_name}: {passed}/{total} endpoints working")
            
            for endpoint, result, description in group_results:
                status = "✅ WORKING" if result else "❌ NOT AVAILABLE"
                print(f"   {status} - {description} ({endpoint})")
        
        print("\n" + "-" * 80)
        print(f"📈 OVERALL RESULTS: {total_passed}/{total_tests} endpoints working ({(total_passed/total_tests)*100:.1f}%)")
        
        if total_passed > 0:
            print(f"🎉 {server_name} has {total_passed} working endpoints!")
        else:
            print(f"⚠️  {server_name} appears to be minimal or has configuration issues")
        
        return total_passed, total_tests

    async def run_comprehensive_test(self):
        """Run comprehensive test of both servers."""
        print("🧪 Comprehensive API Testing Suite")
        print(f"⏰ Started at: {datetime.now()}")
        print("=" * 80)
        
        # Test server availability
        minimal_available = await self.test_server_availability(self.minimal_server_url, "Minimal Auth Server")
        full_api_available = await self.test_server_availability(self.full_api_url, "Full API Server")
        
        test_results = {}
        
        # Test minimal server if available
        if minimal_available:
            if await self.login_and_get_token(self.minimal_server_url):
                minimal_results = await self.test_comprehensive_endpoints(self.minimal_server_url, "Minimal Auth Server")
                test_results["Minimal Server"] = minimal_results
        
        # Test full API server if available
        if full_api_available:
            if await self.login_and_get_token(self.full_api_url):
                full_results = await self.test_comprehensive_endpoints(self.full_api_url, "Full API Server")
                test_results["Full API Server"] = full_results
        
        # Generate reports
        print("\n" + "🎯" * 40)
        print("FINAL COMPREHENSIVE REPORT")
        print("🎯" * 40)
        
        for server_name, results in test_results.items():
            passed, total = await self.generate_test_report(results, server_name)
        
        if not test_results:
            print("❌ No servers were available for testing!")
            return False
        
        print(f"\n⏰ Testing completed at: {datetime.now()}")
        return True

async def main():
    """Main function to run the comprehensive test suite."""
    tester = FullAPITester()
    success = await tester.run_comprehensive_test()
    
    if success:
        print("\n✅ Comprehensive API testing completed!")
        sys.exit(0)
    else:
        print("\n❌ Comprehensive API testing failed!")
        sys.exit(1)

if __name__ == "__main__":
    print("🔍 Comprehensive API Tester")
    print("📝 This script tests all available API endpoints on both servers")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)
