"""
Unified authentication dependency that supports both JWT tokens and API keys.
This enables seamless authentication for VS Code extensions using persistent API keys.
"""

from typing import Optional, Union, Any # Added Any import
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import sys
import logging

from ..config import settings
from ..database import get_database # Changed from get_db to get_database
from ..models.user import User
from .jwt import verify_token
from .api_key_auth_clean import api_key_service
from ..services.openrouter_keys import ensure_user_openrouter_key

# Setup logging
logger = logging.getLogger(__name__)

# HTTP Bearer token scheme (for JWT)
security = HTTPBearer(auto_error=False)


async def get_current_user_unified(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Any = Depends(get_database) # Changed type hint from Session to Any, and get_db to get_database
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
    print(f"DEBUG [unified_auth]: Function called", flush=True)
    sys.stdout.flush()
    print(f"DEBUG [unified_auth]: credentials present: {credentials is not None}", flush=True)
    sys.stdout.flush()
    if credentials:
        print(f"DEBUG [unified_auth]: credentials.credentials[:20]: {credentials.credentials[:20] if hasattr(credentials, 'credentials') else 'NO CREDENTIALS ATTR'}", flush=True)
        sys.stdout.flush()
    
    user = None
    auth_method = "unknown"
    
    # Method 1: Check for X-API-Key header (preferred for VS Code extensions)
    api_key = request.headers.get("X-API-Key")
    if api_key:
        auth_method = "X-API-Key header"
        result = await api_key_service.validate_api_key(api_key, db)
        if result:
            user, _ = result
    
    # Method 2: Check Authorization header
    if not user and credentials and hasattr(credentials, 'credentials'):
        auth_header = credentials.credentials
        
        # Check if it's an API key (starts with sk_)
        if auth_header.startswith("sk_"):
            auth_method = "Authorization header (API key)"
            result = await api_key_service.validate_api_key(auth_header, db)
            if result:
                user, _ = result
        
        # Otherwise treat as JWT token
        else:
            auth_method = "Authorization header (JWT)"
            try:
                from jose import jwt as jose_jwt, JWTError
                
                # Debug: Print token header and try unverified decode
                try:
                    header = jose_jwt.get_unverified_header(auth_header)
                    print(f"DEBUG [JWT]: Token header: {header}")
                    unverified = jose_jwt.decode(
                        auth_header,
                        settings.jwt_secret_key,
                        algorithms=["HS256"],
                        options={"verify_signature": False}
                    )
                    print(f"DEBUG [JWT]: Unverified payload sub={unverified.get('sub')}, email={unverified.get('email')}")
                except Exception as dbg_e:
                    print(f"DEBUG [JWT]: Pre-decode error: {dbg_e}")
                
                payload = jose_jwt.decode(
                    auth_header,
                    settings.jwt_secret_key,
                    algorithms=["HS256"]
                )
                
                if payload:
                    user_id = payload.get("sub")
                    email = payload.get("email")
                    print(f"DEBUG [unified_auth]: JWT payload - sub: {user_id}, email: {email}")
                    
                    # Try to find user by email first (most reliable)
                    if email:
                        user = await User.find_one(User.email == email)
                        print(f"DEBUG [unified_auth]: User lookup by email result: {user}")
                    
                    # If not found by email, try by user_id
                    if not user and user_id:
                        try:
                            user = await User.get(user_id)
                        except Exception:
                            user = None
                    
                    # Create user if not found (auto-registration)
                    if not user and email:
                        name = payload.get("name") or email.split("@")[0]
                        user = User(
                            email=email,
                            name=name,
                            is_active=True
                        )
                        await user.insert()
                        print(f"DEBUG [unified_auth]: Created new user: {email}")
                    
                    if not user:
                        auth_method += " - User not found"
                else:
                    auth_method += " - Token verification failed"
            except JWTError as e:
                print(f"DEBUG [JWT]: JWTError type={type(e).__name__}, msg={str(e)}")
                auth_method += f" - JWT Error: {str(e)}"
            except Exception as e:
                auth_method += f" - Exception: {str(e)}"
    elif not user and credentials and not hasattr(credentials, 'credentials'):
        auth_method = "Authorization header present but missing credentials attribute"
    elif not user and not credentials:
        auth_method = "No Authorization header provided"
    
    # Authentication failed
    if not user:
        detail_message = f"Could not validate credentials using {auth_method}. Please provide a valid JWT token or API key."
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail_message,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Provision OpenRouter key if user doesn't have one (for existing users)
    print(f"DEBUG [unified_auth]: Checking OpenRouter key for user {user.email}, current key: {user.openrouter_api_key}", flush=True)
    sys.stdout.flush()
    
    if not user.openrouter_api_key:
        print(f"DEBUG [unified_auth]: User {user.email} has no OpenRouter key, provisioning...", flush=True)
        sys.stdout.flush()
        try:
            await ensure_user_openrouter_key(user)
            logger.info(f"Provisioned OpenRouter key for existing user on login: {user.email}")
            print(f"DEBUG [unified_auth]: Successfully provisioned OpenRouter key for {user.email}", flush=True)
            sys.stdout.flush()
        except Exception as e:
            logger.warning(f"Failed to provision OpenRouter key for existing user {user.email}: {e}")
            print(f"DEBUG [unified_auth]: Failed to provision OpenRouter key: {e}", flush=True)
            sys.stdout.flush()
    else:
        print(f"DEBUG [unified_auth]: User {user.email} already has OpenRouter key", flush=True)
        sys.stdout.flush()
    
    return user


async def get_optional_current_user_unified(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Any = Depends(get_database) # Changed type hint from Session to Any, and get_db to get_database
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
