import asyncio
import os
import sys
from datetime import datetime
import razorpay

# Add current directory to path
sys.path.append(os.getcwd())

# Mock settings to avoid import issues if env is missing
class MockSettings:
    razorpay_key_id = "rzp_test_Rqxl4tVNxYqSuO"
    razorpay_key_secret = "f6dpsDsOyxnl25UsTudmow1N"

settings = MockSettings()

def log(msg):
    print(msg)
    with open("debug_output.txt", "a") as f:
        f.write(f"{datetime.now()}: {msg}\n")

async def test_razorpay():
    log("Starting Razorpay Debug...")
    
    try:
        # 1. Initialize Client
        log(f"Initializing client with Key: {settings.razorpay_key_id}")
        client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
        log("Client initialized.")
        
        # 2. Create Order
        amount_inr = 299
        amount_paisa = int(amount_inr * 100)
        
        order_data = {
            "amount": amount_paisa,
            "currency": "INR",
            "receipt": f"debug_rcpt_{int(datetime.now().timestamp())}",
            "notes": {
                "plan_name": "pro",
                "debug": "true"
            }
        }
        
        log(f"Creating order with data: {order_data}")
        
        order = client.order.create(data=order_data)
        
        log(f"Order created successfully: {order['id']}")
        log(f"Order details: {order}")
        
    except Exception as e:
        log(f"ERROR: {str(e)}")
        import traceback
        log(traceback.format_exc())

if __name__ == "__main__":
    # Clear log file
    with open("debug_output.txt", "w") as f:
        f.write("DEBUG LOG START\n")
    
    asyncio.run(test_razorpay())
