from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field
from beanie import Document, PydanticObjectId
from beanie.odm.fields import Indexed
from enum import Enum

class ContentStatus(str, Enum):
    """Content status enumeration"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class Template(Document):
    """Template model for MongoDB"""
    title: str
    category: str  # Navigation, Layout, Forms, Data Display, etc.
    type: str  # React, Vue, Angular, HTML/CSS, Svelte, Flutter
    language: str  # TypeScript, JavaScript, etc.
    difficulty_level: str  # Easy, Medium, Tough
    plan_type: str  # Free, Premium
    rating: float = 0.0
    downloads: int = 0
    views: int = 0
    likes: int = 0
    short_description: str
    full_description: str
    preview_images: List[str] = Field(default_factory=list)  # Optional - using live_demo_url for preview
    git_repo_url: Optional[str] = None
    live_demo_url: Optional[str] = None  # Main source for preview generation
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    developer_name: str
    developer_experience: str
    is_available_for_dev: bool = True
    featured: bool = False
    popular: bool = False
    
    # User who created this template
    user_id: PydanticObjectId
    
    # Template content
    code: Optional[str] = None  # The actual code content
    readme_content: Optional[str] = None  # README/documentation content
    
    # Approval Workflow
    approval_status: ContentStatus = ContentStatus.PENDING_APPROVAL
    submitted_for_approval_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[PydanticObjectId] = None
    rejection_reason: Optional[str] = None
    
    # Purchase and Interaction Tracking
    is_purchasable: bool = True
    purchase_count: int = 0
    average_rating: float = 0.0
    total_ratings: int = 0
    comments_count: int = 0
    last_comment_at: Optional[datetime] = None
    
    # Rating Distribution
    rating_distribution: Dict[str, int] = Field(default_factory=lambda: {
        "5_star": 0,
        "4_star": 0,
        "3_star": 0,
        "2_star": 0,
        "1_star": 0
    })
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "templates"
        indexes = [
            [("user_id", 1)],
            [("category", 1)],
            [("type", 1)],
            [("plan_type", 1)],
            [("approval_status", 1)],
            [("featured", 1)],
            [("popular", 1)],
            [("created_at", -1)],
            [("category", 1), ("type", 1)],
            [("featured", 1), ("popular", 1)],
            [("approval_status", 1), ("created_at", -1)],
            [("average_rating", -1)],
            [("purchase_count", -1)]
        ]

    def __repr__(self):
        return f"<Template(title='{self.title}', category='{self.category}')>"

    def __str__(self):
        return self.title

    @property
    def status(self):
        """Compatibility property for frontend"""
        return self.approval_status

    def to_dict(self):
        """Convert template to dictionary for API responses (snake_case format)"""
        # Manually create dict to ensure git_repo_url is included
        data = {
            'id': str(self.id) if self.id else None,
            'title': self.title,
            'category': self.category,
            'type': self.type,
            'language': self.language,
            'difficulty_level': self.difficulty_level,
            'plan_type': self.plan_type,
            'rating': self.rating,
            'downloads': self.downloads,
            'views': self.views,
            'likes': self.likes,
            'short_description': self.short_description,
            'full_description': self.full_description,
            'preview_images': self.preview_images or [],
            'git_repo_url': self.git_repo_url,  # Explicitly include this
            'live_demo_url': self.live_demo_url,
            'dependencies': self.dependencies or [],
            'tags': self.tags or [],
            'developer_name': self.developer_name,
            'developer_experience': self.developer_experience,
            'is_available_for_dev': self.is_available_for_dev,
            'featured': self.featured,
            'popular': self.popular,
            'code': self.code,
            'readme_content': self.readme_content,
            'user_id': str(self.user_id) if self.user_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'status': self.approval_status,
            'approval_status': self.approval_status,
        }
        return data


class TemplateLike(Document):
    """Template like model for tracking user likes"""
    template_id: PydanticObjectId
    user_id: PydanticObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "template_likes"
        indexes = [
            [("template_id", 1), ("user_id", 1)],
            [("template_id", 1)],
            [("user_id", 1)]
        ]

    def __repr__(self):
        return f"<TemplateLike(template_id='{self.template_id}', user_id='{self.user_id}')>"


class TemplateDownload(Document):
    """Template download model for tracking downloads"""
    template_id: PydanticObjectId
    user_id: PydanticObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "template_downloads"
        indexes = [
            [("template_id", 1)],
            [("user_id", 1)],
            [("created_at", -1)]
        ]

    def __repr__(self):
        return f"<TemplateDownload(template_id='{self.template_id}', user_id='{self.user_id}')>"


class TemplateView(Document):
    """Template view model for tracking views"""
    template_id: PydanticObjectId
    user_id: Optional[PydanticObjectId] = None  # Can be null for anonymous views
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "template_views"
        indexes = [
            [("template_id", 1)],
            [("user_id", 1)],
            [("created_at", -1)]
        ]

    def __repr__(self):
        return f"<TemplateView(template_id='{self.template_id}', user_id='{self.user_id}')>"


class TemplateComment(Document):
    """Template comment model for user feedback"""
    template_id: PydanticObjectId
    user_id: PydanticObjectId
    comment: str
    rating: Optional[int] = None  # 1-5 stars
    is_approved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "template_comments"
        indexes = [
            [("template_id", 1)],
            [("user_id", 1)],
            [("is_approved", 1)],
            [("created_at", -1)]
        ]

    def __repr__(self):
        return f"<TemplateComment(template_id='{self.template_id}', user_id='{self.user_id}')>"


class TemplateCategory(Document):
    """Template category model for managing categories"""
    name: str = Field(index=True)
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "template_categories"
        indexes = [
            [("name", 1)],
            [("sort_order", 1)]
        ]

    def __repr__(self):
        return f"<TemplateCategory(name='{self.name}')>"