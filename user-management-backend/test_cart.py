"""
Test script to debug cart endpoint error
"""
import requests

BASE_URL = "http://localhost:8000"

# Test with a simple health check first
print("1. Testing health endpoint...")
r = requests.get(f"{BASE_URL}/health")
print(f"   Status: {r.status_code}")

# Test cart endpoint without auth (should be 401)
print("\n2. Testing cart endpoint without auth...")
r = requests.get(f"{BASE_URL}/api/cart")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text[:200]}")

# Test with a test user login
print("\n3. Registering and logging in test user...")
import random
test_email = f"carttest_{random.randint(1000,9999)}@test.com"
r = requests.post(f"{BASE_URL}/api/auth/register", json={
    "email": test_email,
    "password": "TestPass123!",
    "name": "Cart Tester"
})
print(f"   Register status: {r.status_code}")

r = requests.post(f"{BASE_URL}/api/auth/login", data={
    "username": test_email,
    "password": "TestPass123!"
})
if r.status_code == 200:
    token = r.json().get("access_token")
    print(f"   Login successful, token: {token[:30]}...")
    
    # Test cart with auth
    print("\n4. Testing cart endpoint with auth...")
    r = requests.get(f"{BASE_URL}/api/cart", headers={"Authorization": f"Bearer {token}"})
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:500]}")
else:
    print(f"   Login failed: {r.text}")
