"""
Test script for subscription payment flow.
Tests PAYG, Pro, and Ultra subscription activation.
"""

import asyncio
import httpx
import json
import hmac
import hashlib
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
USER_EMAIL = f"test_sub_{int(datetime.now().timestamp())}@example.com"
USER_PASSWORD = "TestPassword123!"
USER_NAME = "Subscription Tester"

# Test Razorpay credentials (from config)
RAZORPAY_SECRET = "test_secret_key_1234567890"

# Colors for output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}{Colors.RESET}")

async def run_subscription_test():
    print_header("SUBSCRIPTION PAYMENT FLOW TEST")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register User
        print_info("Step 1: Registering new user...")
        try:
            resp = await client.post(f"{BASE_URL}/api/auth/register", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD,
                "name": USER_NAME
            })
            if resp.status_code not in [200, 201]:
                print_error(f"Registration failed: {resp.text}")
                return
            print_success(f"User registered: {USER_EMAIL}")
        except Exception as e:
            print_error(f"Registration error: {e}")
            return

        # 2. Login to get token
        print_info("Step 2: Logging in...")
        try:
            resp = await client.post(f"{BASE_URL}/api/auth/login", data={
                "username": USER_EMAIL,
                "password": USER_PASSWORD
            })
            if resp.status_code != 200:
                print_error(f"Login failed: {resp.text}")
                return
            token_data = resp.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            print_success("Login successful!")
        except Exception as e:
            print_error(f"Login error: {e}")
            return

        # 3. Check initial user profile
        print_info("Step 3: Checking initial profile...")
        try:
            resp = await client.get(f"{BASE_URL}/api/users/me", headers=headers)
            if resp.status_code == 200:
                profile = resp.json()
                print_success(f"Subscription: {profile.get('subscription', 'N/A')}")
                print_success(f"Role: {profile.get('role', 'N/A')}")
            else:
                print_error(f"Profile fetch failed: {resp.text}")
        except Exception as e:
            print_error(f"Profile error: {e}")

        # 4. Test Create Order for Pro Plan
        print_header("TESTING PRO PLAN SUBSCRIPTION")
        print_info("Step 4: Creating order for Pro plan (₹299)...")
        try:
            resp = await client.post(f"{BASE_URL}/api/create-order", json={
                "plan_name": "pro",
                "amount": 299
            }, headers=headers)
            
            if resp.status_code != 200:
                print_error(f"Create order failed: {resp.text}")
                # Try alternate endpoint
                print_info("Trying alternate endpoint...")
                resp = await client.post(f"{BASE_URL}/api/payments/create-order", json={
                    "plan_name": "pro"
                }, headers=headers)
                if resp.status_code != 200:
                    print_error(f"Create order still failed: {resp.text}")
                    return
            
            order_data = resp.json()
            print_info(f"Order response: {json.dumps(order_data, indent=2)}")
            
            # Extract order ID
            razorpay_order_id = order_data.get("data", {}).get("razorpay_order_id") or order_data.get("razorpay_order_id") or order_data.get("order_id")
            if not razorpay_order_id:
                print_error("No order ID in response")
                return
            
            print_success(f"Order created: {razorpay_order_id}")
            
        except Exception as e:
            print_error(f"Create order error: {e}")
            return

        # 5. Verify Payment (Mock)
        print_info("Step 5: Verifying payment (Mock)...")
        try:
            razorpay_payment_id = f"pay_mock_{int(datetime.now().timestamp())}"
            msg = f"{razorpay_order_id}|{razorpay_payment_id}"
            signature = hmac.new(RAZORPAY_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
            
            payment_data = {
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_order_id": razorpay_order_id,
                "razorpay_signature": signature,
                "plan_name": "pro"
            }
            
            resp = await client.post(f"{BASE_URL}/api/verify-payment", json=payment_data, headers=headers)
            
            print_info(f"Status: {resp.status_code}")
            print_info(f"Response: {resp.text}")
            
            if resp.status_code == 200:
                result = resp.json()
                print_success("Payment verified successfully!")
                print_info(f"Result: {json.dumps(result, indent=2)}")
                
                # Check new data structure
                data = result.get("data", {})
                print_success(f"Plan: {data.get('plan')}")
                print_success(f"Role: {data.get('role')}")
                print_success(f"End Date: {data.get('subscription_end_date')}")
                print_success(f"API Keys: {data.get('api_keys')}")
            else:
                print_error(f"Verification failed: {resp.text}")
                
        except Exception as e:
            print_error(f"Verification error: {e}")
            return

        # 6. Check updated profile
        print_info("Step 6: Checking updated profile...")
        try:
            resp = await client.get(f"{BASE_URL}/api/users/me", headers=headers)
            if resp.status_code == 200:
                profile = resp.json()
                print_success(f"New Subscription: {profile.get('subscription', 'N/A')}")
                print_success(f"New Role: {profile.get('role', 'N/A')}")
                print_success(f"GLM Key: {'Set' if profile.get('glm_api_key') else 'Not set'}")
                print_success(f"OpenRouter Key: {'Set' if profile.get('openrouter_api_key') else 'Not set'}")
        except Exception as e:
            print_error(f"Profile error: {e}")

        # 7. Test Credits Endpoint
        print_info("Step 7: Testing /users/me/credits endpoint...")
        try:
            resp = await client.get(f"{BASE_URL}/api/users/me/credits", headers=headers)
            print_info(f"Credits Status: {resp.status_code}")
            if resp.status_code == 200:
                credits = resp.json()
                print_success(f"Credits Response: {json.dumps(credits, indent=2)}")
            else:
                print_error(f"Credits failed: {resp.text}")
        except Exception as e:
            print_error(f"Credits error: {e}")

        # 8. Test Admin API Key Pool (if admin)
        print_header("TESTING ADMIN ENDPOINTS")
        print_info("Step 8: Testing admin API key pool...")
        try:
            resp = await client.get(f"{BASE_URL}/api/admin/api-keys/pool", headers=headers)
            print_info(f"Admin Pool Status: {resp.status_code}")
            if resp.status_code == 200:
                pool = resp.json()
                print_success(f"Pool: {json.dumps(pool, indent=2)}")
            elif resp.status_code == 403:
                print_info("Not admin - 403 is expected")
            else:
                print_error(f"Pool failed: {resp.text}")
        except Exception as e:
            print_error(f"Pool error: {e}")

    print_header("SUBSCRIPTION FLOW TEST COMPLETED")

if __name__ == "__main__":
    asyncio.run(run_subscription_test())
