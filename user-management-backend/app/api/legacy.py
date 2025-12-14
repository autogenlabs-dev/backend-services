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
    credits = await get_openrouter_credits(current_user)
    
    return {
        "success": True,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "subscription": current_user.subscription.value if current_user.subscription else "free",
            "role": getattr(current_user, 'role', 'user'),
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        },
        "credits": credits,
        "has_openrouter_key": bool(current_user.openrouter_api_key),
        "has_glm_key": bool(current_user.glm_api_key),
    }


@router.get("/user/purchased-items")
async def legacy_purchased_items(
    limit: int = 20,
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Legacy: Get user's purchased items."""
    from ..services.payment_service import payment_service
    
    result = await payment_service.get_user_purchase_history(
        user=current_user,
        page=1,
        page_size=limit
    )
    
    return result
