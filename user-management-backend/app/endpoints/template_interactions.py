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
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    verified_purchase = False
    if template_id:
        # Check if user has purchased this template
        from app.models.purchased_item import PurchasedItem
        purchase = await PurchasedItem.find_one({
            "user_id": user_id,
            "item_id": template_id,
            "item_type": "template"
        })
        verified_purchase = purchase is not None
    
    return UserInfo(
        id=str(user.id),
        username=user.username,
        profile_picture=user.profile_picture,
        verified_purchase=verified_purchase
    )


@router.post("/templates/{template_id}/comments", response_model=TemplateCommentResponse)
async def create_template_comment(
    template_id: str,
    comment_data: TemplateCommentCreate,
    current_user: User = Depends(require_auth)
):
    """Create a new comment on a template"""
    try:
        # Verify template exists
        template = await Template.get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Validate parent comment if provided
        if comment_data.parent_comment_id:
            parent_comment = await TemplateCommentEnhanced.get(comment_data.parent_comment_id)
            if not parent_comment or parent_comment.template_id != template_id:
                raise HTTPException(status_code=400, detail="Invalid parent comment")
        
        # Create comment
        comment = TemplateCommentEnhanced(
            template_id=template_id,
            user_id=str(current_user.id),
            content=comment_data.content,
            rating=comment_data.rating,
            parent_comment_id=comment_data.parent_comment_id,
            is_approved=True  # Auto-approve for now
        )
        
        await comment.insert()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action="CREATE_TEMPLATE_COMMENT",
            resource_type="template_comment",
            resource_id=str(comment.id),
            details={
                "template_id": template_id,
                "has_rating": comment_data.rating is not None,
                "is_reply": comment_data.parent_comment_id is not None
            }
        )
        
        # Get user info and return response
        user_info = await get_user_info(str(current_user.id), template_id)
        
        return TemplateCommentResponse(
            id=str(comment.id),
            template_id=template_id,
            user=user_info,
            content=comment.content,
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
        
    except Exception as e:
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
        
        # Build query for top-level comments (no parent)
        query = {"template_id": template_id, "is_approved": True}
        if not include_replies:
            query["parent_comment_id"] = None
        
        # Apply sorting
        sort_options = {
            CommentSortBy.newest: [("created_at", -1)],
            CommentSortBy.oldest: [("created_at", 1)],
            CommentSortBy.most_helpful: [("helpful_votes", -1), ("created_at", -1)],
            CommentSortBy.rating_high: [("rating", -1), ("created_at", -1)],
            CommentSortBy.rating_low: [("rating", 1), ("created_at", -1)]
        }
        
        sort_criteria = sort_options.get(sort_by, [("created_at", -1)])
        
        # Get total count
        total_count = await TemplateCommentEnhanced.count(query)
        
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
            user_info = await get_user_info(comment.user_id, template_id)
            
            response_comments.append(TemplateCommentResponse(
                id=str(comment.id),
                template_id=template_id,
                user=user_info,
                content=comment.content,
                rating=comment.rating,
                parent_comment_id=comment.parent_comment_id,
                replies_count=reply_counts.get(str(comment.id), 0),
                helpful_votes=comment.helpful_votes,
                has_user_voted_helpful=str(comment.id) in user_helpful_votes,
                is_flagged=comment.is_flagged,
                is_approved=comment.is_approved,
                created_at=comment.created_at,
                updated_at=comment.updated_at
            ))
        
        # Calculate rating statistics
        rating_stats = await TemplateCommentEnhanced.aggregate([
            {"$match": {"template_id": template_id, "rating": {"$ne": None}, "is_approved": True}},
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
    current_user: User = Depends(require_auth)
):
    """Update a template comment (only by comment author)"""
    try:
        # Get comment
        comment = await TemplateCommentEnhanced.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Verify ownership
        if comment.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Can only edit your own comments")
        
        # Verify template match
        if comment.template_id != template_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this template")
        
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
            action="UPDATE_TEMPLATE_COMMENT",
            resource_type="template_comment",
            resource_id=comment_id,
            details={
                "template_id": template_id,
                "updated_fields": list(update_data.keys())
            }
        )
        
        # Get updated comment
        updated_comment = await TemplateCommentEnhanced.get(comment_id)
        user_info = await get_user_info(str(current_user.id), template_id)
        
        # Count replies
        replies_count = await TemplateCommentEnhanced.count({
            "parent_comment_id": comment_id,
            "is_approved": True
        })
        
        # Check if user voted helpful
        user_voted = await TemplateHelpfulVote.find_one({
            "user_id": str(current_user.id),
            "comment_id": comment_id
        })
        
        return TemplateCommentResponse(
            id=str(updated_comment.id),
            template_id=template_id,
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


@router.delete("/templates/{template_id}/comments/{comment_id}")
async def delete_template_comment(
    template_id: str,
    comment_id: str,
    current_user: User = Depends(require_auth)
):
    """Delete a template comment (only by comment author or admin)"""
    try:
        # Get comment
        comment = await TemplateCommentEnhanced.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Verify ownership or admin rights
        if comment.user_id != str(current_user.id) and current_user.role != "Admin":
            raise HTTPException(status_code=403, detail="Can only delete your own comments")
        
        # Verify template match
        if comment.template_id != template_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this template")
        
        # Delete all replies first
        await TemplateCommentEnhanced.find({"parent_comment_id": comment_id}).delete()
        
        # Delete helpful votes
        await TemplateHelpfulVote.find({"comment_id": comment_id}).delete()
        
        # Delete comment
        await comment.delete()
        
        # Log audit event
        await log_audit_event(
            user_id=str(current_user.id),
            action="DELETE_TEMPLATE_COMMENT",
            resource_type="template_comment",
            resource_id=comment_id,
            details={
                "template_id": template_id,
                "deleted_by_admin": current_user.role == "Admin"
            }
        )
        
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
            await comment.update({"$inc": {"helpful_votes": -1}})
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
            await comment.update({"$inc": {"helpful_votes": 1}})
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
            helpful_votes=updated_comment.helpful_votes
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
