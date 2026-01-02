
import requests
import sys
import time

BASE_URL = "http://localhost:8000"
EMAIL = f"test_user_{int(time.time())}@example.com"
PASSWORD = "TestPassword123!"

def print_result(name, success, message=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {name}")
    if message:
        print(f"   {message}")
    if not success:
        sys.exit(1)

def wait_for_backend():
    print("Waiting for backend to be ready...")
    for _ in range(30):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("Backend is ready!")
                return
        except requests.ConnectionError:
            pass
        time.sleep(1)
    print_result("Backend Health", False, "Backend did not start in time")

def test_registration():
    print(f"\n1. Registering user: {EMAIL}")
    payload = {
        "email": EMAIL,
        "password": PASSWORD,
        "name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
    
    if response.status_code == 200:
        print_result("Registration", True, f"User ID: {response.json().get('id')}")
    else:
        print_result("Registration", False, f"Status: {response.status_code}, Body: {response.text}")

def test_login_and_rehash():
    print("\n2. Logging in (should use bcrypt)")
    payload = {
        "username": EMAIL,
        "password": PASSWORD
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", data=payload)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print_result("Login", True, "Got access token")
        return token
    else:
        print_result("Login", False, f"Status: {response.status_code}, Body: {response.text}")

def test_token_validation(token):
    print("\n3. Verifying token")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        print_result("Token Validation", True, f"Authenticated as: {user.get('email')}")
    else:
        print_result("Token Validation", False, f"Status: {response.status_code}, Body: {response.text}")

if __name__ == "__main__":
    try:
        wait_for_backend()
        test_registration()
        token = test_login_and_rehash()
        test_token_validation(token)
        print("\n✨ All auth tests passed!")
    except Exception as e:
        print_result("Test Execution", False, str(e))
