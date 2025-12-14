"""
Webhook endpoints for payment providers (Razorpay).
"""

import hmac
import hashlib
import logging
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional

from app.config import settings
from app.models.user import User
from app.services.subscription_service import PlanSubscriptionService
from app.utils.email_service import email_service

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)


def verify_razorpay_signature(
    body: bytes, 
    signature: str, 
    secret: str
) -> bool:
    """Verify Razorpay webhook signature."""
    try:
        expected = hmac.new(
            secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None)
):
    """
    Handle Razorpay webhook events.
    
    Supported events:
    - payment.captured: Payment successful
    - payment.failed: Payment failed
    - refund.processed: Refund completed
    """
    try:
        body = await request.body()
        
        # Verify signature if configured
        webhook_secret = getattr(settings, 'razorpay_webhook_secret', None)
        if webhook_secret and x_razorpay_signature:
            if not verify_razorpay_signature(body, x_razorpay_signature, webhook_secret):
                logger.warning("Invalid Razorpay webhook signature")
                raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Parse payload
        import json
        payload = json.loads(body)
        
        event = payload.get("event")
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        
        logger.info(f"Received Razorpay webhook: {event}")
        
        if event == "payment.captured":
            # Payment successful
            await handle_payment_captured(payment_entity)
        
        elif event == "payment.failed":
            # Payment failed
            await handle_payment_failed(payment_entity)
        
        elif event == "refund.processed":
            # Refund completed
            refund_entity = payload.get("payload", {}).get("refund", {}).get("entity", {})
            await handle_refund_processed(refund_entity)
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        # Return 200 to prevent retries for now
        return {"status": "error", "message": str(e)}


async def handle_payment_captured(payment: dict):
    """Handle successful payment."""
    try:
        notes = payment.get("notes", {})
        user_email = notes.get("user_email")
        plan_name = notes.get("plan_name")
        
        if user_email and plan_name:
            user = await User.find_one({"email": user_email})
            if user:
                logger.info(f"Webhook: Payment captured for {user_email}, plan: {plan_name}")
                # Note: Actual subscription activation is done via /verify-payment endpoint
                # This webhook is for logging and backup processing
    except Exception as e:
        logger.error(f"Error handling payment.captured: {e}")


async def handle_payment_failed(payment: dict):
    """Handle failed payment."""
    try:
        notes = payment.get("notes", {})
        user_email = notes.get("user_email")
        error_description = payment.get("error_description", "Payment failed")
        
        if user_email:
            user = await User.find_one({"email": user_email})
            if user:
                logger.warning(f"Webhook: Payment failed for {user_email}: {error_description}")
                # Could send failure notification email here
    except Exception as e:
        logger.error(f"Error handling payment.failed: {e}")


async def handle_refund_processed(refund: dict):
    """Handle processed refund."""
    try:
        payment_id = refund.get("payment_id")
        amount = refund.get("amount", 0) / 100  # Convert from paisa
        
        logger.info(f"Webhook: Refund processed for payment {payment_id}, amount: ₹{amount}")
        
        # Find user by payment_id and potentially downgrade
        user = await User.find_one({"last_payment_id": payment_id})
        if user:
            # Could implement subscription cancellation on refund
            logger.info(f"Refund for user: {user.email}")
    except Exception as e:
        logger.error(f"Error handling refund.processed: {e}")
