"""Component API endpoints for UI component management (mirroring templates)."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from beanie import PydanticObjectId
from datetime import datetime, timezone

from ..models.component import Component
from ..models.user import User
from ..auth.unified_auth import get_current_user_unified
from ..schemas.component import ComponentCreateRequest, ComponentUpdateRequest
from pydantic import BaseModel

router = APIRouter(prefix="/components", tags=["Components"])

@router.post("/", response_model=Dict[str, Any])
async def create_component(
    request: ComponentCreateRequest,
    current_user: User = Depends(get_current_user_unified)
):
    """Create a new component."""
    # Check if user has developer or admin role
    if current_user.role not in ["developer", "admin", "superadmin"]:
        raise HTTPException(
            status_code=403,
            detail="Developer or Admin access required"
        )
    
    try:
        component = Component(
            **request.dict(),
            user_id=current_user.id,  # Keep as PydanticObjectId, not string
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        await component.insert()
        return {
            "success": True,
            "component": component.to_dict(),
            "message": "Component created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create component: {str(e)}"
        )

@router.get("/", response_model=Dict[str, Any])
async def get_all_components(
    category: Optional[str] = Query(None, description="Filter by category"),
    plan_type: Optional[str] = Query(None, description="Filter by plan type (Free/Paid)"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    featured: Optional[bool] = Query(None, description="Filter featured components"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of components per page")
):
    """Get all components with optional filtering and pagination."""
    try:
        # Build filter query
        filter_query = {"is_active": True}
        
        if category:
            filter_query["category"] = category
        if plan_type:
            filter_query["plan_type"] = plan_type
        if difficulty_level:
            filter_query["difficulty_level"] = difficulty_level
        if featured is not None:
            filter_query["featured"] = featured
        
        # Add search functionality
        if search:
            filter_query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"short_description": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count for pagination
        total_count = await Component.find(filter_query).count()
        
        # Get paginated results
        skip = (page - 1) * limit
        components = await Component.find(filter_query).sort("-created_at").skip(skip).limit(limit).to_list()
        
        # Convert to dictionary format
        component_list = [component.to_dict() for component in components]
        
        return {
            "success": True,
            "components": component_list,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch components: {str(e)}"
        )

@router.get("/my", response_model=Dict[str, Any])
async def get_my_components(
    current_user: User = Depends(get_current_user_unified),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of components per page")
):
    """Get components created by the current user."""
    try:
        # Build filter query for user's components
        filter_query = {"user_id": current_user.id, "is_active": True}
        
        # Calculate skip value for pagination
        skip = (page - 1) * limit
        
        # Get components with pagination
        components = await Component.find(filter_query).skip(skip).limit(limit).to_list()
        
        # Get total count for pagination
        total_count = await Component.find(filter_query).count()
        
        # Convert to dict format
        components_data = [component.to_dict() for component in components]
        
        return {
            "success": True,
            "components": components_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user components: {str(e)}"
        )


@router.get("/my-components", response_model=Dict[str, Any])
async def get_my_components_legacy(
    current_user: User = Depends(get_current_user_unified),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of components per page")
):
    """Get components created by the current user. Legacy route for backward compatibility."""
    # Call the main function
    return await get_my_components(current_user, page, limit)

@router.get("/{component_id}", response_model=Dict[str, Any])
async def get_component(component_id: str):
    """Get a specific component by ID."""
    try:
        # Skip validation for special routes
        if component_id in ['my', 'my-components', 'favorites', 'categories', 'stats']:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Convert string ID to ObjectId
        if not PydanticObjectId.is_valid(component_id):
            raise HTTPException(status_code=400, detail="Invalid component ID")
        
        component = await Component.get(PydanticObjectId(component_id))
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        return {"success": True, "component": component.to_dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch component: {str(e)}"
        )

@router.put("/{component_id}", response_model=Dict[str, Any])
async def update_component(
    component_id: str,
    request: ComponentUpdateRequest,
    current_user: User = Depends(get_current_user_unified)
):
    component = await Component.get(component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    if str(component.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this component")
    update_data = {k: v for k, v in request.dict().items() if v is not None}
    for k, v in update_data.items():
        setattr(component, k, v)
    component.updated_at = datetime.now(timezone.utc)
    await component.save()
    return {"success": True, "component": component.to_dict(), "message": "Component updated successfully"}

@router.delete("/{component_id}", response_model=Dict[str, Any])
async def delete_component(
    component_id: str,
    current_user: User = Depends(get_current_user_unified)
):
    component = await Component.get(component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    if str(component.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this component")
    await component.delete()
    return {"success": True, "message": "Component deleted successfully"}
