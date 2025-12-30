"""Authentication API endpoints."""

from datetime import timedelta
from typing import Dict, Any, Optional
from uuid import UUID
import hashlib
import base64
import secrets

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from beanie import PydanticObjectId
from datetime import datetime

from ..database import get_database, get_redis
from ..schemas.auth import TokenRefresh, OAuthCallback, UserCreate, UserLogin
from ..models.user import User
from ..auth.jwt import create_access_token, create_refresh_token, verify_token, get_password_hash
from ..auth.oauth import get_oauth_client, get_provider_config, oauth
from ..auth.dependencies import get_current_user
from ..auth.unified_auth import get_current_user_unified
from ..services.user_service import (
    get_or_create_user_by_oauth, 
    update_user_last_login, 
    create_user_with_password,
    authenticate_user
)
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserInfoRequest(BaseModel):
    """Request model for getting user info from OAuth provider."""
    code: str = Field(..., description="Authorization code from OAuth provider")


class UserResponse(BaseModel):
    """Response model for user information."""
    id: str
    email: EmailStr
    is_active: bool
    created_at: str | None = None
    updated_at: str | None = None
    last_login_at: str | None = None


class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None


class PKCETokenRequest(BaseModel):
    """Request model for PKCE token exchange."""
    grant_type: str = Field(..., description="Must be 'authorization_code'")
    code: str = Field(..., description="Authorization code from OAuth callback")
    code_verifier: str = Field(..., description="PKCE code verifier")
    redirect_uri: str = Field(..., description="Redirect URI used in authorization request")


class PKCETokenResponse(BaseModel):
    """Response model for PKCE token exchange."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    session_id: str
    organization_id: Optional[str] = None


@router.get("/providers")
async def list_oauth_providers() -> Dict[str, Any]:
    """List available OAuth providers."""
    from ..auth.oauth import OAUTH_PROVIDERS
    
    providers = []
    for name, config in OAUTH_PROVIDERS.items():
        # Use getattr to access settings attributes dynamically
        client_id = getattr(settings, f'{name}_client_id', None)
        client_secret = getattr(settings, f'{name}_client_secret', None)
        if client_id and client_secret:
            providers.append({
                "name": name,
                "display_name": config["display_name"],
                "authorization_url": f"/api/auth/{name}/login"
            })
    return {"providers": providers}


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Register a new user with email and password."""
    try:
        user = await create_user_with_password(db, user_data)
        return UserResponse(
            id=str(user.id),
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"Registration error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup_user(user_data: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Alias for user registration to support /signup route with token generation."""
    try:
        # Register the user
        user = await register_user(user_data, db)
        
        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Return user data and tokens
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        import traceback
        print(f"Error in signup: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Login user with email and password."""
    user = await authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    if user.id:
        await update_user_last_login(db, user.id)
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "a4f_api_key": settings.a4f_api_key,
        "api_endpoint": "http://localhost:8000",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
        }
    }
        

@router.post("/login-json", response_model=Token)
async def login_user_json(
    user_data: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Login user with email and password using JSON."""
    user = await authenticate_user(db, user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    if user.id:
        await update_user_last_login(db, user.id)
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "a4f_api_key": settings.a4f_api_key,
        "api_endpoint": "http://localhost:8000",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
        }
    }


# Google Login (redirect user to Google's OAuth page)
@router.get("/google/login")
@router.head("/google/login")
async def google_login(
    request: Request,
    state: Optional[str] = None,
    source: Optional[str] = None,  # ← Added source parameter
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    redis_client = Depends(get_redis)
):
    """
    Initiate Google OAuth login with optional PKCE support.
    
    Parameters:
    - state: CSRF protection token
    - source: Origin of request ('vscode' for VS Code extension, 'web' for web app)
    - code_challenge: PKCE code challenge (SHA256 hash of code_verifier)
    - code_challenge_method: PKCE method (S256 or plain)
    - redirect_uri: Custom redirect URI for the callback
    """
    # Use provided redirect_uri or fallback to configured one
    oauth_redirect_uri = redirect_uri or settings.google_redirect_uri
    
    # Ensure OAuth client is properly initialized
    if not oauth.google:
        # Re-register OAuth clients if not available
        from ..auth.oauth import register_oauth_clients
        register_oauth_clients()
    
    if not oauth.google:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth client is not available"
        )
    
    # Store PKCE parameters in Redis if provided
    if state and code_challenge:
        import json
        pkce_data = {
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method or "S256",
            "redirect_uri": oauth_redirect_uri,
            "source": source or "web",  # ← Store source parameter
            "created_at": datetime.utcnow().isoformat()
        }
        # Store with 10 minute expiry
        redis_client.setex(f"oauth:pkce:{state}", 600, json.dumps(pkce_data))
    
    return await oauth.google.authorize_redirect(request, oauth_redirect_uri, state=state)


# Google OAuth callback
@router.get("/google/callback")
async def google_callback(
    request: Request,
    state: Optional[str] = None,
    redis_client = Depends(get_redis),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Handle Google OAuth callback.
    
    Supports both traditional OAuth flow (returns tokens directly) and
    PKCE flow (generates authorization code for token exchange).
    """
    try:
        # Ensure OAuth client is properly initialized
        if not oauth.google:
            # Re-register OAuth clients if not available
            from ..auth.oauth import register_oauth_clients
            register_oauth_clients()
        
        if not oauth.google:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Google OAuth client is not available"
            )
        
        # Check if this is an extension or PKCE flow
        import json
        pkce_data = None
        extension_data = None
        
        if state:
            # Check for extension auth flow
            extension_key = f"extension:auth:{state}"
            extension_data_str = redis_client.get(extension_key)
            if extension_data_str:
                extension_data = json.loads(extension_data_str)
                # Delete extension data after reading (one-time use)
                redis_client.delete(extension_key)
            
            # Check for PKCE flow
            pkce_key = f"oauth:pkce:{state}"
            pkce_data_str = redis_client.get(pkce_key)
            if pkce_data_str:
                pkce_data = json.loads(pkce_data_str)
                # Delete PKCE data after reading (one-time use)
                redis_client.delete(pkce_key)
        
        # Exchange authorization code for access token
        token = await oauth.google.authorize_access_token(request)

        # Fetch user info from Google
        user_info = await oauth.google.get("userinfo", token=token)
        user_data = user_info.json()

        # Example: Extract useful info
        email = user_data.get("email")
        name = user_data.get("name")
        picture = user_data.get("picture")

        # Get or create user in database
        user = await get_or_create_user_by_oauth(
            db=db,
            provider_name="google",
            provider_user_id=user_data.get("id"),
            email=email
        )

        # Update last login
        if user and user.id:
            await update_user_last_login(db, user.id)
        
        # If extension flow, generate ticket and redirect
        if extension_data:
            # Generate authorization ticket
            ticket = secrets.token_urlsafe(32)
            
            # Store ticket with user data in Redis
            ticket_data = {
                "user_id": str(user.id),
                "email": user.email,
                "created_at": datetime.utcnow().isoformat()
            }
            # Store with 5 minute expiry (tickets should be short-lived)
            redis_client.setex(f"extension:ticket:{ticket}", 300, json.dumps(ticket_data))
            
            # Redirect to extension callback with ticket
            auth_redirect = extension_data.get("auth_redirect")
            # Append /auth/clerk/callback path to the vscode:// URI
            redirect_url = f"{auth_redirect}/auth/clerk/callback?code={ticket}&state={state}"
            
            return RedirectResponse(
                url=redirect_url,
                status_code=302
            )
        
        # If PKCE flow, generate authorization code and redirect
        if pkce_data:
            # Generate authorization code
            auth_code = secrets.token_urlsafe(32)
            
            # Store authorization code with user data in Redis
            auth_code_data = {
                "user_id": str(user.id),
                "email": user.email,
                "code_challenge": pkce_data.get("code_challenge"),
                "code_challenge_method": pkce_data.get("code_challenge_method"),
                "redirect_uri": pkce_data.get("redirect_uri"),
                "created_at": datetime.utcnow().isoformat()
            }
            # Store with 5 minute expiry (authorization codes should be short-lived)
            redis_client.setex(f"oauth:code:{auth_code}", 300, json.dumps(auth_code_data))
            
            # Redirect to VS Code extension callback with authorization code
            redirect_uri = pkce_data.get("redirect_uri")
            redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
            
            return RedirectResponse(
                url=redirect_url,
                status_code=302
            )

        # Traditional OAuth flow - return tokens directly
        # Create JWT tokens
        access_token_jwt = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        refresh_token_jwt = create_refresh_token(
            data={"sub": str(user.id)}
        )

        # ← Check source from PKCE data or default to web
        source = pkce_data.get("source", "web") if pkce_data else "web"
        
        # Redirect based on source
        if source == "vscode":
            # Redirect to HTML page that will open VS Code
            redirect_url = f"http://localhost:8000/static/vscode-callback.html?token={access_token_jwt}"
        else:
            # Redirect to web app
            redirect_url = f"http://localhost:3000/auth/callback?access_token={access_token_jwt}&refresh_token={refresh_token_jwt}&user_id={str(user.id)}"
        
        return RedirectResponse(
            url=redirect_url,
            status_code=302
        )

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.post("/token", response_model=PKCETokenResponse)
async def exchange_authorization_code(
    token_request: PKCETokenRequest,
    redis_client = Depends(get_redis),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Exchange authorization code for access token with PKCE validation.
    
    This endpoint implements the OAuth 2.0 Authorization Code Flow with PKCE
    (Proof Key for Code Exchange) as specified in RFC 7636.
    
    Flow:
    1. Client generates code_verifier and code_challenge
    2. Client requests authorization with code_challenge
    3. Backend stores code_challenge with authorization code
    4. Client exchanges authorization code + code_verifier for tokens
    5. Backend validates code_verifier matches stored code_challenge
    """
    try:
        # Validate grant type
        if token_request.grant_type != "authorization_code":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid grant_type. Must be 'authorization_code'"
            )
        
        # Retrieve stored authorization data from Redis
        auth_data_key = f"oauth:code:{token_request.code}"
        stored_data = redis_client.get(auth_data_key)
        
        if not stored_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired authorization code"
            )
        
        # Parse stored data
        import json
        auth_data = json.loads(stored_data)
        
        # Validate redirect URI matches
        if auth_data.get("redirect_uri") != token_request.redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Redirect URI mismatch"
            )
        
        # Validate PKCE code_verifier
        stored_code_challenge = auth_data.get("code_challenge")
        code_challenge_method = auth_data.get("code_challenge_method", "S256")
        
        if stored_code_challenge:
            # Compute challenge from verifier
            if code_challenge_method == "S256":
                computed_challenge = base64.urlsafe_b64encode(
                    hashlib.sha256(token_request.code_verifier.encode()).digest()
                ).decode().rstrip("=")
            elif code_challenge_method == "plain":
                computed_challenge = token_request.code_verifier
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unsupported code_challenge_method"
                )
            
            # Verify challenge matches
            if computed_challenge != stored_code_challenge:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid code_verifier"
                )
        
        # Get user data
        user_id = auth_data.get("user_id")
        email = auth_data.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authorization code data"
            )
        
        # Fetch user from database
        from ..services.user_service import get_user_by_id
        try:
            user_obj_id = PydanticObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        user = await get_user_by_id(db, user_obj_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        if not user.id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User ID is missing"
            )
        
        # Update last login
        await update_user_last_login(db, user.id)
        
        # Generate tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        # Generate session ID
        session_id = secrets.token_urlsafe(32)
        
        # Store session in Redis (optional, for session management)
        session_key = f"session:{session_id}"
        redis_client.setex(
            session_key,
            86400,  # 24 hours
            json.dumps({
                "user_id": str(user.id),
                "email": user.email,
                "created_at": datetime.utcnow().isoformat()
            })
        )
        
        # Delete used authorization code
        redis_client.delete(auth_data_key)
        
        return PKCETokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            session_id=session_id,
            organization_id=auth_data.get("organization_id")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Token exchange error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to exchange authorization code for token"
        )


@router.post("/refresh")
async def refresh_access_token(
    token_data: TokenRefresh,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Token:
    """Refresh an access token using a refresh token."""
    # Verify token
    payload = verify_token(token_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify user still exists and is active
    from ..services.user_service import get_user_by_id
    from beanie import PydanticObjectId
    
    # Convert string ID to PydanticObjectId for MongoDB
    try:
        user_obj_id = PydanticObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format"
        )
    
    user = await get_user_by_id(db, user_obj_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user = Depends(get_current_user_unified),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Logout current user and invalidate tokens."""
    try:
        # Get the authorization header to extract the token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            # In a production system, you would blacklist the token here
            # For now, we'll update the user's last logout time
            from ..services.user_service import update_user_last_logout
            try:
                await update_user_last_logout(db, current_user.id)
            except Exception as e:
                print(f"Warning: Could not update last logout time: {e}")
        
        return {
            "success": True,
            "message": "Successfully logged out",
            "user_id": str(current_user.id)
        }
    except Exception as e:
        print(f"Logout error: {e}")
        # Even if there's an error, we should still return success for logout
        return {
            "success": True,
            "message": "Successfully logged out",
            "user_id": str(current_user.id)
        }


@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user_unified)):
    """Get current user information."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "last_login_at": current_user.last_login_at
    }


@router.get("/debug/oauth")
async def debug_oauth_flow(request: Request):
    """Debug endpoint to check OAuth configuration and state"""
    from ..auth.oauth import OAUTH_PROVIDERS
    
    debug_info = {
        "oauth_providers": {},
        "session_data": {},
        "request_headers": dict(request.headers),
        "request_cookies": dict(request.cookies)
    }
    
    # Check OAuth provider configurations
    for name, config in OAUTH_PROVIDERS.items():
        client_id = getattr(settings, f'{name}_client_id', None)
        client_secret = getattr(settings, f'{name}_client_secret', None)
        
        debug_info["oauth_providers"][name] = {
            "configured": bool(client_id and client_secret),
            "client_id_set": bool(client_id),
            "client_secret_set": bool(client_secret),
            "is_placeholder": client_id and "your_" in client_id
        }
    
    # Check session data if available
    if hasattr(request, 'session') and request.session:
        debug_info["session_data"] = dict(request.session)
    
    return debug_info


@router.get("/debug/cleanup")
async def cleanup_oauth_session(request: Request):
    """Cleanup OAuth session data for testing"""
    if hasattr(request, 'session'):
        request.session.clear()
    
    return {"message": "Session cleared successfully"}


@router.get("/vscode-config")
async def get_vscode_configuration(
    current_user: User = Depends(get_current_user_unified)
):
    """Get configuration for VS Code extension auto-setup."""
    return {
        "success": True,
        "config": {
            "a4f_api_key": settings.a4f_api_key,
            "api_endpoint": "http://localhost:8000",
            "user": {
                "id": str(current_user.id),
                "email": current_user.email,
                "subscription": getattr(current_user, 'subscription_tier', 'free')
            },
            "providers": {
                "a4f": {
                    "base_url": "https://api.a4f.co/v1",
                    "enabled": True
                },
                "openrouter": {
                    "enabled": True
                },
                "glama": {
                    "enabled": True
                },
                "google": {
                    "enabled": True
                },
                "github": {
                    "enabled": True
                }
            }
        }
    }


# Extension OAuth endpoints
class ClerkToTicketRequest(BaseModel):
    """Request model for converting Clerk token to extension ticket."""
    state: str
    auth_redirect: str


@router.post("/extension/clerk-to-ticket")
async def clerk_to_ticket(
    request: ClerkToTicketRequest,
    current_user: User = Depends(get_current_user_unified),
    redis = Depends(get_redis)
):
    """
    Convert Clerk authentication to extension ticket.
    Called by frontend when user is already signed in with Clerk.
    """
    try:
        import json
        # Generate a one-time ticket
        ticket = secrets.token_urlsafe(32)
        
        # Store ticket in Redis with user info (expires in 5 minutes)
        # Use the same key pattern as google_callback for consistency
        ticket_data = {
            "user_id": str(current_user.id),
            "email": current_user.email,
            "created_at": datetime.utcnow().isoformat()
        }
        
        redis.setex(
            f"extension:ticket:{ticket}",
            300,  # 5 minutes
            json.dumps(ticket_data)
        )
        
        return {
            "success": True,
            "ticket": ticket
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate ticket: {str(e)}"
        )


@router.get("/extension/sign-in")
async def extension_sign_in(
    state: str,
    auth_redirect: str,
    redis = Depends(get_redis)
):
    """
    Extension sign-in endpoint - redirects to Google OAuth with extension parameters.
    Called by frontend when user is not signed in with Clerk.
    """
    try:
        # Store extension parameters in Redis with the key pattern expected by callback
        import json
        extension_data = {
            "state": state,
            "auth_redirect": auth_redirect,
            "is_extension": True
        }
        
        # Store with key pattern that google_callback expects: extension:auth:{state}
        redis.setex(
            f"extension:auth:{state}",
            600,  # 10 minutes
            json.dumps(extension_data)
        )
        
        # Redirect to Google OAuth with extension state
        google_config = get_provider_config("google")
        # Use production URL if in production, otherwise localhost
        base_url = settings.production_backend_url if settings.environment == "production" else "http://localhost:8000"
        redirect_uri = f"{base_url}/api/auth/google/callback"
        
        oauth_url = (
            f"{google_config['auth_url']}?"
            f"response_type=code&"
            f"client_id={google_config['client_id']}&"
            f"redirect_uri={redirect_uri}&"
            f"scope=openid email profile&"
            f"state={state}&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        
        return RedirectResponse(url=oauth_url, status_code=302)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth: {str(e)}"
        )


@router.post("/extension/exchange-ticket")
async def exchange_extension_ticket(
    ticket: str,
    redis = Depends(get_redis)
):
    """
    Exchange extension ticket for access token.
    Called by VS Code extension after receiving ticket from frontend redirect.
    """
    try:
        import json
        # Get ticket data from Redis (using the key pattern from google_callback)
        ticket_key = f"extension:ticket:{ticket}"
        ticket_data_str = redis.get(ticket_key)
        
        if not ticket_data_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired ticket"
            )
        
        # Delete ticket (one-time use)
        redis.delete(ticket_key)
        
        # Parse ticket data
        ticket_data = json.loads(ticket_data_str)
        
        # Get user from database
        user = await User.find_one(User.id == PydanticObjectId(ticket_data["user_id"]))
        
        if not user or not user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update last login
        db = await get_database().__anext__()
        await update_user_last_login(db, user.id)
        
        # Generate tokens
        access_token_jwt = create_access_token(data={"sub": user.email})
        refresh_token_jwt = create_refresh_token(data={"sub": user.email})
        
        # Generate session ID
        session_id = secrets.token_urlsafe(32)
        
        # Store session in Redis (7 days)
        session_data = {
            "user_id": str(user.id),
            "email": user.email,
            "access_token": access_token_jwt,
            "refresh_token": refresh_token_jwt,
            "created_at": datetime.utcnow().isoformat()
        }
        
        redis.setex(
            f"session:{session_id}",
            604800,  # 7 days
            json.dumps(session_data)
        )
        
        return {
            "access_token": access_token_jwt,
            "refresh_token": refresh_token_jwt,
            "token_type": "bearer",
            "expires_in": 3600,
            "user_id": str(user.id),
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to exchange ticket: {str(e)}"
        )


# ============== PASSWORD RESET ENDPOINTS ==============

class ForgotPasswordRequest(BaseModel):
    """Request model for forgot password."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request model for reset password."""
    token: str
    new_password: str = Field(..., min_length=8)


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis_client = Depends(get_redis)
):
    """
    Request a password reset. Generates a reset token stored in Redis.
    In production, this should send an email with the reset link.
    """
    # Find user by email
    user = await User.find_one(User.email == request.email)
    
    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If an account with this email exists, a reset link has been sent."}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    
    # Store token in Redis with 15 minute expiry
    import json
    token_data = {
        "user_id": str(user.id),
        "email": user.email,
        "created_at": datetime.utcnow().isoformat()
    }
    redis_client.setex(
        f"password_reset:{reset_token}",
        900,  # 15 minutes
        json.dumps(token_data)
    )
    
    # In development, return the token. In production, send email instead.
    frontend_url = getattr(settings, 'frontend_url', None) or 'http://localhost:3000'
    reset_url = f"{frontend_url}/reset-password?token={reset_token}"
    
    # Log for development (remove in production)
    print(f"🔑 Password reset token for {user.email}: {reset_token}")
    print(f"🔗 Reset URL: {reset_url}")
    
    return {
        "message": "If an account with this email exists, a reset link has been sent.",
        # DEV ONLY: Remove in production
        "dev_token": reset_token,
        "dev_reset_url": reset_url
    }


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis_client = Depends(get_redis)
):
    """
    Reset password using a valid reset token.
    """
    import json
    from datetime import timezone
    
    # Get token data from Redis
    token_key = f"password_reset:{request.token}"
    token_data_str = redis_client.get(token_key)
    
    if not token_data_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    token_data = json.loads(token_data_str)
    user_id = token_data.get("user_id")
    
    # Find user
    try:
        user = await User.get(PydanticObjectId(user_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    # Update password using the existing password hash function
    user.password_hash = get_password_hash(request.new_password)
    user.updated_at = datetime.now(timezone.utc)
    await user.save()
    
    # Delete used token
    redis_client.delete(token_key)
    
    return {"message": "Password has been reset successfully. You can now sign in."}


class ProvisionOAuthUserRequest(BaseModel):
    """Request model for provisioning OAuth user."""
    email: EmailStr
    name: str
    avatar: Optional[str] = None
    provider: str  # google, github, etc.
    provider_id: Optional[str] = None


@router.post("/provision-oauth-user")
async def provision_oauth_user(
    request: ProvisionOAuthUserRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Provision or retrieve an OAuth user.
    This endpoint is called by the frontend after successful OAuth sign-in
    to ensure the user exists in the backend database.
    """
    from datetime import timezone
    
    # Check if user already exists by email
    existing_user = await User.find_one(User.email == request.email)
    
    if existing_user:
        # Update last login
        existing_user.last_login_at = datetime.now(timezone.utc)
        await existing_user.save()
        
        return {
            "id": str(existing_user.id),
            "email": existing_user.email,
            "name": existing_user.name or request.name,
            "subscription_tier": existing_user.subscription_tier or "free",
            "is_new": False
        }
    
    # Create new user
    new_user = User(
        email=request.email,
        name=request.name,
        profile_picture=request.avatar,
        oauth_provider=request.provider,
        oauth_provider_id=request.provider_id,
        is_active=True,
        subscription_tier="free",
        created_at=datetime.now(timezone.utc),
        last_login_at=datetime.now(timezone.utc),
    )
    
    await new_user.insert()
    
    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "name": new_user.name,
        "subscription_tier": new_user.subscription_tier,
        "is_new": True
    }

