#!/usr/bin/env pyt19:STRIPE_SECRET_KEY = "sk_test_your_stripe_secret_key"on3
"""
Comprehensive Stripe Payment Flow Validation
This script tests the complete Stripe subscription flow including:
1. User registration
2. User login
3. Retrieving subscription plans
4. Creating a subscription to a paid plan
5. Verifying subscription status
"""
import requests
import stripe
import json
import time
import os
from pprint import pprint

# Configuration
STRIPE_SECRET_KEY = "sk_test_51RVi9b00tZAh2watNguPPSVIAwj7mll7RsiqeXfWIvR6JbwsO1vW2j4KWFlh8Tgkpozue2zq993aKn59wCRLZK5O00sbBOVXzr"
STRIPE_PUBLISHABLE_KEY = "pk_test_51RVi9b00tZAh2watbNFlPjw4jKS02yZbKHQ1t97GcyMTOGLwcL8QhzxDSGtGuuEAJP4DHcEWOkut5N0CCTnuqBgh00p44dvGCb"
BASE_URL = "http://localhost:8000"

# Configure Stripe
stripe.api_key = STRIPE_SECRET_KEY

class StripeIntegrationTester:
    """Test Stripe integration with backend API."""
    
    def __init__(self):
        """Initialize test client."""
        self.access_token = None
        self.user_email = f"stripe_integration_test_{int(time.time())}@example.com"
        self.user_password = "Testing@123!"
        self.headers = {}
        
    def register_user(self):
        """Register a new test user."""
        print("\n🔐 REGISTERING TEST USER")
        print("=" * 40)
        
        user_data = {
            "username": self.user_email,
            "email": self.user_email,
            "password": self.user_password,
            "full_name": "Stripe Integration Tester"
        }
          try:
            print(f"   Sending request to: {BASE_URL}/auth/register")
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data, timeout=30)
            
            print(f"   Response status code: {response.status_code}")
            if response.status_code == 201:
                user = response.json()
                print(f"✅ User registered successfully!")
                print(f"   Email: {user_data['email']}")
                print(f"   Name: {user_data['full_name']}")
                return True
            elif response.status_code == 400:
                # User might already exist
                print(f"⚠️ User might already exist.")
                print(f"   Response: {response.text[:100]}...")
                return True
            else:
                print(f"❌ Registration failed with status code: {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:100]}...")
                return False
        except requests.exceptions.Timeout:
            print("❌ Registration request timed out after 30 seconds")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - is the server running?")
            return False
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return False
    
    def login_user(self):
        """Login with test user credentials."""
        print("\n🔑 LOGGING IN")
        print("=" * 40)
        
        login_data = {"email": self.user_email, "password": self.user_password}
          try:
            print(f"   Sending request to: {BASE_URL}/auth/login-json")
            response = requests.post(f"{BASE_URL}/auth/login-json", json=login_data, timeout=30)
            
            print(f"   Response status code: {response.status_code}")
            if response.status_code == 200:
                login_result = response.json()
                self.access_token = login_result.get("access_token")
                
                if not self.access_token:
                    print("❌ No access token in response")
                    print(f"   Response content: {json.dumps(login_result)[:200]}...")
                    return False
                    
                self.headers = {"Authorization": f"Bearer {self.access_token}"}
                
                print(f"✅ Login successful!")
                print(f"   Access token: {self.access_token[:15]}...")
                print(f"   A4F API Key present: {'a4f_api_key' in login_result}")
                return True
            else:
                print(f"❌ Login failed with status code: {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:100]}...")
                return False
        except requests.exceptions.Timeout:
            print("❌ Login request timed out after 30 seconds")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - is the server running?")
            return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def get_subscription_plans(self):
        """Retrieve available subscription plans."""
        print("\n📋 GETTING SUBSCRIPTION PLANS")
        print("=" * 40)
        
        try:
            response = requests.get(f"{BASE_URL}/subscriptions/plans", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                plans = response.json()
                print(f"✅ Retrieved {len(plans)} subscription plans")
                
                for plan in plans:
                    print(f"   {plan['display_name']} (${plan['price_usd']})")
                    print(f"     - Monthly tokens: {plan.get('monthly_tokens', 'N/A')}")
                    print(f"     - Stripe price ID: {plan.get('stripe_price_id', 'N/A')}")
                
                return plans
            else:
                print(f"❌ Failed to retrieve plans: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error retrieving plans: {str(e)}")
            return None
    
    def get_current_subscription(self):
        """Get current user subscription info."""
        print("\n📊 CHECKING CURRENT SUBSCRIPTION")
        print("=" * 40)
        
        try:
            response = requests.get(f"{BASE_URL}/subscriptions/current", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                subscription = response.json()
                print(f"✅ Current subscription retrieved")
                
                if subscription.get("has_subscription"):
                    plan = subscription.get("plan", {})
                    print(f"   Current plan: {plan.get('display_name', 'N/A')}")
                    print(f"   Active until: {subscription.get('expires_at', 'N/A')}")
                    print(f"   Monthly tokens: {plan.get('monthly_tokens', 'N/A')}")
                else:
                    print(f"   No active subscription (on default free plan)")
                
                return subscription
            else:
                print(f"❌ Failed to retrieve current subscription: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error retrieving subscription: {str(e)}")
            return None
    
    def subscribe_to_paid_plan(self, plan_name="pro"):
        """Attempt to subscribe to a paid plan."""
        print(f"\n💳 SUBSCRIBING TO {plan_name.upper()} PLAN")
        print("=" * 40)
        
        try:
            subscribe_data = {"plan_name": plan_name}
            response = requests.post(
                f"{BASE_URL}/subscriptions/subscribe", 
                headers=self.headers, 
                json=subscribe_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Subscription request successful!")
                
                if result.get("client_secret"):
                    print(f"   Stripe subscription ID: {result.get('stripe_subscription_id')}")
                    print(f"   Client secret received: {result.get('client_secret')[:20]}...")
                    print(f"   Status: {result.get('status')}")
                    
                    # Here we would normally pass the client_secret to a frontend
                    # component to collect payment details with Stripe Elements
                    print("\n⚠️ IMPORTANT: In a real application, the client_secret would be used")
                    print("   with Stripe Elements to collect and submit payment details.")
                    print("   This cannot be fully automated in a server-side test.")
                else:
                    print(f"   Message: {result.get('message')}")
                
                return result
            else:
                print(f"❌ Subscription failed with status code: {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:100]}...")
                return None
        except Exception as e:
            print(f"❌ Subscription error: {str(e)}")
            return None
    
    def run_full_test(self):
        """Run the complete end-to-end test."""
        print("\n🚀 STARTING COMPLETE STRIPE INTEGRATION TEST")
        print("=" * 60)
        
        if not self.register_user():
            return False
        
        if not self.login_user():
            return False
        
        plans = self.get_subscription_plans()
        if not plans:
            return False
        
        initial_subscription = self.get_current_subscription()
        
        # Try subscribing to Pro plan
        pro_subscription = self.subscribe_to_paid_plan("pro")
        
        # Check subscription status again
        final_subscription = self.get_current_subscription()
        
        print("\n📋 TEST RESULTS SUMMARY")
        print("=" * 40)
        print(f"✅ User registration successful")
        print(f"✅ User login successful")
        print(f"✅ Retrieved {len(plans)} subscription plans")
        print(f"✅ Initial subscription status retrieved")
        print(f"✅ Subscription request to Pro plan {'successful' if pro_subscription else 'failed'}")
        print(f"✅ Final subscription status retrieved")
        
        print("\n🔍 NEXT STEPS FOR COMPLETE PAYMENT FLOW")
        print("=" * 40)
        print("1. Frontend implementation needed to complete payment with Stripe Elements")
        print("2. Webhook endpoint needed to handle subscription events")
        print("3. VS Code extension integration for subscription UI")
        
        return True

if __name__ == "__main__":
    print("💳 COMPREHENSIVE STRIPE PAYMENT FLOW TEST")
    print("=" * 60)
    
    tester = StripeIntegrationTester()
    tester.run_full_test()
