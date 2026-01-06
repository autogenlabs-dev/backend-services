"""
Legacy API routes for frontend compatibility.
Maps old paths to new handlers.
"""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database import get_database
from ..auth.unified_auth import get_current_user_unified
from ..models.user import User
from ..services.openrouter_keys import get_openrouter_credits

router = APIRouter(tags=["Legacy"])


@router.get("/user/dashboard")
async def legacy_user_dashboard(
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Legacy: Get user dashboard data."""
    from ..services.payment_service import payment_service
    
    credits = await get_openrouter_credits(current_user)
    
    # Get marketplace purchase stats
    try:
        purchase_history = await payment_service.get_user_purchase_history(
            user=current_user,
            page=1,
            page_size=100  # Get all to count stats
        )
        purchases = purchase_history.get("purchases", [])
        
        marketplace_purchases = len(purchases)
        marketplace_spent = sum(p.get("price_paid_inr", 0) for p in purchases)
        templates_owned = len([p for p in purchases if p.get("item_type") == "template"])
        components_owned = len([p for p in purchases if p.get("item_type") == "component"])
    except Exception as e:
        print(f"Error fetching purchase stats: {e}")
        marketplace_purchases = 0
        marketplace_spent = 0
        templates_owned = 0
        components_owned = 0
    
    # Get subscription purchase stats
    subscription_purchases = 0
    subscription_spent = 0
    try:
        # user_id in razorpay_orders is stored as string
        subscription_orders = await db.razorpay_orders.find({
            "user_id": str(current_user.id),
            "status": "completed"
        }).to_list(length=100)
        subscription_purchases = len(subscription_orders)
        subscription_spent = sum(o.get("amount_inr", 0) for o in subscription_orders)
    except Exception as e:
        print(f"Error fetching subscription stats: {e}")
    
    # Combined stats
    total_purchases = marketplace_purchases + subscription_purchases
    total_spent_inr = marketplace_spent + subscription_spent
    
    return {
        "success": True,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "subscription": current_user.subscription.value if current_user.subscription else "free",
            "subscription_end_date": current_user.subscription_end_date.isoformat() if current_user.subscription_end_date else None,
            "role": getattr(current_user, 'role', 'user'),
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            # Include actual API keys for frontend display
            "glm_api_key": current_user.glm_api_key,
            "openrouter_api_key": current_user.openrouter_api_key,
            "bytez_api_key": current_user.bytez_api_key,
        },
        "credits": credits,
        "has_openrouter_key": bool(current_user.openrouter_api_key),
        "has_glm_key": bool(current_user.glm_api_key),
        # Purchase stats (combined)
        "total_purchases": total_purchases,
        "total_spent_inr": total_spent_inr,
        "templates_owned": templates_owned,
        "components_owned": components_owned,
        "subscription_purchases": subscription_purchases,
    }


@router.get("/user/purchased-items")
async def legacy_purchased_items(
    limit: int = 20,
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Legacy: Get user's purchased items including subscriptions."""
    from ..services.payment_service import payment_service
    
    # Get marketplace purchases
    result = await payment_service.get_user_purchase_history(
        user=current_user,
        page=1,
        page_size=limit
    )
    
    purchases = result.get("purchases", [])
    
    # Also get subscription purchases from razorpay_orders
    try:
        # user_id in razorpay_orders is stored as string
        subscription_orders = await db.razorpay_orders.find({
            "user_id": str(current_user.id),
            "status": "completed"
        }).sort("created_at", -1).to_list(length=limit)
        
        for order in subscription_orders:
            plan_name = order.get("plan_name", "subscription").capitalize()
            purchases.append({
                "id": str(order.get("_id")),
                "item_type": "subscription",
                "item_title": f"{plan_name} Plan Subscription",
                "price_paid_inr": order.get("amount_inr", 0),
                "purchase_date": order.get("created_at").isoformat() if order.get("created_at") else None,
                "status": "completed",
                "razorpay_order_id": order.get("razorpay_order_id"),
                "plan_name": order.get("plan_name")
            })
    except Exception as e:
        print(f"Error fetching subscription orders: {e}")
    
    # Sort all purchases by date (newest first)
    purchases.sort(key=lambda x: x.get("purchase_date") or "", reverse=True)
    
    # Update stats
    total_purchases = len(purchases)
    total_spent_inr = sum(p.get("price_paid_inr", 0) for p in purchases)
    
    return {
        "success": True,
        "purchases": purchases[:limit],
        "statistics": {
            "total_purchases": total_purchases,
            "total_spent_inr": total_spent_inr
        }
    }

