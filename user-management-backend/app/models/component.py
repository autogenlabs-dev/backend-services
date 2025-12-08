from beanie import Document, PydanticObjectId
from typing import List, Optional, Dict, Union
from datetime import datetime
from pydantic import Field
from enum import Enum

class ContentStatus(str, Enum):
    """Content status enumeration"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class Component(Document):
    title: str
    category: str
    type: str
    language: str
    difficulty_level: str
    plan_type: str
    short_description: str
    full_description: str
    preview_images: List[str] = Field(default_factory=list)
    git_repo_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    developer_name: str
    developer_experience: str
    is_available_for_dev: bool = True
    featured: bool = False
    code: Optional[Union[str, Dict[str, str]]] = None
    html_code: Optional[str] = None
    css_code: Optional[str] = None
    preview_code: Optional[str] = None
    readme_content: Optional[str] = None
    user_id: Optional[PydanticObjectId] = None
    
    # New fields for approval workflow
    approval_status: ContentStatus = ContentStatus.PENDING_APPROVAL
    submitted_for_approval_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[PydanticObjectId] = None
    rejection_reason: Optional[str] = None
    
    # Purchase and interaction tracking
    is_purchasable: bool = True
    purchase_count: int = 0
    rating: float = 0.0
    downloads: int = 0
    views: int = 0
    likes: int = 0
    average_rating: float = 0.0
    total_ratings: int = 0
    comments_count: int = 0
    last_comment_at: Optional[datetime] = None
    
    # Rating distribution
    rating_distribution: Dict[str, int] = Field(default_factory=lambda: {
        "5_star": 0,
        "4_star": 0,
        "3_star": 0,
        "2_star": 0,
        "1_star": 0
    })
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "components"
        indexes = [
            "user_id",
            "category",
            "type",
            "plan_type",
            "approval_status",
            "featured",
            "created_at",
            [("category", 1), ("type", 1)],
            [("approval_status", 1), ("created_at", -1)],
            [("average_rating", -1)],
            [("purchase_count", -1)]
        ]

    @property
    def status(self):
        """Compatibility property for frontend"""
        return self.approval_status

    def to_dict(self):
        """Convert component to dictionary for API responses"""
        # Explicitly create dict to ensure all fields are properly serialized
        # This matches the Template model pattern which works correctly
        data = {
            'id': str(self.id) if self.id else None,
            'title': self.title,
            'category': self.category,
            'type': self.type,
            'language': self.language,
            'difficulty_level': self.difficulty_level,
            'plan_type': self.plan_type,
            'short_description': self.short_description,
            'full_description': self.full_description,
            'preview_images': self.preview_images or [],
            'git_repo_url': self.git_repo_url,
            'live_demo_url': self.live_demo_url,
            'dependencies': self.dependencies or [],
            'tags': self.tags or [],
            'developer_name': self.developer_name,
            'developer_experience': self.developer_experience,
            'is_available_for_dev': self.is_available_for_dev,
            'featured': self.featured,
            'user_id': str(self.user_id) if self.user_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            # Approval workflow fields
            'status': self.approval_status,
            'approval_status': self.approval_status,
            'submitted_for_approval_at': self.submitted_for_approval_at.isoformat() if self.submitted_for_approval_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'rejection_reason': self.rejection_reason,
            # Purchase and interaction tracking
            'is_purchasable': self.is_purchasable,
            'purchase_count': self.purchase_count,
            'rating': self.rating,
            'downloads': self.downloads,
            'views': self.views,
            'likes': self.likes,
            'average_rating': self.average_rating,
            'total_ratings': self.total_ratings,
            'comments_count': self.comments_count,
            'last_comment_at': self.last_comment_at.isoformat() if self.last_comment_at else None,
            'rating_distribution': self.rating_distribution,
        }
        
        # Handle code field (preserve dict structure if it exists)
        if self.code is not None:
            data['code'] = self.code if isinstance(self.code, dict) else str(self.code)
        else:
            data['code'] = None
            
        # Handle readme_content
        data['readme_content'] = self.readme_content
        
        # Handle html_code and css_code for live preview
        data['html_code'] = self.html_code
        data['css_code'] = self.css_code
        data['preview_code'] = self.preview_code
        
        return data
