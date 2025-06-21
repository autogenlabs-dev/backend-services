from sqlalchemy import Column, String, Boolean, DateTime, Integer, DECIMAL, Text, ForeignKey, JSON
# SQLite doesn't support UUID natively, so we'll use String(36) instea    request_metadata = Column(JSON, nullable=True)  # Additional request metadata
# But keep the PostgreSQL UUID import for future compatibility
from sqlalchemy.types import String
UUID = String(36)

# SQLite doesn't support JSONB, so we'll use JSON instead
try:
    from sqlalchemy.dialects.postgresql import JSONB
except ImportError:
    # For SQLite compatibility
    JSONB = JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import uuid


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth-only users
    name = Column(String(255), nullable=True)  # User display name
    full_name = Column(String(255), nullable=True)  # User full name
    stripe_customer_id = Column(String(255), nullable=True)  # Stripe customer ID
    subscription = Column(String(20), nullable=False, default="free")  # free, pro, enterprise
    tokens_remaining = Column(Integer, nullable=False, default=10000)  # Current month remaining tokens
    tokens_used = Column(Integer, nullable=False, default=0)  # Current month used tokens
    monthly_limit = Column(Integer, nullable=False, default=10000)  # Monthly token limit
    reset_date = Column(DateTime(timezone=True), nullable=True)  # Next reset date
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    role = Column(String(20), nullable=False, default="user")  # user, developer, admin, superadmin
    
    # Sub-user management fields
    parent_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    is_sub_user = Column(Boolean, default=False)
    sub_user_permissions = Column(JSON, nullable=True)  # Permissions specific to this sub-user
    sub_user_limits = Column(JSON, nullable=True)  # Token limits and restrictions
    
    # Relationships
    oauth_accounts = relationship("UserOAuthAccount", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")
    token_usage_logs = relationship("TokenUsageLog", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    organization_memberships = relationship("OrganizationMember", back_populates="user", cascade="all, delete-orphan")
    owned_organizations = relationship("Organization", back_populates="owner", cascade="all, delete-orphan")
    
    # Sub-user relationships
    parent_user = relationship("User", remote_side=[id], back_populates="sub_users")
    sub_users = relationship("User", back_populates="parent_user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email='{self.email}')>"


class OAuthProvider(Base):
    """OAuth provider model"""
    __tablename__ = "oauth_providers"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    name = Column(String(50), unique=True, nullable=False)  # "openrouter", "glama", "requesty"
    display_name = Column(String(100), nullable=False)     # "OpenRouter", "Glama", "Requesty"
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_accounts = relationship("UserOAuthAccount", back_populates="provider")
    
    def __repr__(self):
        return f"<OAuthProvider(name='{self.name}')>"


class UserOAuthAccount(Base):
    """User OAuth account model"""
    __tablename__ = "user_oauth_accounts"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    provider_id = Column(String(36), ForeignKey("oauth_providers.id"), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="oauth_accounts")
    provider = relationship("OAuthProvider", back_populates="user_accounts")
    
    def __repr__(self):
        return f"<UserOAuthAccount(user_id='{self.user_id}', provider='{self.provider.name}')>"


class SubscriptionPlan(Base):
    """Subscription plan model"""
    __tablename__ = "subscription_plans"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    name = Column(String(50), unique=True, nullable=False)  # "Free", "Pro", "Enterprise"
    display_name = Column(String(100), nullable=False)
    monthly_tokens = Column(Integer, nullable=False)  # Token allowance per month
    price_monthly = Column(DECIMAL(10, 2), nullable=False)  # Price in USD
    stripe_price_id = Column(String(255), nullable=True)  # Stripe price ID
    features = Column(JSON, nullable=True)  # Plan features as JSON
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_subscriptions = relationship("UserSubscription", back_populates="plan")
    
    def __repr__(self):
        return f"<SubscriptionPlan(name='{self.name}', price='{self.price_monthly}')>"


class UserSubscription(Base):
    """User subscription model"""
    __tablename__ = "user_subscriptions"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    plan_id = Column(String(36), ForeignKey("subscription_plans.id"), nullable=False)
    stripe_subscription_id = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="active")  # active, inactive, cancelled, past_due
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="user_subscriptions")
    
    def __repr__(self):
        return f"<UserSubscription(user_id='{self.user_id}', plan='{self.plan.name}', status='{self.status}')>"


class TokenUsageLog(Base):
    """Token usage log model"""
    __tablename__ = "token_usage_logs"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)  # For org usage
    provider = Column(String(50), nullable=False)  # "openrouter", "glama", "requesty"
    model_name = Column(String(100), nullable=False)
    tokens_used = Column(Integer, nullable=False)
    cost_usd = Column(DECIMAL(10, 6), nullable=True)
    request_type = Column(String(50), nullable=False)  # "completion", "chat", "embedding"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    request_metadata = Column(JSON, nullable=True)  # Additional request metadata
    
    # Relationships
    user = relationship("User", back_populates="token_usage_logs")
    
    def __repr__(self):
        return f"<TokenUsageLog(user_id='{self.user_id}', tokens='{self.tokens_used}', provider='{self.provider}')>"


class ApiKey(Base):
    """API key model"""
    __tablename__ = "api_keys"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)  # For org keys
    key_hash = Column(String(255), nullable=False)  # Hashed API key
    key_preview = Column(String(8), nullable=False)  # First 8 characters for display
    name = Column(String(100), nullable=False)  # User-defined name
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiration date
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<ApiKey(user_id='{self.user_id}', name='{self.name}', preview='{self.key_preview}...')>"


class Organization(Base):
    """Organization model for enterprise features"""
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subscription_plan = Column(String(20), nullable=False, default="enterprise")
    monthly_token_limit = Column(Integer, nullable=False, default=1000000)
    tokens_used = Column(Integer, nullable=False, default=0)
    reset_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    owner = relationship("User", back_populates="owned_organizations")
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    invitations = relationship("OrganizationInvitation", back_populates="organization", cascade="all, delete-orphan")
    keys = relationship("OrganizationKey", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organization(name='{self.name}', slug='{self.slug}')>"


class OrganizationMember(Base):
    """Organization member model"""
    __tablename__ = "organization_members"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False, default="member")  # owner, admin, member
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organization_memberships")
    
    def __repr__(self):
        return f"<OrganizationMember(org='{self.organization.name}', user='{self.user.email}', role='{self.role}')>"


class OrganizationInvitation(Base):
    """Organization invitation model"""
    __tablename__ = "organization_invitations"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="member")
    status = Column(String(20), nullable=False, default="pending")  # pending, accepted, expired
    invited_by_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)  # Invitation token
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="invitations")
    invited_by = relationship("User")
    
    def __repr__(self):
        return f"<OrganizationInvitation(org='{self.organization.name}', email='{self.email}')>"


class OrganizationKey(Base):
    """Organization API keys for team access."""
    __tablename__ = "organization_keys"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)  # Added name attribute
    key_hash = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSON, default=lambda: {})
    monthly_limit = Column(Integer, default=100000)
    tokens_used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_used_at = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", back_populates="keys")
    creator = relationship("User", foreign_keys=[created_by])
    usage_logs = relationship("KeyUsageLog", back_populates="organization_key")
    
    def __repr__(self):
        return f"<OrganizationKey(name='{self.name}', org='{self.organization.name}')>"


class KeyUsageLog(Base):
    """Log organization key usage for analytics."""
    __tablename__ = "key_usage_logs"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    organization_key_id = Column(String(36), ForeignKey("organization_keys.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)
    model_name = Column(String(100), nullable=False)
    tokens_used = Column(Integer, nullable=False)
    cost_usd = Column(DECIMAL(10, 6))
    request_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
      # Relationships
    organization_key = relationship("OrganizationKey", back_populates="usage_logs")
    user = relationship("User")
    
    def __repr__(self):
        return f"<KeyUsageLog(key='{self.organization_key.name}', tokens={self.tokens_used})>"
