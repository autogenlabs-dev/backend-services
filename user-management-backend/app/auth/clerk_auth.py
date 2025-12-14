"""
Clerk Authentication Middleware for FastAPI Backend.

This module provides authentication using Clerk JWT tokens from the frontend.
It validates Clerk session tokens and syncs user data with the backend database.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import httpx
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from beanie import PydanticObjectId

from ..config import settings
from ..models.user import User, UserRole
from ..database import get_database

# HTTP Bearer token scheme
security = HTTPBearer()

# Clerk JWKS URL for token verification
CLERK_JWKS_URL = "https://apt-clam-53.clerk.accounts.dev/.well-known/jwks.json"
CLERK_ISSUER = "https://apt-clam-53.clerk.accounts.dev"


async def get_clerk_jwks() -> Dict[str, Any]:
    """Fetch Clerk's JSON Web Key Set (JWKS) for token verification."""
    async with httpx.AsyncClient() as client:
        response = await client.get(CLERK_JWKS_URL)
        response.raise_for_status()
        return response.json()


async def verify_clerk_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Clerk JWT token and return payload.
    
    Args:
        token: The JWT token from Clerk
        
    Returns:
        Token payload if valid, None otherwise
    """
    try:
        # First get unverified claims for debugging
        unverified_payload = jwt.get_unverified_claims(token)
        
        # Basic validation
        if not unverified_payload.get("sub"):
            print("❌ Token missing 'sub' claim")
            return None
        
        # Check issuer if present
        issuer = unverified_payload.get("iss")
        if issuer and issuer != CLERK_ISSUER:
            print(f"❌ Invalid issuer: {issuer}, expected: {CLERK_ISSUER}")
            return None
        
        # Proper JWKS verification for production
        try:
            # Get the key ID from token header
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            
            if not kid:
                print("⚠️ Token missing 'kid' in header - may be legacy JWT")
                # Fall back to unverified for development only — explicit debug message
                if settings.debug:
                    print("⚠️ Debug mode - unverified token accepted")
                    return unverified_payload
                print("❌ Rejecting token: missing 'kid'")
                return None
            
            # Fetch JWKS from Clerk
            jwks_data = await get_clerk_jwks()
            
            # Find matching key in JWKS
            signing_key = None
            for key in jwks_data.get("keys", []):
                if key.get("kid") == kid:
                    signing_key = key
                    break
            
            if not signing_key:
                print(f"❌ No matching key found in JWKS for kid: {kid}")
                # Fall back to unverified for development only — explicit debug message
                if settings.debug:
                    print("⚠️ Debug mode - unverified token accepted")
                    return unverified_payload
                return None
            
            # Verify the token with proper signature validation
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                issuer=CLERK_ISSUER,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_aud": False  # Clerk doesn't always include aud
                }
            )
            
            print(f"✅ Clerk token verified for user: {payload.get('sub')}")
            return payload
            
        except Exception as jwks_error:
            print(f"⚠️ JWKS verification failed: {jwks_error}")
            # In debug mode, fall back to unverified claims with clear message
            if settings.debug:
                print("⚠️ Debug mode - unverified token accepted")
                return unverified_payload
            return None
        
    except JWTError as e:
        print(f"❌ JWT verification error: {e}")
        return None
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def get_or_create_user_from_clerk(clerk_payload: Dict[str, Any], db: Any) -> User:
    """
    Get or create a user from Clerk token payload.
    
    Args:
        clerk_payload: The decoded Clerk JWT payload
        db: Database connection
        
    Returns:
        User object from database
    """
    clerk_user_id = clerk_payload.get("sub")
    email = clerk_payload.get("email")
    
    if not clerk_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token: missing user ID"
        )
    
    # Try to find user by Clerk ID first
    user = await User.find_one(User.clerk_id == clerk_user_id)
    
    # If not found by Clerk ID, try by email
    if not user and email:
        user = await User.find_one(User.email == email)
        
        # If found by email, update with Clerk ID
        if user:
            user.clerk_id = clerk_user_id
            await user.save()
    
    # If still not found, create new user
    if not user:
        # Extract user data from Clerk token
        name = clerk_payload.get("name") or clerk_payload.get("full_name") or "User"
        first_name = clerk_payload.get("given_name") or clerk_payload.get("first_name")
        last_name = clerk_payload.get("family_name") or clerk_payload.get("last_name")
        
        user = User(
            email=email or f"{clerk_user_id}@clerk.user",  # Fallback email
            clerk_id=clerk_user_id,
            name=name,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            email_verified=clerk_payload.get("email_verified", False),
            role=UserRole.USER,
            tokens_remaining=10000,  # Default tokens for new users
            tokens_used=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await user.insert()
        print(f"✅ Created new user from Clerk: {email} (Clerk ID: {clerk_user_id})")
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    await user.save()
    
    return user


async def get_current_user_clerk(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Any = Depends(get_database)
) -> User:
    """
    Get the current authenticated user from Clerk JWT token.
    
    This is the main dependency for protecting routes with Clerk authentication.
    
    Usage:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user_clerk)):
            return {"user_id": str(current_user.id), "email": current_user.email}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        # Verify Clerk token
        payload = await verify_clerk_token(token)
        
        if payload is None:
            raise credentials_exception
        
        # Get or create user from Clerk data
        user = await get_or_create_user_from_clerk(payload, db)
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Authentication error: {e}")
        raise credentials_exception


async def get_optional_current_user_clerk(
    authorization: Optional[str] = Header(None),
    db: Any = Depends(get_database)
) -> Optional[User]:
    """
    Get the current user if authenticated with Clerk, None otherwise.
    
    This is useful for endpoints that have optional authentication.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = await verify_clerk_token(token)
        
        if payload is None:
            return None
        
        user = await get_or_create_user_from_clerk(payload, db)
        
        if not user.is_active:
            return None
        
        return user
        
    except Exception as e:
        print(f"Optional auth error: {e}")
        return None


async def require_clerk_auth(
    current_user: User = Depends(get_current_user_clerk)
) -> User:
    """
    Require Clerk authentication (alias for compatibility).
    """
    return current_user
