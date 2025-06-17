"""Pydantic schemas for organization management."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


# Organization schemas
class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    description: Optional[str] = Field(None, max_length=1000, description="Organization description")


class OrganizationCreate(OrganizationBase):
    slug: str = Field(..., min_length=1, max_length=100, description="Organization slug (URL-friendly)")
    
    @validator('slug')
    def validate_slug(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower()


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    monthly_token_limit: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class OrganizationResponse(OrganizationBase):
    id: UUID
    slug: str
    owner_id: UUID
    subscription_plan: str
    monthly_token_limit: int
    tokens_used: int
    reset_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    member_count: Optional[int] = None

    class Config:
        from_attributes = True


# Organization member schemas
class OrganizationMemberBase(BaseModel):
    role: str = Field(..., description="Member role: owner, admin, member")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['owner', 'admin', 'member']:
            raise ValueError('Role must be one of: owner, admin, member')
        return v


class OrganizationMemberCreate(BaseModel):
    email: str = Field(..., description="Email of user to invite")
    role: str = Field(default="member", description="Member role: admin, member")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['admin', 'member']:
            raise ValueError('Role must be one of: admin, member')
        return v


class OrganizationMemberUpdate(BaseModel):
    role: str = Field(..., description="New member role: admin, member")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['admin', 'member']:
            raise ValueError('Role must be one of: admin, member')
        return v


class OrganizationMemberResponse(OrganizationMemberBase):
    id: UUID
    organization_id: UUID
    user_id: UUID
    user_email: str
    user_full_name: Optional[str]
    joined_at: datetime

    class Config:
        from_attributes = True


# Organization invitation schemas
class OrganizationInvitationCreate(BaseModel):
    email: str = Field(..., description="Email to invite")
    role: str = Field(default="member", description="Role for invited user")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['admin', 'member']:
            raise ValueError('Role must be one of: admin, member')
        return v


class OrganizationInvitationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    email: str
    role: str
    status: str
    invited_by_id: UUID
    invited_by_email: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


# Organization API key schemas
class OrganizationApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="API key name")
    permissions: List[str] = Field(..., description="List of permissions for the API key")


class OrganizationApiKeyResponse(BaseModel):
    id: UUID
    name: str
    key_preview: str
    created_at: datetime
    last_used_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class OrganizationApiKeyCreateResponse(OrganizationApiKeyResponse):
    """Response when creating a new API key - includes the full key"""
    api_key: str


# Organization statistics schemas
class OrganizationStats(BaseModel):
    total_members: int
    total_api_keys: int
    monthly_tokens_used: int
    monthly_token_limit: int
    token_usage_percentage: float
    days_until_reset: int
    recent_activity_count: int


class OrganizationUsageHistory(BaseModel):
    date: str
    tokens_used: int
    requests_count: int
    unique_users: int


class OrganizationAnalytics(BaseModel):
    current_period_usage: int
    previous_period_usage: int
    usage_trend: str  # "up", "down", "stable"
    top_users: List[dict]
    usage_by_provider: List[dict]
    daily_usage: List[OrganizationUsageHistory]
