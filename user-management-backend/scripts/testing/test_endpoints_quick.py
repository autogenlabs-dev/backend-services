"""
Basic endpoint test script.
Run this to verify all new endpoints are working.
"""
import requests
import json

BASE_URL = "http://localhost:8000"
# Set your auth token here for authenticated endpoints
AUTH_TOKEN = ""  # User will provide if needed

def test_endpoint(name, method, url, headers=None, json_data=None):
    """Test a single endpoint and print results."""
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*50}")
    
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=json_data, timeout=10)
        
        print(f"Status: {r.status_code}")
        
        # Interpret status
        if r.status_code == 200:
            print("Result: SUCCESS ✅")
        elif r.status_code == 401:
            print("Result: AUTH REQUIRED (expected) ✅")
        elif r.status_code == 403:
            print("Result: FORBIDDEN (need admin) ✅")
        elif r.status_code == 404:
            print("Result: NOT FOUND ❌ (route not loaded)")
        elif r.status_code == 405:
            print("Result: METHOD NOT ALLOWED (expected for POST-only) ✅")
        else:
            print(f"Result: {r.status_code}")
        
        # Show response body (truncated)
        try:
            body = r.json()
            print(f"Response: {json.dumps(body, indent=2)[:300]}")
        except:
            print(f"Response: {r.text[:200]}")
            
        return r.status_code
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("CODEMURF PAYMENT SYSTEM - ENDPOINT VERIFICATION")
    print("="*60)
    
    headers = {}
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    
    results = {}
    
    # 1. Health check
    results["health"] = test_endpoint(
        "Health Check",
        "GET",
        f"{BASE_URL}/health"
    )
    
    # 2. Admin API Key Pool (should be 401/403, NOT 404)
    results["admin_pool"] = test_endpoint(
        "Admin API Key Pool",
        "GET",
        f"{BASE_URL}/api/admin/api-keys/pool",
        headers=headers if AUTH_TOKEN else None
    )
    
    # 3. Admin Pool Stats
    results["admin_stats"] = test_endpoint(
        "Admin Pool Stats",
        "GET",
        f"{BASE_URL}/api/admin/api-keys/pool/stats",
        headers=headers if AUTH_TOKEN else None
    )
    
    # 4. User Credits Endpoint
    results["credits"] = test_endpoint(
        "User Credits",
        "GET",
        f"{BASE_URL}/api/users/me/credits",
        headers=headers if AUTH_TOKEN else None
    )
    
    # 5. Webhook Endpoint (POST-only, so GET = 405)
    results["webhook_get"] = test_endpoint(
        "Webhook (GET - expect 405)",
        "GET",
        f"{BASE_URL}/webhooks/razorpay"
    )
    
    # 6. Webhook POST test
    results["webhook_post"] = test_endpoint(
        "Webhook (POST)",
        "POST",
        f"{BASE_URL}/webhooks/razorpay",
        json_data={"event": "test"}
    )
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    new_endpoints_ok = True
    for name, status in results.items():
        if status == 404:
            print(f"❌ {name}: NOT FOUND - Routes not loaded!")
            new_endpoints_ok = False
        elif status in [200, 401, 403, 405]:
            print(f"✅ {name}: OK (status {status})")
        else:
            print(f"⚠️ {name}: status {status}")
    
    print("\n" + "="*60)
    if new_endpoints_ok:
        print("✅ ALL NEW ENDPOINTS ARE REGISTERED!")
    else:
        print("❌ SOME ENDPOINTS RETURN 404 - Docker rebuild needed")
    print("="*60)

if __name__ == "__main__":
    main()
