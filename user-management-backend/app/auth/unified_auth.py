"""
Unified authentication dependency that supports both JWT tokens and API keys.
This enables seamless authentication for VS Code extensions using persistent API keys.
"""

from typing import Optional, Union
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from .jwt import verify_token
from .api_key_auth_clean import api_key_service

# HTTP Bearer token scheme (for JWT)
security = HTTPBearer(auto_error=False)


async def get_current_user_unified(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user using either JWT token or API key.
    
    Authentication methods (in order of preference):
    1. X-API-Key header
    2. Authorization header with API key (Bearer sk_...)
    3. Authorization header with JWT token (Bearer eyJ...)
    
    This unified approach allows VS Code extensions to use persistent API keys
    while still supporting web applications using JWT tokens.
    """
    user = None
    auth_method = "unknown"
    
    # Method 1: Check for X-API-Key header (preferred for VS Code extensions)
    api_key = request.headers.get("X-API-Key")
    if api_key:
        auth_method = "X-API-Key header"
        result = api_key_service.validate_api_key(api_key, db)
        if result:
            user, _ = result
    
    # Method 2: Check Authorization header
    if not user and credentials:
        auth_header = credentials.credentials
        
        # Check if it's an API key (starts with sk_)
        if auth_header.startswith("sk_"):
            auth_method = "Authorization header (API key)"
            result = api_key_service.validate_api_key(auth_header, db)
            if result:
                user, _ = result
        
        # Otherwise treat as JWT token
        else:
            auth_method = "Authorization header (JWT)"
            try:
                payload = verify_token(auth_header)
                if payload:
                    user_id = payload.get("sub")
                    if user_id:
                        user_uuid = UUID(user_id)
                        user = db.query(User).filter(
                            User.id == user_uuid,
                            User.is_active == True
                        ).first()
            except (ValueError, TypeError):
                pass
    
    # Authentication failed
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials. Please provide a valid JWT token or API key.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_optional_current_user_unified(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authenticated (either JWT or API key), None otherwise.
    """
    try:
        return await get_current_user_unified(request, credentials, db)
    except HTTPException:
        return None


# Aliases for backward compatibility
get_current_user_api_or_jwt = get_current_user_unified
get_optional_current_user_api_or_jwt = get_optional_current_user_unified
