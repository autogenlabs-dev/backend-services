from app.services.razorpay_service import RazorpayService
from unittest.mock import MagicMock

# Original method
original_verify_payment = RazorpayService.verify_payment

async def mock_verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
    print(f"DEBUG [mock_verify]: Mocking verification for {razorpay_order_id}")
    
    # Simulate successful verification
    return {
        "verified": True,
        "payment_id": razorpay_payment_id,
        "order_id": razorpay_order_id,
        "amount": 2541500,
        "currency": "INR",
        "status": "captured",
        "method": "card",
        "user_id": "mock_user_id", # This might need to be fetched from DB if critical
        "plan_name": "pro"
    }

# Apply patch
RazorpayService.verify_payment = mock_verify_payment
print("✅ RazorpayService.verify_payment patched with mock")
