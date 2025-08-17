#!/usr/bin/env python3

import requests
import json

# Test template comment update
def test_template_comment_update():
    template_id = "6898d5559e068f63839d55aa"
    comment_id = "689fb5714edc5d6288cdfafc"  # From the URL in browser
    
    url = f"http://localhost:8000/templates/{template_id}/comments/{comment_id}"
    data = {
        "content": "Updated comment content"
    }
    
    print(f"Testing PUT endpoint: {url}")
    print(f"Data: {data}")
    
    try:
        response = requests.put(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Response data:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("❌ ERROR Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")

if __name__ == "__main__":
    test_template_comment_update()
