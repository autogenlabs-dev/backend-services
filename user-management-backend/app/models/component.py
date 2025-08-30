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
        data = super().to_dict() if hasattr(super(), 'to_dict') else self.__dict__.copy()
        data["status"] = self.approval_status
        data["approval_status"] = self.approval_status
        
        # Convert ObjectId fields to strings
        if hasattr(self, 'id'):
            data["id"] = str(self.id)
        if hasattr(self, 'user_id') and self.user_id:
            data["user_id"] = str(self.user_id)
            
        # Convert datetime fields to ISO strings
        if hasattr(self, 'created_at') and self.created_at:
            data["created_at"] = self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at)
        if hasattr(self, 'updated_at') and self.updated_at:
            data["updated_at"] = self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else str(self.updated_at)
        if hasattr(self, 'submitted_for_approval_at') and self.submitted_for_approval_at:
            data["submitted_for_approval_at"] = self.submitted_for_approval_at.isoformat() if hasattr(self.submitted_for_approval_at, 'isoformat') else str(self.submitted_for_approval_at)
        if hasattr(self, 'approved_at') and self.approved_at:
            data["approved_at"] = self.approved_at.isoformat() if hasattr(self.approved_at, 'isoformat') else str(self.approved_at)
        
        # Ensure code field is properly handled (preserve dict structure if it exists)
        if hasattr(self, 'code') and self.code is not None:
            data["code"] = self.code
            
        return data
