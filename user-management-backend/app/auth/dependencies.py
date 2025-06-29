"""FastAPI authentication dependencies."""

from typing import Optional, Any # Added Any import
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_database # Changed from get_db to get_database
from ..models.user import User
from .jwt import verify_token

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Any = Depends(get_database) # Changed type hint from Session to Any, and get_db to get_database
) -> User:
    """Get the current authenticated user from JWT token."""
    from .jwt import verify_token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Convert user_id to UUID if it's a string
        try:
            if isinstance(user_id, str):
                user_id = UUID(user_id)
        except (ValueError, TypeError):
            raise credentials_exception
            
        # Get user from database
        # MongoDB: Find user by ID
        user = await User.get(user_id) # Use Beanie's get method
        if user is None:
            raise credentials_exception
            
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
            
    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user (alias for compatibility)."""
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Any = Depends(get_database) # Changed type hint from Session to Any, and get_db to get_database
) -> Optional[User]:
    """Get the current user if authenticated, None otherwise."""
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
            
        user_uuid = UUID(user_id)
        # MongoDB: Find user by ID and active status
        user = await User.find_one(User.id == user_uuid, User.is_active == True) # Use Beanie's find_one method
        return user
        
    except (ValueError, TypeError):
        return None
