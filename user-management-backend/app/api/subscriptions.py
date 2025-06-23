"""Subscription management API endpoints with Stripe integration."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase # Added import

from fastapi import APIRouter, Depends, HTTPException, status, Request

from ..database import get_database # Changed from get_db
from ..auth.dependencies import get_current_user
from ..auth.unified_auth import get_current_user_unified
from ..models.user import SubscriptionPlan, UserSubscription, User
from ..services.subscription_service import SubscriptionService
from ..services.stripe_service import StripeService
from ..services.token_service import TokenService
from ..schemas.auth import UserResponse, SubscriptionPlanResponse


router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


class SubscribeRequest(BaseModel):
    plan_name: str
    payment_method_id: str = None


class UpgradeRequest(BaseModel):
    plan_name: str


@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def list_plans(db: AsyncIOMotorDatabase = Depends(get_database)): # Changed from Session = Depends(get_db)
    """List all available subscription plans."""
    subscription_service = SubscriptionService(db)
    return await subscription_service.get_all_plans() # Added await


@router.get("/plans/compare")
async def compare_plans(db: AsyncIOMotorDatabase = Depends(get_database)): # Changed from Session = Depends(get_db)
    """Get a detailed comparison of all subscription plans."""
    subscription_service = SubscriptionService(db)
    return await subscription_service.compare_plans() # Added await


@router.get("/current")
async def get_current_subscription( # Added async
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Get the current user's subscription details."""
    subscription_service = SubscriptionService(db)
    return await subscription_service.get_subscription_status(current_user) # Added await


@router.post("/subscribe")
async def subscribe_to_plan( # Added async
    request: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Subscribe the current user to a plan with Stripe payment."""
    try:
        stripe_service = StripeService(db)
        
        # For free plan, just update locally
        if request.plan_name == "free":
            subscription_service = SubscriptionService(db)
            subscription = await subscription_service.subscribe_user_to_plan( # Added await
                user=current_user,
                plan_name="free"
            )
            return {
                "success": True,
                "plan": request.plan_name,
                "subscription_id": str(subscription.id),
                "message": "Successfully subscribed to free plan"
            }
        
        # For paid plans, use Stripe
        result = await stripe_service.create_subscription(current_user, request.plan_name) # Added await
        return {
            "success": True,
            "plan": request.plan_name,
            "stripe_subscription_id": result["stripe_subscription_id"], # Changed from subscription_id
            "client_secret": result["client_secret"],
            "status": result["status"],
            "message": f"Successfully subscribed to {request.plan_name} plan"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/upgrade")
async def upgrade_subscription( # Added async
    request: UpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Upgrade the current user's subscription."""
    try:
        subscription_service = SubscriptionService(db)
        current_plan = await subscription_service.get_user_plan(current_user) # Added await
        
        # Check if it's actually an upgrade
        new_plan = await subscription_service.get_plan_by_name(request.plan_name) # Added await
        if not new_plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        if new_plan.price_monthly <= current_plan.price_monthly:
            raise HTTPException(status_code=400, detail="New plan must be a higher tier")
        
        # Use Stripe for paid plans
        if new_plan.price_monthly > 0:
            stripe_service = StripeService(db)
            result = await stripe_service.upgrade_subscription(current_user, request.plan_name) # Added await
        else:
            # Shouldn't happen, but handle gracefully
            result = {"message": "Upgraded to free plan"}
        
        return {
            "success": True,
            "plan": request.plan_name,
            "message": result.get("message", f"Successfully upgraded to {request.plan_name}"),
            "details": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/downgrade")
async def downgrade_subscription( # Added async
    request: UpgradeRequest,  # Same structure as upgrade
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Downgrade the current user's subscription."""
    try:
        subscription_service = SubscriptionService(db)
        current_plan = await subscription_service.get_user_plan(current_user) # Added await
        
        # Check if it's actually a downgrade
        new_plan = await subscription_service.get_plan_by_name(request.plan_name) # Added await
        if not new_plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        if new_plan.price_monthly >= current_plan.price_monthly:
            raise HTTPException(status_code=400, detail="New plan must be a lower tier")
        
        # Handle downgrade (may require special Stripe handling)
        subscription = await subscription_service.downgrade_user_subscription(current_user, request.plan_name) # Added await
        
        return {
            "success": True,
            "plan": request.plan_name,
            "subscription_id": str(subscription.id),
            "message": f"Successfully downgraded to {request.plan_name}",
            "effective_date": subscription.current_period_end if subscription.current_period_end else "immediately"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cancel")
async def cancel_subscription( # Added async
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Cancel the current user's subscription."""
    try:
        stripe_service = StripeService(db)
        result = await stripe_service.cancel_subscription(current_user) # Added await
        
        return {
            "success": True,
            "message": result.get("message", "Subscription cancelled"),
            "cancel_at": result.get("cancel_at"),
            "details": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/usage")
async def get_usage_stats( # Added async
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Get detailed usage statistics for the current user."""
    try:
        token_service = TokenService(db)
        subscription_service = SubscriptionService(db)
        
        # Get current plan and usage
        plan = await subscription_service.get_user_plan(current_user) # Added await
        usage_stats = await token_service.get_usage_stats(current_user) # Changed from get_user_usage_stats and added await
        
        return {
            "plan": {
                "name": plan.name,
                "display_name": plan.display_name,
                "monthly_tokens": plan.monthly_tokens,
                "price_monthly": float(plan.price_monthly)
            },
            "usage": {
                "tokens_used": usage_stats["total_tokens"], # Changed from current_month_usage
                "tokens_remaining": max(0, plan.monthly_tokens - usage_stats["total_tokens"]), # Changed from current_month_usage
                "monthly_limit": plan.monthly_tokens,
                "usage_percentage": min(100, (usage_stats["total_tokens"] / plan.monthly_tokens) * 100) if plan.monthly_tokens > 0 else 0, # Changed from current_month_usage and added division by zero check
                "reset_date": usage_stats.get("next_reset_date") # This might need adjustment based on how token_service calculates it
            },
            "statistics": {
                "total_requests": usage_stats["total_requests"] if "total_requests" in usage_stats else 0, # Added check
                "total_cost": usage_stats["total_cost"],
                "avg_tokens_per_request": usage_stats["average_tokens_per_request"] if "average_tokens_per_request" in usage_stats else 0, # Changed key
                "most_used_provider": None, # Removed as it's not directly available from token_service.get_usage_stats
                "most_used_model": None # Removed as it's not directly available from token_service.get_usage_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage stats: {str(e)}")


@router.get("/upgrade-options")
async def get_upgrade_options( # Added async
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Get available upgrade options for the current user."""
    subscription_service = SubscriptionService(db)
    return {
        "upgrade_options": await subscription_service.get_upgrade_options(current_user) # Added await
    }


@router.get("/payment-methods")
async def get_payment_methods( # Added async
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Get user's saved payment methods."""
    try:
        stripe_service = StripeService(db)
        payment_methods = await stripe_service.get_payment_methods(current_user) # Added await
        
        return {
            "payment_methods": payment_methods
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payment methods: {str(e)}")


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: AsyncIOMotorDatabase = Depends(get_database)): # Changed from Session = Depends(get_db)
    """Handle Stripe webhook events."""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        stripe_service = StripeService(db)
        result = await stripe_service.handle_webhook(payload.decode(), sig_header) # Added await
        
        return {"status": "success", "processed": result}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")
