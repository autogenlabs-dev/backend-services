"""
Component interaction models for likes, comments, views, and downloads.
Provides comprehensive interaction tracking for marketplace components.
"""

from datetime import datetime
from typing import Optional, List
from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field


class ComponentLike(Document):
    """Track component likes from users."""
    
    class Settings:
        name = "component_likes"
        indexes = [
            [("component_id", 1), ("user_id", 1)],  # Unique constraint
            "component_id",
            "user_id",
            "created_at"
        ]
    
    component_id: PydanticObjectId
    user_id: PydanticObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ComponentComment(Document):
    """Component comments with rating and reply support."""
    
    class Settings:
        name = "component_comments"
        indexes = [
            "component_id",
            "user_id", 
            "parent_comment_id",
            "created_at",
            "rating",
            "is_approved",
            "is_flagged",
            [("component_id", 1), ("is_approved", 1), ("created_at", -1)]
        ]
    
    component_id: PydanticObjectId
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
    
    def to_dict(self) -> dict:
        """Convert to dictionary with string IDs."""
        return {
            "id": str(self.id),
            "component_id": str(self.component_id),
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


class ComponentView(Document):
    """Track component views."""
    
    class Settings:
        name = "component_views"
        indexes = [
            "component_id",
            "user_id",
            "created_at",
            "ip_address"
        ]
    
    component_id: PydanticObjectId
    user_id: Optional[PydanticObjectId] = None  # Anonymous views allowed
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ComponentDownload(Document):
    """Track component downloads."""
    
    class Settings:
        name = "component_downloads"
        indexes = [
            "component_id",
            "user_id",
            "created_at",
            [("component_id", 1), ("user_id", 1), ("created_at", -1)]
        ]
    
    component_id: PydanticObjectId
    user_id: PydanticObjectId
    download_type: str = "full"  # full, preview, source
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ComponentHelpfulVote(Document):
    """Track helpful/unhelpful votes on component comments."""
    
    class Settings:
        name = "component_helpful_votes"
        indexes = [
            [("comment_id", 1), ("user_id", 1)],  # Unique constraint
            "comment_id",
            "user_id", 
            "created_at"
        ]
    
    comment_id: PydanticObjectId
    user_id: PydanticObjectId
    is_helpful: bool  # True = helpful, False = unhelpful
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Pydantic models for requests/responses
class ComponentCommentCreate(BaseModel):
    """Request model for creating component comments."""
    comment: str = Field(min_length=1, max_length=2000)
    rating: Optional[int] = Field(None, ge=1, le=5)
    parent_comment_id: Optional[str] = None


class ComponentCommentUpdate(BaseModel):
    """Request model for updating component comments."""
    comment: Optional[str] = Field(None, min_length=1, max_length=2000)
    rating: Optional[int] = Field(None, ge=1, le=5)


class ComponentCommentResponse(BaseModel):
    """Response model for component comments with user details."""
    id: str
    component_id: str
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
    replies: List["ComponentCommentResponse"] = []  # For nested replies


class ComponentRatingStats(BaseModel):
    """Component rating statistics."""
    average_rating: float = 0.0
    total_ratings: int = 0
    rating_distribution: dict = Field(default_factory=lambda: {
        "5_star": 0, "4_star": 0, "3_star": 0, "2_star": 0, "1_star": 0
    })


class ComponentInteractionStats(BaseModel):
    """Complete component interaction statistics."""
    likes: int = 0
    views: int = 0
    downloads: int = 0
    comments: int = 0
    rating_stats: ComponentRatingStats = ComponentRatingStats()


# Allow forward references
ComponentCommentResponse.model_rebuild()
