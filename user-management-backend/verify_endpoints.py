import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(path):
    print(f"Testing {path}...")
    try:
        r = requests.post(f"{BASE_URL}{path}", json={"plan_name": "pro", "amount": 299})
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

test_endpoint("/api/create-order")
test_endpoint("/api/payments/create-order")
