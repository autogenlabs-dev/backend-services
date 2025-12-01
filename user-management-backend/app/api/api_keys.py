"""
API Key management endpoints.
Provides CRUD operations for user API keys.
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_database as get_db
from app.auth.dependencies import get_current_user
from app.auth.unified_auth import get_current_user_unified
from app.auth.api_key_auth_clean import (
    api_key_service,
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyCreateResponse
)
from app.models.user import User
from app.middleware.rate_limiting import apply_rate_limit

router = APIRouter(prefix="/api/keys", tags=["API Keys"])

@router.post("/", response_model=ApiKeyCreateResponse)
async def create_api_key(
    key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Any = Depends(get_db),
    rate_info: dict = Depends(apply_rate_limit)
):
    """
    Create a new API key for the current user.
    
    **Important**: The full API key is only returned once in this response.
    Store it securely as it cannot be retrieved again.
    """
    try:
        api_key = api_key_service.create_api_key(
            user_id=str(current_user.id),
            name=key_data.name,
            db=db,
            description=key_data.description,
            expires_in_days=key_data.expires_in_days
        )
        
        return api_key
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API key: {str(e)}"
        )

@router.get("/", response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Any = Depends(get_db),
    rate_info: dict = Depends(apply_rate_limit)
):
    """
    List all active API keys for the current user.
    
    Returns key metadata but not the actual key values.
    """
    try:
        api_keys = api_key_service.list_user_api_keys(
            user_id=str(current_user.id),
            db=db
        )
        
        return api_keys
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve API keys: {str(e)}"
        )

@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Any = Depends(get_db),
    rate_info: dict = Depends(apply_rate_limit)
):
    """
    Revoke (deactivate) an API key.
    
    This action cannot be undone. The API key will immediately stop working.
    """
    try:
        success = api_key_service.revoke_api_key(
            key_id=key_id,
            user_id=str(current_user.id),
            db=db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found or access denied"
            )
        
        return {
            "message": "API key revoked successfully",
            "key_id": key_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke API key: {str(e)}"
        )

@router.get("/validate")
async def validate_current_key(
    current_user: User = Depends(get_current_user_unified),
    rate_info: dict = Depends(apply_rate_limit)
):
    """
    Validate the current API key and return user information.
    
    This endpoint can be used to test if an API key is working correctly.
    """
    return {
        "valid": True,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "subscription": current_user.subscription,
            "tokens_remaining": current_user.tokens_remaining
        },
        "message": "API key is valid and active"
    }
