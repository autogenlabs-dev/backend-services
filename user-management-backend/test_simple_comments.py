import requests
import json

# Test the simplified GET comments endpoint
url = "http://localhost:8000/components/6898e97ba4f90603e5afe1e9/comments"
print(f"Testing endpoint: {url}")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Response data:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ ERROR Response: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")
