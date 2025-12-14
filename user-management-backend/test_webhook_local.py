"""
Test Razorpay webhook locally by simulating webhook events.
No ngrok required - sends mock events directly to localhost.
"""
import requests
import json
import hmac
import hashlib

BASE_URL = "http://localhost:8000"
# Leave empty to skip signature verification, or set your webhook secret
WEBHOOK_SECRET = ""

def create_signature(body: str, secret: str) -> str:
    """Create Razorpay webhook signature."""
    return hmac.new(
        secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def send_webhook_event(event_type: str, payload: dict):
    """Send a mock webhook event to the local server."""
    print(f"\n{'='*60}")
    print(f"Sending: {event_type}")
    print(f"{'='*60}")
    
    body = json.dumps(payload)
    headers = {"Content-Type": "application/json"}
    
    if WEBHOOK_SECRET:
        signature = create_signature(body, WEBHOOK_SECRET)
        headers["X-Razorpay-Signature"] = signature
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhooks/razorpay",
            data=body,
            headers=headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

# Mock payment.captured event
payment_captured = {
    "event": "payment.captured",
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_test123456789",
                "amount": 29900,  # ₹299 in paisa
                "currency": "INR",
                "status": "captured",
                "order_id": "order_test123456",
                "method": "card",
                "email": "test@example.com",
                "notes": {
                    "user_email": "test@example.com",
                    "plan_name": "pro"
                }
            }
        }
    }
}

# Mock payment.failed event
payment_failed = {
    "event": "payment.failed",
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_failed123456",
                "amount": 29900,
                "currency": "INR",
                "status": "failed",
                "error_description": "Your payment didn't go through as it was declined by the bank.",
                "notes": {
                    "user_email": "test@example.com",
                    "plan_name": "pro"
                }
            }
        }
    }
}

# Mock refund.processed event
refund_processed = {
    "event": "refund.processed",
    "payload": {
        "refund": {
            "entity": {
                "id": "rfnd_test123456",
                "payment_id": "pay_test123456789",
                "amount": 29900,
                "status": "processed"
            }
        }
    }
}

if __name__ == "__main__":
    print("\n" + "="*60)
    print("RAZORPAY WEBHOOK LOCAL TEST")
    print("="*60)
    
    # Test all webhook events
    send_webhook_event("payment.captured", payment_captured)
    send_webhook_event("payment.failed", payment_failed)
    send_webhook_event("refund.processed", refund_processed)
    
    print("\n" + "="*60)
    print("WEBHOOK TESTS COMPLETE")
    print("="*60)
