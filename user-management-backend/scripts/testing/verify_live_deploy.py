import requests
import sys

BASE_URL = 'https://api.codemurf.com'
EMAIL = 'downshiftrides@gmail.com'
PASSWORD = 'FinalPass789!' 

print(f"🌍 TRINITY LIVE DEPLOYMENT TEST: {BASE_URL}")
print("=" * 60)

# 1. Test Root
print("\n1. Root Endpoint...")
try:
    r = requests.get(f'{BASE_URL}/docs') # Docs usually available
    print(f"   Status: {r.status_code}")
except Exception as e:
    print(f"   ❌ Network Error: {e}")
    # Don't exit, might be just root path issue

# 2. Test Login
print("\n2. Login...")
token = None
# Try new password
r = requests.post(f'{BASE_URL}/api/auth/login', data={'username': EMAIL, 'password': PASSWORD})
if r.status_code == 200:
    print(f"   ✅ Login Successful!")
    token = r.json().get('access_token')
else:
    print(f"   ⚠️ New password failed ({r.status_code}). Trying backup...")
    # Try old password
    r = requests.post(f'{BASE_URL}/api/auth/login', data={'username': EMAIL, 'password': 'ResetPass456!'})
    if r.status_code == 200:
        print(f"   ✅ Login Successful with backup!")
        token = r.json().get('access_token')
    else:
        print(f"   ❌ Login Failed: {r.text}")

if token:
    headers = {'Authorization': f'Bearer {token}'}

    # 3. Test Profile
    print("\n3. Get Profile...")
    r = requests.get(f'{BASE_URL}/api/users/me', headers=headers)
    if r.status_code == 200:
        data = r.json()
        print(f"   ✅ Sub: {data.get('subscription')}")
        print(f"   ✅ GLM Key: {'Yes' if data.get('glm_api_key') else 'No'}")
        print(f"   ✅ OpenRouter Key: {'Yes' if data.get('openrouter_api_key') else 'No'}")
    else:
        print(f"   ❌ Failed: {r.text}")

    # 4. Test Extension Refresh Endpoint
    print("\n4. Extension Key Refresh...")
    r = requests.post(f'{BASE_URL}/api/users/me/refresh-api-keys', headers=headers, json={})
    if r.status_code == 200:
         print(f"   ✅ Keys Refreshed: {r.json().get('success')}")
    else:
         print(f"   ❌ Failed: {r.text}")

# 5. Check OAuth Redirects
print("\n5. OAuth Redirects...")
try:
    r = requests.get(f'{BASE_URL}/api/auth/google/login', allow_redirects=False)
    print(f"   Google: {r.status_code} - Dests: {r.headers.get('location', '')[:40]}...")

    r = requests.get(f'{BASE_URL}/api/auth/github/login', allow_redirects=False)
    print(f"   GitHub: {r.status_code} - Dests: {r.headers.get('location', '')[:40]}...")
except Exception as e:
    print(f"   ❌ OAuth Check Error: {e}")
