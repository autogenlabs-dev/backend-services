"""Pydantic schemas for authentication and user management."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie.odm.fields import PydanticObjectId

from pydantic import BaseModel, EmailStr, Field

from ..models.user import SubscriptionPlan


# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    # A4F API key for VS Code extension auto-configuration
    a4f_api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    user: Optional[Dict[str, Any]] = None


class TokenRefresh(BaseModel):
    refresh_token: str


# User schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    username: Optional[str] = Field(None, max_length=50, description="Username (will use email prefix if not provided)")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: Optional[str] = Field(None, max_length=100, description="Display name (will use username if not provided)")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, description="New password")
    is_active: Optional[bool] = None
    name: Optional[str] = Field(None, max_length=100, description="Display name")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    first_name: Optional[str] = Field(None, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, max_length=50, description="Last name")
    role: Optional[str] = Field(None, description="User role (user, admin)")


class UserResponse(UserBase):
    id: PydanticObjectId
    name: Optional[str] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "user"
    subscription: Optional[SubscriptionPlan] = SubscriptionPlan.FREE
    tokens_remaining: Optional[int] = 10000
    tokens_used: Optional[int] = 0
    monthly_limit: Optional[int] = 10000
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# OAuth schemas
class OAuthProviderResponse(BaseModel):
    id: PydanticObjectId
    name: str
    display_name: str
    is_active: bool

    class Config:
        from_attributes = True


class UserOAuthAccountResponse(BaseModel):
    id: PydanticObjectId
    provider_id: PydanticObjectId
    provider_user_id: str
    email: str
    connected_at: datetime
    last_used_at: Optional[datetime]
    provider: OAuthProviderResponse

    class Config:
        from_attributes = True


# Subscription schemas
class SubscriptionPlanResponse(BaseModel):
    id: PydanticObjectId
    name: str
    display_name: str
    monthly_tokens: int
    price_monthly: float
    features: Optional[List[str]]  # Changed from Dict to List to match model
    is_active: bool

    class Config:
        from_attributes = True


class UserSubscriptionResponse(BaseModel):
    id: PydanticObjectId
    plan_id: PydanticObjectId
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    plan: SubscriptionPlanResponse

    class Config:
        from_attributes = True


# Token usage schemas
class TokenUsageLogResponse(BaseModel):
    id: PydanticObjectId
    provider: str
    model_name: str
    tokens_used: int
    cost_usd: Optional[float]
    request_type: str
    created_at: datetime
    request_metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class TokenUsageCreate(BaseModel):
    provider: str = Field(..., description="Provider name (openrouter, glama, requesty)")
    model_name: str = Field(..., description="Model name used")
    tokens_used: int = Field(..., ge=0, description="Number of tokens used")
    cost_usd: Optional[float] = Field(None, ge=0, description="Cost in USD")
    request_type: str = Field(..., description="Type of request (completion, chat, embedding)")
    request_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional request metadata")


class TokenUsageStats(BaseModel):
    total_tokens: int
    total_cost: float
    tokens_by_provider: Dict[str, int]
    cost_by_provider: Dict[str, float]
    tokens_by_model: Dict[str, int]


# API Key schemas
class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Human-readable name for the API key")


class ApiKeyResponse(BaseModel):
    id: PydanticObjectId
    name: str
    key_preview: str
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class ApiKeyWithSecret(ApiKeyResponse):
    """Schema that includes the actual API key (only returned on creation)."""
    api_key: str


class ManagedApiKeyCreate(BaseModel):
    key: str = Field(..., min_length=10, description="Raw API key value")
    label: Optional[str] = Field(None, max_length=120, description="Optional label for grouping")


class ManagedApiKeyBulkCreate(BaseModel):
    keys: List[str] = Field(..., min_items=1, description="List of raw API keys to add")
    label: Optional[str] = Field(None, max_length=120)


class ManagedApiKeyResponse(BaseModel):
    id: PydanticObjectId
    key_value: Optional[str] = None
    key_preview: str
    label: Optional[str]
    is_active: bool
    assigned_user_id: Optional[PydanticObjectId]
    assigned_user_email: Optional[EmailStr] = None
    assigned_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ManagedApiKeyAssignmentResponse(BaseModel):
    managed_key_id: PydanticObjectId
    key_value: str
    key_preview: str
    assigned_at: datetime
    label: Optional[str]


# OAuth callback schemas
class OAuthCallback(BaseModel):
    code: str
    state: Optional[str] = None


# User profile schemas
class UserProfile(BaseModel):  # Changed to inherit from BaseModel instead of UserResponse
    id: str
    email: EmailStr
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    last_login_at: Optional[datetime]
    oauth_accounts: List[UserOAuthAccountResponse]
    subscription: Optional[str] = None  # Subscription plan: "free", "pro", or "ultra"
    api_keys: List[ApiKeyResponse]
    glm_api_key: Optional[str] = None  # User's GLM API key
    bytez_api_key: Optional[str] = None  # User's Bytez API key
    openrouter_api_key: Optional[str] = None
    role: str
    can_publish_content: bool = False
    
    class Config:
        from_attributes = True


# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
