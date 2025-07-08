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
    amount_usd: float


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
        
        # Create the order
        order_details = await razorpay_service.create_order(
            amount_usd=request.amount_usd,
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
    try:
        razorpay_service = RazorpayService(db)
        subscription_service = SubscriptionService(db)
        
        # Verify the payment
        verification_result = await razorpay_service.verify_payment(
            razorpay_order_id=request.razorpay_order_id,
            razorpay_payment_id=request.razorpay_payment_id,
            razorpay_signature=request.razorpay_signature
        )
        
        if verification_result["verified"]:
            # Payment verified successfully, activate subscription
            subscription = await subscription_service.subscribe_user_to_plan(
                user=current_user,
                plan_name=request.plan_name,
                payment_id=request.razorpay_payment_id
            )
            
            return {
                "success": True,
                "verified": True,
                "subscription_id": str(subscription.id) if subscription else None,
                "plan_name": request.plan_name,
                "payment_details": verification_result,
                "message": f"Payment verified and {request.plan_name} plan activated successfully"
            }
        else:
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
