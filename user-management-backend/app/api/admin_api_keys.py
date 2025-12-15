"""
Admin API endpoints for managing API key pools (GLM/Bytez).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from app.models.user import User, UserRole
from app.models.api_key_pool import ApiKeyPool
from app.auth.unified_auth import get_current_user_unified
from app.utils.audit_logger import log_audit_event


router = APIRouter(prefix="/admin/api-keys", tags=["Admin - API Keys"])


# Request/Response Models
class AddKeyRequest(BaseModel):
    key_type: str = Field(..., description="Type of key: 'glm' or 'bytez'")
    key_value: str = Field(..., description="The API key value")
    label: Optional[str] = Field(None, description="Optional label for identification")
    max_users: int = Field(10, ge=1, le=100, description="Maximum users per key")


class UpdateKeyRequest(BaseModel):
    max_users: Optional[int] = Field(None, ge=1, le=100)
    is_active: Optional[bool] = None
    label: Optional[str] = None


class KeyPoolStats(BaseModel):
    total_keys: int
    active_keys: int
    total_capacity: int
    total_assigned: int
    glm_keys: int
    bytez_keys: int


# Helper function to check admin role
async def require_admin(current_user: User = Depends(get_current_user_unified)) -> User:
    """Require admin role for access."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/pool")
async def list_api_keys(
    key_type: Optional[str] = Query(None, description="Filter by type: 'glm' or 'bytez'"),
    include_inactive: bool = Query(False, description="Include inactive keys"),
    current_user: User = Depends(require_admin)
):
    """List all API keys in the pool."""
    try:
        query = {}
        if key_type:
            query["key_type"] = key_type
        if not include_inactive:
            query["is_active"] = True
        
        keys = await ApiKeyPool.find(query).to_list()
        
        return {
            "success": True,
            "keys": [key.to_dict() for key in keys],
            "total": len(keys)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list keys: {str(e)}")


@router.post("/pool")
async def add_api_key(
    request: AddKeyRequest,
    current_user: User = Depends(require_admin)
):
    """Add a new API key to the pool."""
    try:
        # Validate key type
        if request.key_type not in ["glm", "bytez"]:
            raise HTTPException(status_code=400, detail="key_type must be 'glm' or 'bytez'")
        
        # Check if key already exists
        existing = await ApiKeyPool.find_one({"key_value": request.key_value})
        if existing:
            raise HTTPException(status_code=400, detail="This API key already exists in the pool")
        
        # Create new key
        new_key = ApiKeyPool(
            key_type=request.key_type,
            key_value=request.key_value,
            label=request.label,
            max_users=request.max_users,
            is_active=True
        )
        await new_key.insert()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action="ADD_API_KEY_TO_POOL",
            resource_type="api_key_pool",
            resource_id=str(new_key.id),
            details={
                "key_type": request.key_type,
                "max_users": request.max_users,
                "label": request.label
            }
        )
        
        return {
            "success": True,
            "message": f"{request.key_type.upper()} key added to pool",
            "key": new_key.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add key: {str(e)}")


@router.patch("/pool/{key_id}")
async def update_api_key(
    key_id: str,
    request: UpdateKeyRequest,
    current_user: User = Depends(require_admin)
):
    """Update an API key's settings."""
    try:
        key = await ApiKeyPool.get(key_id)
        if not key:
            raise HTTPException(status_code=404, detail="Key not found")
        
        # Update fields
        if request.max_users is not None:
            key.max_users = request.max_users
        if request.is_active is not None:
            key.is_active = request.is_active
        if request.label is not None:
            key.label = request.label
        
        key.updated_at = datetime.now(timezone.utc)
        await key.save()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action="UPDATE_API_KEY_POOL",
            resource_type="api_key_pool",
            resource_id=key_id,
            details=request.dict(exclude_none=True)
        )
        
        return {
            "success": True,
            "message": "Key updated successfully",
            "key": key.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update key: {str(e)}")


@router.delete("/pool/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(require_admin)
):
    """Remove an API key from the pool."""
    try:
        key = await ApiKeyPool.get(key_id)
        if not key:
            raise HTTPException(status_code=404, detail="Key not found")
        
        # Check if key has assigned users
        if key.current_users > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete key with {key.current_users} assigned users. Deactivate it instead."
            )
        
        await key.delete()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action="DELETE_API_KEY_FROM_POOL",
            resource_type="api_key_pool",
            resource_id=key_id,
            details={"key_type": key.key_type}
        )
        
        return {
            "success": True,
            "message": "Key removed from pool"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete key: {str(e)}")


@router.get("/pool/stats")
async def get_pool_stats(
    current_user: User = Depends(require_admin)
):
    """Get statistics about the API key pool."""
    try:
        all_keys = await ApiKeyPool.find().to_list()
        
        glm_keys = [k for k in all_keys if k.key_type == "glm"]
        bytez_keys = [k for k in all_keys if k.key_type == "bytez"]
        active_keys = [k for k in all_keys if k.is_active]
        
        stats = {
            "total_keys": len(all_keys),
            "active_keys": len(active_keys),
            "total_capacity": sum(k.max_users for k in active_keys),
            "total_assigned": sum(k.current_users for k in all_keys),
            "glm": {
                "total": len(glm_keys),
                "active": len([k for k in glm_keys if k.is_active]),
                "capacity": sum(k.max_users for k in glm_keys if k.is_active),
                "assigned": sum(k.current_users for k in glm_keys)
            },
            "bytez": {
                "total": len(bytez_keys),
                "active": len([k for k in bytez_keys if k.is_active]),
                "capacity": sum(k.max_users for k in bytez_keys if k.is_active),
                "assigned": sum(k.current_users for k in bytez_keys)
            }
        }
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/pool/{key_id}/users")
async def get_key_users(
    key_id: str,
    current_user: User = Depends(require_admin)
):
    """Get list of users assigned to a specific key."""
    try:
        key = await ApiKeyPool.get(key_id)
        if not key:
            raise HTTPException(status_code=404, detail="Key not found")
        
        # Fetch user details
        users = []
        for user_id in key.assigned_user_ids:
            user = await User.get(user_id)
            if user:
                # Calculate days remaining
                days_left = 0
                if user.subscription_end_date:
                    try:
                        now = datetime.now(timezone.utc)
                        end_date = user.subscription_end_date
                        if end_date.tzinfo is None:
                            end_date = end_date.replace(tzinfo=timezone.utc)
                        
                        if end_date > now:
                            delta = end_date - now
                            days_left = delta.days
                    except Exception:
                        pass  # Fallback to 0 if calculation fails

                users.append({
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name,
                    "subscription": user.subscription.value if user.subscription else "free",
                    "days_left": days_left
                })
        
        return {
            "success": True,
            "key": key.to_dict(),
            "users": users
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")


class ReassignUserRequest(BaseModel):
    user_id: str = Field(..., description="User ID to reassign")
    target_key_id: str = Field(..., description="Target key ID to assign to")


@router.post("/pool/{key_id}/reassign")
async def reassign_user(
    key_id: str,
    request: ReassignUserRequest,
    current_user: User = Depends(require_admin)
):
    """Reassign a user from one API key to another."""
    try:
        from beanie import PydanticObjectId
        
        # Get source key
        source_key = await ApiKeyPool.get(key_id)
        if not source_key:
            raise HTTPException(status_code=404, detail="Source key not found")
        
        # Get target key
        target_key = await ApiKeyPool.get(request.target_key_id)
        if not target_key:
            raise HTTPException(status_code=404, detail="Target key not found")
        
        # Validate same key type
        if source_key.key_type != target_key.key_type:
            raise HTTPException(status_code=400, detail="Cannot reassign to different key type")
        
        # Check target capacity
        if not target_key.has_capacity:
            raise HTTPException(status_code=400, detail="Target key at capacity")
        
        # Get user
        user = await User.get(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_oid = PydanticObjectId(request.user_id)
        
        # Remove from source key
        if not source_key.release_user(user_oid):
            raise HTTPException(status_code=400, detail="User not assigned to source key")
        
        # Add to target key
        if not target_key.assign_user(user_oid):
            # Rollback source change
            source_key.assign_user(user_oid)
            raise HTTPException(status_code=400, detail="Failed to assign to target key")
        
        # Update user's API key field
        if source_key.key_type == "glm":
            user.glm_api_key = target_key.key_value
        elif source_key.key_type == "bytez":
            user.bytez_api_key = target_key.key_value
        
        # Save all changes
        await source_key.save()
        await target_key.save()
        await user.save()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action="REASSIGN_USER_API_KEY",
            resource_type="api_key_pool",
            resource_id=key_id,
            details={
                "user_id": request.user_id,
                "from_key_id": key_id,
                "to_key_id": request.target_key_id,
                "key_type": source_key.key_type
            }
        )
        
        return {
            "success": True,
            "message": f"User reassigned from {source_key.label} to {target_key.label}",
            "source_key": source_key.to_dict(),
            "target_key": target_key.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reassign: {str(e)}")


@router.delete("/pool/{key_id}/users/{user_id}")
async def unassign_user(
    key_id: str,
    user_id: str,
    current_user: User = Depends(require_admin)
):
    """Unassign a user from an API key."""
    try:
        from beanie import PydanticObjectId
        
        # Get key
        key = await ApiKeyPool.get(key_id)
        if not key:
            raise HTTPException(status_code=404, detail="Key not found")
        
        user_oid = PydanticObjectId(user_id)
        
        # Remove user
        if not key.release_user(user_oid):
            raise HTTPException(status_code=404, detail="User not assigned to this key")
        
        await key.save()
        
        # Also clear the user's key field in their profile
        user = await User.get(user_id)
        if user:
            if key.key_type == "glm" and user.glm_api_key == key.key_value:
                user.glm_api_key = None
                await user.save()
            elif key.key_type == "bytez" and user.bytez_api_key == key.key_value:
                user.bytez_api_key = None
                await user.save()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action="UNASSIGN_USER_FROM_POOL_KEY",
            resource_type="api_key_pool",
            resource_id=key_id,
            details={
                "unassigned_user_id": user_id,
                "key_type": key.key_type
            }
        )
        
        return {
            "success": True,
            "message": "User unassigned successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unassign user: {str(e)}")
