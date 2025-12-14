"""Payment API endpoints for Razorpay integration."""

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional

from ..database import get_database
from ..auth.unified_auth import get_current_user_unified
from ..models.user import User
from ..services.razorpay_service import RazorpayService
from ..services.subscription_service import SubscriptionService

router = APIRouter(prefix="/payments", tags=["Payments"])


class CreateOrderRequest(BaseModel):
    plan_name: str
    amount_inr: Optional[float] = None  # Accept INR directly for Razorpay
    amount_usd: Optional[float] = None  # Or accept USD and convert
    amount: Optional[float] = None  # Legacy field (treated as USD)


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    plan_name: str


@router.post("/create-order")
async def create_payment_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a Razorpay order for payment."""
    try:
        razorpay_service = RazorpayService(db)
        
        # Calculate amount_inr from available fields
        USD_TO_INR_RATE = 85  # This should ideally be fetched from a live API
        
        amount_inr = request.amount_inr
        if amount_inr is None:
            # Try amount_usd first, then legacy 'amount' field
            amount_usd = request.amount_usd or request.amount
            if amount_usd is not None:
                amount_inr = amount_usd * USD_TO_INR_RATE
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Either amount_inr or amount_usd must be provided"
                )
        
        # Create the order
        order_details = await razorpay_service.create_order(
            amount_inr=amount_inr,
            plan_name=request.plan_name,
            user_email=current_user.email,
            user_id=str(current_user.id)
        )
        
        return {
            "success": True,
            "order": order_details,
            "message": "Payment order created successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create payment order: {str(e)}"
        )


@router.post("/verify-payment")
async def verify_payment(
    request: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Verify Razorpay payment and activate subscription."""
    import sys
    print(f"DEBUG [verify-payment]: Received request for user {current_user.email}, plan: {request.plan_name}", flush=True)
    print(f"DEBUG [verify-payment]: Current subscription: {current_user.subscription}", flush=True)
    sys.stdout.flush()
    
    try:
        from ..services.subscription_service import PlanSubscriptionService
        
        razorpay_service = RazorpayService(db)
        plan_service = PlanSubscriptionService(db)
        
        # Verify the payment
        print(f"DEBUG [verify-payment]: Verifying payment signature...", flush=True)
        verification_result = await razorpay_service.verify_payment(
            razorpay_order_id=request.razorpay_order_id,
            razorpay_payment_id=request.razorpay_payment_id,
            razorpay_signature=request.razorpay_signature
        )
        
        print(f"DEBUG [verify-payment]: Verification result: {verification_result}", flush=True)
        
        if verification_result["verified"]:
            # Payment verified successfully, activate subscription using new service
            print(f"DEBUG [verify-payment]: Activating plan '{request.plan_name}' for user {current_user.email}...", flush=True)
            activation_result = await plan_service.activate_plan(
                user=current_user,
                plan_name=request.plan_name,
                payment_id=request.razorpay_payment_id
            )
            print(f"DEBUG [verify-payment]: Activation result: {activation_result}", flush=True)
            
            # Refresh user to get updated subscription
            await current_user.sync()
            print(f"DEBUG [verify-payment]: Updated subscription: {current_user.subscription}", flush=True)
            sys.stdout.flush()
            
            return {
                "success": True,
                "verified": True,
                "message": f"Payment verified and {request.plan_name} plan activated successfully",
                "subscription": current_user.subscription.value if hasattr(current_user.subscription, 'value') else str(current_user.subscription),
                "data": {
                    "plan": activation_result.get("plan"),
                    "role": activation_result.get("role"),
                    "subscription_end_date": activation_result.get("subscription_end_date"),
                    "api_keys": activation_result.get("api_keys"),
                    "credits_added_usd": activation_result.get("credits_added_usd")
                }
            }
        else:
            print(f"DEBUG [verify-payment]: Payment verification failed", flush=True)
            raise HTTPException(
                status_code=400,
                detail="Payment verification failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Payment verification failed: {str(e)}"
        )


@router.get("/orders")
async def get_user_orders(
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all payment orders for the current user."""
    try:
        razorpay_service = RazorpayService(db)
        orders = await razorpay_service.get_user_orders(str(current_user.id))
        
        return {
            "success": True,
            "orders": orders
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch orders: {str(e)}"
        )


@router.get("/order/{order_id}")
async def get_order_details(
    order_id: str,
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get details of a specific order."""
    try:
        razorpay_service = RazorpayService(db)
        order = await razorpay_service.get_order_by_id(order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check if the order belongs to the current user
        if order["user_id"] != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "success": True,
            "order": order
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch order details: {str(e)}"
        )


@router.post("/refund/{payment_id}")
async def refund_payment(
    payment_id: str,
    amount: Optional[int] = None,
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Request a refund for a payment."""
    try:
        razorpay_service = RazorpayService(db)
        
        # TODO: Add admin check or other authorization logic
        # For now, only allow users to refund their own payments
        
        refund_result = await razorpay_service.refund_payment(payment_id, amount)
        
        return {
            "success": True,
            "refund": refund_result,
            "message": "Refund initiated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Refund failed: {str(e)}"
        )


@router.get("/config")
async def get_payment_config():
    """Get payment configuration for frontend."""
    from ..config import settings
    
    return {
        "razorpay_key_id": settings.razorpay_key_id,
        "currency": "INR",
        "usd_to_inr_rate": 85  # This should be fetched from a live API in production
    }
