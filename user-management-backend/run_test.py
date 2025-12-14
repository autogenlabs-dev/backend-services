"""
Basic endpoint test - writes results to file.
"""
import requests
import json

BASE_URL = "http://localhost:8000"
OUTPUT_FILE = "test_results_output.txt"

def log(msg):
    """Print and log to file."""
    print(msg)
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def test_endpoint(name, method, url, json_data=None):
    """Test endpoint and return status."""
    log(f"\n{'='*50}")
    log(f"Testing: {name}")
    log(f"URL: {url}")
    
    try:
        if method == "GET":
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, json=json_data, timeout=10)
        
        log(f"Status: {r.status_code}")
        
        if r.status_code == 404:
            log("Result: NOT FOUND - route not loaded!")
        elif r.status_code in [200, 401, 403, 405]:
            log(f"Result: OK")
        
        try:
            log(f"Body: {r.text[:150]}")
        except:
            pass
            
        return r.status_code
    except Exception as e:
        log(f"Error: {e}")
        return None

# Clear output file
with open(OUTPUT_FILE, "w") as f:
    f.write("ENDPOINT TEST RESULTS\n")
    f.write("="*50 + "\n")

results = {}
results["health"] = test_endpoint("Health", "GET", f"{BASE_URL}/health")
results["admin_pool"] = test_endpoint("Admin Pool", "GET", f"{BASE_URL}/api/admin/api-keys/pool")
results["admin_stats"] = test_endpoint("Admin Stats", "GET", f"{BASE_URL}/api/admin/api-keys/pool/stats")
results["credits"] = test_endpoint("Credits", "GET", f"{BASE_URL}/api/users/me/credits")
results["webhook"] = test_endpoint("Webhook POST", "POST", f"{BASE_URL}/webhooks/razorpay", {"event": "test"})

log("\n" + "="*50)
log("SUMMARY")
log("="*50)
has_404 = any(s == 404 for s in results.values())
if has_404:
    log("SOME ENDPOINTS RETURN 404 - Docker rebuild needed")
else:
    log("ALL ENDPOINTS REGISTERED!")

for name, status in results.items():
    symbol = "X" if status == 404 else "OK"
    log(f"[{symbol}] {name}: {status}")

log("\nDone. Results saved to " + OUTPUT_FILE)
