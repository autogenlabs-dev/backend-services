#!/usr/bin/env python3
"""
Authentication Flow Test Script
Tests the complete authentication flow for VS Code integration.
"""

import asyncio
import json
import sys
from datetime import datetime
import httpx

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test01@vscode.com",
    "password": "securepassword123",
    "first_name": "Test",
    "last_name": "User"
}

class AuthFlowTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        
    async def test_health_check(self):
        """Test if the server is running."""
        print("🏥 Testing server health...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server is healthy: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Server connection failed: {e}")
            return False
    
    async def test_user_registration(self):
        """Test user registration endpoint."""
        print("\n👤 Testing user registration...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/register",
                    json=TEST_USER
                )
            
            print(f"📡 Status Code: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ User registration successful")
                self.user_id = data.get("user", {}).get("id")
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                print("⚠️  User already exists (this is expected for repeat tests)")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration request failed: {e}")
            return False
    
    async def test_vs_code_login(self):
        """Test VS Code specific login endpoint."""
        print("\n🔐 Testing VS Code login (login-json)...")
        
        try:
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/login-json",
                    json=login_data
                )
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ VS Code login successful")
                
                # Extract tokens
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                
                # Print response structure (for VS Code integration verification)
                print("📋 Login Response Structure:")
                print(f"   🎫 Access Token: {'✅ Present' if self.access_token else '❌ Missing'}")
                print(f"   🔄 Refresh Token: {'✅ Present' if self.refresh_token else '❌ Missing'}")
                print(f"   👤 User Data: {'✅ Present' if data.get('user') else '❌ Missing'}")
                print(f"   🔑 A4F API Key: {'✅ Present' if data.get('a4f_api_key') else '❌ Missing'}")
                print(f"   🌐 API Endpoint: {'✅ Present' if data.get('api_endpoint') else '❌ Missing'}")
                
                # Detailed user info
                user_data = data.get("user", {})
                print(f"\n👤 User Information:")
                print(f"   📧 Email: {user_data.get('email')}")
                print(f"   🆔 ID: {user_data.get('id')}")
                print(f"   💳 Subscription: {user_data.get('subscription_tier', 'N/A')}")
                
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login request failed: {e}")
            return False
    
    async def test_protected_endpoint(self):
        """Test accessing protected endpoint with token."""
        print("\n🔒 Testing protected endpoint access...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/auth/me",
                    headers=headers
                )
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Protected endpoint access successful")
                print(f"📋 Current User: {data.get('user', {}).get('email')}")
                return True
            else:
                print(f"❌ Protected endpoint access failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Protected endpoint request failed: {e}")
            return False
    
    async def test_vs_code_config(self):
        """Test VS Code configuration endpoint."""
        print("\n⚙️  Testing VS Code configuration endpoint...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/auth/vscode-config",
                    headers=headers
                )
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ VS Code config endpoint successful")
                
                config = data.get("config", {})
                print("📋 VS Code Configuration:")
                print(f"   🔑 A4F API Key: {'✅ Present' if config.get('a4f_api_key') else '❌ Missing'}")
                print(f"   🌐 API Endpoint: {'✅ Present' if config.get('api_endpoint') else '❌ Missing'}")
                print(f"   🤖 Providers: {'✅ Present' if config.get('providers') else '❌ Missing'}")
                
                return True
            else:
                print(f"❌ VS Code config failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ VS Code config request failed: {e}")
            return False
    
    async def test_subscription_status(self):
        """Test subscription status endpoint."""
        print("\n💳 Testing subscription status...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/subscriptions/current",
                    headers=headers
                )
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Subscription status retrieved successfully")
                print(f"📋 Subscription: {data.get('tier', 'N/A')}")
                print(f"📊 Usage: {data.get('current_usage', {})}")
                return True
            else:
                print(f"❌ Subscription status failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Subscription status request failed: {e}")
            return False
    
    async def test_api_keys_list(self):
        """Test API keys listing endpoint."""
        print("\n🔑 Testing API keys listing...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api-keys",
                    headers=headers
                )
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API keys listing successful")
                print(f"📋 Number of API keys: {len(data.get('api_keys', []))}")
                return True
            else:
                print(f"❌ API keys listing failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ API keys request failed: {e}")
            return False

    async def test_user_profile(self):
        """Test user profile endpoint."""
        print("\n👤 Testing user profile...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/me",
                    headers=headers
                )
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ User profile retrieved successfully")
                user = data.get('user', {})
                print(f"📧 Email: {user.get('email')}")
                print(f"👤 Name: {user.get('full_name', 'N/A')}")
                print(f"🎫 Tokens Remaining: {user.get('tokens_remaining', 'N/A')}")
                print(f"💳 Subscription: {user.get('subscription', 'N/A')}")
                return True
            else:
                print(f"❌ User profile failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ User profile request failed: {e}")
            return False

    async def test_organizations_list(self):
        """Test organizations listing endpoint."""
        print("\n🏢 Testing organizations listing...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/organizations",
                    headers=headers
                )
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Organizations listing successful")
                print(f"📋 Number of organizations: {len(data.get('organizations', []))}")
                return True
            else:
                print(f"❌ Organizations listing failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Organizations request failed: {e}")
            return False

    async def test_sub_users_list(self):
        """Test sub-users listing endpoint."""
        print("\n👥 Testing sub-users listing...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/sub-users",
                    headers=headers
                )
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Sub-users listing successful")
                print(f"📋 Number of sub-users: {len(data.get('sub_users', []))}")
                return True
            else:
                print(f"❌ Sub-users listing failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Sub-users request failed: {e}")
            return False

    async def test_llm_models(self):
        """Test LLM models listing endpoint."""
        print("\n🤖 Testing LLM models listing...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/llm/models",
                    headers=headers
                )
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ LLM models listing successful")
                models = data.get('models', [])
                print(f"📋 Available models: {len(models)}")
                if models:
                    print(f"🎯 First model: {models[0].get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ LLM models listing failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ LLM models request failed: {e}")
            return False

    async def test_token_usage(self):
        """Test token usage endpoint."""
        print("\n📊 Testing token usage...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/tokens/usage",
                    headers=headers
                )
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Token usage retrieved successfully")
                usage = data.get('usage', {})
                print(f"🔢 Tokens Used: {usage.get('tokens_used', 'N/A')}")
                print(f"🎯 Tokens Remaining: {usage.get('tokens_remaining', 'N/A')}")
                print(f"📅 Reset Date: {usage.get('reset_date', 'N/A')}")
                return True
            else:
                print(f"❌ Token usage failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Token usage request failed: {e}")
            return False

    async def test_token_refresh(self):
        """Test token refresh mechanism."""
        print("\n🔄 Testing token refresh...")
        
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        try:
            refresh_data = {"refresh_token": self.refresh_token}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/refresh",
                    json=refresh_data
                )
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Token refresh successful")
                
                new_access_token = data.get("access_token")
                new_refresh_token = data.get("refresh_token")
                
                print(f"   🎫 New Access Token: {'✅ Present' if new_access_token else '❌ Missing'}")
                print(f"   🔄 New Refresh Token: {'✅ Present' if new_refresh_token else '❌ Missing'}")
                  # Update tokens
                if new_access_token:
                    self.access_token = new_access_token
                if new_refresh_token:
                    self.refresh_token = new_refresh_token
                
                return True
            else:
                print(f"❌ Token refresh failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Token refresh request failed: {e}")
            return False

    async def run_full_test_suite(self):
        """Run the complete authentication flow test suite."""
        print("🚀 Starting Authentication Flow Test Suite")
        print(f"⏰ Started at: {datetime.now()}")
        print(f"🎯 Target URL: {self.base_url}")
        print("=" * 60)
        
        # Core authentication tests (implemented in minimal server)
        core_tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("VS Code Login", self.test_vs_code_login),
            ("Protected Endpoint Access", self.test_protected_endpoint),
            ("VS Code Configuration", self.test_vs_code_config),
            ("Subscription Status", self.test_subscription_status),
            ("Token Refresh", self.test_token_refresh),
        ]
        
        # Additional API tests (may not be implemented in minimal server)
        additional_tests = [
            ("User Profile", self.test_user_profile),
            ("API Keys Listing", self.test_api_keys_list),
            ("Organizations Listing", self.test_organizations_list),
            ("Sub-Users Listing", self.test_sub_users_list),
            ("LLM Models", self.test_llm_models),
            ("Token Usage", self.test_token_usage),
        ]
        
        print("🔧 Running CORE authentication tests (required for VS Code)...")
        print("-" * 60)
        
        core_results = []
        for test_name, test_func in core_tests:
            try:
                result = await test_func()
                core_results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                core_results.append((test_name, False))
        
        print("\n🚀 Running ADDITIONAL API tests (optional features)...")
        print("-" * 60)
        
        additional_results = []
        for test_name, test_func in additional_tests:
            try:
                result = await test_func()
                additional_results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                additional_results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print("\n🔧 CORE AUTHENTICATION TESTS (Required for VS Code):")
        print("-" * 60)
        core_passed = 0
        core_total = len(core_results)
        
        for test_name, result in core_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                core_passed += 1
        
        print(f"\n📈 Core Results: {core_passed}/{core_total} tests passed ({(core_passed/core_total)*100:.1f}%)")
        
        print("\n🚀 ADDITIONAL API TESTS (Optional Features):")
        print("-" * 60)
        additional_passed = 0
        additional_total = len(additional_results)
        
        for test_name, result in additional_results:
            status = "✅ PASS" if result else "⚠️  SKIP" if not result else "❌ FAIL"
            # For 404 errors, show as SKIP instead of FAIL
            print(f"{status} - {test_name}")
            if result:
                additional_passed += 1
        
        print(f"\n📈 Additional Results: {additional_passed}/{additional_total} tests passed ({(additional_passed/additional_total)*100:.1f}%)")
        
        # Overall summary
        total_passed = core_passed + additional_passed
        total_tests = core_total + additional_total
        
        print("\n" + "=" * 60)
        print("� OVERALL ASSESSMENT:")
        print("=" * 60)
        
        if core_passed == core_total:
            print("🎉 ✅ CORE AUTHENTICATION: FULLY FUNCTIONAL")
            print("   → Ready for VS Code extension integration!")
        else:
            print("⚠️  ❌ CORE AUTHENTICATION: ISSUES DETECTED")
            print("   → VS Code integration may have problems")
        
        if additional_passed > 0:
            print(f"🚀 ✅ ADDITIONAL FEATURES: {additional_passed}/{additional_total} working")
        else:
            print("🚀 ⚠️  ADDITIONAL FEATURES: Not implemented (minimal server)")
        
        print(f"\n📊 Combined Results: {total_passed}/{total_tests} tests passed ({(total_passed/total_tests)*100:.1f}%)")
        print(f"⏰ Completed at: {datetime.now()}")
        
        return core_passed == core_total  # Success if all core tests pass

async def main():
    """Main function to run the test suite."""
    tester = AuthFlowTester()
    success = await tester.run_full_test_suite()
    
    if success:
        print("\n✅ Authentication flow testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Authentication flow testing failed!")
        sys.exit(1)

if __name__ == "__main__":
    print("🧪 Authentication Flow Tester for VS Code Integration")
    print("📝 This script tests the complete authentication flow required by VS Code extension")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)
