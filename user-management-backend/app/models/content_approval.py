from datetime import datetime
from typing import Optional
from pydantic import Field
from beanie import Document, PydanticObjectId
from enum import Enum

class ContentStatus(str, Enum):
    """Content status enumeration"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class ContentType(str, Enum):
    """Content type enumeration"""
    TEMPLATE = "template"
    COMPONENT = "component"

class ContentApproval(Document):
    """Content approval model for workflow management"""
    content_id: PydanticObjectId = Field(index=True)
    content_type: ContentType
    content_title: Optional[str] = None  # Added missing field
    
    # Status Tracking
    status: ContentStatus = ContentStatus.PENDING_APPROVAL
    previous_status: Optional[ContentStatus] = None
    
    # Submission Details
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_by: PydanticObjectId = Field(index=True)
    
    # Review Details
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[PydanticObjectId] = None
    rejection_reason: Optional[str] = None
    approval_notes: Optional[str] = None
    
    # Admin Notes
    internal_notes: Optional[str] = None
    requires_changes: bool = False
    change_requests: Optional[str] = None
    
    # Priority and Classification
    priority: str = "normal"  # low, normal, high, urgent
    category: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "content_approvals"
        indexes = [
            "content_id",
            "content_type",
            "status",
            "submitted_by",
            "reviewed_by",
            "submitted_at",
            "reviewed_at",
            [("content_type", 1), ("status", 1)],  # Compound index
            "created_at"
        ]

    def __repr__(self):
        return f"<ContentApproval(content_id='{self.content_id}', status='{self.status}')>"

    def __str__(self):
        return f"Approval: {self.content_type} {self.content_id} - {self.status}"
