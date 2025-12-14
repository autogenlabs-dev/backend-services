from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..auth.unified_auth import get_current_user_unified
from ..services.user_service import get_or_create_user_api_key

router = APIRouter(prefix="/user", tags=["User (compat)"])

@router.get("/api-key")
async def get_my_api_key(current_user=Depends(get_current_user_unified), db: AsyncIOMotorDatabase = Depends()):
    """Get the user's primary API key (compat for legacy frontend)."""
    api_key_record, full_key = await get_or_create_user_api_key(db, current_user.id)
    # Only return the full key if it was just created
    return {
        "id": str(api_key_record.id),
        "name": api_key_record.name,
        "key_preview": api_key_record.key_preview,
        "created_at": api_key_record.created_at,
        "last_used_at": api_key_record.last_used_at,
        "is_active": api_key_record.is_active,
        "api_key": full_key or api_key_record.key_preview
    }
