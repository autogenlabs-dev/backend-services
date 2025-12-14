"""
Single user API endpoints (singular /user routes for frontend compatibility).
This router provides singular /user endpoints that the frontend expects.
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from fastapi import APIRouter, Depends, HTTPException, status

from ..database import get_database
from ..auth.unified_auth import get_current_user_unified
from ..models.user import User
from ..services.user_service import get_or_create_user_api_key

router = APIRouter(prefix="/user", tags=["User (Singular)"])


@router.get("/api-key")
async def get_user_api_key(
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get or create the user's API key.
    
    This endpoint returns the user's existing API key (preview only)
    or creates a new one if none exists.
    
    For the full API key, it's only returned once when first created.
    Subsequent calls return only the preview (first 8 characters).
    """
    try:
        # Get or create API key for the user
        api_key_record, full_key = await get_or_create_user_api_key(db, current_user.id)
        
        # Return the full key if available (newly created), otherwise preview
        return {
            "success": True,
            "api_key": full_key if full_key else api_key_record.key_preview,
            "key_preview": api_key_record.key_preview,
            "created_at": api_key_record.created_at.isoformat() if api_key_record.created_at else None,
            "last_used_at": api_key_record.last_used_at.isoformat() if api_key_record.last_used_at else None,
            "is_active": api_key_record.is_active,
            "note": "Full API key is only shown once when created. Store it securely." if full_key else "This is a preview. Full key was shown at creation time."
        }
        
    except Exception as e:
        print(f"Error getting API key for user {current_user.email}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get API key: {str(e)}"
        )
