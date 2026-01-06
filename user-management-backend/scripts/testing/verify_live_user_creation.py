import requests
import time
import random
import string

BASE_URL = 'https://api.codemurf.com'

# Generate unique user details
timestamp = int(time.time())
random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
EMAIL = f'live.test.user.{timestamp}.{random_suffix}@codemurf.com'
PASSWORD = 'LiveTestPass123!'
NAME = f'Live Test User {timestamp}'

print(f"🌍 TRINITY LIVE PRODUCTION TEST: {BASE_URL}")
print("=" * 60)
print(f"Details to create:")
print(f"   Email: {EMAIL}")
print(f"   Pass:  {PASSWORD}")
print("-" * 60)

# 1. Register
print("\n1. Registering new user...")
try:
    r = requests.post(f'{BASE_URL}/api/auth/register', json={
        'email': EMAIL,
        'password': PASSWORD,
        'name': NAME
    })
    print(f"   Status: {r.status_code}")
    if r.status_code not in [200, 201]:
        print(f"   ❌ Registration Failed: {r.text}")
        exit(1)
    print(f"   ✅ Registration Successful!")
    # Some APIs return token on register, some require login. Let's assume login needed.
except Exception as e:
    print(f"   ❌ Network/Request Error: {e}")
    exit(1)

# 2. Login
print("\n2. Logging in...")
try:
    r = requests.post(f'{BASE_URL}/api/auth/login', data={
        'username': EMAIL,
        'password': PASSWORD
    })
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✅ Login Successful!")
        token = r.json().get('access_token')
    else:
        print(f"   ❌ Login Failed: {r.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ Login Error: {e}")
    exit(1)

# 3. Verify Endpoints
if token:
    headers = {'Authorization': f'Bearer {token}'}

    # 3.1 Profile
    print("\n3. Verifying Profile (/api/users/me)...")
    r = requests.get(f'{BASE_URL}/api/users/me', headers=headers)
    if r.status_code == 200:
        data = r.json()
        print(f"   ✅ Name: {data.get('name')}")
        print(f"   ✅ Email: {data.get('email')}")
        print(f"   ✅ Subscription: {data.get('subscription')}")
        print(f"   ✅ OpenRouter Key: {'Yes' if data.get('openrouter_api_key') else 'No'} (Should be Yes for free users)")
        print(f"   ✅ GLM Key: {'Yes' if data.get('glm_api_key') else 'No'} (Should be No for free users)")
    else:
        print(f"   ❌ Profile Fetch Failed: {r.text}")

    # 3.2 API Key Refresh
    print("\n4. Verifying Extension Key Refresh (/api/users/me/refresh-api-keys)...")
    # This endpoint mimics what the extension does on startup
    r = requests.post(f'{BASE_URL}/api/users/me/refresh-api-keys', headers=headers, json={})
    if r.status_code == 200:
        data = r.json()
        print(f"   ✅ Success: {data.get('success')}")
        print(f"   ✅ Current Keys: {list(data.get('current_keys', {}).keys())}")
        print(f"   ✅ Subscription data returned: {data.get('subscription')}")
    else:
         print(f"   ❌ Refresh Failed: {r.text}")

print("\n" + "=" * 60)
print(f"TEST COMPLETE. User {EMAIL} created successfully.")
print("=" * 60)
