#!/usr/bin/env python3

import requests
import json

def test_get_template_comments():
    """Test getting template comments"""
    template_id = "689bd2f5a5e07fc09b45c40b"  # Use the template ID from browser
    url = f"http://localhost:8000/templates/{template_id}/comments"
    
    print(f"Testing GET endpoint: {url}")
    
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
        print(f"❌ REQUEST FAILED: {e}")

if __name__ == "__main__":
    test_get_template_comments()
