"""Template API endpoints for template management."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from beanie import PydanticObjectId
from datetime import datetime

from ..models.template import Template, TemplateView, TemplateLike, TemplateDownload
from ..models.user import User
from ..auth.unified_auth import get_current_user_unified
from pydantic import BaseModel

router = APIRouter(prefix="/templates", tags=["Templates"])


class TemplateCreateRequest(BaseModel):
    title: str
    category: str
    type: str
    language: str
    difficulty_level: str
    plan_type: str
    pricing_inr: int = 0
    pricing_usd: int = 0
    short_description: str
    full_description: str
    preview_images: List[str] = []
    git_repo_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    dependencies: List[str] = []
    tags: List[str] = []
    developer_name: str
    developer_experience: str
    is_available_for_dev: bool = True
    featured: bool = False
    code: Optional[str] = None
    readme_content: Optional[str] = None


class TemplateUpdateRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    language: Optional[str] = None
    difficulty_level: Optional[str] = None
    plan_type: Optional[str] = None
    pricing_inr: Optional[int] = None
    pricing_usd: Optional[int] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    preview_images: Optional[List[str]] = None
    git_repo_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    dependencies: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    developer_name: Optional[str] = None
    developer_experience: Optional[str] = None
    is_available_for_dev: Optional[bool] = None
    featured: Optional[bool] = None
    code: Optional[str] = None
    readme_content: Optional[str] = None


@router.post("/", response_model=Dict[str, Any])
async def create_template(
    request: TemplateCreateRequest,
    current_user: User = Depends(get_current_user_unified)
):
    """Create a new template."""
    try:
        # Create template document
        template = Template(
            title=request.title,
            category=request.category,
            type=request.type,
            language=request.language,
            difficulty_level=request.difficulty_level,
            plan_type=request.plan_type,
            pricing_inr=request.pricing_inr,
            pricing_usd=request.pricing_usd,
            short_description=request.short_description,
            full_description=request.full_description,
            preview_images=request.preview_images,
            git_repo_url=request.git_repo_url,
            live_demo_url=request.live_demo_url,
            dependencies=request.dependencies,
            tags=request.tags,
            developer_name=request.developer_name,
            developer_experience=request.developer_experience,
            is_available_for_dev=request.is_available_for_dev,
            featured=request.featured,
            code=request.code,
            readme_content=request.readme_content,
            user_id=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to database
        await template.insert()
        
        return {
            "success": True,
            "template": template.to_dict(),
            "message": "Template created successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create template: {str(e)}"
        )


@router.get("/", response_model=Dict[str, Any])
async def get_all_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    plan_type: Optional[str] = Query(None, description="Filter by plan type (Free/Paid)"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    featured: Optional[bool] = Query(None, description="Filter featured templates"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of templates per page")
):
    """Get all templates with optional filtering and pagination."""
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
        
        # Text search
        if search:
            filter_query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"short_description": {"$regex": search, "$options": "i"}},
                {"full_description": {"$regex": search, "$options": "i"}},
                {"tags": {"$in": [search]}}
            ]
        
        # Get total count
        total_count = await Template.find(filter_query).count()
        
        # Get paginated results
        skip = (page - 1) * limit
        templates = await Template.find(filter_query).sort("-created_at").skip(skip).limit(limit).to_list()
        
        # Convert to dictionary format
        template_list = [template.to_dict() for template in templates]
        
        return {
            "success": True,
            "templates": template_list,
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
            detail=f"Failed to fetch templates: {str(e)}"
        )


@router.get("/{template_id}", response_model=Dict[str, Any])
async def get_template_by_id(template_id: str):
    """Get a specific template by ID."""
    try:
        # Convert string ID to ObjectId
        if not PydanticObjectId.is_valid(template_id):
            raise HTTPException(status_code=400, detail="Invalid template ID")
        
        # Find template
        template = await Template.get(PydanticObjectId(template_id))
        
        if not template or not template.is_active:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Increment view count
        await template.update({"$inc": {"views": 1}})
        
        return {
            "success": True,
            "template": template.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch template: {str(e)}"
        )


@router.put("/{template_id}", response_model=Dict[str, Any])
async def update_template(
    template_id: str,
    request: TemplateUpdateRequest,
    current_user: User = Depends(get_current_user_unified)
):
    """Update a template."""
    try:
        # Convert string ID to ObjectId
        if not PydanticObjectId.is_valid(template_id):
            raise HTTPException(status_code=400, detail="Invalid template ID")
        
        # Find template
        template = await Template.get(PydanticObjectId(template_id))
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check if user owns the template
        if template.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this template")
        
        # Prepare update data
        update_data = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        # Add updated timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # Update template
        await template.update({"$set": update_data})
        
        # Fetch updated template
        updated_template = await Template.get(PydanticObjectId(template_id))
        
        return {
            "success": True,
            "template": updated_template.to_dict(),
            "message": "Template updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update template: {str(e)}"
        )


@router.delete("/{template_id}", response_model=Dict[str, Any])
async def delete_template(
    template_id: str,
    current_user: User = Depends(get_current_user_unified)
):
    """Delete a template (soft delete by setting is_active to False)."""
    try:
        # Convert string ID to ObjectId
        if not PydanticObjectId.is_valid(template_id):
            raise HTTPException(status_code=400, detail="Invalid template ID")
        
        # Find template
        template = await Template.get(PydanticObjectId(template_id))
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check if user owns the template
        if template.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this template")
        
        # Soft delete (set is_active to False)
        await template.update({"$set": {"is_active": False, "updated_at": datetime.utcnow()}})
        
        return {
            "success": True,
            "message": "Template deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete template: {str(e)}"
        )


@router.get("/user/my-templates", response_model=Dict[str, Any])
async def get_my_templates(
    current_user: User = Depends(get_current_user_unified),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of templates per page")
):
    """Get all templates created by the current user."""
    try:
        # Build filter query for user's templates
        filter_query = {
            "user_id": current_user.id,
            "is_active": True
        }
        
        # Get total count
        total_count = await Template.find(filter_query).count()
        
        # Get paginated results
        skip = (page - 1) * limit
        templates = await Template.find(filter_query).sort("-created_at").skip(skip).limit(limit).to_list()
        
        # Convert to dictionary format
        template_list = [template.to_dict() for template in templates]
        
        return {
            "success": True,
            "templates": template_list,
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
            detail=f"Failed to fetch user templates: {str(e)}"
        )


@router.post("/{template_id}/like", response_model=Dict[str, Any])
async def like_template(
    template_id: str,
    current_user: User = Depends(get_current_user_unified)
):
    """Like or unlike a template."""
    try:
        # Convert string ID to ObjectId
        if not PydanticObjectId.is_valid(template_id):
            raise HTTPException(status_code=400, detail="Invalid template ID")
        
        template_obj_id = PydanticObjectId(template_id)
        
        # Check if template exists
        template = await Template.get(template_obj_id)
        if not template or not template.is_active:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check if user already liked this template
        existing_like = await TemplateLike.find_one({
            "template_id": template_obj_id,
            "user_id": current_user.id
        })
        
        if existing_like:
            # Unlike - remove the like
            await existing_like.delete()
            await template.update({"$inc": {"likes": -1}})
            message = "Template unliked successfully"
            liked = False
        else:
            # Like - add the like
            like = TemplateLike(
                template_id=template_obj_id,
                user_id=current_user.id
            )
            await like.insert()
            await template.update({"$inc": {"likes": 1}})
            message = "Template liked successfully"
            liked = True
        
        # Get updated template
        updated_template = await Template.get(template_obj_id)
        
        return {
            "success": True,
            "liked": liked,
            "likes_count": updated_template.likes,
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to like/unlike template: {str(e)}"
        )


@router.post("/{template_id}/download", response_model=Dict[str, Any])
async def download_template(
    template_id: str,
    current_user: User = Depends(get_current_user_unified)
):
    """Record a template download."""
    try:
        # Convert string ID to ObjectId
        if not PydanticObjectId.is_valid(template_id):
            raise HTTPException(status_code=400, detail="Invalid template ID")
        
        template_obj_id = PydanticObjectId(template_id)
        
        # Check if template exists
        template = await Template.get(template_obj_id)
        if not template or not template.is_active:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Record the download
        download = TemplateDownload(
            template_id=template_obj_id,
            user_id=current_user.id
        )
        await download.insert()
        
        # Increment download count
        await template.update({"$inc": {"downloads": 1}})
        
        # Get updated template
        updated_template = await Template.get(template_obj_id)
        
        return {
            "success": True,
            "template": updated_template.to_dict(),
            "message": "Download recorded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to record download: {str(e)}"
        )


@router.get("/categories/list", response_model=Dict[str, Any])
async def get_template_categories():
    """Get all available template categories."""
    try:
        # Get unique categories from templates
        categories = await Template.distinct("category", {"is_active": True})
        
        # Default categories if none exist
        default_categories = [
            "Admin Panel",
            "Portfolio",
            "E-commerce", 
            "Dashboard",
            "Blog",
            "Landing Page",
            "SaaS Tool",
            "Learning Management System"
        ]
        
        # Use existing categories or default ones
        category_list = categories if categories else default_categories
        
        return {
            "success": True,
            "categories": sorted(category_list)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch categories: {str(e)}"
        )


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_template_stats():
    """Get template statistics overview."""
    try:
        # Get various counts
        total_templates = await Template.find({"is_active": True}).count()
        free_templates = await Template.find({"is_active": True, "plan_type": "Free"}).count()
        paid_templates = await Template.find({"is_active": True, "plan_type": "Paid"}).count()
        featured_templates = await Template.find({"is_active": True, "featured": True}).count()
        
        # Get categories count
        categories = await Template.distinct("category", {"is_active": True})
        categories_count = len(categories)
        
        return {
            "success": True,
            "stats": {
                "total_templates": total_templates,
                "free_templates": free_templates,
                "paid_templates": paid_templates,
                "featured_templates": featured_templates,
                "categories_count": categories_count,
                "categories": sorted(categories)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch template stats: {str(e)}"
        )