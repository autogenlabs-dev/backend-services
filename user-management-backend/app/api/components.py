"""Component API endpoints for UI component management (mirroring templates)."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from beanie import PydanticObjectId
from datetime import datetime, timezone

from ..models.component import Component
from ..models.user import User, UserRole
from ..auth.unified_auth import get_current_user_unified
from ..schemas.component import ComponentCreateRequest, ComponentUpdateRequest
from pydantic import BaseModel

router = APIRouter(prefix="/components", tags=["Components"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=Dict[str, Any])
async def create_component(
    request: ComponentCreateRequest,
    current_user: User = Depends(get_current_user_unified)
):
    """Create a new component."""
    # Allow all authenticated users to create components
    # if not (getattr(current_user, 'can_publish_content', False) or current_user.role == UserRole.ADMIN):
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Creator or Admin access required"
    #     )
    
    try:
        component = Component(
            **request.dict(),
            user_id=current_user.id,  # Keep as PydanticObjectId, not string
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        await component.insert()
        
        # Refresh to ensure ID is populated
        await component.save()
        
        # Verify ID exists
        if not component.id:
            logger.error("❌ Component insert succeeded but ID is None")
            raise HTTPException(
                status_code=500,
                detail="Component created but ID was not generated"
            )
        
        # Convert to dict for response
        component_dict = component.to_dict()
        component_id = component_dict.get('id')
        
        logger.info(f"✅ Component created successfully with ID: {component_id}")
        logger.debug(f"Component data: {component_dict}")
        
        return {
            "success": True,
            "component": component_dict,
            "message": "Component created successfully"
        }
    except Exception as e:
        logger.error(f"❌ Component creation failed: {str(e)}")
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
        logger.info(f"🔍 GET /api/components/ called with params: category={category}, plan_type={plan_type}, limit={limit}, page={page}")
        
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
        
        logger.debug(f"📋 Filter query: {filter_query}")
        
        # Get total count for pagination
        total_count = await Component.find(filter_query).count()
        logger.info(f"📊 Total count matching filter: {total_count}")
        
        # Get paginated results
        skip = (page - 1) * limit
        logger.debug(f"📄 Pagination: skip={skip}, limit={limit}")
        
        components = await Component.find(filter_query).sort("-created_at").skip(skip).limit(limit).to_list()
        logger.info(f"✅ Retrieved {len(components)} components from database")
        
        # Convert to dictionary format
        component_list = [component.to_dict() for component in components]
        logger.debug(f"📝 Converted {len(component_list)} components to dict format")
        
        result = {
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
        
        logger.info(f"🎉 Returning response with {len(component_list)} components")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in get_all_components: {e}", exc_info=True)
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
        
        logger.info(f"🔍 GET /components/{component_id} - Starting request")
        logger.debug(f"   Request component_id type: {type(component_id)}, value: '{component_id}'")
        
        # Convert string ID to ObjectId
        if not PydanticObjectId.is_valid(component_id):
            logger.warning(f"❌ Invalid component ID format: {component_id}")
            raise HTTPException(status_code=400, detail="Invalid component ID")
        
        logger.debug(f"✅ Component ID is valid format")
        
        # Convert to ObjectId
        object_id = PydanticObjectId(component_id)
        logger.debug(f"🔄 Converted to ObjectId: {object_id}")
        logger.debug(f"   ObjectId type: {type(object_id)}")
        
        # Fetch component using Beanie's get method
        logger.debug(f"📡 Calling Component.get({object_id})")
        component = await Component.find_one({"_id": object_id})
        
        if not component:
            logger.warning(f"❌ Component not found for ID: {component_id}")
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Log what we actually got back
        logger.info(f"✅ Component.get() returned a document")
        logger.info(f"   Returned component ID: {component.id}")
        logger.info(f"   Returned component title: '{component.title}'")
        logger.info(f"   Returned component type: '{component.type}'")
        logger.info(f"   Returned component language: '{component.language}'")
        
        # Verify the ID matches
        if str(component.id) != component_id:
            logger.error(f"🚨 ID MISMATCH DETECTED!")
            logger.error(f"   Requested ID: {component_id}")
            logger.error(f"   Returned ID:  {component.id}")
            logger.error(f"   This indicates Component.get() returned the wrong document!")
            raise HTTPException(status_code=500, detail="Database integrity error: ID mismatch")
        else:
            logger.debug(f"✅ ID verification passed: {str(component.id)} == {component_id}")
        
        # Convert to dict
        component_dict = component.to_dict()
        logger.debug(f"📝 Converted to dict, ID in dict: {component_dict.get('id')}")
        
        logger.info(f"✅ Returning component: {component_id}")
        return {"success": True, "component": component_dict}
        
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
    """Update a component."""
    # Validate and convert ID
    if not PydanticObjectId.is_valid(component_id):
        raise HTTPException(status_code=400, detail="Invalid component ID")
    
    # Get component with proper ID conversion
    component = await Component.get(PydanticObjectId(component_id))
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    if str(component.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this component")
    
    # Update component fields
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
    """Delete a component."""
    # Validate and convert ID
    if not PydanticObjectId.is_valid(component_id):
        raise HTTPException(status_code=400, detail="Invalid component ID")
    
    # Get component with proper ID conversion
    component = await Component.get(PydanticObjectId(component_id))
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    if str(component.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this component")
    
    await component.delete()
    return {"success": True, "message": "Component deleted successfully"}
