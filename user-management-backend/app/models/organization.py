"""Organization models for enterprise features."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field
from beanie import Document, PydanticObjectId
from beanie.odm.fields import Indexed


class Organization(Document):
    """Organization model for enterprise customers."""
    
    name: str
    admin_user_id: PydanticObjectId
    subscription_plan: str = "enterprise"
    token_pool: int = 1000000
    tokens_used: int = 0
    monthly_limit: int = 1000000
    reset_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Organization settings
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_active: bool = True
    
    class Settings:
        name = "organizations"
        indexes = [
            "admin_user_id",
            "name"
        ]

    def __repr__(self):
        return f"<Organization(name='{self.name}')>"


class OrganizationKey(Document):
    """API keys for organizations."""
    
    organization_id: PydanticObjectId
    key_name: str
    key_hash: str
    description: Optional[str] = None
    permissions: Dict[str, Any] = Field(default_factory=dict)
    monthly_limit: int = 100000
    tokens_used: int = 0
    is_active: bool = True
    expires_at: Optional[datetime] = None
    created_by: PydanticObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None
    
    class Settings:
        name = "organization_keys"
        indexes = [
            "organization_id",
            "key_hash",
            "created_by"
        ]


class OrganizationMember(Document):
    """Organization member relationships."""
    
    organization_id: PydanticObjectId
    user_id: PydanticObjectId
    role: str = "member"  # owner, admin, member, viewer
    assigned_key_id: Optional[PydanticObjectId] = None
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    invited_by: Optional[PydanticObjectId] = None
    is_active: bool = True
    
    class Settings:
        name = "organization_members"
        indexes = [
            "organization_id",
            "user_id",
            ("organization_id", "user_id")  # Compound index
        ]


class KeyUsageLog(Document):
    """Log organization key usage for analytics."""
    
    organization_key_id: PydanticObjectId
    user_id: PydanticObjectId
    provider: str
    model_name: str
    tokens_used: int
    cost_usd: Optional[float] = None
    request_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "key_usage_logs"
        indexes = [
            "organization_key_id",
            "user_id",
            "created_at",
            ("organization_key_id", "created_at")  # Compound index
        ]


class OrganizationInvitation(Document):
    """Organization invitations for new members."""
    
    organization_id: PydanticObjectId
    email: str
    role: str = "member"
    token: str
    created_by: PydanticObjectId
    expires_at: datetime
    is_used: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = None
    
    class Settings:
        name = "organization_invitations"
        indexes = [
            "organization_id",
            "email",
            "token",
            "expires_at"
        ]
