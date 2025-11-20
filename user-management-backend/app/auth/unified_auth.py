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

from ..database import get_database # Changed from get_db to get_database
from ..models.user import User
from .jwt import verify_token
from .clerk_verifier import verify_clerk_token
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
                # First try local JWT verification
                payload = verify_token(auth_header)

                # If local JWT verification failed, try Clerk JWKS verification
                if not payload:
                    try:
                        payload = verify_clerk_token(auth_header)
                        auth_method += " (verified via Clerk JWKS)"
                        print(f"DEBUG [unified_auth]: Clerk token verified, payload: {payload}")
                    except HTTPException as e:
                        auth_method += f" - Clerk verification failed (HTTPException): {e.detail}"
                        print(f"DEBUG [unified_auth]: Clerk verification HTTPException: {e.detail}")
                    except Exception as e:
                        auth_method += f" - Clerk verification failed: {str(e)}"
                        print(f"DEBUG [unified_auth]: Clerk verification Exception: {str(e)}")

                if payload:
                    # Prefer email-based lookup for external tokens
                    user_id = payload.get("sub")
                    user = None
                    print(f"DEBUG [unified_auth]: Looking up user with sub: {user_id}")
                    # Try by user id first when present
                    if user_id:
                        try:
                            user = await User.get(user_id)
                        except Exception:
                            user = None

                    # If not found by id, try email (common for Clerk tokens)
                    if not user:
                        email = payload.get("email")
                        print(f"DEBUG [unified_auth]: Email from payload: {email}")
                        if email:
                            user = await User.find_one(User.email == email)
                            print(f"DEBUG [unified_auth]: User lookup by email result: {user}")
                        
                        # If no email in token, use placeholder email format (for Clerk tokens)
                        if not email and user_id:
                            placeholder_email = f"{user_id}@clerk.user"
                            print(f"DEBUG [unified_auth]: Using placeholder email: {placeholder_email}")
                            user = await User.find_one(User.email == placeholder_email)
                            print(f"DEBUG [unified_auth]: User lookup by placeholder result: {user}")

                    # If still not found, create a minimal user record
                    if not user:
                        email = payload.get("email")
                        # Use placeholder email if no email in token (for Clerk)
                        if not email and user_id:
                            email = f"{user_id}@clerk.user"
                        
                        name = payload.get("name") or payload.get("full_name") or payload.get("preferred_username")
                        if email:
                            user = User(
                                email=email,
                                name=name or email.split("@")[0],
                                is_active=True
                            )
                            await user.insert()

                    if user:
                        # Map Clerk public_metadata to local roles/capabilities (if present)
                        try:
                            public_md = payload.get("public_metadata") or payload.get("metadata") or {}
                            if isinstance(public_md, str):
                                import json as _json
                                try:
                                    public_md = _json.loads(public_md)
                                except Exception:
                                    public_md = {}

                            role_md = public_md.get("role") or public_md.get("role_name")
                            if role_md:
                                from ..models.user import UserRole
                                role_md_l = str(role_md).lower()
                                if role_md_l == "admin" and user.role != UserRole.ADMIN:
                                    user.role = UserRole.ADMIN
                                    await user.save()
                                if role_md_l in ("developer", "dev") and not getattr(user, 'can_publish_content', False):
                                    user.can_publish_content = True
                                    await user.save()
                        except Exception:
                            pass
                        if not getattr(user, "is_active", True):
                            auth_method += " - User found but inactive"
                    else:
                        auth_method += " - User not found or inactive"
                else:
                    auth_method += " - Token verification failed"
            except (ValueError, TypeError) as e:
                auth_method += f" - Exception during token processing: {str(e)}"
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
