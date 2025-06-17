#!/usr/bin/env python3
"""
Simple Stripe Payment Flow Test
"""
import requests
import json

# Test the server's health check endpoint
print("\n🏥 TESTING SERVER HEALTH")
print("=" * 40)

try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        health_data = response.json()
        print(f"✅ Server is healthy: {health_data}")
    else:
        print(f"❌ Server health check failed: {response.status_code}")
except Exception as e:
    print(f"❌ Server connection error: {str(e)}")

# Test user registration
print("\n👤 TESTING USER REGISTRATION")
print("=" * 40)

user_data = {
    "username": "stripe_test_user@example.com",
    "email": "stripe_test_user@example.com",
    "password": "StripeTesting123!",
    "full_name": "Stripe Test User"
}

try:
    response = requests.post("http://localhost:8000/auth/register", json=user_data, timeout=5)
    print(f"Response status: {response.status_code}")
    if response.status_code in [201, 400]:  # 400 if user already exists
        print(f"✅ Registration endpoint working")
        print(f"   Response: {response.text[:100]}...")
    else:
        print(f"❌ Registration endpoint error: {response.status_code}")
except Exception as e:
    print(f"❌ Registration request error: {str(e)}")

# Test login
print("\n🔑 TESTING LOGIN")
print("=" * 40)

login_data = {
    "email": "stripe_test_user@example.com",
    "password": "StripeTesting123!"
}

access_token = None
try:
    response = requests.post("http://localhost:8000/auth/login-json", json=login_data, timeout=5)
    print(f"Login response status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        access_token = result.get("access_token")
        print(f"✅ Login successful")
        print(f"   Access token: {access_token[:15] if access_token else 'None'}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
except Exception as e:
    print(f"❌ Login request error: {str(e)}")

# Test subscription plans endpoint
if access_token:
    print("\n📋 TESTING SUBSCRIPTION PLANS")
    print("=" * 40)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get("http://localhost:8000/subscriptions/plans", headers=headers, timeout=5)
        if response.status_code == 200:
            plans = response.json()
            print(f"✅ Retrieved {len(plans)} subscription plans")
            for plan in plans:
                print(f"   {plan['name']}: ${plan['price_usd']} ({plan.get('stripe_price_id', 'No price ID')})")
        else:
            print(f"❌ Failed to retrieve plans: {response.status_code}")
    except Exception as e:
        print(f"❌ Plans request error: {str(e)}")
    
    # Test current subscription
    print("\n📊 TESTING CURRENT SUBSCRIPTION")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/subscriptions/current", headers=headers, timeout=5)
        if response.status_code == 200:
            subscription = response.json()
            print(f"✅ Current subscription endpoint working")
            print(f"   Subscription data: {json.dumps(subscription)[:100]}...")
        else:
            print(f"❌ Failed to get current subscription: {response.status_code}")
    except Exception as e:
        print(f"❌ Current subscription request error: {str(e)}")
    
    # Test subscribing to free plan
    print("\n🆓 TESTING FREE PLAN SUBSCRIPTION")
    print("=" * 40)
    
    try:
        data = {"plan_name": "free"}
        response = requests.post(
            "http://localhost:8000/subscriptions/subscribe",
            headers=headers,
            json=data,
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Free plan subscription successful")
            print(f"   Response: {json.dumps(result)[:100]}...")
        else:
            print(f"❌ Free plan subscription failed: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Free subscription request error: {str(e)}")
    
    # Test subscribing to pro plan (payment required)
    print("\n💳 TESTING PRO PLAN SUBSCRIPTION (STRIPE)")
    print("=" * 40)
    
    try:
        data = {"plan_name": "pro"}
        response = requests.post(
            "http://localhost:8000/subscriptions/subscribe",
            headers=headers,
            json=data,
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Pro plan subscription initiated")
            if "client_secret" in result:
                print(f"   Stripe client secret received: {result['client_secret'][:20]}...")
                print(f"   Stripe subscription ID: {result.get('stripe_subscription_id')}")
            else:
                print(f"   Result: {json.dumps(result)[:100]}...")
        else:
            print(f"❌ Pro plan subscription failed: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Pro subscription request error: {str(e)}")

print("\n✅ TEST COMPLETED")
print("=" * 40)
