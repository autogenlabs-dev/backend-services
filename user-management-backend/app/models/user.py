from datetime import datetime, UTC
from typing import Optional, List, Dict, Any, Union
from pydantic import Field, EmailStr, ConfigDict, field_validator
from beanie import Document, PydanticObjectId
from beanie.odm.fields import Indexed # Import Indexed explicitly
from enum import Enum

class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"

class SubscriptionPlan(str, Enum):
    """Subscription plan enumeration"""
    FREE = "free"
    PRO = "pro"
    ULTRA = "ultra"

class User(Document):
    """User model for MongoDB"""
    model_config = ConfigDict(protected_namespaces=())
    
    email: EmailStr = Field(index=True)
    password_hash: Optional[str] = None
    name: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None  # Added username field
    stripe_customer_id: Optional[str] = None
    subscription: SubscriptionPlan = SubscriptionPlan.FREE  # free, pro, ultra
    tokens_remaining: int = 10000
    tokens_used: int = 0
    monthly_limit: int = 10000
    reset_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    last_login_at: Optional[datetime] = None
    last_logout_at: Optional[datetime] = None
    role: UserRole = UserRole.USER
    
    # Enhanced profile fields
    bio: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[Dict[str, str]] = Field(default_factory=dict)
    profile_image: Optional[str] = None
    wallet_balance: float = 0.0
    glm_api_key: Optional[str] = None  # User's GLM API key
    openrouter_api_key: Optional[str] = None  # User-specific OpenRouter API key
    openrouter_api_key_hash: Optional[str] = None
    # Capability flags (preserve developer-like privileges while keeping two roles)
    can_publish_content: bool = True
    can_sell_content: bool = True
    
    # Sub-user management fields (references to other users by ID)
    parent_user_id: Optional[PydanticObjectId] = None
    is_sub_user: bool = False
    sub_user_permissions: Optional[Dict[str, Any]] = None
    sub_user_limits: Optional[Dict[str, Any]] = None

    class Settings:
        name = "users"
        indexes = [
            "email",
            "role",
            "parent_user_id",
            "created_at",
            "is_active"
        ]
    
    @field_validator('subscription', mode='before')
    @classmethod
    def validate_subscription(cls, v):
        """Convert string subscription values to enum for backward compatibility"""
        if isinstance(v, str):
            # Handle old string values from database
            if v == "free":
                return SubscriptionPlan.FREE
            elif v == "pro":
                return SubscriptionPlan.PRO
            elif v in ("ultra", "enterprise"):  # Map old "enterprise" to "ultra"
                return SubscriptionPlan.ULTRA
            # If it's already a valid enum string, let Pydantic handle it
            return v
        return v

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

    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "full_name": self.full_name,
            "username": self.username or self.name or self.email.split('@')[0],  # Fallback username
            "role": self.role,
            "is_active": self.is_active,
            "subscription": self.subscription,
            "tokens_remaining": self.tokens_remaining,
            "tokens_used": self.tokens_used,
            "created_at": self.created_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "bio": self.bio,
            "website": self.website,
            "wallet_balance": self.wallet_balance,
            "profile_image": self.profile_image
        }


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
    connected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
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


class SubscriptionPlanModel(Document):
    """Subscription plan model for MongoDB"""
    name: Indexed(str)  # "Free", "Pro", "Ultra"
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
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


class ManagedApiKey(Document):
    """Admin-managed API keys that can be distributed to users."""
    key_value: str
    key_preview: str
    label: Optional[str] = None
    is_active: bool = True
    assigned_user_id: Optional[PydanticObjectId] = None
    assigned_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_rotated_at: Optional[datetime] = None

    class Settings:
        name = "managed_api_keys"
        indexes = [
            "is_active",
            "assigned_user_id",
            "created_at"
        ]

    def __repr__(self):
        return f"<ManagedApiKey(label='{self.label}', preview='{self.key_preview}...')>"


class Organization(Document):
    """Organization model for ultra-tier features in MongoDB"""
    name: str
    slug: Indexed(str) # Corrected Indexed usage
    description: Optional[str] = None
    owner_id: PydanticObjectId
    subscription_plan: str = "ultra"
    monthly_token_limit: int = 1000000
    tokens_used: int = 0
    reset_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
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
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
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
