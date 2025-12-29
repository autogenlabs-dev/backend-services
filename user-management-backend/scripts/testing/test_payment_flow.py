"""
Test script to verify the subscription update flow.
Run with the user's JWT token to test the verify-payment endpoint.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test user token 
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTgwMjY0NjkyMDg0NTUwODQ3NTQiLCJlbWFpbCI6ImRvd25zaGlmdHJpZGVzQGdtYWlsLmNvbSIsIm5hbWUiOiJkb3duc2hpZnQgcmlkZXMiLCJpYXQiOjE3NjU2MTUzNzksImV4cCI6MTc2NTYxODk3OX0.2obNee4BzwcbcaqyRuK1X2sO2kJ51-iAFBqHfvr33VE"

headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. Check current subscription
print("1. Current user subscription:")
r = requests.get(f"{BASE_URL}/user/dashboard", headers=headers)
data = r.json()
print(f"   Subscription: {data.get('user', {}).get('subscription')}")
print(f"   has_glm_key: {data.get('has_glm_key')}")

# 2. Test create order
print("\n2. Creating test order for 'pro' plan...")
r = requests.post(f"{BASE_URL}/api/payments/create-order", 
    headers=headers,
    json={"plan_name": "pro", "amount_inr": 299}
)
if r.status_code == 200:
    order_data = r.json()
    print(f"   Order created: {order_data.get('order', {}).get('id')}")
else:
    print(f"   ERROR: {r.status_code} - {r.text}")

# 3. Test verify-payment endpoint with fake data (will fail signature check but shows if endpoint works)
print("\n3. Testing verify-payment endpoint (with fake signature - will fail verification)...")
r = requests.post(f"{BASE_URL}/api/payments/verify-payment",
    headers=headers,
    json={
        "razorpay_order_id": "order_test_123",
        "razorpay_payment_id": "pay_test_456",
        "razorpay_signature": "fake_signature_for_testing",
        "plan_name": "pro"
    }
)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text[:500] if r.text else 'empty'}")

print("\n4. Check if /api/payments/verify-payment route exists...")
# Check routes
r = requests.options(f"{BASE_URL}/api/payments/verify-payment")
print(f"   OPTIONS status: {r.status_code}")

print("\n5. Check available routes for payments...")
r = requests.get(f"{BASE_URL}/openapi.json")
if r.status_code == 200:
    routes = [path for path in r.json().get("paths", {}).keys() if "payment" in path.lower() or "verify" in path.lower()]
    print(f"   Payment routes: {routes}")
