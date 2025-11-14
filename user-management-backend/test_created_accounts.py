#!/usr/bin/env python3
"""
Test script to verify the created production accounts work properly
"""
import asyncio
import requests
import json
from datetime import datetime

# API endpoint (adjust if different)
BASE_URL = "http://localhost:8000"

# Test accounts created by the reset script
TEST_ACCOUNTS = [
    {
        "email": "superadmin@codemurf.com",
        "password": "SuperAdmin2025!@#",
        "role": "superadmin",
        "name": "System SuperAdmin"
    },
    {
        "email": "admin@codemurf.com", 
        "password": "Admin2025!@#",
        "role": "admin",
        "name": "Platform Administrator"
    },
    {
        "email": "dev1@codemurf.com",
        "password": "Dev1Pass2025!",
        "role": "developer",
        "name": "Lead Developer"
    },
    {
        "email": "dev2@codemurf.com",
        "password": "Dev2Pass2025!",
        "role": "developer", 
        "name": "Senior Developer"
    }
]

def test_login(email: str, password: str, role: str, name: str):
    """Test login for a specific account"""
    print(f"\n{'='*60}")
    print(f"🔐 Testing {role.upper()} Account")
    print(f"{'='*60}")
    print(f"📧 Email: {email}")
    print(f"👤 Expected Name: {name}")
    print(f"🎭 Expected Role: {role}")
    
    try:
        # Attempt login
        login_data = {
            "username": email,  # FastAPI OAuth2 uses 'username' field
            "password": password
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/login", 
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            
            print(f"✅ Login successful!")
            print(f"🎟️  Access Token: {token[:20]}..." if token else "❌ No token received")
            
            # Test getting user profile with the token
            if token:
                profile_response = requests.get(
                    f"{BASE_URL}/auth/profile",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    print(f"📋 Profile Retrieved:")
                    print(f"   👤 Name: {profile.get('name', 'N/A')}")
                    print(f"   🎭 Role: {profile.get('role', 'N/A')}")
                    print(f"   🎟️  Tokens: {profile.get('tokens_remaining', 'N/A')}")
                    print(f"   📅 Created: {profile.get('created_at', 'N/A')}")
                    print(f"   ✅ Profile test PASSED")
                    return True
                else:
                    print(f"❌ Profile retrieval failed: {profile_response.status_code}")
                    print(f"   Response: {profile_response.text[:200]}")
                    return False
            else:
                print(f"⚠️  Login succeeded but no token received")
                return False
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - Is the server running on {BASE_URL}?")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout - Server may be slow")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    """Test all created accounts"""
    print(f"\n🧪 PRODUCTION ACCOUNT VERIFICATION")
    print(f"{'='*80}")
    print(f"🕒 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Endpoint: {BASE_URL}")
    print(f"👥 Testing {len(TEST_ACCOUNTS)} accounts")
    
    results = []
    for account in TEST_ACCOUNTS:
        success = test_login(**account)
        results.append({
            "email": account["email"],
            "role": account["role"],
            "success": success
        })
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 VERIFICATION SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {result['role'].upper():>12} | {result['email']}")
    
    print(f"\n📈 Overall Result: {passed}/{total} accounts working")
    
    if passed == total:
        print(f"🎉 All accounts are working perfectly!")
        return 0
    else:
        print(f"⚠️  {total - passed} account(s) have issues")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)