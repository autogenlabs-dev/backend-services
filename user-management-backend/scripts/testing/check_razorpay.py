"""
Verify Razorpay configuration by checking which keys the backend is using.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("="*60)
print("RAZORPAY CONFIGURATION CHECK")
print("="*60)

# Check if we can get the key from create-order response
print("\n1. Testing /api/razorpay-config endpoint (if exists)...")
try:
    r = requests.get(f"{BASE_URL}/api/razorpay-config", timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   Not available: {e}")

print("\n2. Checking health...")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"   Status: {r.status_code}")
except Exception as e:
    print(f"   Error: {e}")

print("\n3. Checking /api/subscriptions/plans endpoint...")
try:
    r = requests.get(f"{BASE_URL}/api/subscriptions/plans", timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        # Check if razorpay key is in response
        print(f"   Response contains 'razorpay': {'razorpay' in str(data).lower()}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*60)
print("To verify the actual key being used, check Docker logs:")
print("docker-compose logs api | grep -i razorpay")
print("="*60)
