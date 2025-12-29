import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"order_test_{int(datetime.now().timestamp())}@test.com"
TEST_PASSWORD = "TestPass123!"

def log(msg):
    print(f"ℹ️ {msg}")

def main():
    # 1. Register
    log("Registering...")
    r = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Order Tester"
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
    
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    main()
