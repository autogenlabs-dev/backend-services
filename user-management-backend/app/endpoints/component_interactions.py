# Component interaction endpoints - Comments, Ratings, Likes, Views, Downloads
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import math
from collections import defaultdict

from app.middleware.auth import require_auth, get_current_user_from_token
from app.models.user import User
from app.models.component import Component
from app.models.component_interactions import (
    ComponentLike, ComponentComment, ComponentView, 
    ComponentDownload, ComponentHelpfulVote
)
from app.models.interaction_schemas import (
    ComponentCommentCreate, ComponentCommentUpdate, ComponentCommentResponse,
    ComponentCommentsResponse, ComponentHelpfulVoteResponse, ComponentLikeResponse,
    UserInfo, CommentSortBy, InteractionAnalytics
)
from app.utils.audit_logger import log_audit_event

router = APIRouter()


async def get_user_info_component(user_id: str, component_id: str = None) -> UserInfo:
    """Get user info with verified purchase status for component"""
    try:
        user = await User.get(user_id)
        if not user:
            print(f"User not found: {user_id}")
            return UserInfo(
                id=user_id,
                username="Unknown User",
                profile_picture=None,
                verified_purchase=False
            )
        
        verified_purchase = False
        if component_id:
            try:
                # Check if user has purchased this component
                from app.models.purchased_item import PurchasedItem
                purchase = await PurchasedItem.find_one({
                    "user_id": user_id,
                    "item_id": component_id,
                    "item_type": "component"
                })
                verified_purchase = purchase is not None
            except Exception as e:
                print(f"Error checking purchase for user {user_id}: {e}")
                verified_purchase = False
        
        return UserInfo(
            id=str(user.id),
            username=user.username or user.email or "Unknown User",  # Fallback for None username
            profile_picture=user.profile_image,  # Fixed: profile_image not profile_picture
            verified_purchase=verified_purchase
        )
        
    except Exception as e:
        print(f"Error getting user info for {user_id}: {e}")
        # Return dummy user info on any error
        return UserInfo(
            id=user_id,
            username="Unknown User", 
            profile_picture=None,
            verified_purchase=False
        )


@router.post("/components/{component_id}/like", response_model=ComponentLikeResponse)
async def toggle_component_like(
    component_id: str,
    current_user: User = Depends(require_auth)
):
    """Toggle like on a component"""
    try:
        # Verify component exists
        component = await Component.get(component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Check if user already liked
        existing_like = await ComponentLike.find_one({
            "user_id": str(current_user.id),
            "component_id": component_id
        })
        
        if existing_like:
            # Remove like
            await existing_like.delete()
            action = "UNLIKE_COMPONENT"
            message = "Component unliked"
            user_has_liked = False
        else:
            # Add like
            like = ComponentLike(
                user_id=str(current_user.id),
                component_id=component_id
            )
            await like.insert()
            action = "LIKE_COMPONENT"
            message = "Component liked"
            user_has_liked = True
        
        # Get total likes count
        total_likes = await ComponentLike.find({"component_id": component_id}).count()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action=action,
            resource_type="component",
            resource_id=component_id,
            details={"total_likes": total_likes}
        )
        
        return ComponentLikeResponse(
            success=True,
            message=message,
            total_likes=total_likes,
            user_has_liked=user_has_liked
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle like: {str(e)}")


@router.post("/components/{component_id}/view")
async def record_component_view(
    component_id: str,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Record a view for a component"""
    try:
        # Verify component exists
        component = await Component.get(component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        user_id = str(current_user.id) if current_user else None
        
        # Check if view already recorded recently (within last hour)
        if user_id:
            recent_view = await ComponentView.find_one({
                "user_id": user_id,
                "component_id": component_id,
                "created_at": {"$gte": datetime.utcnow().replace(minute=0, second=0, microsecond=0)}
            })
            
            if recent_view:
                return {"message": "View already recorded"}
        
        # Record view
        view = ComponentView(
            user_id=user_id,
            component_id=component_id,
            ip_address=None,  # Could be added from request
            user_agent=None   # Could be added from request
        )
        await view.insert()
        
        # Log audit event (only for authenticated users)
        if user_id:
            await log_audit_event(
                user_id=user_id,
                action="VIEW_COMPONENT",
                resource_type="component",
                resource_id=component_id,
                details={}
            )
        
        return {"message": "View recorded"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record view: {str(e)}")


@router.post("/components/{component_id}/download")
async def record_component_download(
    component_id: str,
    current_user: User = Depends(require_auth)
):
    """Record a download for a component"""
    try:
        # Verify component exists
        component = await Component.get(component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Check if component is free or user has purchased it
        if component.price > 0:
            from app.models.purchased_item import PurchasedItem
            purchase = await PurchasedItem.find_one({
                "user_id": str(current_user.id),
                "item_id": component_id,
                "item_type": "component"
            })
            if not purchase:
                raise HTTPException(status_code=403, detail="Component must be purchased before download")
        
        # Record download
        download = ComponentDownload(
            user_id=str(current_user.id),
            component_id=component_id
        )
        await download.insert()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action="DOWNLOAD_COMPONENT",
            resource_type="component",
            resource_id=component_id,
            details={"component_price": component.price}
        )
        
        return {"message": "Download recorded"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record download: {str(e)}")


@router.post("/components/{component_id}/comments", response_model=ComponentCommentResponse)
async def create_component_comment(
    component_id: str,
    comment_data: ComponentCommentCreate,
    current_user: User = Depends(require_auth)
):
    """Create a new comment on a component"""
    try:
        print(f"Creating component comment - component_id: {component_id}")
        print(f"Comment data: {comment_data}")
        print(f"User: {current_user.username if current_user else 'None'}")
        
        # Verify component exists
        component = await Component.get(component_id)
        if not component:
            print(f"Component not found: {component_id}")
            raise HTTPException(status_code=404, detail="Component not found")
        
        print(f"Component found: {component.title}")
        
        # Validate parent comment if provided
        if comment_data.parent_comment_id:
            parent_comment = await ComponentComment.get(comment_data.parent_comment_id)
            if not parent_comment or parent_comment.component_id != component_id:
                raise HTTPException(status_code=400, detail="Invalid parent comment")
        
        # Create comment
        print(f"Creating ComponentComment object...")
        comment = ComponentComment(
            component_id=component_id,
            user_id=str(current_user.id),
            comment=comment_data.content,  # Map 'content' to 'comment' field
            rating=comment_data.rating,
            parent_comment_id=comment_data.parent_comment_id,
            is_approved=True  # Auto-approve for now
        )
        
        print(f"Inserting comment to database...")
        await comment.insert()
        print(f"Comment inserted successfully with ID: {comment.id}")
        
        # Log audit event (disabled for now to avoid blocking)
        print(f"Audit logging disabled temporarily...")
        try:
            # Temporarily disable audit logging
            pass
            # await log_audit_event(
            #     user_id=str(current_user.id),
            #     action="CREATE_COMPONENT_COMMENT",
            #     resource_type="component_comment",
            #     resource_id=str(comment.id),
            #     details={
            #         "component_id": component_id,
            #         "has_rating": comment_data.rating is not None,
            #         "is_reply": comment_data.parent_comment_id is not None
            #     }
            # )
        except Exception as audit_error:
            print(f"Audit logging failed: {audit_error}")
            # Continue despite audit failure
        
        # Get user info and return response
        print(f"Getting user info...")
        user_info = await get_user_info_component(str(current_user.id), component_id)
        
        print(f"Creating response object...")
        response = ComponentCommentResponse(
            id=str(comment.id),
            component_id=component_id,
            user=user_info,
            content=comment.comment,  # Map 'comment' field back to 'content' for API response
            rating=comment.rating,
            parent_comment_id=comment.parent_comment_id,
            replies_count=0,
            helpful_votes=0,
            has_user_voted_helpful=False,
            is_flagged=comment.is_flagged,
            is_approved=comment.is_approved,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
        
        print(f"Comment created successfully!")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Unexpected error in create_component_comment: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create comment: {str(e)}")


@router.get("/components/{component_id}/comments", response_model=ComponentCommentsResponse)
async def get_component_comments(
    component_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: CommentSortBy = Query(CommentSortBy.newest, description="Sort order"),
    include_replies: bool = Query(True, description="Include comment replies"),
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Get comments for a component with pagination and sorting"""
    try:
        print(f"Getting comments for component: {component_id}")
        
        # Verify component exists
        component = await Component.get(component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        print(f"Component found: {component.title}")
        
        # Convert string ID to ObjectId for querying
        from bson import ObjectId
        component_object_id = ObjectId(component_id)
        
        # Build query
        query = {"component_id": component_object_id, "is_approved": True}
        print(f"Query: {query}")
        
        # Get comments with pagination
        skip = (page - 1) * page_size
        
        # Get total count
        total_count = await ComponentComment.find(query).count()
        print(f"Total comments found: {total_count}")
        
        # Get comments for current page
        sort_field = "created_at"
        sort_direction = -1 if sort_by == CommentSortBy.newest else 1
        
        comments = await ComponentComment.find(query)\
            .sort([(sort_field, sort_direction)])\
            .skip(skip)\
            .limit(page_size)\
            .to_list()
        
        print(f"Comments retrieved: {len(comments)}")
        
        # Build simplified response without user lookups for now  
        comment_responses = []
        for comment in comments:
            print(f"Comment: {comment.id} - {comment.comment[:20]}...")
            
            # Create response with correct field names according to ComponentCommentResponse schema
            comment_response = ComponentCommentResponse(
                id=str(comment.id),
                component_id=str(comment.component_id),
                content=comment.comment,  # content field in schema
                rating=comment.rating,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                is_approved=comment.is_approved,
                helpful_votes=0,  # Will fix later
                replies_count=0,    # replies_count in schema
                # Fixed UserInfo with correct field name 'user' and proper type conversion
                user=UserInfo(
                    id=str(comment.user_id),  # Convert ObjectId to string
                    username="User",
                    profile_picture=None,
                    verified_purchase=False
                )
            )
            comment_responses.append(comment_response)
        
        # Calculate pagination
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0
        
        return ComponentCommentsResponse(
            comments=comment_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            average_rating=None,  # Will calculate later
            rating_distribution={}  # Will calculate later
        )
        
    except Exception as e:
        print(f"Error in get_component_comments: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")


@router.put("/components/{component_id}/comments/{comment_id}", response_model=ComponentCommentResponse)
async def update_component_comment(
    component_id: str,
    comment_id: str,
    comment_data: ComponentCommentUpdate,
    current_user: User = Depends(require_auth)
):
    """Update a component comment (only by comment author)"""
    try:
        # Get comment
        comment = await ComponentComment.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Verify ownership
        if comment.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Can only edit your own comments")
        
        # Verify component match
        if comment.component_id != component_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this component")
        
        # Update fields
        update_data = {}
        if comment_data.content is not None:
            update_data["content"] = comment_data.content
        if comment_data.rating is not None:
            update_data["rating"] = comment_data.rating
        
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await comment.update({"$set": update_data})
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action="UPDATE_COMPONENT_COMMENT",
            resource_type="component_comment",
            resource_id=comment_id,
            details={
                "component_id": component_id,
                "updated_fields": list(update_data.keys())
            }
        )
        
        # Get updated comment
        updated_comment = await ComponentComment.get(comment_id)
        user_info = await get_user_info_component(str(current_user.id), component_id)
        
        # Count replies
        replies_count = await ComponentComment.find({
            "parent_comment_id": comment_id,
            "is_approved": True
        }).count()
        
        # Check if user voted helpful
        user_voted = await ComponentHelpfulVote.find_one({
            "user_id": str(current_user.id),
            "comment_id": comment_id
        })
        
        return ComponentCommentResponse(
            id=str(updated_comment.id),
            component_id=component_id,
            user=user_info,
            content=updated_comment.content,
            rating=updated_comment.rating,
            parent_comment_id=updated_comment.parent_comment_id,
            replies_count=replies_count,
            helpful_votes=updated_comment.helpful_votes,
            has_user_voted_helpful=user_voted is not None,
            is_flagged=updated_comment.is_flagged,
            is_approved=updated_comment.is_approved,
            created_at=updated_comment.created_at,
            updated_at=updated_comment.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update comment: {str(e)}")


@router.delete("/components/{component_id}/comments/{comment_id}")
async def delete_component_comment(
    component_id: str,
    comment_id: str,
    current_user: User = Depends(require_auth)
):
    """Delete a component comment (only by comment author or admin)"""
    try:
        # Get comment
        comment = await ComponentComment.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Verify ownership or admin rights
        if comment.user_id != str(current_user.id) and current_user.role != "Admin":
            raise HTTPException(status_code=403, detail="Can only delete your own comments")
        
        # Verify component match
        if comment.component_id != component_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this component")
        
        # Delete all replies first
        await ComponentComment.find({"parent_comment_id": comment_id}).delete()
        
        # Delete helpful votes
        await ComponentHelpfulVote.find({"comment_id": comment_id}).delete()
        
        # Delete comment
        await comment.delete()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action="DELETE_COMPONENT_COMMENT",
            resource_type="component_comment",
            resource_id=comment_id,
            details={
                "component_id": component_id,
                "deleted_by_admin": current_user.role == "Admin"
            }
        )
        
        return {"message": "Comment deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")


@router.post("/components/{component_id}/comments/{comment_id}/helpful", response_model=ComponentHelpfulVoteResponse)
async def toggle_component_helpful_vote(
    component_id: str,
    comment_id: str,
    current_user: User = Depends(require_auth)
):
    """Toggle helpful vote on a component comment"""
    try:
        # Verify comment exists and belongs to component
        comment = await ComponentComment.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if comment.component_id != component_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this component")
        
        # Check if user already voted
        existing_vote = await ComponentHelpfulVote.find_one({
            "user_id": str(current_user.id),
            "comment_id": comment_id
        })
        
        if existing_vote:
            # Remove vote
            await existing_vote.delete()
            await comment.update({"$inc": {"helpful_votes": -1}})
            action = "REMOVE_COMPONENT_HELPFUL_VOTE"
            message = "Helpful vote removed"
        else:
            # Add vote
            vote = ComponentHelpfulVote(
                user_id=str(current_user.id),
                comment_id=comment_id,
                component_id=component_id
            )
            await vote.insert()
            await comment.update({"$inc": {"helpful_votes": 1}})
            action = "ADD_COMPONENT_HELPFUL_VOTE"
            message = "Helpful vote added"
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action=action,
            resource_type="component_comment",
            resource_id=comment_id,
            details={"component_id": component_id}
        )
        
        # Get updated helpful votes count
        updated_comment = await ComponentComment.get(comment_id)
        
        return ComponentHelpfulVoteResponse(
            success=True,
            message=message,
            helpful_votes=updated_comment.helpful_votes
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle helpful vote: {str(e)}")


@router.get("/components/{component_id}/comments/{comment_id}/replies", response_model=List[ComponentCommentResponse])
async def get_component_comment_replies(
    component_id: str,
    comment_id: str,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Get replies to a specific component comment"""
    try:
        # Verify parent comment exists
        parent_comment = await ComponentComment.get(comment_id)
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        
        if parent_comment.component_id != component_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this component")
        
        # Get replies
        replies = await ComponentComment.find({
            "parent_comment_id": comment_id,
            "is_approved": True
        }).sort([("created_at", 1)]).to_list()
        
        # Get user helpful votes if authenticated
        user_helpful_votes = set()
        if current_user:
            user_votes = await ComponentHelpfulVote.find({
                "user_id": str(current_user.id),
                "comment_id": {"$in": [str(r.id) for r in replies]}
            }).to_list()
            user_helpful_votes = {vote.comment_id for vote in user_votes}
        
        # Build response
        response_replies = []
        for reply in replies:
            user_info = await get_user_info_component(reply.user_id, component_id)
            
            response_replies.append(ComponentCommentResponse(
                id=str(reply.id),
                component_id=component_id,
                user=user_info,
                content=reply.content,
                rating=reply.rating,
                parent_comment_id=reply.parent_comment_id,
                replies_count=0,  # Replies to replies not supported yet
                helpful_votes=reply.helpful_votes,
                has_user_voted_helpful=str(reply.id) in user_helpful_votes,
                is_flagged=reply.is_flagged,
                is_approved=reply.is_approved,
                created_at=reply.created_at,
                updated_at=reply.updated_at
            ))
        
        return response_replies
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get replies: {str(e)}")


@router.post("/components/{component_id}/comments/{comment_id}/flag")
async def flag_component_comment(
    component_id: str,
    comment_id: str,
    current_user: User = Depends(require_auth)
):
    """Flag a component comment for moderation"""
    try:
        # Get comment
        comment = await ComponentComment.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if comment.component_id != component_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this component")
        
        # Update flag status
        await comment.update({"$set": {"is_flagged": True, "updated_at": datetime.utcnow()}})
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action="FLAG_COMPONENT_COMMENT",
            resource_type="component_comment",
            resource_id=comment_id,
            details={"component_id": component_id}
        )
        
        return {"message": "Comment flagged for moderation"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to flag comment: {str(e)}")


@router.get("/components/{component_id}/analytics", response_model=InteractionAnalytics)
async def get_component_analytics(
    component_id: str,
    current_user: User = Depends(require_auth)
):
    """Get interaction analytics for a component (component owner or admin only)"""
    try:
        # Verify component exists
        component = await Component.get(component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Check permissions (component owner or admin)
        if component.developer_id != str(current_user.id) and current_user.role != "Admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get analytics data
        total_likes = await ComponentLike.find({"component_id": component_id}).count()
        total_views = await ComponentView.find({"component_id": component_id}).count()
        total_downloads = await ComponentDownload.find({"component_id": component_id}).count()
        total_comments = await ComponentComment.find({"component_id": component_id, "is_approved": True}).count()
        
        # Calculate rating statistics
        rating_stats = await ComponentComment.aggregate([
            {"$match": {"component_id": component_id, "rating": {"$ne": None}, "is_approved": True}},
            {"$group": {
                "_id": None,
                "avg_rating": {"$avg": "$rating"},
                "ratings": {"$push": "$rating"}
            }}
        ]).to_list()
        
        average_rating = None
        rating_distribution = {}
        
        if rating_stats:
            average_rating = round(rating_stats[0]["avg_rating"], 2)
            ratings = rating_stats[0]["ratings"]
            rating_distribution = {str(i): ratings.count(i) for i in range(1, 6)}
        
        # Get recent activity (last 10 interactions)
        recent_activity = []
        
        # Recent comments
        recent_comments = await ComponentComment.find({
            "component_id": component_id,
            "is_approved": True
        }).sort([("created_at", -1)]).limit(5).to_list()
        
        for comment in recent_comments:
            user = await User.get(comment.user_id)
            recent_activity.append({
                "type": "comment",
                "user": user.username if user else "Unknown",
                "content": comment.content[:100] + "..." if len(comment.content) > 100 else comment.content,
                "created_at": comment.created_at
            })
        
        # Recent likes
        recent_likes = await ComponentLike.find({
            "component_id": component_id
        }).sort([("created_at", -1)]).limit(5).to_list()
        
        for like in recent_likes:
            user = await User.get(like.user_id)
            recent_activity.append({
                "type": "like",
                "user": user.username if user else "Unknown",
                "created_at": like.created_at
            })
        
        # Sort recent activity by date
        recent_activity.sort(key=lambda x: x["created_at"], reverse=True)
        recent_activity = recent_activity[:10]  # Keep only 10 most recent
        
        return InteractionAnalytics(
            total_comments=total_comments,
            total_likes=total_likes,
            total_views=total_views,
            total_downloads=total_downloads,
            average_rating=average_rating,
            rating_distribution=rating_distribution,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")
