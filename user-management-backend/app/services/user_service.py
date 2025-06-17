"""User service functions for database operations."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4
import secrets
import hashlib

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models.user import User, UserOAuthAccount, OAuthProvider, UserSubscription, TokenUsageLog, ApiKey
from ..schemas.auth import UserCreate, UserUpdate, TokenUsageCreate, ApiKeyCreate
from ..auth.jwt import get_password_hash, verify_password


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def create_user_with_password(db: Session, user_data: UserCreate) -> User:
    """Create a new user with email and password."""
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("User with this email already exists")
    
    hashed_password = get_password_hash(user_data.password)
    
    # Extract username from email if no full_name provided
    username = user_data.email.split('@')[0] if not hasattr(user_data, 'username') else getattr(user_data, 'username', user_data.email.split('@')[0])
    
    db_user = User(
        id=uuid4(),
        email=user_data.email,
        password_hash=hashed_password,
        name=username,  # Use username or email prefix as name
        is_active=True,
        subscription="free",
        tokens_remaining=10000,
        tokens_used=0,
        monthly_limit=10000,
        created_at=datetime.now(timezone.utc),  # Explicitly set created_at
        # Optionally set full_name if provided
        full_name=getattr(user_data, 'full_name', None)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    user = get_user_by_email(db, email)
    if not user or not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user."""
    db_user = User(
        id=uuid4(),
        email=user_data.email,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
    """Update user information."""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def update_user_last_login(db: Session, user_id: UUID) -> None:
    """Update user's last login timestamp."""
    user = get_user_by_id(db, user_id)
    if user:
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()


def get_or_create_user_by_oauth(
    db: Session, 
    provider_name: str, 
    provider_user_id: str, 
    email: str
) -> User:
    """Get or create user from OAuth provider information."""
    # Get provider
    provider = db.query(OAuthProvider).filter(OAuthProvider.name == provider_name).first()
    if not provider:
        raise ValueError(f"Unknown OAuth provider: {provider_name}")
    
    # Check if OAuth account exists
    oauth_account = db.query(UserOAuthAccount).filter(
        and_(
            UserOAuthAccount.provider_id == provider.id,
            UserOAuthAccount.provider_user_id == provider_user_id
        )
    ).first()
    
    if oauth_account:
        # Update last used time
        oauth_account.last_used_at = datetime.now(timezone.utc)
        db.commit()
        return oauth_account.user
    
    # Check if user exists by email
    user = get_user_by_email(db, email)
    if not user:
        # Create new user
        user = create_user(db, UserCreate(email=email))
    
    # Create OAuth account link
    oauth_account = UserOAuthAccount(
        id=uuid4(),
        user_id=user.id,
        provider_id=provider.id,
        provider_user_id=provider_user_id,
        email=email,
        last_used_at=datetime.now(timezone.utc)
    )
    db.add(oauth_account)
    db.commit()
    
    return user


def get_user_oauth_accounts(db: Session, user_id: UUID) -> List[UserOAuthAccount]:
    """Get all OAuth accounts for a user."""
    return db.query(UserOAuthAccount).filter(UserOAuthAccount.user_id == user_id).all()


def get_user_subscription(db: Session, user_id: UUID) -> Optional[UserSubscription]:
    """Get user's current active subscription."""
    return db.query(UserSubscription).filter(
        and_(
            UserSubscription.user_id == user_id,
            UserSubscription.status == "active"
        )
    ).first()


def log_token_usage(db: Session, user_id: UUID, usage_data: TokenUsageCreate) -> TokenUsageLog:
    """Log token usage for a user."""
    log_entry = TokenUsageLog(
        id=uuid4(),
        user_id=user_id,
        provider=usage_data.provider,
        model_name=usage_data.model_name,
        tokens_used=usage_data.tokens_used,
        cost_usd=usage_data.cost_usd,
        request_type=usage_data.request_type,
        request_metadata=usage_data.request_metadata
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def get_user_token_usage(
    db: Session, 
    user_id: UUID, 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    provider: Optional[str] = None
) -> List[TokenUsageLog]:
    """Get token usage logs for a user with optional filters."""
    query = db.query(TokenUsageLog).filter(TokenUsageLog.user_id == user_id)
    
    if start_date:
        query = query.filter(TokenUsageLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(TokenUsageLog.created_at <= end_date)
    
    if provider:
        query = query.filter(TokenUsageLog.provider == provider)
    
    return query.order_by(TokenUsageLog.created_at.desc()).all()


def get_user_token_usage_stats(
    db: Session, 
    user_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> dict:
    """Get aggregated token usage statistics for a user."""
    query = db.query(TokenUsageLog).filter(TokenUsageLog.user_id == user_id)
    
    if start_date:
        query = query.filter(TokenUsageLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(TokenUsageLog.created_at <= end_date)
    
    logs = query.all()
    
    # Aggregate statistics
    total_tokens = sum(log.tokens_used for log in logs)
    total_cost = sum(log.cost_usd or 0 for log in logs)
    
    tokens_by_provider = {}
    cost_by_provider = {}
    tokens_by_model = {}
    
    for log in logs:
        # By provider
        tokens_by_provider[log.provider] = tokens_by_provider.get(log.provider, 0) + log.tokens_used
        cost_by_provider[log.provider] = cost_by_provider.get(log.provider, 0) + (log.cost_usd or 0)
        
        # By model
        tokens_by_model[log.model_name] = tokens_by_model.get(log.model_name, 0) + log.tokens_used
    
    return {
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "tokens_by_provider": tokens_by_provider,
        "cost_by_provider": cost_by_provider,
        "tokens_by_model": tokens_by_model
    }


def create_api_key(db: Session, user_id: UUID, key_data: ApiKeyCreate) -> tuple[ApiKey, str]:
    """Create a new API key for a user."""
    # Generate a secure random API key
    api_key = f"sk-{secrets.token_urlsafe(32)}"
    
    # Hash the API key for storage
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Create database record
    db_api_key = ApiKey(
        id=uuid4(),
        user_id=user_id,
        key_hash=key_hash,
        key_preview=api_key[:8],
        name=key_data.name,
        is_active=True
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return db_api_key, api_key


def get_user_api_keys(db: Session, user_id: UUID) -> List[ApiKey]:
    """Get all API keys for a user."""
    return db.query(ApiKey).filter(ApiKey.user_id == user_id).all()


def verify_api_key(db: Session, api_key: str) -> Optional[User]:
    """Verify an API key and return the associated user."""
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    api_key_record = db.query(ApiKey).filter(
        and_(
            ApiKey.key_hash == key_hash,
            ApiKey.is_active == True
        )
    ).first()
    
    if not api_key_record:
        return None
    
    # Update last used time
    api_key_record.last_used_at = datetime.now(timezone.utc)
    db.commit()
    
    # Return the user
    return api_key_record.user


def deactivate_api_key(db: Session, user_id: UUID, api_key_id: UUID) -> bool:
    """Deactivate an API key."""
    api_key = db.query(ApiKey).filter(
        and_(
            ApiKey.id == api_key_id,
            ApiKey.user_id == user_id
        )
    ).first()
    
    if not api_key:
        return False
    
    api_key.is_active = False
    db.commit()
    return True
