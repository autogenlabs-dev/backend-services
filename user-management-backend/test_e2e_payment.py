"""
End-to-End Payment System Test
Tests the complete flow: Health -> Register -> Login -> Create Order -> Verify Payment
"""
import requests
import json
import hmac
import hashlib
from datetime import datetime

BASE_URL = "http://localhost:8000"
RAZORPAY_SECRET = "f6dpsDsOyxnl25UsTudmow1N"  # Test secret

# Unique test user
TEST_EMAIL = f"e2e_test_{int(datetime.now().timestamp())}@test.com"
TEST_PASSWORD = "TestPass123!"

def log(msg, level="INFO"):
    symbols = {"INFO": "ℹ️", "OK": "✅", "FAIL": "❌", "WARN": "⚠️"}
    print(f"{symbols.get(level, 'ℹ️')} {msg}")

def test_health():
    """Test 1: Health check"""
    log("Testing health endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=10)
        if r.status_code == 200:
            log("Server is healthy", "OK")
            return True
        log(f"Health failed: {r.status_code}", "FAIL")
        return False
    except Exception as e:
        log(f"Server not reachable: {e}", "FAIL")
        return False

def test_register():
    """Test 2: Register user"""
    log("Registering test user...")
    try:
        r = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": "E2E Tester"
        }, timeout=10)
        if r.status_code in [200, 201]:
            log(f"User registered: {TEST_EMAIL}", "OK")
            return True
        log(f"Registration failed: {r.status_code} - {r.text[:100]}", "FAIL")
        return False
    except Exception as e:
        log(f"Registration error: {e}", "FAIL")
        return False

def test_login():
    """Test 3: Login and get token"""
    log("Logging in...")
    try:
        r = requests.post(f"{BASE_URL}/api/auth/login", data={
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD
        }, timeout=10)
        if r.status_code == 200:
            token = r.json().get("access_token")
            log("Login successful", "OK")
            return token
        log(f"Login failed: {r.status_code}", "FAIL")
        return None
    except Exception as e:
        log(f"Login error: {e}", "FAIL")
        return None

def test_create_order(token):
    """Test 4: Create payment order"""
    log("Creating payment order for Pro plan...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.post(f"{BASE_URL}/api/create-order", json={
            "plan_name": "pro",
            "amount": 299
        }, headers=headers, timeout=15)
        
        if r.status_code == 200:
            data = r.json()
            order_id = data.get("data", {}).get("razorpay_order_id") or data.get("razorpay_order_id") or data.get("order_id")
            key_id = data.get("data", {}).get("key_id") or data.get("key_id")
            
            if order_id:
                log(f"Order created: {order_id}", "OK")
                log(f"Razorpay Key: {key_id}", "INFO")
                
                # Check if using test key
                if key_id and key_id.startswith("rzp_test"):
                    log("Using TEST mode ✓", "OK")
                elif key_id and key_id.startswith("rzp_live"):
                    log("WARNING: Using LIVE mode!", "WARN")
                
                return order_id
            
        log(f"Create order failed: {r.status_code} - {r.text[:200]}", "FAIL")
        return None
    except Exception as e:
        log(f"Create order error: {e}", "FAIL")
        return None

def test_verify_payment(token, order_id):
    """Test 5: Verify payment (mock)"""
    log("Verifying payment (mock signature)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    payment_id = f"pay_test_{int(datetime.now().timestamp())}"
    msg = f"{order_id}|{payment_id}"
    signature = hmac.new(RAZORPAY_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
    
    try:
        r = requests.post(f"{BASE_URL}/api/verify-payment", json={
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
            "plan_name": "pro"
        }, headers=headers, timeout=15)
        
        log(f"Verify response: {r.status_code}", "INFO")
        
        if r.status_code == 200:
            data = r.json()
            log("Payment verified!", "OK")
            log(f"Response: {json.dumps(data, indent=2)[:500]}", "INFO")
            return data
        else:
            log(f"Verify failed: {r.text[:300]}", "FAIL")
            return None
    except Exception as e:
        log(f"Verify error: {e}", "FAIL")
        return None

def test_user_profile(token):
    """Test 6: Check user profile after payment"""
    log("Checking user profile...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{BASE_URL}/api/users/me", headers=headers, timeout=10)
        if r.status_code == 200:
            profile = r.json()
            log(f"Subscription: {profile.get('subscription', 'N/A')}", "OK")
            log(f"OpenRouter Key: {'Set' if profile.get('openrouter_api_key') else 'Not set'}", "INFO")
            return profile
        log(f"Profile failed: {r.status_code}", "FAIL")
        return None
    except Exception as e:
        log(f"Profile error: {e}", "FAIL")
        return None

def test_credits_endpoint(token):
    """Test 7: Check credits endpoint"""
    log("Testing credits endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{BASE_URL}/api/users/me/credits", headers=headers, timeout=10)
        log(f"Credits status: {r.status_code}", "INFO")
        if r.status_code == 200:
            log(f"Credits: {r.json()}", "OK")
            return True
        return r.status_code != 404  # 401 is expected, 404 means route not loaded
    except Exception as e:
        log(f"Credits error: {e}", "FAIL")
        return False

def test_admin_endpoints():
    """Test 8: Check admin endpoints are registered"""
    log("Testing admin endpoints (expect 401)...")
    try:
        r = requests.get(f"{BASE_URL}/api/admin/api-keys/pool", timeout=10)
        if r.status_code == 401 or r.status_code == 403:
            log("Admin pool endpoint registered (auth required)", "OK")
            return True
        elif r.status_code == 404:
            log("Admin endpoint NOT FOUND - routes not loaded!", "FAIL")
            return False
        else:
            log(f"Admin endpoint: {r.status_code}", "INFO")
            return True
    except Exception as e:
        log(f"Admin error: {e}", "FAIL")
        return False

def test_webhook_endpoint():
    """Test 9: Check webhook endpoint"""
    log("Testing webhook endpoint...")
    try:
        r = requests.post(f"{BASE_URL}/webhooks/razorpay", json={"event": "test"}, timeout=10)
        if r.status_code != 404:
            log(f"Webhook endpoint registered: {r.status_code}", "OK")
            return True
        log("Webhook endpoint NOT FOUND!", "FAIL")
        return False
    except Exception as e:
        log(f"Webhook error: {e}", "FAIL")
        return False

def main():
    print("\n" + "="*60)
    print("🚀 END-TO-END PAYMENT SYSTEM TEST")
    print("="*60 + "\n")
    
    results = {}
    
    # Test 1: Health
    results["health"] = test_health()
    if not results["health"]:
        print("\n❌ Server not running. Aborting tests.")
        return
    
    # Test 2: Register
    results["register"] = test_register()
    
    # Test 3: Login
    token = test_login()
    results["login"] = token is not None
    
    if not token:
        print("\n❌ Cannot continue without auth token.")
        return
    
    # Test 4: Create Order
    order_id = test_create_order(token)
    results["create_order"] = order_id is not None
    
    # Test 5: Verify Payment (if order created)
    if order_id:
        verify_result = test_verify_payment(token, order_id)
        results["verify_payment"] = verify_result is not None
    else:
        results["verify_payment"] = False
    
    # Test 6: Check Profile
    test_user_profile(token)
    
    # Test 7: Credits Endpoint
    results["credits"] = test_credits_endpoint(token)
    
    # Test 8: Admin Endpoints
    results["admin"] = test_admin_endpoints()
    
    # Test 9: Webhook
    results["webhook"] = test_webhook_endpoint()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, passed_test in results.items():
        symbol = "✅" if passed_test else "❌"
        print(f"  {symbol} {name}")
    
    print(f"\n  Result: {passed}/{total} tests passed")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
