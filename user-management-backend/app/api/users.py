"""User management API endpoints."""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from beanie.odm.fields import PydanticObjectId # Changed from UUID
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase # Added AsyncIOMotorDatabase
from fastapi import APIRouter, Depends, HTTPException, status, Query
from ..database import get_database # Changed from get_db
from ..schemas.auth import (
    UserResponse, UserProfile, UserUpdate, TokenUsageLogResponse,
    TokenUsageCreate, TokenUsageStats, ApiKeyCreate, ApiKeyResponse,
    ApiKeyWithSecret, ManagedApiKeyAssignmentResponse
)
from ..auth.dependencies import get_current_user
from ..auth.unified_auth import get_current_user_unified
from ..models.user import User
from ..services.user_service import (
    get_user_by_id, update_user, get_user_oauth_accounts, get_user_subscription,
    log_token_usage, get_user_token_usage, get_user_token_usage_stats,
    create_api_key, get_user_api_keys, deactivate_api_key,
    ensure_managed_api_key_for_user, refresh_managed_api_key_for_user
)
from ..services.openrouter_keys import refresh_user_openrouter_key

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get current user's complete profile."""
    print(f"DEBUG [get_my_profile]: Endpoint reached, current_user: {current_user}")
    # Ensure current_user and current_user.id are not None
    if not current_user or not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    
    # Auto-provision API keys if missing for eligible users
    keys_updated = False
    subscription = current_user.subscription.value if current_user.subscription else "free"
    
    # Auto-provision OpenRouter key for all users
    if not current_user.openrouter_api_key:
        try:
            openrouter_result = await refresh_user_openrouter_key(current_user, db)
            if openrouter_result.get("success"):
                keys_updated = True
                print(f"[get_my_profile] Auto-provisioned OpenRouter key for {current_user.email}")
        except Exception as e:
            print(f"[get_my_profile] Failed to auto-provision OpenRouter key: {e}")
    
    # Auto-provision GLM key for Pro+ users from ApiKeyPool
    if subscription in ["pro", "ultra"] and not current_user.glm_api_key:
        try:
            from ..models.api_key_pool import ApiKeyPool
            
            # Find all active GLM keys and pick one with capacity
            all_glm_keys = await ApiKeyPool.find(
                ApiKeyPool.key_type == "glm",
                ApiKeyPool.is_active == True
            ).to_list()
            
            # Find a key with available capacity
            available_key = None
            for key in all_glm_keys:
                if key.has_capacity:
                    available_key = key
                    break
            
            if available_key:
                # Assign user to this key
                if available_key.assign_user(current_user.id):
                    await available_key.save()
                    current_user.glm_api_key = available_key.key_value
                    keys_updated = True
                    print(f"[get_my_profile] Assigned GLM key '{available_key.label}' to {current_user.email}")
            else:
                print(f"[get_my_profile] No available GLM keys with capacity for {current_user.email}")
        except Exception as e:
            print(f"[get_my_profile] Failed to auto-provision GLM key from pool: {e}")

    
    # Save if keys were updated
    if keys_updated:
        await current_user.save()
        await current_user.sync()
    
    # Get OAuth accounts
    oauth_accounts_raw = await get_user_oauth_accounts(db, current_user.id)
    
    # Simplify OAuth accounts response - just return basic info for now
    oauth_accounts = []
    for account in oauth_accounts_raw:
        oauth_accounts.append({
            "id": str(account.id),
            "provider_id": str(account.provider_id),
            "provider_user_id": account.provider_user_id,
            "email": account.email,
            "connected_at": account.connected_at.isoformat() if account.connected_at else None,
            "last_used_at": account.last_used_at.isoformat() if account.last_used_at else None
        })
    
    # Get API keys
    api_keys = await get_user_api_keys(db, current_user.id)
    
    # Simplify API keys response
    api_keys_response = []
    for key in api_keys:
        api_keys_response.append({
            "id": str(key.id),
            "name": key.name,
            "key_preview": key.key_preview,
            "created_at": key.created_at.isoformat() if key.created_at else None,
            "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
            "is_active": key.is_active
        })
    
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login_at=current_user.last_login_at,
        oauth_accounts=oauth_accounts,
        subscription=current_user.subscription.value if current_user.subscription else "free",  # Use enum value
        api_keys=api_keys_response,
        glm_api_key=current_user.glm_api_key,  # Include GLM API key
        bytez_api_key=current_user.bytez_api_key,  # Include Bytez API key for Ultra users
        openrouter_api_key=current_user.openrouter_api_key,
        role=getattr(current_user, 'role', 'user'),
        # Always allow publishing content to merge user and developer roles
        can_publish_content=True 
    )


@router.post("/me/glm-api-key")
async def set_glm_api_key(
    api_key: str,
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Set or update the user's GLM API key."""
    if current_user.subscription not in {"pro", "ultra"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="GLM API key is available for paid plans only (pro or ultra)")
    current_user.glm_api_key = api_key
    await current_user.save()
    return {"message": "GLM API key updated successfully", "glm_api_key": api_key}


@router.post("/me/openrouter-key/refresh")
async def refresh_openrouter_key(
    current_user: User = Depends(get_current_user_unified)
):
    """Generate a brand-new OpenRouter API key for the current user."""
    try:
        key_value = await refresh_user_openrouter_key(current_user)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    return {"openrouter_api_key": key_value}


@router.get("/me/credits")
async def get_my_credits(
    current_user: User = Depends(get_current_user_unified)
):
    """Get user's OpenRouter remaining credits (for PAYG users)."""
    from ..services.openrouter_keys import get_openrouter_credits
    
    credits = await get_openrouter_credits(current_user)
    
    if credits is None:
        return {
            "success": True,
            "has_credits": False,
            "message": "No OpenRouter key found",
            "credits": None
        }
    
    return {
        "success": True,
        "has_credits": True,
        "credits": credits
    }


@router.get("/me/managed-api-key", response_model=ManagedApiKeyAssignmentResponse)
async def get_my_managed_api_key(
    current_user: User = Depends(get_current_user_unified)
):
    """Return the admin-managed API key assigned to the current user."""
    try:
        managed_key = await ensure_managed_api_key_for_user(current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    assigned_at = managed_key.assigned_at or datetime.now(timezone.utc)
    return ManagedApiKeyAssignmentResponse(
        managed_key_id=managed_key.id,
        key_value=managed_key.key_value,
        key_preview=managed_key.key_preview,
        assigned_at=assigned_at,
        label=managed_key.label
    )


@router.post("/me/managed-api-key/refresh", response_model=ManagedApiKeyAssignmentResponse)
async def refresh_my_managed_api_key(
    current_user: User = Depends(get_current_user_unified)
):
    """Rotate the managed API key for the current user."""
    try:
        managed_key = await refresh_managed_api_key_for_user(current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    assigned_at = managed_key.assigned_at or datetime.now(timezone.utc)
    return ManagedApiKeyAssignmentResponse(
        managed_key_id=managed_key.id,
        key_value=managed_key.key_value,
        key_preview=managed_key.key_preview,
        assigned_at=assigned_at,
        label=managed_key.label
    )


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Update current user's profile."""
    updated_user = await update_user(db, current_user.id, user_data) # Added await
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: PydanticObjectId, # Changed from UUID
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Get user by ID (admin only or self)."""
    # For now, users can only access their own profile
    # In the future, you might want to add admin role checking
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user = await get_user_by_id(db, user_id) # Added await
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


# Token Usage Endpoints
@router.post("/me/token-usage", response_model=TokenUsageLogResponse)
async def log_my_token_usage(
    usage_data: TokenUsageCreate,
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Log token usage for the current user."""
    return await log_token_usage(db, current_user.id, usage_data) # Added await


@router.get("/me/token-usage", response_model=List[TokenUsageLogResponse])
async def get_my_token_usage(
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database), # Changed from Session = Depends(get_db)
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
):
    """Get token usage logs for the current user."""
    logs = await get_user_token_usage(db, current_user.id, start_date, end_date, provider) # Added await
    return logs[:limit]


@router.get("/me/token-usage/stats", response_model=TokenUsageStats)
async def get_my_token_usage_stats(
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database), # Changed from Session = Depends(get_db)
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering")
):
    """Get aggregated token usage statistics for the current user."""
    stats = await get_user_token_usage_stats(db, current_user.id, start_date, end_date) # Added await
    return TokenUsageStats(**stats)


# API Key Management Endpoints
@router.post("/me/api-keys", response_model=ApiKeyWithSecret)
async def create_my_api_key(
    key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Create a new API key for the current user."""
    api_key_record, api_key = await create_api_key(db, current_user.id, key_data) # Added await
    
    # Convert ObjectId to string for response
    return ApiKeyWithSecret(
        id=str(api_key_record.id),  # Convert ObjectId to string
        name=api_key_record.name,
        key_preview=api_key_record.key_preview,
        created_at=api_key_record.created_at,
        last_used_at=api_key_record.last_used_at,
        expires_at=api_key_record.expires_at,
        is_active=api_key_record.is_active,
        api_key=api_key
    )


@router.get("/me/api-keys", response_model=List[ApiKeyResponse])
async def get_my_api_keys(
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Get all API keys for the current user."""
    return await get_user_api_keys(db, current_user.id) # Added await


@router.delete("/me/api-keys/{api_key_id}")
async def deactivate_my_api_key(
    api_key_id: PydanticObjectId, # Changed from UUID
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """Deactivate an API key."""
    success = await deactivate_api_key(db, current_user.id, api_key_id) # Added await
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return {"message": "API key deactivated successfully"}


@router.get("/user/name-matches", tags=["User"])
async def user_name_matches(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database) # Changed from Session = Depends(get_db)
):
    """User endpoint: Count users with the same name as the current user."""
    if not current_user.name:
        return {"count": 0, "message": "Current user has no name set."}
    count = await User.find(User.name == current_user.name).count() # Changed from db.query(User).filter(User.name == current_user.name).count()
    return {"count": count, "name": current_user.name}


@router.get("/user/dashboard", tags=["User"])
async def get_user_dashboard(
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get user dashboard data including profile, subscription, and credits."""
    from ..services.openrouter_keys import get_openrouter_credits
    
    # Get credits info
    credits = await get_openrouter_credits(current_user)
    
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
            # Include actual API keys for display
            "glm_api_key": current_user.glm_api_key,
            "openrouter_api_key": current_user.openrouter_api_key,
            "bytez_api_key": current_user.bytez_api_key,
        },
        "credits": credits,
        "has_openrouter_key": bool(current_user.openrouter_api_key),
        "has_glm_key": bool(current_user.glm_api_key),
    }


@router.post("/me/refresh-api-keys")
async def refresh_api_keys(
    current_user: User = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Refresh or create API keys based on user's subscription plan.
    
    - Free: OpenRouter key only (basic tier)
    - Pro: OpenRouter + GLM key
    - Ultra: OpenRouter + GLM + Bytez key
    """
    from ..services.subscription_service import SubscriptionService
    
    result = {
        "success": True,
        "user_id": str(current_user.id),
        "email": current_user.email,
        "subscription": current_user.subscription.value if current_user.subscription else "free",
        "keys_updated": [],
        "keys_status": {}
    }
    
    subscription = current_user.subscription.value if current_user.subscription else "free"
    
    # 1. OpenRouter key - available for all plans
    try:
        if not current_user.openrouter_api_key:
            # Try to provision a new key
            openrouter_result = await refresh_user_openrouter_key(current_user, db)
            if openrouter_result.get("success"):
                result["keys_updated"].append("openrouter")
                result["keys_status"]["openrouter"] = "created"
            else:
                result["keys_status"]["openrouter"] = f"failed: {openrouter_result.get('error', 'unknown')}"
        else:
            result["keys_status"]["openrouter"] = "exists"
    except Exception as e:
        result["keys_status"]["openrouter"] = f"error: {str(e)}"
    
    # 2. GLM key - available for Pro and Ultra plans (from ApiKeyPool)
    if subscription in ["pro", "ultra"]:
        try:
            if not current_user.glm_api_key:
                from ..models.api_key_pool import ApiKeyPool
                
                # Find all active GLM keys and pick one with capacity
                all_glm_keys = await ApiKeyPool.find(
                    ApiKeyPool.key_type == "glm",
                    ApiKeyPool.is_active == True
                ).to_list()
                
                # Find a key with available capacity
                available_key = None
                for key in all_glm_keys:
                    if key.has_capacity:
                        available_key = key
                        break
                
                if available_key:
                    if available_key.assign_user(current_user.id):
                        await available_key.save()
                        current_user.glm_api_key = available_key.key_value
                        await current_user.save()
                        result["keys_updated"].append("glm")
                        result["keys_status"]["glm"] = f"assigned from {available_key.label}"
                else:
                    result["keys_status"]["glm"] = "no_key_available"
            else:
                result["keys_status"]["glm"] = "exists"
        except Exception as e:
            result["keys_status"]["glm"] = f"error: {str(e)}"
    else:

        result["keys_status"]["glm"] = "not_available_for_plan"
    
    # 3. Bytez key - available for Ultra plan only
    if subscription == "ultra":
        try:
            if not current_user.bytez_api_key:
                result["keys_status"]["bytez"] = "requires_provisioning"
            else:
                result["keys_status"]["bytez"] = "exists"
        except Exception as e:
            result["keys_status"]["bytez"] = f"error: {str(e)}"
    else:
        result["keys_status"]["bytez"] = "not_available_for_plan"
    
    # Reload user to get updated keys
    await current_user.sync()
    
    result["current_keys"] = {
        "openrouter_api_key": current_user.openrouter_api_key[:20] + "..." if current_user.openrouter_api_key else None,
        "glm_api_key": current_user.glm_api_key[:20] + "..." if current_user.glm_api_key else None,
        "bytez_api_key": current_user.bytez_api_key[:20] + "..." if current_user.bytez_api_key else None,
    }
    
    return result
