#!/usr/bin/env python3
"""
Test login on the live API endpoint: api.codemurf.com
"""
import requests
import json
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://api.codemurf.com"

print("\n" + "="*80)
print("🧪 TESTING LIVE API LOGIN - api.codemurf.com")
print("="*80)

# Test accounts
test_accounts = [
    {"email": "admin@codemurf.com", "password": "Admin2025!@#", "role": "admin"},
    {"email": "superadmin@codemurf.com", "password": "SuperAdmin2025!@#", "role": "superadmin"},
]

print(f"\n📍 API Endpoint: {API_URL}")
print(f"🔍 Testing login endpoint: {API_URL}/auth/login")

# First, check if API is reachable
print("\n1️⃣ Checking API Health...")
try:
    response = requests.get(f"{API_URL}/docs", timeout=5, verify=False)
    if response.status_code == 200:
        print(f"   ✅ API is reachable (docs page accessible)")
    else:
        print(f"   ⚠️  API responded with status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Cannot reach API: {e}")
    exit(1)

# Test login for each account
for account in test_accounts:
    print(f"\n{'='*80}")
    print(f"🔐 Testing {account['role'].upper()} Login")
    print(f"{'='*80}")
    print(f"📧 Email: {account['email']}")
    print(f"🔑 Password: {account['password']}")
    
    # Try login
    try:
        # OAuth2 format (form-data)
        login_data = {
            "username": account['email'],
            "password": account['password']
        }
        
        print(f"\n📤 Sending login request...")
        response = requests.post(
            f"{API_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
            verify=False
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ LOGIN SUCCESSFUL!")
            print(f"\n📋 Response:")
            print(f"   Token Type: {result.get('token_type', 'N/A')}")
            
            access_token = result.get('access_token')
            if access_token:
                print(f"   Access Token: {access_token[:30]}...")
                
                # Test getting profile with token
                print(f"\n🔍 Testing profile endpoint with token...")
                profile_response = requests.get(
                    f"{API_URL}/auth/profile",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10,
                    verify=False
                )
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    print(f"   ✅ Profile retrieved successfully!")
                    print(f"      Email: {profile.get('email', 'N/A')}")
                    print(f"      Role: {profile.get('role', 'N/A')}")
                    print(f"      Name: {profile.get('name', 'N/A')}")
                    print(f"      Tokens: {profile.get('tokens_remaining', 'N/A')}")
                else:
                    print(f"   ❌ Profile request failed: {profile_response.status_code}")
                    print(f"      {profile_response.text[:200]}")
            else:
                print(f"   ⚠️  No access token in response")
                
        elif response.status_code == 401:
            print(f"❌ LOGIN FAILED - Unauthorized")
            try:
                error = response.json()
                print(f"\n📋 Error Details:")
                print(f"   {json.dumps(error, indent=2)}")
            except:
                print(f"\n📋 Raw Response:")
                print(f"   {response.text[:500]}")
                
        else:
            print(f"❌ LOGIN FAILED - Status {response.status_code}")
            print(f"\n📋 Response:")
            print(f"   {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - Cannot reach {API_URL}")
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

print(f"\n{'='*80}")
print("📊 TEST COMPLETE")
print(f"{'='*80}")
print("\nIf login still fails with 'Invalid salt', check:")
print("• Docker container needs restart: docker-compose restart")
print("• Code changes need deployment: git pull && docker-compose build --no-cache")
print("• API is using old code cached in memory")
