import requests
import json
import hmac
import hashlib
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"verify_test_{int(datetime.now().timestamp())}@test.com"
TEST_PASSWORD = "TestPass123!"
RAZORPAY_SECRET = "5DLMyLZXEPtQkCjEK139XJm3"

def log(msg):
    print(f"ℹ️ {msg}")

def main():
    # 1. Register
    log("Registering...")
    r = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Verify Tester"
    })
    if r.status_code not in [200, 201]:
        print(f"❌ Register failed: {r.text}")
        return

    # 2. Login
    log("Logging in...")
    r = requests.post(f"{BASE_URL}/api/auth/login", data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if r.status_code != 200:
        print(f"❌ Login failed: {r.text}")
        return
    
    token = r.json().get("access_token")
    
    # 3. Create Order
    log("Creating order...")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{BASE_URL}/api/payments/create-order", json={
        "plan_name": "pro",
        "amount": 299
    }, headers=headers)
    
    if r.status_code != 200:
        print(f"❌ Create order failed: {r.text}")
        return

    data = r.json()
    order_data = data.get("order", {}) or data.get("data", {})
    order_id = order_data.get("order_id") or order_data.get("razorpay_order_id")
    
    print(f"Order ID: {order_id}")
    
    # 4. Verify Payment
    log("Verifying payment...")
    payment_id = f"pay_test_{int(datetime.now().timestamp())}"
    msg = f"{order_id}|{payment_id}"
    signature = hmac.new(RAZORPAY_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
    
    verify_payload = {
        "razorpay_order_id": order_id,
        "razorpay_payment_id": payment_id,
        "razorpay_signature": signature,
        "plan_name": "pro"
    }
    
    print(f"Payload: {json.dumps(verify_payload, indent=2)}")
    
    r = requests.post(f"{BASE_URL}/api/payments/verify-payment", json=verify_payload, headers=headers)
    
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    main()
