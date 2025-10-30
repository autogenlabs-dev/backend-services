"""User service functions for database operations."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
import secrets
import hashlib

from motor.motor_asyncio import AsyncIOMotorDatabase
from beanie.odm.fields import PydanticObjectId
# Removed SQLAlchemy imports
# from sqlalchemy.orm import Session
# from sqlalchemy import func, and_

from ..models.user import User, UserOAuthAccount, OAuthProvider, UserSubscription, TokenUsageLog, ApiKey
from ..schemas.auth import UserCreate, UserUpdate, TokenUsageCreate, ApiKeyCreate
from ..auth.jwt import get_password_hash, verify_password


async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: PydanticObjectId) -> Optional[User]:
    """Get user by ID."""
    # Beanie's get method works directly with PydanticObjectId
    return await User.get(user_id)


async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[User]:
    """Get user by email."""
    return await User.find_one(User.email == email)


async def create_user_with_password(db: AsyncIOMotorDatabase, user_data: UserCreate) -> User:
    """Create a new user with email and password."""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("User with this email already exists")

    hashed_password = get_password_hash(user_data.password)

    # Determine username: use provided username, or extract from email
    username = user_data.username if user_data.username else user_data.email.split('@')[0]
    
    # Determine name: use provided name, fallback to username, then email prefix
    name = user_data.name if user_data.name else username

    db_user = User(
        # Beanie generates ID automatically, no need for uuid4()
        email=user_data.email,
        password_hash=hashed_password,
        username=username,  # Set username field properly
        name=name,  # Use name from input or derived value
        is_active=True,
        subscription="free", # Default subscription
        tokens_remaining=10000, # Default tokens
        tokens_used=0,
        monthly_limit=10000, # Default monthly limit
        created_at=datetime.now(timezone.utc),  # Explicitly set created_at
        updated_at=datetime.now(timezone.utc), # Set updated_at on creation
        last_login_at=None, # No login yet
        full_name=user_data.full_name if user_data.full_name else None  # Set full_name if provided
    )
    await db_user.insert() # Use Beanie's insert method
    return db_user


async def authenticate_user(db: AsyncIOMotorDatabase, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    user = await get_user_by_email(db, email)
    if not user or not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def create_user(db: AsyncIOMotorDatabase, user_data: UserCreate) -> User:
    """Create a new user (simplified version, maybe for OAuth)."""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        # Return existing user if found, or raise error? Original code created a new user
        # even if email existed if it was called via create_user_with_password.
        # Let's align with the likely intent: if email exists, return that user.
        # If this function is only for OAuth, email might not be unique initially,
        # but the OAuth account link handles that. Let's stick to the original logic
        # of creating a new user if email doesn't exist via this path.
        # The create_user_with_password handles the email uniqueness check.
        pass # Allow creating user with existing email if not using password flow? Revisit this logic later if needed.

    db_user = User(
        # Beanie generates ID automatically
        email=user_data.email,
        is_active=True,
        subscription="free", # Default subscription
        tokens_remaining=10000, # Default tokens
        tokens_used=0,
        monthly_limit=10000, # Default monthly limit
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        last_login_at=None,
        full_name=getattr(user_data, 'full_name', None) # Allow full_name here too
    )
    await db_user.insert()
    return db_user


async def update_user(db: AsyncIOMotorDatabase, user_id: PydanticObjectId, user_data: UserUpdate) -> Optional[User]:
    """Update user information."""
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    # Use Beanie's update method or manual update and save
    # Manual update and save gives more control and is often clearer
    update_fields = user_data.model_dump(exclude_unset=True)

    # Check if email is being updated and if it's already in use by another user
    if 'email' in update_fields and update_fields['email'] != user.email:
        existing_user = await get_user_by_email(db, update_fields['email'])
        if existing_user and existing_user.id != user.id:
            raise ValueError("Email already in use by another user")
        user.email = update_fields['email']

    # Handle first_name and last_name to construct full_name
    first_name = update_fields.get('first_name')
    last_name = update_fields.get('last_name')
    
    if first_name is not None or last_name is not None:
        # If either first_name or last_name is provided, update full_name
        current_first = first_name if first_name is not None else (user.full_name.split(' ')[0] if user.full_name else '')
        current_last = last_name if last_name is not None else (' '.join(user.full_name.split(' ')[1:]) if user.full_name and len(user.full_name.split(' ')) > 1 else '')
        user.full_name = f"{current_first} {current_last}".strip()
        
        # Also update the name field with the full name
        if user.full_name:
            user.name = user.full_name    # Update other fields
    for field, value in update_fields.items():
        if field not in ['email', 'first_name', 'last_name']: # Skip already handled fields
             setattr(user, field, value)

    user.updated_at = datetime.now(timezone.utc)
    
    # Save the updated user
    await user.save()
    return user


async def update_user_last_login(db: AsyncIOMotorDatabase, user_id: PydanticObjectId) -> None:
    """Update user's last login timestamp."""
    user = await get_user_by_id(db, user_id)
    if user:
        user.last_login_at = datetime.now(timezone.utc)
        await user.save()


async def update_user_last_logout(db: AsyncIOMotorDatabase, user_id: PydanticObjectId) -> None:
    """Update user's last logout timestamp."""
    user = await get_user_by_id(db, user_id)
    if user:
        # Add last_logout_at field if it doesn't exist in the model
        user.last_logout_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        await user.save()


async def get_or_create_user_by_oauth(
    db: AsyncIOMotorDatabase,
    provider_name: str,
    provider_user_id: str,
    email: str,
    name: Optional[str] = None # Added name parameter for OAuth user creation
) -> User:
    """Get or create user from OAuth provider information."""
    # Get provider - Assuming OAuthProvider is also a Beanie Document
    # Need to ensure OAuthProvider document exists, maybe create defaults on startup
    provider = await OAuthProvider.find_one(OAuthProvider.name == provider_name)
    if not provider:
        # If provider doesn't exist, create it for now for simplicity
        # Get display name from OAuth providers configuration
        from ..auth.oauth import OAUTH_PROVIDERS
        provider_config = OAUTH_PROVIDERS.get(provider_name, {})
        display_name = provider_config.get("display_name", provider_name.title())
        
        provider = OAuthProvider(
            name=provider_name,
            display_name=display_name
        )
        await provider.insert()


    # Check if OAuth account exists
    oauth_account = await UserOAuthAccount.find_one(
        UserOAuthAccount.provider_id == provider.id,
        UserOAuthAccount.provider_user_id == provider_user_id
    )

    if oauth_account:
        # Update last used time
        oauth_account.last_used_at = datetime.now(timezone.utc)
        await oauth_account.save()
        # Need to fetch the user document explicitly
        user = await User.get(oauth_account.user_id)
        # Also update user's last login time
        if user:
            await update_user_last_login(db, user.id)
        return user

    # Check if user exists by email
    user = await get_user_by_email(db, email)
    if not user:
        # Create new user
        user = User(
            email=email,
            name=name or email.split('@')[0], # Use provided name or email prefix
            is_active=True,
            subscription="free", # Default subscription
            tokens_remaining=10000, # Default tokens
            tokens_used=0,
            monthly_limit=10000, # Default monthly limit
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            last_login_at=datetime.now(timezone.utc), # Set last login on creation
            full_name=name # Use provided name as full_name
        )
        await user.insert()

    # Create OAuth account link
    oauth_account = UserOAuthAccount(
        user_id=user.id,
        provider_id=provider.id,
        provider_user_id=provider_user_id,
        email=email,
        last_used_at=datetime.now(timezone.utc)
    )
    await oauth_account.insert()

    # Need to return the user document
    return user


async def get_user_oauth_accounts(db: AsyncIOMotorDatabase, user_id: PydanticObjectId) -> List[UserOAuthAccount]:
    """Get all OAuth accounts for a user."""
    # Beanie find returns a FindMany query builder, use to_list() to execute
    return await UserOAuthAccount.find(UserOAuthAccount.user_id == user_id).to_list()


async def get_user_subscription(db: AsyncIOMotorDatabase, user_id: PydanticObjectId) -> Optional[UserSubscription]:
    """Get user's current active subscription."""
    # Beanie find_one with multiple conditions
    return await UserSubscription.find_one(
        UserSubscription.user_id == user_id,
        UserSubscription.status == "active"
    )


async def log_token_usage(db: AsyncIOMotorDatabase, user_id: PydanticObjectId, usage_data: TokenUsageCreate) -> TokenUsageLog:
    """Log token usage for a user."""
    log_entry = TokenUsageLog(
        user_id=user_id,
        provider=usage_data.provider,
        model_name=usage_data.model_name,
        tokens_used=usage_data.tokens_used,
        cost_usd=usage_data.cost_usd,
        request_type=usage_data.request_type,
        request_metadata=usage_data.request_metadata,
        created_at=datetime.now(timezone.utc) # Explicitly set created_at
    )
    await log_entry.insert()
    return log_entry


async def get_user_token_usage(
    db: AsyncIOMotorDatabase,
    user_id: PydanticObjectId,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    provider: Optional[str] = None,
    limit: int = 100, # Added limit and offset for pagination
    offset: int = 0
) -> List[TokenUsageLog]:
    """Get token usage logs for a user with optional filters and pagination."""
    query = TokenUsageLog.find(TokenUsageLog.user_id == user_id)

    if start_date:
        query = query.find(TokenUsageLog.created_at >= start_date)

    if end_date:
        query = query.find(TokenUsageLog.created_at <= end_date)

    if provider:
        query = query.find(TokenUsageLog.provider == provider)

    # Apply sorting, skipping, and limiting
    return await query.sort(-TokenUsageLog.created_at).skip(offset).limit(limit).to_list()


async def get_user_token_usage_stats(
    db: AsyncIOMotorDatabase,
    user_id: PydanticObjectId,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> dict:
    """Get aggregated token usage statistics for a user."""
    query = TokenUsageLog.find(TokenUsageLog.user_id == user_id)

    if start_date:
        query = query.find(TokenUsageLog.created_at >= start_date)

    if end_date:
        query = query.find(TokenUsageLog.created_at <= end_date)

    logs = await query.to_list()

    # Aggregate statistics manually from the fetched logs
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


async def create_api_key(db: AsyncIOMotorDatabase, user_id: PydanticObjectId, key_data: ApiKeyCreate) -> tuple[ApiKey, str]:
    """Create a new API key for a user."""
    # Generate a secure random API key
    api_key = f"sk-{secrets.token_urlsafe(32)}"

    # Hash the API key for storage
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Create database record
    db_api_key = ApiKey(
        user_id=user_id,
        key_hash=key_hash,
        key_preview=api_key[:8],
        name=key_data.name,
        is_active=True,
        created_at=datetime.now(timezone.utc), # Explicitly set created_at
        last_used_at=None # Not used yet
    )

    await db_api_key.insert()

    return db_api_key, api_key


async def get_user_api_keys(db: AsyncIOMotorDatabase, user_id: PydanticObjectId) -> List[ApiKey]:
    """Get all API keys for a user."""
    return await ApiKey.find(ApiKey.user_id == user_id).to_list()


async def verify_api_key(db: AsyncIOMotorDatabase, api_key: str) -> Optional[User]:
    """Verify an API key and return the associated user."""
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    api_key_record = await ApiKey.find_one(
        ApiKey.key_hash == key_hash,
        ApiKey.is_active == True
    )

    if not api_key_record:
        return None

    # Update last used time
    api_key_record.last_used_at = datetime.now(timezone.utc)
    await api_key_record.save()

    # Return the user - Need to fetch the user document explicitly
    user = await User.get(api_key_record.user_id)
    return user


async def deactivate_api_key(db: AsyncIOMotorDatabase, user_id: PydanticObjectId, api_key_id: PydanticObjectId) -> bool:
    """Deactivate an API key."""
    api_key = await ApiKey.find_one(
        ApiKey.id == api_key_id,
        ApiKey.user_id == user_id
    )

    if not api_key:
        return False

    api_key.is_active = False
    await api_key.save()
    return True
