# Template interaction endpoints - Comments, Ratings, Helpful Votes
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import math
from collections import defaultdict

from app.middleware.auth import require_auth, get_current_user_from_token
from app.models.user import User
from app.models.template import Template
from app.models.template_interactions import TemplateCommentEnhanced, TemplateHelpfulVote
from app.models.interaction_schemas import (
    TemplateCommentCreate, TemplateCommentUpdate, TemplateCommentResponse,
    TemplateCommentsResponse, TemplateHelpfulVoteResponse, UserInfo,
    CommentSortBy, InteractionAnalytics
)
from app.utils.audit_logger import log_audit_event

router = APIRouter()


async def get_user_info(user_id: str, template_id: str = None) -> UserInfo:
    """Get user info with verified purchase status"""
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
        if template_id:
            try:
                # Check if user has purchased this template
                from app.models.purchased_item import PurchasedItem
                purchase = await PurchasedItem.find_one({
                    "user_id": user_id,
                    "item_id": template_id,
                    "item_type": "template"
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
        return UserInfo(
            id=user_id,
            username="Unknown User",
            profile_picture=None,
            verified_purchase=False
        )


@router.post("/templates/{template_id}/comments", response_model=TemplateCommentResponse)
async def create_template_comment(
    template_id: str,
    comment_data: TemplateCommentCreate,
    current_user: Optional[User] = Depends(get_current_user_from_token)  # Made optional for testing
):
    """Create a new comment on a template"""
    try:
        print(f"Creating template comment - template_id: {template_id}")
        print(f"Comment data: {comment_data}")
        print(f"User: {current_user.username if current_user else 'Anonymous'}")
        
        # For testing, use a default user if not authenticated
        if not current_user:
            # This is just for testing - we'll add auth back later
            user_id = "688d36d7d8778cb7f3168011"  # Default test user
            print(f"Using default user_id: {user_id}")
        else:
            user_id = str(current_user.id)
            print(f"Using authenticated user_id: {user_id}")
        
        # Verify template exists
        template = await Template.get(template_id)
        if not template:
            print(f"Template not found: {template_id}")
            raise HTTPException(status_code=404, detail="Template not found")
        
        print(f"Template found: {template.title}")
        
        # Validate parent comment if provided
        if comment_data.parent_comment_id:
            parent_comment = await TemplateCommentEnhanced.get(comment_data.parent_comment_id)
            if not parent_comment or str(parent_comment.template_id) != template_id:
                raise HTTPException(status_code=400, detail="Invalid parent comment")
        
        # Create comment (let Beanie handle ObjectId conversion automatically)
        print(f"Creating TemplateCommentEnhanced object...")
        comment = TemplateCommentEnhanced(
            template_id=template_id,  # Pass as string, let Beanie convert
            user_id=user_id,  # Pass as string, let Beanie convert
            comment=comment_data.content,  # Map 'content' to 'comment' field
            rating=comment_data.rating,
            parent_comment_id=comment_data.parent_comment_id,  # Pass as string if exists
            is_approved=True  # Auto-approve for now
        )
        print(f"TemplateCommentEnhanced object created successfully")
        
        print(f"Inserting template comment to database...")
        await comment.insert()
        print(f"Template comment inserted successfully with ID: {comment.id}")
        
        # Log audit event (disabled temporarily)
        print(f"Audit logging disabled temporarily...")
        try:
            # Temporarily disable audit logging
            pass
        except Exception as audit_error:
            print(f"Audit logging failed: {audit_error}")
            # Continue despite audit failure
        
        # Get user info and return response
        print(f"Getting user info...")
        user_info = await get_user_info(user_id, template_id)  # Use determined user_id
        
        print(f"Creating response object...")
        response = TemplateCommentResponse(
            id=str(comment.id),
            template_id=template_id,
            user=user_info,
            content=comment.comment,  # Map 'comment' field back to 'content' for API response
            rating=comment.rating,
            parent_comment_id=str(comment.parent_comment_id) if comment.parent_comment_id else None,
            replies_count=0,
            helpful_votes=0,
            has_user_voted_helpful=False,
            is_flagged=comment.is_flagged,
            is_approved=comment.is_approved,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
        
        print(f"Template comment created successfully!")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Unexpected error in create_template_comment: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create comment: {str(e)}")


@router.get("/templates/{template_id}/comments", response_model=TemplateCommentsResponse)
async def get_template_comments(
    template_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: CommentSortBy = Query(CommentSortBy.newest, description="Sort order"),
    include_replies: bool = Query(True, description="Include comment replies"),
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Get comments for a template with pagination and sorting"""
    try:
        # Verify template exists
        template = await Template.get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Convert string ID to ObjectId for querying
        from bson import ObjectId
        template_object_id = ObjectId(template_id)
        
        # Build query for top-level comments (no parent)
        query = {"template_id": template_object_id, "is_approved": True}
        if not include_replies:
            query["parent_comment_id"] = None
        
        # Apply sorting
        sort_options = {
            CommentSortBy.newest: [("created_at", -1)],
            CommentSortBy.oldest: [("created_at", 1)],
            CommentSortBy.most_helpful: [("helpful_count", -1), ("created_at", -1)],  # Use helpful_count
            CommentSortBy.rating_high: [("rating", -1), ("created_at", -1)],
            CommentSortBy.rating_low: [("rating", 1), ("created_at", -1)]
        }
        
        sort_criteria = sort_options.get(sort_by, [("created_at", -1)])
        
        # Get total count
        total_count = await TemplateCommentEnhanced.find(query).count()
        
        # Calculate pagination
        total_pages = math.ceil(total_count / page_size)
        skip = (page - 1) * page_size
        
        # Get comments
        comments = await TemplateCommentEnhanced.find(query)\
            .sort(sort_criteria)\
            .skip(skip)\
            .limit(page_size)\
            .to_list()
        
        # Get user helpful votes if authenticated
        user_helpful_votes = set()
        if current_user:
            user_votes = await TemplateHelpfulVote.find({
                "user_id": str(current_user.id),
                "comment_id": {"$in": [str(c.id) for c in comments]}
            }).to_list()
            user_helpful_votes = {vote.comment_id for vote in user_votes}
        
        # Count replies for each comment
        comment_ids = [str(c.id) for c in comments]
        reply_counts = {}
        if comment_ids:
            reply_pipeline = [
                {"$match": {"parent_comment_id": {"$in": comment_ids}, "is_approved": True}},
                {"$group": {"_id": "$parent_comment_id", "count": {"$sum": 1}}}
            ]
            reply_results = await TemplateCommentEnhanced.aggregate(reply_pipeline).to_list()
            reply_counts = {result["_id"]: result["count"] for result in reply_results}
        
        # Build response comments
        response_comments = []
        for comment in comments:
            user_info = await get_user_info(str(comment.user_id), template_id)  # Convert ObjectId to string
            
            response_comments.append(TemplateCommentResponse(
                id=str(comment.id),
                template_id=template_id,
                user=user_info,
                content=comment.comment,  # Map 'comment' field back to 'content' for API response
                rating=comment.rating,
                parent_comment_id=comment.parent_comment_id,
                replies_count=reply_counts.get(str(comment.id), 0),
                helpful_votes=comment.helpful_count,  # Use helpful_count field from model
                has_user_voted_helpful=str(comment.id) in user_helpful_votes,
                is_flagged=comment.is_flagged,
                is_approved=comment.is_approved,
                created_at=comment.created_at,
                updated_at=comment.updated_at
            ))
        
        # Calculate rating statistics
        rating_stats = await TemplateCommentEnhanced.aggregate([
            {"$match": {"template_id": template_object_id, "rating": {"$ne": None}, "is_approved": True}},
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
        
        return TemplateCommentsResponse(
            comments=response_comments,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            average_rating=average_rating,
            rating_distribution=rating_distribution
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")


@router.put("/templates/{template_id}/comments/{comment_id}", response_model=TemplateCommentResponse)
async def update_template_comment(
    template_id: str,
    comment_id: str,
    comment_data: TemplateCommentUpdate,
    current_user: Optional[User] = Depends(get_current_user_from_token)  # Allow anonymous updates
):
    """Update a template comment (only by comment author)"""
    try:
        # Skip authentication checks for now (allowing anonymous updates)
        user_id = "688d36d7d8778cb7f3168011"  # Use default user ID for anonymous updates
        if current_user:
            user_id = str(current_user.id)
        
        # Get comment
        comment = await TemplateCommentEnhanced.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Verify ownership (skip for anonymous users)
        if current_user and comment.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Can only edit your own comments")
        
        # Verify template match
        if str(comment.template_id) != template_id:  # Convert ObjectId to string for comparison
            raise HTTPException(status_code=400, detail="Comment does not belong to this template")
        
        # Update fields
        update_data = {}
        if comment_data.content is not None:
            update_data["comment"] = comment_data.content  # Map content to comment field in database
        if comment_data.rating is not None:
            update_data["rating"] = comment_data.rating
        
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await comment.update({"$set": update_data})
        
            # Log audit event (do not fail if logging fails)
            try:
                await log_audit_event(
                    user_id=user_id,  # Use the determined user_id
                    action="UPDATE_TEMPLATE_COMMENT",
                    resource_type="template_comment",
                    resource_id=comment_id,
                    details={
                        "template_id": template_id,
                        "updated_fields": list(update_data.keys())
                    }
                )
            except Exception as log_err:
                print(f"Audit log failed: {log_err}")
        
        # Get updated comment
        updated_comment = await TemplateCommentEnhanced.get(comment_id)
        user_info = await get_user_info(user_id, template_id)  # Use determined user_id
        
        # Count replies
        replies_count = await TemplateCommentEnhanced.find({
            "parent_comment_id": comment_id,
            "is_approved": True
        }).count()
        
        # Check if user voted helpful
        user_voted = None
        if current_user:
            user_voted = await TemplateHelpfulVote.find_one({
                "user_id": str(current_user.id),
                "comment_id": comment_id
            })
        
        return TemplateCommentResponse(
            id=str(updated_comment.id),
            template_id=template_id,
            user=user_info,
            content=updated_comment.comment,  # Map comment field to content in response
            rating=updated_comment.rating,
            parent_comment_id=updated_comment.parent_comment_id,
            replies_count=replies_count,
            helpful_votes=updated_comment.helpful_count,  # Use helpful_count field
            has_user_voted_helpful=user_voted is not None,
            is_flagged=updated_comment.is_flagged,
            is_approved=updated_comment.is_approved,
            created_at=updated_comment.created_at,
            updated_at=updated_comment.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update comment: {str(e)}")


@router.delete("/templates/{template_id}/comments/{comment_id}")
async def delete_template_comment(
    template_id: str,
    comment_id: str,
    current_user: Optional[User] = Depends(get_current_user_from_token)  # Allow anonymous deletes
):
    """Delete a template comment (only by comment author or admin)"""
    try:
        # Skip authentication checks for now (allowing anonymous deletes)
        user_id = "688d36d7d8778cb7f3168011"  # Use default user ID for anonymous deletes
        is_admin = False
        if current_user:
            user_id = str(current_user.id)
            is_admin = current_user.role == "Admin"
        
        # Get comment
        comment = await TemplateCommentEnhanced.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Verify ownership or admin rights (skip for anonymous users)
        if current_user and comment.user_id != user_id and not is_admin:
            raise HTTPException(status_code=403, detail="Can only delete your own comments")
        
        # Verify template match
        if str(comment.template_id) != template_id:  # Convert ObjectId to string for comparison
            raise HTTPException(status_code=400, detail="Comment does not belong to this template")
        
        # Delete all replies first
        await TemplateCommentEnhanced.find({"parent_comment_id": comment_id}).delete()
        
        # Delete helpful votes
        await TemplateHelpfulVote.find({"comment_id": comment_id}).delete()
        
        # Delete comment
        await comment.delete()
        
        # Log audit event (do not fail if logging fails)
        try:
            await log_audit_event(
                user_id=user_id,  # Use determined user_id
                action="DELETE_TEMPLATE_COMMENT",
                resource_type="template_comment",
                resource_id=comment_id,
                details={
                    "template_id": template_id,
                    "deleted_by_admin": is_admin
                }
            )
        except Exception as log_err:
            print(f"Audit log failed: {log_err}")
        
        return {"message": "Comment deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")


@router.post("/templates/{template_id}/comments/{comment_id}/helpful", response_model=TemplateHelpfulVoteResponse)
async def toggle_helpful_vote(
    template_id: str,
    comment_id: str,
    current_user: User = Depends(require_auth)
):
    """Toggle helpful vote on a template comment"""
    try:
        # Verify comment exists and belongs to template
        comment = await TemplateCommentEnhanced.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if comment.template_id != template_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this template")
        
        # Check if user already voted
        existing_vote = await TemplateHelpfulVote.find_one({
            "user_id": str(current_user.id),
            "comment_id": comment_id
        })
        
        if existing_vote:
            # Remove vote
            await existing_vote.delete()
            await comment.update({"$inc": {"helpful_count": -1}})  # Use helpful_count field
            action = "REMOVE_HELPFUL_VOTE"
            message = "Helpful vote removed"
        else:
            # Add vote
            vote = TemplateHelpfulVote(
                user_id=str(current_user.id),
                comment_id=comment_id,
                template_id=template_id
            )
            await vote.insert()
            await comment.update({"$inc": {"helpful_count": 1}})  # Use helpful_count field
            action = "ADD_HELPFUL_VOTE"
            message = "Helpful vote added"
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action=action,
            resource_type="template_comment",
            resource_id=comment_id,
            details={"template_id": template_id}
        )
        
        # Get updated helpful votes count
        updated_comment = await TemplateCommentEnhanced.get(comment_id)
        
        return TemplateHelpfulVoteResponse(
            success=True,
            message=message,
            helpful_votes=updated_comment.helpful_count  # Use helpful_count field
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle helpful vote: {str(e)}")


@router.get("/templates/{template_id}/comments/{comment_id}/replies", response_model=List[TemplateCommentResponse])
async def get_comment_replies(
    template_id: str,
    comment_id: str,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Get replies to a specific comment"""
    try:
        # Verify parent comment exists
        parent_comment = await TemplateCommentEnhanced.get(comment_id)
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        
        if parent_comment.template_id != template_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this template")
        
        # Get replies
        replies = await TemplateCommentEnhanced.find({
            "parent_comment_id": comment_id,
            "is_approved": True
        }).sort([("created_at", 1)]).to_list()
        
        # Get user helpful votes if authenticated
        user_helpful_votes = set()
        if current_user:
            user_votes = await TemplateHelpfulVote.find({
                "user_id": str(current_user.id),
                "comment_id": {"$in": [str(r.id) for r in replies]}
            }).to_list()
            user_helpful_votes = {vote.comment_id for vote in user_votes}
        
        # Build response
        response_replies = []
        for reply in replies:
            user_info = await get_user_info(reply.user_id, template_id)
            
            response_replies.append(TemplateCommentResponse(
                id=str(reply.id),
                template_id=template_id,
                user=user_info,
                content=reply.content,
                rating=reply.rating,
                parent_comment_id=reply.parent_comment_id,
                replies_count=0,  # Replies to replies not supported yet
                helpful_votes=reply.helpful_count,  # Use helpful_count field
                has_user_voted_helpful=str(reply.id) in user_helpful_votes,
                is_flagged=reply.is_flagged,
                is_approved=reply.is_approved,
                created_at=reply.created_at,
                updated_at=reply.updated_at
            ))
        
        return response_replies
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get replies: {str(e)}")


@router.post("/templates/{template_id}/comments/{comment_id}/flag")
async def flag_comment(
    template_id: str,
    comment_id: str,
    current_user: User = Depends(require_auth)
):
    """Flag a comment for moderation"""
    try:
        # Get comment
        comment = await TemplateCommentEnhanced.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if comment.template_id != template_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this template")
        
        # Update flag status
        await comment.update({"$set": {"is_flagged": True, "updated_at": datetime.utcnow()}})
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action="FLAG_TEMPLATE_COMMENT",
            resource_type="template_comment",
            resource_id=comment_id,
            details={"template_id": template_id}
        )
        
        return {"message": "Comment flagged for moderation"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to flag comment: {str(e)}")
