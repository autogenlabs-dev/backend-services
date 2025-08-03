import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_all_templates():
    print("Testing GET /templates")
    response = requests.get(f"{BASE_URL}/templates")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_get_all_templates()
