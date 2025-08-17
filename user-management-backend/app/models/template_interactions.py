"""
Enhanced template interaction models with comprehensive comment, rating, and interaction features.
"""

from datetime import datetime
from typing import Optional, List
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class TemplateCommentEnhanced(Document):
    """Enhanced template comments with rating, replies, and moderation support."""
    
    template_id: PydanticObjectId
    user_id: PydanticObjectId
    comment: str = Field(min_length=1, max_length=2000)
    rating: Optional[int] = Field(None, ge=1, le=5)  # 1-5 stars
    parent_comment_id: Optional[PydanticObjectId] = None  # For replies
    is_verified_purchase: bool = False
    is_approved: bool = True  # Admin moderation
    is_flagged: bool = False
    helpful_count: int = 0
    unhelpful_count: int = 0
    reply_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "template_comments_enhanced"
        indexes = [
            "template_id",
            "user_id", 
            "parent_comment_id",
            "created_at",
            "rating",
            "is_approved",
            "is_flagged",
            [("template_id", 1), ("is_approved", 1), ("created_at", -1)]
        ]
    
    def to_dict(self) -> dict:
        """Convert to dictionary with string IDs."""
        return {
            "id": str(self.id),
            "template_id": str(self.template_id),
            "user_id": str(self.user_id),
            "comment": self.comment,
            "rating": self.rating,
            "parent_comment_id": str(self.parent_comment_id) if self.parent_comment_id else None,
            "is_verified_purchase": self.is_verified_purchase,
            "is_approved": self.is_approved,
            "is_flagged": self.is_flagged,
            "helpful_count": self.helpful_count,
            "unhelpful_count": self.unhelpful_count,
            "reply_count": self.reply_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class TemplateHelpfulVote(Document):
    """Track helpful/unhelpful votes on template comments."""
    
    class Settings:
        name = "template_helpful_votes"
        arbitrary_types_allowed = True
        indexes = [
            [("comment_id", 1), ("user_id", 1)],  # Unique vote per user per comment
            "comment_id",
            "user_id", 
            "created_at"
        ]
    
    comment_id: PydanticObjectId
    user_id: PydanticObjectId
    is_helpful: bool  # True = helpful, False = unhelpful
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Pydantic models for requests/responses
class TemplateCommentCreate(BaseModel):
    """Request model for creating template comments."""
    content: str = Field(min_length=1, max_length=2000)
    rating: Optional[int] = Field(None, ge=1, le=5)
    parent_comment_id: Optional[str] = None


class TemplateCommentUpdate(BaseModel):
    """Request model for updating template comments."""
    content: Optional[str] = Field(None, min_length=1, max_length=2000)
    rating: Optional[int] = Field(None, ge=1, le=5)


class TemplateCommentResponse(BaseModel):
    """Response model for template comments with user details."""
    id: str
    template_id: str
    comment: str
    rating: Optional[int] = None
    parent_comment_id: Optional[str] = None
    is_verified_purchase: bool
    is_approved: bool
    helpful_count: int
    unhelpful_count: int
    reply_count: int
    created_at: str
    updated_at: str
    user: dict  # User details
    replies: List["TemplateCommentResponse"] = []  # For nested replies


class TemplateRatingStats(BaseModel):
    """Template rating statistics."""
    average_rating: float = 0.0
    total_ratings: int = 0
    rating_distribution: dict = Field(default_factory=lambda: {
        "5_star": 0, "4_star": 0, "3_star": 0, "2_star": 0, "1_star": 0
    })


class TemplateInteractionStats(BaseModel):
    """Complete template interaction statistics."""
    likes: int = 0
    views: int = 0
    downloads: int = 0
    comments: int = 0
    rating_stats: TemplateRatingStats = TemplateRatingStats()


class CommentModerationRequest(BaseModel):
    """Request model for comment moderation."""
    action: str = Field(..., pattern="^(approve|reject|flag|unflag)$")
    reason: Optional[str] = None
    admin_notes: Optional[str] = None


class HelpfulVoteRequest(BaseModel):
    """Request model for marking comments as helpful/unhelpful."""
    is_helpful: bool


# Allow forward references
TemplateCommentResponse.model_rebuild()
