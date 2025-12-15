
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
