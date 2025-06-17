from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ..database import get_db
from ..auth.jwt_auth import get_current_user
from ..services.sub_user_service import SubUserService
from ..models.user import User
from ..schemas.sub_user import (
    SubUserCreateRequest, SubUserUpdateRequest, SubUserResponse, 
    SubUserUsageStats, SubUserApiKeyCreate, SubUserBulkOperation
)
from ..schemas.api_key import ApiKeyResponse
from ..exceptions import ValidationError, NotFoundError, PermissionError
import uuid

router = APIRouter(prefix="/sub-users", tags=["sub-users"])

@router.post("/", response_model=SubUserResponse)
async def create_sub_user(
    request: SubUserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new sub-user"""
    try:
        service = SubUserService(db)
        sub_user = service.create_sub_user(
            parent_user_id=current_user.id,
            email=request.email,
            name=request.name,
            permissions=request.permissions,
            token_limits=request.token_limits,
            password=request.password
        )
        
        return SubUserResponse(
            id=str(sub_user.id),
            email=sub_user.email,
            name=sub_user.name,
            is_sub_user=sub_user.is_sub_user,
            sub_user_permissions=sub_user.sub_user_permissions,
            sub_user_limits=sub_user.sub_user_limits,
            tokens_used=sub_user.tokens_used,
            tokens_remaining=sub_user.tokens_remaining,
            monthly_limit=sub_user.monthly_limit,
            is_active=sub_user.is_active,
            created_at=sub_user.created_at.isoformat(),
            last_login_at=sub_user.last_login_at.isoformat() if sub_user.last_login_at else None
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.get("/", response_model=List[SubUserResponse])
async def get_sub_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all sub-users for the current user"""
    service = SubUserService(db)
    sub_users = service.get_sub_users(current_user.id)
    
    return [
        SubUserResponse(
            id=str(sub_user.id),
            email=sub_user.email,
            name=sub_user.name,
            is_sub_user=sub_user.is_sub_user,
            sub_user_permissions=sub_user.sub_user_permissions,
            sub_user_limits=sub_user.sub_user_limits,
            tokens_used=sub_user.tokens_used,
            tokens_remaining=sub_user.tokens_remaining,
            monthly_limit=sub_user.monthly_limit,
            is_active=sub_user.is_active,
            created_at=sub_user.created_at.isoformat(),
            last_login_at=sub_user.last_login_at.isoformat() if sub_user.last_login_at else None
        )
        for sub_user in sub_users
    ]

@router.put("/{sub_user_id}/permissions", response_model=SubUserResponse)
async def update_sub_user_permissions(
    sub_user_id: uuid.UUID,
    request: SubUserUpdatePermissionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update permissions for a sub-user"""
    try:
        service = SubUserService(db)
        sub_user = service.update_sub_user_permissions(
            parent_user_id=current_user.id,
            sub_user_id=sub_user_id,
            permissions=request.permissions
        )
        
        return SubUserResponse(
            id=str(sub_user.id),
            email=sub_user.email,
            name=sub_user.name,
            is_sub_user=sub_user.is_sub_user,
            sub_user_permissions=sub_user.sub_user_permissions,
            sub_user_limits=sub_user.sub_user_limits,
            tokens_used=sub_user.tokens_used,
            tokens_remaining=sub_user.tokens_remaining,
            monthly_limit=sub_user.monthly_limit,
            is_active=sub_user.is_active,
            created_at=sub_user.created_at.isoformat(),
            last_login_at=sub_user.last_login_at.isoformat() if sub_user.last_login_at else None
        )
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{sub_user_id}/limits", response_model=SubUserResponse)
async def update_sub_user_limits(
    sub_user_id: uuid.UUID,
    request: SubUserUpdateLimitsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update token and rate limits for a sub-user"""
    try:
        service = SubUserService(db)
        sub_user = service.update_sub_user_limits(
            parent_user_id=current_user.id,
            sub_user_id=sub_user_id,
            limits=request.limits
        )
        
        return SubUserResponse(
            id=str(sub_user.id),
            email=sub_user.email,
            name=sub_user.name,
            is_sub_user=sub_user.is_sub_user,
            sub_user_permissions=sub_user.sub_user_permissions,
            sub_user_limits=sub_user.sub_user_limits,
            tokens_used=sub_user.tokens_used,
            tokens_remaining=sub_user.tokens_remaining,
            monthly_limit=sub_user.monthly_limit,
            is_active=sub_user.is_active,
            created_at=sub_user.created_at.isoformat(),
            last_login_at=sub_user.last_login_at.isoformat() if sub_user.last_login_at else None
        )
        
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if isinstance(e, ValidationError) else status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/{sub_user_id}/api-keys", response_model=ApiKeyResponse)
async def create_sub_user_api_key(
    sub_user_id: uuid.UUID,
    request: ApiKeyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an API key for a sub-user"""
    try:
        service = SubUserService(db)
        api_key = service.create_sub_user_api_key(
            parent_user_id=current_user.id,
            sub_user_id=sub_user_id,
            name=request.name
        )
        
        return ApiKeyResponse(
            id=str(api_key.id),
            name=api_key.name,
            key=api_key.key,
            is_active=api_key.is_active,
            created_at=api_key.created_at.isoformat(),
            last_used_at=api_key.last_used_at.isoformat() if api_key.last_used_at else None,
            metadata=api_key.metadata
        )
        
    except (NotFoundError, PermissionError, ValidationError) as e:
        status_code = status.HTTP_404_NOT_FOUND
        if isinstance(e, PermissionError):
            status_code = status.HTTP_403_FORBIDDEN
        elif isinstance(e, ValidationError):
            status_code = status.HTTP_400_BAD_REQUEST
            
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )

@router.get("/{sub_user_id}/usage")
async def get_sub_user_usage(
    sub_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage statistics for a sub-user"""
    try:
        service = SubUserService(db)
        
        # Verify ownership
        service._get_sub_user_with_verification(current_user.id, sub_user_id)
        
        stats = service.get_sub_user_usage_stats(sub_user_id)
        return stats
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/{sub_user_id}")
async def delete_sub_user(
    sub_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a sub-user"""
    try:
        service = SubUserService(db)
        success = service.delete_sub_user(current_user.id, sub_user_id)
        
        if success:
            return {"message": "Sub-user deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete sub-user"
            )
            
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
