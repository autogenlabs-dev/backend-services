from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field, EmailStr
from beanie import Document, PydanticObjectId
from beanie.odm.fields import Indexed # Import Indexed explicitly

class User(Document):
    """User model for MongoDB"""
    email: Indexed(EmailStr) # Corrected Indexed usage
    password_hash: Optional[str] = None
    name: Optional[str] = None
    full_name: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    subscription: str = "free"  # free, pro, enterprise
    tokens_remaining: int = 10000
    tokens_used: int = 0
    monthly_limit: int = 10000
    reset_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    last_login_at: Optional[datetime] = None
    role: str = "user"  # user, developer, admin, superadmin
    
    # Sub-user management fields (references to other users by ID)
    parent_user_id: Optional[PydanticObjectId] = None
    is_sub_user: bool = False
    sub_user_permissions: Optional[Dict[str, Any]] = None
    sub_user_limits: Optional[Dict[str, Any]] = None

    class Settings:
        name = "users"
        indexes = [
            "email",
            "parent_user_id"
        ]

    def __repr__(self):
        return f"<User(email='{self.email}')>"

    def __str__(self):
        return self.email

    def __hash__(self):
        return hash(self.email)

    def __eq__(self, other):
        if isinstance(other, User):
            return self.email == other.email
        return False


class OAuthProvider(Document):
    """OAuth provider model for MongoDB"""
    name: Indexed(str)  # "openrouter", "glama", "requesty"
    display_name: str     # "OpenRouter", "Glama", "Requesty"
    is_active: bool = True

    class Settings:
        name = "oauth_providers"
        indexes = [
            "name"
        ]

    def __repr__(self):
        return f"<OAuthProvider(name='{self.name}')>"


class UserOAuthAccount(Document):
    """User OAuth account model for MongoDB"""
    user_id: PydanticObjectId
    provider_id: PydanticObjectId
    provider_user_id: str
    email: EmailStr
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None

    class Settings:
        name = "user_oauth_accounts"
        indexes = [
            "user_id",
            "provider_id",
            "provider_user_id"
        ]

    def __repr__(self):
        return f"<UserOAuthAccount(user_id='{self.user_id}', provider_id='{self.provider_id}')>"


class SubscriptionPlan(Document):
    """Subscription plan model for MongoDB"""
    name: Indexed(str)  # "Free", "Pro", "Enterprise"
    display_name: str
    monthly_tokens: int
    price_monthly: float
    stripe_price_id: Optional[str] = None
    features: Optional[List[str]] = None
    is_active: bool = True

    class Settings:
        name = "subscription_plans"
        indexes = [
            "name"
        ]

    def __repr__(self):
        return f"<SubscriptionPlan(name='{self.name}', price='{self.price_monthly}')>"


class UserSubscription(Document):
    """User subscription model for MongoDB"""
    user_id: PydanticObjectId
    plan_id: PydanticObjectId
    stripe_subscription_id: Optional[str] = None
    status: str = "active"  # active, inactive, cancelled, past_due
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "user_subscriptions"
        indexes = [
            "user_id",
            "plan_id"
        ]

    def __repr__(self):
        return f"<UserSubscription(user_id='{self.user_id}', plan_id='{self.plan_id}', status='{self.status}')>"


class TokenUsageLog(Document):
    """Token usage log model for MongoDB"""
    user_id: PydanticObjectId
    organization_id: Optional[PydanticObjectId] = None
    provider: str  # "openrouter", "glama", "requesty"
    model_name: str
    tokens_used: int
    cost_usd: Optional[float] = None
    request_type: str  # "completion", "chat", "embedding"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    request_metadata: Optional[Dict[str, Any]] = None

    class Settings:
        name = "token_usage_logs"
        indexes = [
            "user_id",
            "organization_id",
            "created_at"
        ]

    def __repr__(self):
        return f"<TokenUsageLog(user_id='{self.user_id}', tokens='{self.tokens_used}', provider='{self.provider}')>"


class ApiKey(Document):
    """API key model for MongoDB"""
    user_id: PydanticObjectId
    organization_id: Optional[PydanticObjectId] = None
    key_hash: Indexed(str) # Corrected Indexed usage
    key_preview: str
    name: str
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "api_keys"
        indexes = [
            "user_id",
            "organization_id",
            "key_hash"
        ]

    def __repr__(self):
        return f"<ApiKey(user_id='{self.user_id}', name='{self.name}', preview='{self.key_preview}...')>"


class Organization(Document):
    """Organization model for enterprise features in MongoDB"""
    name: str
    slug: Indexed(str) # Corrected Indexed usage
    description: Optional[str] = None
    owner_id: PydanticObjectId
    subscription_plan: str = "enterprise"
    monthly_token_limit: int = 1000000
    tokens_used: int = 0
    reset_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "organizations"
        indexes = [
            "slug",
            "owner_id"
        ]

    def __repr__(self):
        return f"<Organization(name='{self.name}', slug='{self.slug}')>"


class OrganizationMember(Document):
    """Organization member model for MongoDB"""
    organization_id: PydanticObjectId
    user_id: PydanticObjectId
    role: str = "member"  # owner, admin, member
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "organization_members"
        indexes = [
            ("organization_id", "user_id", {"unique": True}),
            "organization_id",
            "user_id"
        ]

    def __repr__(self):
        return f"<OrganizationMember(org_id='{self.organization_id}', user_id='{self.user_id}', role='{self.role}')>"


class OrganizationInvitation(Document):
    """Organization invitation model for MongoDB"""
    organization_id: PydanticObjectId
    email: EmailStr
    role: str = "member"
    status: str = "pending"  # pending, accepted, expired
    invited_by_id: PydanticObjectId
    token: Indexed(str) # Corrected Indexed usage
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "organization_invitations"
        indexes = [
            "organization_id",
            "email",
            "token"
        ]

    def __repr__(self):
        return f"<OrganizationInvitation(org_id='{self.organization_id}', email='{self.email}')>"


class OrganizationKey(Document):
    """Organization API keys for team access in MongoDB."""
    organization_id: PydanticObjectId
    name: str
    key_hash: Indexed(str) # Corrected Indexed usage
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

    def __repr__(self):
        return f"<OrganizationKey(name='{self.name}', org_id='{self.organization_id}')>"


class KeyUsageLog(Document):
    """Log organization key usage for analytics in MongoDB."""
    organization_key_id: PydanticObjectId
    user_id: PydanticObjectId
    provider: str
    model_name: str
    tokens_used: int
    cost_usd: Optional[float] = None
    request_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    request_metadata: Optional[Dict[str, Any]] = None

    class Settings:
        name = "key_usage_logs"
        indexes = [
            "organization_key_id",
            "user_id",
            "created_at"
        ]

    def __repr__(self):
        return f"<KeyUsageLog(key_id='{self.organization_key_id}', tokens={self.tokens_used})>"
