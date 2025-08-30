"""
API Key authentication system for the FastAPI marketplace backend.
Provides secure API key generation, validation, and management.
"""

import secrets
import hashlib
import string
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple, List
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Any # Added Any import
from beanie import PydanticObjectId # Added PydanticObjectId import
from app.database import get_database # Changed from get_db to get_database
from app.models.user import User, ApiKey
from pydantic import BaseModel

security = HTTPBearer(auto_error=False)

class ApiKeyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    expires_in_days: Optional[int] = None  # None means no expiration

class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key_preview: str
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool

class ApiKeyCreateResponse(BaseModel):
    id: str
    name: str
    api_key: str  # Full key only returned once
    key_preview: str
    created_at: datetime
    expires_at: Optional[datetime]

class ApiKeyService:
    """Service for managing API keys"""
    
    @staticmethod
    def generate_api_key(prefix: str = "sk") -> str:
        """
        Generate a secure API key
        Format: sk_live_[32_random_chars] or sk_test_[32_random_chars]
        """
        # Generate 32 random characters (alphanumeric)
        random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        return f"{prefix}_live_{random_part}"
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def get_key_preview(api_key: str) -> str:
        """Get first 8 characters for display purposes"""
        return api_key[:8] if len(api_key) >= 8 else api_key

    async def create_api_key( # Added async
        self,
        user_id: PydanticObjectId, # Changed type hint from str to PydanticObjectId
        name: str,
        db: Any, # Changed type hint from Session to Any
        description: Optional[str] = None,
        expires_in_days: Optional[int] = None
    ) -> ApiKeyCreateResponse:
        """Create a new API key for a user"""
        
        # Generate the API key
        api_key = self.generate_api_key()
        key_hash = self.hash_api_key(api_key)
        key_preview = self.get_key_preview(api_key)
        
        # Calculate expiration date
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        
        # Create API key record
        api_key_obj = ApiKey(
            user_id=user_id,
            key_hash=key_hash,
            key_preview=key_preview,
            name=name,
            expires_at=expires_at,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        await api_key_obj.insert() # Use Beanie's insert method
        
        return ApiKeyCreateResponse(
            id=str(api_key_obj.id),
            name=api_key_obj.name,
            api_key=api_key,  # Only returned once
            key_preview=key_preview,
            created_at=api_key_obj.created_at,
            expires_at=expires_at
        )
    
    async def validate_api_key( # Added async
        self,
        api_key: str,
        db: Any # Changed type hint from Session to Any
    ) -> Optional[Tuple[User, ApiKey]]:
        """
        Validate API key and return associated user and key object
        
        Returns:
            Tuple of (User, ApiKey) if valid, None if invalid
        """
        try:
            # Hash the provided key
            key_hash = self.hash_api_key(api_key)
            
            # Find the API key record using Beanie
            api_key_obj = await ApiKey.find_one(
                ApiKey.key_hash == key_hash,
                ApiKey.is_active == True
            )
            
            if not api_key_obj:
                return None
            
            # Get the associated user
            user = await User.get(api_key_obj.user_id)
            
            if not user or not user.is_active:
                return None
            
            # Check if key has expired
            if api_key_obj.expires_at and api_key_obj.expires_at < datetime.now(timezone.utc):
                # Automatically deactivate expired keys
                api_key_obj.is_active = False
                db.commit()
                return None
            
            # Update last used timestamp
            api_key_obj.last_used_at = datetime.now(timezone.utc)
            await api_key_obj.save() # Use Beanie's save method
            
            return user, api_key_obj
            
        except Exception as e:
            print(f"API key validation error: {e}")
            return None
    
    async def list_user_api_keys( # Added async
        self,
        user_id: PydanticObjectId, # Changed type hint from str to PydanticObjectId
        db: Any # Changed type hint from Session to Any
    ) -> List[ApiKeyResponse]:
        """List all API keys for a user (without the actual key values)"""
        
        # List all API keys for a user using Beanie
        api_keys = await ApiKey.find(
            ApiKey.user_id == user_id,
            ApiKey.is_active == True
        ).sort(-ApiKey.created_at).to_list()
        
        return [
            ApiKeyResponse(
                id=str(key.id),
                name=key.name,
                key_preview=key.key_preview,
                created_at=key.created_at,
                last_used_at=key.last_used_at,
                expires_at=key.expires_at,
                is_active=key.is_active
            )
            for key in api_keys
        ]
    
    async def revoke_api_key( # Added async
        self,
        key_id: PydanticObjectId, # Changed type hint from str to PydanticObjectId
        user_id: PydanticObjectId, # Changed type hint from str to PydanticObjectId
        db: Any # Changed type hint from Session to Any
    ) -> bool:
        """Revoke (deactivate) an API key"""
        
        api_key = await ApiKey.find_one(
            ApiKey.id == key_id,
            ApiKey.user_id == user_id
        )
        if not api_key:
            return False
        
        api_key.is_active = False
        await api_key.save() # Use Beanie's save method
        return True

# Global service instance
api_key_service = ApiKeyService()

class ApiKeyAuth:
    """API Key authentication dependency"""
    
    def __init__(self, required: bool = True):
        self.required = required
    
    async def __call__(
        self,
        request: Request,
        db: Any = Depends(get_database) # Changed type hint from Session to Any, and get_db to get_database
    ) -> Optional[Tuple[User, ApiKey]]:
        """
        Extract and validate API key from request
        
        Checks multiple locations:
        1. X-API-Key header
        2. Authorization header with "Bearer" or "Api-Key" scheme
        3. api_key query parameter (less secure, for testing only)
        """
        
        api_key = None
        
        # Method 1: X-API-Key header (preferred)
        api_key = request.headers.get("X-API-Key")
        
        # Method 2: Authorization header
        if not api_key:
            auth_header = request.headers.get("Authorization")
            if auth_header:
                if auth_header.startswith("Api-Key "):
                    api_key = auth_header[8:]  # Remove "Api-Key " prefix
                elif auth_header.startswith("Bearer ") and auth_header[7:].startswith("sk_"):
                    api_key = auth_header[7:]  # Remove "Bearer " prefix
        
        # Method 3: Query parameter (less secure, for testing)
        if not api_key:
            api_key = request.query_params.get("api_key")
        
        if not api_key:
            if self.required:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key required",
                    headers={"WWW-Authenticate": "Api-Key"}
                )
            return None
        
        # Validate the API key
        result = api_key_service.validate_api_key(api_key, db)
        
        if not result:
            if self.required:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired API key",
                    headers={"WWW-Authenticate": "Api-Key"}
                )
            return None
        
        return result

# Dependency instances
require_api_key = ApiKeyAuth(required=True)
optional_api_key = ApiKeyAuth(required=False)

async def get_current_user_from_api_key(
    auth_result: Tuple[User, ApiKey] = Depends(require_api_key)
) -> User:
    """Get current user from API key authentication"""
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    user, api_key = auth_result
    return user

async def get_api_key_info(
    auth_result: Tuple[User, ApiKey] = Depends(require_api_key)
) -> ApiKey:
    """Get API key information from authentication"""
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    user, api_key = auth_result
    return api_key
