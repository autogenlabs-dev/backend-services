# Admin moderation endpoints for comments and interactions
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timezone
import math

from app.middleware.auth import require_admin
from app.models.user import User
from app.models.template import Template
from app.models.component import Component
from app.models.template_interactions import TemplateCommentEnhanced
from app.models.component_interactions import ComponentComment
from app.models.interaction_schemas import (
    AdminCommentResponse, AdminCommentsResponse, AdminModerationRequest,
    AdminModerationResponse, ModerationAction, UserInfo, ContentAnalytics,
    InteractionAnalytics
)
from app.utils.audit_logger import log_audit_event

router = APIRouter()


async def get_admin_user_info(user_id: str) -> UserInfo:
    """Get user info for admin responses"""
    user = await User.get(user_id)
    if not user:
        return UserInfo(
            id=user_id,
            username="Unknown User",
            profile_picture=None,
            verified_purchase=False
        )
    
    return UserInfo(
        id=str(user.id),
        username=user.username,
        profile_picture=user.profile_picture,
        verified_purchase=False  # Not relevant for admin view
    )


@router.get("/admin/comments", response_model=AdminCommentsResponse)
async def get_all_comments_for_moderation(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    content_type: Optional[str] = Query(None, pattern="^(template|component)$", description="Filter by content type"),
    is_flagged: Optional[bool] = Query(None, description="Filter by flagged status"),
    is_approved: Optional[bool] = Query(None, description="Filter by approval status"),
    current_user: User = Depends(require_admin)
):
    """Get all comments for admin moderation"""
    try:
        # Build queries for both template and component comments
        template_query = {"is_approved": True}  # Base query
        component_query = {"is_approved": True}  # Base query
        
        # Apply filters
        if is_flagged is not None:
            template_query["is_flagged"] = is_flagged
            component_query["is_flagged"] = is_flagged
        
        if is_approved is not None:
            template_query["is_approved"] = is_approved
            component_query["is_approved"] = is_approved
        
        all_comments = []
        
        # Get template comments if not filtering by component type
        if content_type != "component":
            template_comments = await TemplateCommentEnhanced.find(template_query)\
                .sort([("created_at", -1)])\
                .to_list()
            
            for comment in template_comments:
                template = await Template.get(comment.template_id)
                user_info = await get_admin_user_info(comment.user_id)
                
                all_comments.append({
                    "comment": comment,
                    "content_type": "template",
                    "content_id": comment.template_id,
                    "content_title": template.title if template else "Unknown Template",
                    "user_info": user_info,
                    "sort_date": comment.created_at
                })
        
        # Get component comments if not filtering by template type
        if content_type != "template":
            component_comments = await ComponentComment.find(component_query)\
                .sort([("created_at", -1)])\
                .to_list()
            
            for comment in component_comments:
                component = await Component.get(comment.component_id)
                user_info = await get_admin_user_info(comment.user_id)
                
                all_comments.append({
                    "comment": comment,
                    "content_type": "component",
                    "content_id": comment.component_id,
                    "content_title": component.title if component else "Unknown Component",
                    "user_info": user_info,
                    "sort_date": comment.created_at
                })
        
        # Sort all comments by date
        all_comments.sort(key=lambda x: x["sort_date"], reverse=True)
        
        # Apply pagination
        total_count = len(all_comments)
        total_pages = math.ceil(total_count / page_size)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_comments = all_comments[start_idx:end_idx]
        
        # Build response
        response_comments = []
        for item in paginated_comments:
            comment = item["comment"]
            response_comments.append(AdminCommentResponse(
                id=str(comment.id),
                content_type=item["content_type"],
                content_id=item["content_id"],
                content_title=item["content_title"],
                user=item["user_info"],
                content=comment.content,
                rating=comment.rating,
                is_flagged=comment.is_flagged,
                is_approved=comment.is_approved,
                flag_reason=getattr(comment, 'flag_reason', None),
                created_at=comment.created_at,
                updated_at=comment.updated_at
            ))
        
        return AdminCommentsResponse(
            comments=response_comments,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")


@router.get("/admin/comments/flagged", response_model=AdminCommentsResponse)
async def get_flagged_comments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_admin)
):
    """Get all flagged comments requiring moderation"""
    try:
        # Get flagged template comments
        flagged_template_comments = await TemplateCommentEnhanced.find({
            "is_flagged": True
        }).sort([("created_at", -1)]).to_list()
        
        # Get flagged component comments
        flagged_component_comments = await ComponentComment.find({
            "is_flagged": True
        }).sort([("created_at", -1)]).to_list()
        
        all_flagged = []
        
        # Process template comments
        for comment in flagged_template_comments:
            template = await Template.get(comment.template_id)
            user_info = await get_admin_user_info(comment.user_id)
            
            all_flagged.append({
                "comment": comment,
                "content_type": "template",
                "content_id": comment.template_id,
                "content_title": template.title if template else "Unknown Template",
                "user_info": user_info,
                "sort_date": comment.created_at
            })
        
        # Process component comments
        for comment in flagged_component_comments:
            component = await Component.get(comment.component_id)
            user_info = await get_admin_user_info(comment.user_id)
            
            all_flagged.append({
                "comment": comment,
                "content_type": "component",
                "content_id": comment.component_id,
                "content_title": component.title if component else "Unknown Component",
                "user_info": user_info,
                "sort_date": comment.created_at
            })
        
        # Sort by date
        all_flagged.sort(key=lambda x: x["sort_date"], reverse=True)
        
        # Apply pagination
        total_count = len(all_flagged)
        total_pages = math.ceil(total_count / page_size)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_comments = all_flagged[start_idx:end_idx]
        
        # Build response
        response_comments = []
        for item in paginated_comments:
            comment = item["comment"]
            response_comments.append(AdminCommentResponse(
                id=str(comment.id),
                content_type=item["content_type"],
                content_id=item["content_id"],
                content_title=item["content_title"],
                user=item["user_info"],
                content=comment.content,
                rating=comment.rating,
                is_flagged=comment.is_flagged,
                is_approved=comment.is_approved,
                flag_reason=getattr(comment, 'flag_reason', None),
                created_at=comment.created_at,
                updated_at=comment.updated_at
            ))
        
        return AdminCommentsResponse(
            comments=response_comments,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get flagged comments: {str(e)}")


@router.post("/admin/comments/{comment_id}/moderate", response_model=AdminModerationResponse)
async def moderate_comment(
    comment_id: str,
    moderation_data: AdminModerationRequest,
    current_user: User = Depends(require_admin)
):
    """Moderate a comment (approve, reject, flag, unflag)"""
    try:
        # Try to find comment in both collections
        template_comment = await TemplateCommentEnhanced.get(comment_id)
        component_comment = await ComponentComment.get(comment_id)
        
        comment = template_comment or component_comment
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        comment_type = "template" if template_comment else "component"
        
        # Apply moderation action
        update_data = {"updated_at": datetime.now(timezone.utc)}
        
        if moderation_data.action == ModerationAction.approve:
            update_data["is_approved"] = True
            update_data["is_flagged"] = False
            action_desc = "approved"
            
        elif moderation_data.action == ModerationAction.reject:
            update_data["is_approved"] = False
            action_desc = "rejected"
            
        elif moderation_data.action == ModerationAction.flag:
            update_data["is_flagged"] = True
            if moderation_data.reason:
                update_data["flag_reason"] = moderation_data.reason
            action_desc = "flagged"
            
        elif moderation_data.action == ModerationAction.unflag:
            update_data["is_flagged"] = False
            update_data["flag_reason"] = None
            action_desc = "unflagged"
        
        # Update comment
        await comment.update({"$set": update_data})
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action=f"MODERATE_{comment_type.upper()}_COMMENT",
            resource_type=f"{comment_type}_comment",
            resource_id=comment_id,
            details={
                "moderation_action": moderation_data.action,
                "reason": moderation_data.reason,
                "content_id": getattr(comment, f"{comment_type}_id")
            }
        )
        
        return AdminModerationResponse(
            success=True,
            message=f"Comment {action_desc} successfully",
            comment_id=comment_id,
            action=moderation_data.action
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to moderate comment: {str(e)}")


@router.delete("/admin/comments/{comment_id}")
async def delete_comment_admin(
    comment_id: str,
    current_user: User = Depends(require_admin)
):
    """Delete a comment (admin only)"""
    try:
        # Try to find comment in both collections
        template_comment = await TemplateCommentEnhanced.get(comment_id)
        component_comment = await ComponentComment.get(comment_id)
        
        comment = template_comment or component_comment
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        comment_type = "template" if template_comment else "component"
        content_id = getattr(comment, f"{comment_type}_id")
        
        # Delete all replies
        if template_comment:
            await TemplateCommentEnhanced.find({"parent_comment_id": comment_id}).delete()
            from app.models.template_interactions import TemplateHelpfulVote
            await TemplateHelpfulVote.find({"comment_id": comment_id}).delete()
        else:
            await ComponentComment.find({"parent_comment_id": comment_id}).delete()
            from app.models.component_interactions import ComponentHelpfulVote
            await ComponentHelpfulVote.find({"comment_id": comment_id}).delete()
        
        # Delete comment
        await comment.delete()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action=f"DELETE_{comment_type.upper()}_COMMENT_ADMIN",
            resource_type=f"{comment_type}_comment",
            resource_id=comment_id,
            details={
                "content_id": content_id,
                "admin_deletion": True
            }
        )
        
        return {"message": "Comment deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")


@router.get("/admin/analytics/interactions", response_model=ContentAnalytics)
async def get_interaction_analytics(
    current_user: User = Depends(require_admin)
):
    """Get comprehensive interaction analytics"""
    try:
        # Template analytics
        template_comments = await TemplateCommentEnhanced.count({"is_approved": True})
        template_likes = await TemplateCommentEnhanced.aggregate([
            {"$match": {"is_approved": True}},
            {"$group": {"_id": None, "total": {"$sum": "$helpful_votes"}}}
        ]).to_list()
        
        from app.models.template import TemplateView, TemplateDownload
        template_views = await TemplateView.count()
        template_downloads = await TemplateDownload.count()
        
        # Template rating stats
        template_rating_stats = await TemplateCommentEnhanced.aggregate([
            {"$match": {"rating": {"$ne": None}, "is_approved": True}},
            {"$group": {
                "_id": None,
                "avg_rating": {"$avg": "$rating"},
                "ratings": {"$push": "$rating"}
            }}
        ]).to_list()
        
        template_avg_rating = None
        template_rating_dist = {}
        if template_rating_stats:
            template_avg_rating = round(template_rating_stats[0]["avg_rating"], 2)
            ratings = template_rating_stats[0]["ratings"]
            template_rating_dist = {str(i): ratings.count(i) for i in range(1, 6)}
        
        template_analytics = InteractionAnalytics(
            total_comments=template_comments,
            total_likes=template_likes[0]["total"] if template_likes else 0,
            total_views=template_views,
            total_downloads=template_downloads,
            average_rating=template_avg_rating,
            rating_distribution=template_rating_dist,
            recent_activity=[]
        )
        
        # Component analytics
        from app.models.component_interactions import ComponentLike, ComponentView, ComponentDownload
        component_comments = await ComponentComment.count({"is_approved": True})
        component_likes = await ComponentLike.count()
        component_views = await ComponentView.count()
        component_downloads = await ComponentDownload.count()
        
        # Component rating stats
        component_rating_stats = await ComponentComment.aggregate([
            {"$match": {"rating": {"$ne": None}, "is_approved": True}},
            {"$group": {
                "_id": None,
                "avg_rating": {"$avg": "$rating"},
                "ratings": {"$push": "$rating"}
            }}
        ]).to_list()
        
        component_avg_rating = None
        component_rating_dist = {}
        if component_rating_stats:
            component_avg_rating = round(component_rating_stats[0]["avg_rating"], 2)
            ratings = component_rating_stats[0]["ratings"]
            component_rating_dist = {str(i): ratings.count(i) for i in range(1, 6)}
        
        component_analytics = InteractionAnalytics(
            total_comments=component_comments,
            total_likes=component_likes,
            total_views=component_views,
            total_downloads=component_downloads,
            average_rating=component_avg_rating,
            rating_distribution=component_rating_dist,
            recent_activity=[]
        )
        
        # Top rated templates
        top_templates = await TemplateCommentEnhanced.aggregate([
            {"$match": {"rating": {"$ne": None}, "is_approved": True}},
            {"$group": {
                "_id": "$template_id",
                "avg_rating": {"$avg": "$rating"},
                "rating_count": {"$sum": 1}
            }},
            {"$match": {"rating_count": {"$gte": 3}}},  # At least 3 ratings
            {"$sort": {"avg_rating": -1}},
            {"$limit": 10}
        ]).to_list()
        
        top_rated_templates = []
        for item in top_templates:
            template = await Template.get(item["_id"])
            if template:
                top_rated_templates.append({
                    "id": str(template.id),
                    "title": template.title,
                    "avg_rating": round(item["avg_rating"], 2),
                    "rating_count": item["rating_count"]
                })
        
        # Top rated components
        top_components = await ComponentComment.aggregate([
            {"$match": {"rating": {"$ne": None}, "is_approved": True}},
            {"$group": {
                "_id": "$component_id",
                "avg_rating": {"$avg": "$rating"},
                "rating_count": {"$sum": 1}
            }},
            {"$match": {"rating_count": {"$gte": 3}}},  # At least 3 ratings
            {"$sort": {"avg_rating": -1}},
            {"$limit": 10}
        ]).to_list()
        
        top_rated_components = []
        for item in top_components:
            component = await Component.get(item["_id"])
            if component:
                top_rated_components.append({
                    "id": str(component.id),
                    "title": component.title,
                    "avg_rating": round(item["avg_rating"], 2),
                    "rating_count": item["rating_count"]
                })
        
        # Most active users (by comment count)
        most_active = await TemplateCommentEnhanced.aggregate([
            {"$match": {"is_approved": True}},
            {"$group": {"_id": "$user_id", "comment_count": {"$sum": 1}}},
            {"$sort": {"comment_count": -1}},
            {"$limit": 10}
        ]).to_list()
        
        most_active_users = []
        for item in most_active:
            user = await User.get(item["_id"])
            if user:
                most_active_users.append({
                    "id": str(user.id),
                    "username": user.username,
                    "comment_count": item["comment_count"]
                })
        
        return ContentAnalytics(
            template_analytics=template_analytics,
            component_analytics=component_analytics,
            top_rated_templates=top_rated_templates,
            top_rated_components=top_rated_components,
            most_active_users=most_active_users
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")
