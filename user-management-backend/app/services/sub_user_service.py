from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any
from ..models.user import User, ApiKey
from ..models.organization import Organization, OrganizationMember
from ..schemas.user import UserCreate, UserResponse
from ..auth.password import hash_password
from ..exceptions import ValidationError, NotFoundError, PermissionError
import uuid
import logging

logger = logging.getLogger(__name__)

class SubUserService:
    """Service for managing sub-users (subscreens)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_sub_user(
        self,
        parent_user_id: uuid.UUID,
        email: str,
        name: str,
        permissions: Dict[str, Any] = None,
        token_limits: Dict[str, int] = None,
        password: str = None
    ) -> User:
        """Create a new sub-user under a parent user"""
        
        # Verify parent user exists and has permission to create sub-users
        parent_user = self.db.query(User).filter(User.id == parent_user_id).first()
        if not parent_user:
            raise NotFoundError("Parent user not found")
        
        # Check if parent user can create sub-users (based on subscription)
        if not self._can_create_sub_users(parent_user):
            raise PermissionError("User subscription does not allow sub-user creation")
        
        # Check sub-user limits
        current_sub_users = self.get_sub_users(parent_user_id)
        max_sub_users = self._get_max_sub_users(parent_user)
        
        if len(current_sub_users) >= max_sub_users:
            raise ValidationError(f"Maximum sub-users limit ({max_sub_users}) reached")
        
        # Set default permissions and limits
        default_permissions = {
            "api_access": True,
            "can_create_api_keys": True,
            "can_view_usage": True,
            "can_modify_settings": False,
            "allowed_endpoints": ["*"]  # All endpoints by default
        }
        
        default_limits = {
            "monthly_tokens": min(5000, parent_user.monthly_limit // 4),  # 25% of parent limit or 5k
            "requests_per_minute": 60,
            "max_api_keys": 3
        }
        
        permissions = {**default_permissions, **(permissions or {})}
        token_limits = {**default_limits, **(token_limits or {})}
        
        # Create sub-user
        try:
            sub_user = User(
                id=uuid.uuid4(),
                email=email,
                name=name,
                password_hash=hash_password(password) if password else None,
                parent_user_id=parent_user_id,
                is_sub_user=True,
                sub_user_permissions=permissions,
                sub_user_limits=token_limits,
                subscription=parent_user.subscription,  # Inherit subscription
                monthly_limit=token_limits["monthly_tokens"],
                tokens_remaining=token_limits["monthly_tokens"],
                role="user"
            )
            
            self.db.add(sub_user)
            self.db.commit()
            self.db.refresh(sub_user)
            
            logger.info(f"Created sub-user {email} for parent {parent_user.email}")
            return sub_user
            
        except IntegrityError:
            self.db.rollback()
            raise ValidationError("Email already exists")
    
    def get_sub_users(self, parent_user_id: uuid.UUID) -> List[User]:
        """Get all sub-users for a parent user"""
        return self.db.query(User).filter(
            User.parent_user_id == parent_user_id,
            User.is_sub_user == True,
            User.is_active == True
        ).all()
    
    def update_sub_user_permissions(
        self,
        parent_user_id: uuid.UUID,
        sub_user_id: uuid.UUID,
        permissions: Dict[str, Any]
    ) -> User:
        """Update permissions for a sub-user"""
        
        # Verify parent user owns the sub-user
        sub_user = self._get_sub_user_with_verification(parent_user_id, sub_user_id)
        
        # Update permissions
        current_permissions = sub_user.sub_user_permissions or {}
        updated_permissions = {**current_permissions, **permissions}
        
        sub_user.sub_user_permissions = updated_permissions
        self.db.commit()
        self.db.refresh(sub_user)
        
        return sub_user
    
    def update_sub_user_limits(
        self,
        parent_user_id: uuid.UUID,
        sub_user_id: uuid.UUID,
        limits: Dict[str, int]
    ) -> User:
        """Update token and rate limits for a sub-user"""
        
        sub_user = self._get_sub_user_with_verification(parent_user_id, sub_user_id)
        
        # Validate limits don't exceed parent user limits
        parent_user = self.db.query(User).filter(User.id == parent_user_id).first()
        
        if limits.get("monthly_tokens", 0) > parent_user.monthly_limit:
            raise ValidationError("Sub-user token limit cannot exceed parent user limit")
        
        # Update limits
        current_limits = sub_user.sub_user_limits or {}
        updated_limits = {**current_limits, **limits}
        
        sub_user.sub_user_limits = updated_limits
        
        # Update monthly_limit if specified
        if "monthly_tokens" in limits:
            sub_user.monthly_limit = limits["monthly_tokens"]
            # Adjust remaining tokens if new limit is lower
            if sub_user.tokens_remaining > limits["monthly_tokens"]:
                sub_user.tokens_remaining = limits["monthly_tokens"]
        
        self.db.commit()
        self.db.refresh(sub_user)
        
        return sub_user
    
    def create_sub_user_api_key(
        self,
        parent_user_id: uuid.UUID,
        sub_user_id: uuid.UUID,
        name: str = "Sub-user API Key"
    ) -> ApiKey:
        """Create an API key for a sub-user"""
        
        sub_user = self._get_sub_user_with_verification(parent_user_id, sub_user_id)
        
        # Check if sub-user can create API keys
        permissions = sub_user.sub_user_permissions or {}
        if not permissions.get("can_create_api_keys", True):
            raise PermissionError("Sub-user does not have permission to create API keys")
        
        # Check API key limits
        current_keys = self.db.query(ApiKey).filter(
            ApiKey.user_id == sub_user_id,
            ApiKey.is_active == True
        ).count()
        
        max_keys = sub_user.sub_user_limits.get("max_api_keys", 3)
        if current_keys >= max_keys:
            raise ValidationError(f"Maximum API keys limit ({max_keys}) reached")
        
        # Create API key with sub-user restrictions
        api_key = ApiKey(
            user_id=sub_user_id,
            name=name,
            key=self._generate_api_key(),
            is_active=True,
            metadata={
                "is_sub_user_key": True,
                "parent_user_id": str(parent_user_id),
                "permissions": permissions,
                "limits": sub_user.sub_user_limits
            }
        )
        
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        
        return api_key
    
    def delete_sub_user(self, parent_user_id: uuid.UUID, sub_user_id: uuid.UUID) -> bool:
        """Delete a sub-user"""
        
        sub_user = self._get_sub_user_with_verification(parent_user_id, sub_user_id)
        
        # Soft delete - deactivate instead of hard delete to preserve logs
        sub_user.is_active = False
        
        # Deactivate all API keys
        self.db.query(ApiKey).filter(ApiKey.user_id == sub_user_id).update(
            {"is_active": False}
        )
        
        self.db.commit()
        return True
    
    def get_sub_user_usage_stats(self, sub_user_id: uuid.UUID) -> Dict[str, Any]:
        """Get usage statistics for a sub-user"""
        
        sub_user = self.db.query(User).filter(User.id == sub_user_id).first()
        if not sub_user or not sub_user.is_sub_user:
            raise NotFoundError("Sub-user not found")
        
        return {
            "user_id": str(sub_user_id),
            "tokens_used": sub_user.tokens_used,
            "tokens_remaining": sub_user.tokens_remaining,
            "monthly_limit": sub_user.monthly_limit,
            "usage_percentage": (sub_user.tokens_used / sub_user.monthly_limit * 100) if sub_user.monthly_limit > 0 else 0,
            "last_active": sub_user.last_login_at,
            "api_keys_count": self.db.query(ApiKey).filter(
                ApiKey.user_id == sub_user_id,
                ApiKey.is_active == True
            ).count()
        }
    
    def _can_create_sub_users(self, user: User) -> bool:
        """Check if user can create sub-users based on subscription"""
        if user.subscription == "free":
            return False
        elif user.subscription == "pro":
            return True
        elif user.subscription == "enterprise":
            return True
        return False
    
    def _get_max_sub_users(self, user: User) -> int:
        """Get maximum sub-users allowed for user subscription"""
        if user.subscription == "pro":
            return 5
        elif user.subscription == "enterprise":
            return 50
        return 0
    
    def _get_sub_user_with_verification(self, parent_user_id: uuid.UUID, sub_user_id: uuid.UUID) -> User:
        """Get sub-user and verify ownership"""
        sub_user = self.db.query(User).filter(
            User.id == sub_user_id,
            User.parent_user_id == parent_user_id,
            User.is_sub_user == True
        ).first()
        
        if not sub_user:
            raise NotFoundError("Sub-user not found or access denied")
        
        return sub_user
    
    def _generate_api_key(self) -> str:
        """Generate a secure API key"""
        import secrets
        import string
        
        # Generate a secure random string
        alphabet = string.ascii_letters + string.digits
        return "sk-sub-" + "".join(secrets.choice(alphabet) for _ in range(32))
