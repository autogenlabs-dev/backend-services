from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

class SubUserPermissions(BaseModel):
    """Sub-user permissions schema"""
    api_access: bool = True
    can_create_api_keys: bool = True
    can_view_usage: bool = True
    can_modify_settings: bool = False
    allowed_endpoints: List[str] = ["*"]
    allowed_models: List[str] = ["*"]
    can_invite_others: bool = False

class SubUserLimits(BaseModel):
    """Sub-user limits schema"""
    monthly_tokens: int = Field(gt=0, le=1000000)
    requests_per_minute: int = Field(gt=0, le=1000)
    requests_per_hour: int = Field(gt=0, le=10000)
    max_api_keys: int = Field(gt=0, le=10)
    max_concurrent_requests: int = Field(gt=0, le=50)

class SubUserCreateRequest(BaseModel):
    """Request schema for creating a sub-user"""
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    permissions: Optional[SubUserPermissions] = None
    limits: Optional[SubUserLimits] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    send_invitation: bool = True

class SubUserUpdateRequest(BaseModel):
    """Request schema for updating a sub-user"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    permissions: Optional[SubUserPermissions] = None
    limits: Optional[SubUserLimits] = None
    is_active: Optional[bool] = None

class SubUserResponse(BaseModel):
    """Response schema for sub-user data"""
    id: str
    email: str
    name: str
    is_sub_user: bool
    is_active: bool
    permissions: Optional[Dict[str, Any]] = None
    limits: Optional[Dict[str, Any]] = None
    tokens_used: int
    tokens_remaining: int
    monthly_limit: int
    created_at: datetime
    last_login_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    api_keys_count: int = 0

    class Config:
        from_attributes = True

class SubUserUsageStats(BaseModel):
    """Sub-user usage statistics"""
    user_id: str
    tokens_used: int
    tokens_remaining: int
    monthly_limit: int
    usage_percentage: float
    requests_today: int = 0
    requests_this_hour: int = 0
    last_active: Optional[datetime] = None
    api_keys_count: int
    total_requests: int = 0

class SubUserInvitation(BaseModel):
    """Sub-user invitation schema"""
    email: EmailStr
    name: str
    permissions: Optional[SubUserPermissions] = None
    limits: Optional[SubUserLimits] = None
    expires_in_hours: int = Field(default=72, ge=1, le=168)  # 1 hour to 1 week
    
class SubUserApiKeyCreate(BaseModel):
    """Schema for creating API keys for sub-users"""
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)

class SubUserBulkOperation(BaseModel):
    """Schema for bulk operations on sub-users"""
    user_ids: List[str] = Field(min_items=1, max_items=50)
    operation: str = Field(regex="^(activate|deactivate|delete|update_limits|update_permissions)$")
    data: Optional[Dict[str, Any]] = None
