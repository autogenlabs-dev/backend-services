# Enhanced interaction schemas for templates and components
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CommentSortBy(str, Enum):
    """Sort options for comments"""
    newest = "newest"
    oldest = "oldest"
    most_helpful = "most_helpful"
    rating_high = "rating_high"
    rating_low = "rating_low"


class ModerationAction(str, Enum):
    """Moderation actions"""
    approve = "approve"
    reject = "reject"
    flag = "flag"
    unflag = "unflag"


# Template Comment Schemas
class TemplateCommentCreate(BaseModel):
    """Create template comment request"""
    content: str = Field(..., min_length=10, max_length=2000, description="Comment content")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5 stars")
    parent_comment_id: Optional[str] = Field(None, description="Parent comment for replies")


class TemplateCommentUpdate(BaseModel):
    """Update template comment request"""
    content: Optional[str] = Field(None, min_length=10, max_length=2000)
    rating: Optional[int] = Field(None, ge=1, le=5)


class UserInfo(BaseModel):
    """User information for responses"""
    id: str
    username: str
    profile_picture: Optional[str] = None
    verified_purchase: bool = False


class TemplateCommentResponse(BaseModel):
    """Template comment response with user details"""
    id: str
    template_id: str
    user: UserInfo
    content: str
    rating: Optional[int] = None
    parent_comment_id: Optional[str] = None
    replies_count: int = 0
    helpful_votes: int = 0
    has_user_voted_helpful: bool = False
    is_flagged: bool = False
    is_approved: bool = True
    created_at: datetime
    updated_at: datetime


class TemplateCommentsResponse(BaseModel):
    """Template comments list response"""
    comments: List[TemplateCommentResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    average_rating: Optional[float] = None
    rating_distribution: dict = Field(default_factory=dict)


class TemplateHelpfulVoteResponse(BaseModel):
    """Helpful vote response"""
    success: bool
    message: str
    helpful_votes: int


# Component Comment Schemas
class ComponentCommentCreate(BaseModel):
    """Create component comment request"""
    content: str = Field(..., min_length=10, max_length=2000, description="Comment content")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5 stars")
    parent_comment_id: Optional[str] = Field(None, description="Parent comment for replies")


class ComponentCommentUpdate(BaseModel):
    """Update component comment request"""
    content: Optional[str] = Field(None, min_length=10, max_length=2000)
    rating: Optional[int] = Field(None, ge=1, le=5)


class ComponentCommentResponse(BaseModel):
    """Component comment response with user details"""
    id: str
    component_id: str
    user: UserInfo
    content: str
    rating: Optional[int] = None
    parent_comment_id: Optional[str] = None
    replies_count: int = 0
    helpful_votes: int = 0
    has_user_voted_helpful: bool = False
    is_flagged: bool = False
    is_approved: bool = True
    created_at: datetime
    updated_at: datetime


class ComponentCommentsResponse(BaseModel):
    """Component comments list response"""
    comments: List[ComponentCommentResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    average_rating: Optional[float] = None
    rating_distribution: dict = Field(default_factory=dict)


class ComponentHelpfulVoteResponse(BaseModel):
    """Component helpful vote response"""
    success: bool
    message: str
    helpful_votes: int


# Component Like Schemas
class ComponentLikeResponse(BaseModel):
    """Component like response"""
    success: bool
    message: str
    total_likes: int
    user_has_liked: bool


# Admin Moderation Schemas
class AdminCommentResponse(BaseModel):
    """Admin comment response for moderation"""
    id: str
    content_type: str  # "template" or "component"
    content_id: str
    content_title: str
    user: UserInfo
    content: str
    rating: Optional[int] = None
    is_flagged: bool = False
    is_approved: bool = True
    flag_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AdminCommentsResponse(BaseModel):
    """Admin comments list response"""
    comments: List[AdminCommentResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class AdminModerationRequest(BaseModel):
    """Admin moderation request"""
    action: ModerationAction
    reason: Optional[str] = Field(None, max_length=500, description="Reason for moderation action")


class AdminModerationResponse(BaseModel):
    """Admin moderation response"""
    success: bool
    message: str
    comment_id: str
    action: str


# Analytics Schemas
class InteractionAnalytics(BaseModel):
    """Interaction analytics response"""
    total_comments: int
    total_likes: int
    total_views: int
    total_downloads: int
    average_rating: Optional[float] = None
    rating_distribution: dict = Field(default_factory=dict)
    recent_activity: List[dict] = Field(default_factory=list)


class ContentAnalytics(BaseModel):
    """Content analytics response"""
    template_analytics: InteractionAnalytics
    component_analytics: InteractionAnalytics
    top_rated_templates: List[dict] = Field(default_factory=list)
    top_rated_components: List[dict] = Field(default_factory=list)
    most_active_users: List[dict] = Field(default_factory=list)
