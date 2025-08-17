import requests
import json

# Test template comment creation
url = "http://localhost:8000/templates/6898d5559e068f63839d55aa/comments"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODhkMzZkN2Q4Nzc4Y2I3ZjMxNjgwMTEiLCJlbWFpbCI6InVzZXIyQGV4YW1wbGUuY29tIiwidXNlcm5hbWUiOiJhdXRvZ2VuX3VzZXJfMiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzQ1MDA5MzMzfQ.ik5pPYZmD6k-K4_U08M9BDQq_SDqP3qYeQR5zj3-_Sk"  # You may need to update this token
}

data = {
    "content": "This is a test comment",
    "rating": 5
}

print(f"Testing endpoint: {url}")
print(f"Headers: {headers}")
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
