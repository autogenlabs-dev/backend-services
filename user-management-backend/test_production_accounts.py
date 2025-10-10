#!/usr/bin/env python3
"""
Test Production Accounts

Quick verification script to test all created production accounts.
"""

import asyncio
import requests
import json
import sys
from typing import Dict, Any

# Production account credentials
ACCOUNTS = {
    "superadmin": {
        "email": "superadmin@codemurf.com",
        "password": "SuperAdmin2025!@#",
        "role": "superadmin"
    },
    "admin": {
        "email": "admin@codemurf.com", 
        "password": "Admin2025!@#",
        "role": "admin"
    },
    "dev1": {
        "email": "dev1@codemurf.com",
        "password": "Dev1Pass2025!",
        "role": "developer"
    },
    "dev2": {
        "email": "dev2@codemurf.com",
        "password": "Dev2Pass2025!",
        "role": "developer"
    }
}

def test_login(base_url: str, email: str, password: str) -> Dict[str, Any]:
    """Test login for a user"""
    
    login_url = f"{base_url}/api/v1/auth/login"
    
    try:
        response = requests.post(
            login_url,
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json(),
                "token": response.json().get("access_token")
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "data": None
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

def test_profile(base_url: str, token: str) -> Dict[str, Any]:
    """Test profile access with token"""
    
    profile_url = f"{base_url}/api/v1/auth/profile"
    
    try:
        response = requests.get(
            profile_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Main test function"""
    
    print("🧪 TESTING PRODUCTION ACCOUNTS")
    print("=" * 80)
    print()
    
    # Get API URL
    api_url = input("Enter your API URL (e.g., https://api.yourdomain.com): ").strip()
    if not api_url:
        api_url = "http://localhost:8000"
        print(f"Using default: {api_url}")
    
    print(f"🔗 Testing against: {api_url}")
    print()
    
    results = {}
    
    # Test each account
    for account_name, account_info in ACCOUNTS.items():
        emoji = {
            "superadmin": "👑",
            "admin": "🛡️",
            "developer": "💻"
        }
        
        role_emoji = emoji.get(account_info["role"], "❓")
        
        print(f"{role_emoji} Testing {account_name.upper()}: {account_info['email']}")
        
        # Test login
        login_result = test_login(api_url, account_info["email"], account_info["password"])
        
        if login_result["success"]:
            print(f"   ✅ Login successful")
            
            # Test profile access
            token = login_result["token"]
            if token:
                profile_result = test_profile(api_url, token)
                
                if profile_result["success"]:
                    user_data = profile_result["data"]
                    print(f"   ✅ Profile access successful")
                    print(f"   👤 Name: {user_data.get('name', 'N/A')}")
                    print(f"   🎭 Role: {user_data.get('role', 'N/A')}")
                    print(f"   🎟️  Tokens: {user_data.get('tokens_remaining', 'N/A')}")
                    
                    results[account_name] = {
                        "login": True,
                        "profile": True,
                        "role": user_data.get('role'),
                        "tokens": user_data.get('tokens_remaining')
                    }
                else:
                    print(f"   ❌ Profile access failed: {profile_result['error']}")
                    results[account_name] = {
                        "login": True,
                        "profile": False,
                        "error": profile_result['error']
                    }
            else:
                print(f"   ❌ No access token received")
                results[account_name] = {
                    "login": True,
                    "profile": False,
                    "error": "No access token"
                }
        else:
            print(f"   ❌ Login failed: {login_result['error']}")
            results[account_name] = {
                "login": False,
                "profile": False,
                "error": login_result['error']
            }
        
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    successful_logins = sum(1 for r in results.values() if r["login"])
    successful_profiles = sum(1 for r in results.values() if r.get("profile", False))
    
    print(f"✅ Successful logins: {successful_logins}/{len(ACCOUNTS)}")
    print(f"✅ Successful profile access: {successful_profiles}/{len(ACCOUNTS)}")
    print()
    
    if successful_logins == len(ACCOUNTS) and successful_profiles == len(ACCOUNTS):
        print("🎉 ALL TESTS PASSED!")
        print("Your production accounts are working correctly.")
    else:
        print("⚠️  SOME TESTS FAILED!")
        print("Check the errors above and verify your setup.")
    
    print()
    print("🔒 SECURITY REMINDER:")
    print("Change these default passwords immediately after testing!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Testing cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        sys.exit(1)