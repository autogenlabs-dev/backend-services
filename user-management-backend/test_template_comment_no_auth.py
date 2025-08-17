import requests
import json

# Test template comment creation without auth
url = "http://localhost:8000/templates/6898d5559e068f63839d55aa/comments"
headers = {
    "Content-Type": "application/json"
}

data = {
    "content": "This is a test comment for templates",
    "rating": 4
}

print(f"Testing endpoint: {url}")
print(f"Data: {data}")

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 422:
        print("❌ Validation Error:")
        print(json.dumps(response.json(), indent=2))
    elif response.status_code == 200 or response.status_code == 201:
        print("✅ SUCCESS! Response data:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ ERROR Response: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")
