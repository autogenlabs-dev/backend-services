#!/usr/8:STRIPE_SECRET_KEY = "sk_test_your_stripe_secret_key"in/env python3
"""
Simple Stripe key validation test
"""
import stripe

# Your new Stripe keys
STRIPE_SECRET_KEY = "sk_test_51RVi9b00tZAh2watNguPPSVIAwj7mll7RsiqeXfWIvR6JbwsO1vW2j4KWFlh8Tgkpozue2zq993aKn59wCRLZK5O00sbBOVXzr"
STRIPE_PUBLISHABLE_KEY = "pk_test_51RVi9b00tZAh2watbNFlPjw4jKS02yZbKHQ1t97GcyMTOGLwcL8QhzxDSGtGuuEAJP4DHcEWOkut5N0CCTnuqBgh00p44dvGCb"

print("🔧 TESTING NEW STRIPE KEYS")
print("=" * 40)

# Configure Stripe
stripe.api_key = STRIPE_SECRET_KEY

try:
    # Test basic connection
    account = stripe.Account.retrieve()
    print(f"✅ Stripe connection successful!")
    print(f"   Account ID: {account.id}")
    print(f"   Country: {account.country}")
    print(f"   Test mode: {not account.livemode}")
    
    # Create a test customer
    customer = stripe.Customer.create(
        email="test@example.com",
        name="Test User"
    )
    print(f"✅ Customer creation successful!")
    print(f"   Customer ID: {customer.id}")
    
    # Create a test product
    product = stripe.Product.create(
        name="Test Product",
        description="Test subscription product"
    )
    print(f"✅ Product creation successful!")
    print(f"   Product ID: {product.id}")
    
    # Create a test price
    price = stripe.Price.create(
        product=product.id,
        unit_amount=2999,  # $29.99
        currency="usd",
        recurring={"interval": "month"}
    )
    print(f"✅ Price creation successful!")
    print(f"   Price ID: {price.id}")
    print(f"   Amount: ${price.unit_amount/100}")
    
    print("\n🎉 ALL STRIPE TESTS PASSED!")
    print("Your Stripe keys are working correctly!")
    
except Exception as e:
    print(f"❌ Stripe test failed: {str(e)}")
    print("Please check your Stripe keys.")

print("\n📋 KEYS USED:")
print(f"Secret Key: {STRIPE_SECRET_KEY[:20]}...")
print(f"Publishable Key: {STRIPE_PUBLISHABLE_KEY[:20]}...")
