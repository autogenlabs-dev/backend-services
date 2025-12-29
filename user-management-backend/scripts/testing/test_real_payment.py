"""
Real Razorpay Payment Test with User Token
Tests the payment flow with the user's actual token.
"""
import requests
import json
import webbrowser

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTE3MTQ0MjYyMjMzNDM2NjQ2NzIiLCJlbWFpbCI6ImF1dG9nZW5jb2RlbGFic0BnbWFpbC5jb20iLCJuYW1lIjoiQWJoaXNoZWsiLCJpYXQiOjE3NjYxNzE0NjYsImV4cCI6MTc2NjE3NTA2Nn0.nYoGE25Bos-9_GaQQpoSNZJqaVEIitZ9P8wvj8woz6g"

def log(msg, level="INFO"):
    symbols = {"INFO": "ℹ️", "OK": "✅", "FAIL": "❌", "WARN": "⚠️"}
    print(f"{symbols.get(level, 'ℹ️')} {msg}")

def main():
    print("\n" + "="*60)
    print("🚀 REAL RAZORPAY PAYMENT TEST")
    print("="*60 + "\n")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # 1. Test user profile first
    log("Checking user profile...")
    r = requests.get(f"{BASE_URL}/api/users/me", headers=headers)
    if r.status_code != 200:
        log(f"Profile failed: {r.status_code} - {r.text}", "FAIL")
        return
    
    profile = r.json()
    log(f"User: {profile.get('email', 'N/A')}", "OK")
    log(f"Current Subscription: {profile.get('subscription', 'N/A')}", "INFO")
    
    # 2. Create order
    log("\nCreating payment order for Pro plan...")
    r = requests.post(f"{BASE_URL}/api/payments/create-order", json={
        "plan_name": "pro",
        "amount": 299  # $299 USD -> will be converted to INR
    }, headers=headers)
    
    if r.status_code != 200:
        log(f"Create order failed: {r.status_code} - {r.text}", "FAIL")
        return
    
    data = r.json()
    order_data = data.get("order", {})
    order_id = order_data.get("order_id")
    key_id = order_data.get("key_id")
    amount = order_data.get("amount")
    amount_inr = order_data.get("amount_inr")
    
    log(f"Order created: {order_id}", "OK")
    log(f"Amount: ₹{amount_inr} ({amount/100} paisa)", "INFO")
    log(f"Key ID: {key_id}", "INFO")
    
    # 3. Generate HTML for Razorpay checkout
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Razorpay Test Payment</title>
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
</head>
<body>
    <h1>Razorpay Test Payment</h1>
    <p>Order ID: {order_id}</p>
    <p>Amount: ₹{amount_inr}</p>
    <button id="pay-btn">Pay Now</button>
    
    <script>
        var options = {{
            "key": "{key_id}",
            "amount": "{amount}",
            "currency": "INR",
            "name": "CodeMurf",
            "description": "Pro Plan Subscription",
            "order_id": "{order_id}",
            "handler": function (response) {{
                alert("Payment successful!\\n\\nPayment ID: " + response.razorpay_payment_id + 
                      "\\nOrder ID: " + response.razorpay_order_id + 
                      "\\nSignature: " + response.razorpay_signature);
                console.log("Payment Response:", response);
                
                // Copy to clipboard
                var text = JSON.stringify(response, null, 2);
                navigator.clipboard.writeText(text).then(function() {{
                    console.log('Copied to clipboard');
                }});
            }},
            "prefill": {{
                "name": "Abhishek",
                "email": "autogencodelabs@gmail.com"
            }},
            "theme": {{
                "color": "#3399cc"
            }}
        }};
        
        var rzp = new Razorpay(options);
        document.getElementById('pay-btn').onclick = function(e) {{
            rzp.open();
            e.preventDefault();
        }};
    </script>
</body>
</html>
"""
    
    # Save HTML file
    html_file = "razorpay_checkout.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    log(f"\nCheckout page saved to: {html_file}", "OK")
    log("Opening in browser...", "INFO")
    
    # Open in browser
    import os
    webbrowser.open(f"file://{os.path.abspath(html_file)}")
    
    print("\n" + "="*60)
    print("📋 NEXT STEPS:")
    print("="*60)
    print("1. Complete payment in the browser")
    print("2. Copy the payment response from the alert")
    print("3. Use those values to test verify-payment endpoint")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
