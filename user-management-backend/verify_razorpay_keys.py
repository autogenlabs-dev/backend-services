import requests
from requests.auth import HTTPBasicAuth

KEY_ID = "rzp_test_Rqxl4tVNxYqSuO"
KEY_SECRET = "f6dpsDsOyxnl25UsTudmow1N"

def verify_keys():
    print(f"Verifying keys: {KEY_ID} / {KEY_SECRET[:4]}...")
    try:
        # Try to fetch payments (standard endpoint to check auth)
        response = requests.get(
            "https://api.razorpay.com/v1/payments",
            auth=HTTPBasicAuth(KEY_ID, KEY_SECRET),
            params={"count": 1}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Auth Successful!")
            print(f"Response: {response.json()}")
        elif response.status_code == 401:
            print("❌ Auth Failed: Invalid Key or Secret")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    verify_keys()
