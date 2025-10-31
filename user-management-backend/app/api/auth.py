"""Authentication API endpoints."""

from datetime import timedelta
from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from beanie import PydanticObjectId
from datetime import datetime

from ..database import get_database
from ..schemas.auth import TokenRefresh, OAuthCallback, UserCreate, UserLogin
from ..models.user import User
from ..auth.jwt import create_access_token, create_refresh_token, verify_token
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


@router.get("/{provider}/login")
async def oauth_login(provider: str, request: Request):
    """Initiate OAuth login with a provider."""
    if provider not in ["openrouter", "google", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth provider"
        )
    
    config = get_provider_config(provider)
    if not config or not config.get("client_id"):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"OAuth provider {provider} is not configured"
        )
    
    try:
        client = oauth.create_client(provider)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"OAuth provider {provider} is not available"
            )
        # Use frontend URL for OAuth redirect - this must match what's registered
        # in the OAuth provider's console (Google Cloud Console, GitHub OAuth App)
        # For development, we use the frontend URL that's registered with Google
        frontend_url = "http://localhost:3000"
        redirect_uri = f"{frontend_url}/auth/callback"
        
        return await client.authorize_redirect(request, redirect_uri)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth login: {str(e)}"
        )


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Handle OAuth callback and create user session."""
    if provider not in ["openrouter", "google", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth provider"
        )
    
    try:
        # Debug: Log the callback URL and parameters
        print(f"🔍 OAuth callback for {provider}")
        print(f"🔍 Callback URL: {request.url}")
        
        # Extract authorization code directly from URL for development
        from urllib.parse import parse_qs
        parsed_url = str(request.url)
        query_params = parse_qs(parsed_url.split('?')[1] if '?' in parsed_url else '')
        
        code = query_params.get('code', [None])[0]
        error = query_params.get('error', [None])[0]
        
        if error:
            print(f"🔍 OAuth error returned: {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth error: {error}"
            )
        
        if not code:
            print("🔍 No authorization code found in callback")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No authorization code received"
            )
        
        print(f"🔍 Authorization code received: {code[:20]}...")
        
        # Exchange code for token directly (bypassing authlib for development)
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': f"http://localhost:3000/auth/callback",
            'client_id': getattr(settings, f'{provider}_client_id', None),
            'client_secret': getattr(settings, f'{provider}_client_secret', None)
        }
        
        import httpx
        config = get_provider_config(provider)
        token_endpoint = config.get("token_endpoint")
        
        if not token_endpoint:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Token endpoint not configured for {provider}"
            )
        
        print(f"🔍 Exchanging code for token at: {token_endpoint}")
        
        async with httpx.AsyncClient() as http_client:
            token_response = await http_client.post(token_endpoint, data=token_data)
            
            if token_response.status_code != 200:
                print(f"🔍 Token exchange failed: {token_response.status_code} - {token_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Token exchange failed: {token_response.text}"
                )
            
            token = token_response.json()
            print("🔍 Token exchange successful!")
        
        # Get user info from provider
        userinfo_endpoint = config.get("userinfo_endpoint")
        access_token = token.get('access_token')
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No access token in response"
            )
        
        user_data = {}
        if userinfo_endpoint:
            print(f"🔍 Getting user info from: {userinfo_endpoint}")
            headers = {'Authorization': f'Bearer {access_token}'}
            
            async with httpx.AsyncClient() as http_client:
                user_response = await http_client.get(userinfo_endpoint, headers=headers)
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    print(f"🔍 User info retrieved: {user_data.get('email', 'No email')}")
                else:
                    print(f"🔍 Failed to get user info: {user_response.status_code}")
        
        # Extract user information
        if provider == "github":
            # GitHub requires a separate call to get email
            email_url = "https://api.github.com/user/emails"
            headers = {'Authorization': f'Bearer {access_token}'}
            async with httpx.AsyncClient() as http_client:
                email_response = await http_client.get(email_url, headers=headers)
                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary_email = next((email for email in emails if email.get("primary")), None)
                    email = primary_email.get("email") if primary_email else user_data.get("email")
                else:
                    email = user_data.get("email")
        else:
            email = user_data.get("email")

        provider_user_id = user_data.get("id") or user_data.get("sub")
        
        if not email or not provider_user_id:
            print(f"🔍 Missing user data - email: {email}, provider_user_id: {provider_user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract user information from OAuth provider"
            )
        
        print(f"🔍 User identified: {email} (ID: {provider_user_id})")
        
        # Get or create user
        user = await get_or_create_user_by_oauth(
            db=db,
            provider_name=provider,
            provider_user_id=str(provider_user_id),
            email=email
        )
        
        # Update last login
        if user and user.id:
            await update_user_last_login(db, user.id)
        
        # Create JWT tokens
        access_token_jwt = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        refresh_token_jwt = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        print(f"🔍 JWT tokens created for user {user.id}")
        
        # Return redirect URL for frontend to handle
        frontend_url = "http://localhost:3000/auth/callback"
        redirect_params = f"?access_token={access_token_jwt}&refresh_token={refresh_token_jwt}&user_id={user.id}"
        
        print(f"🔍 Redirecting to: {frontend_url}{redirect_params[:50]}...")
        
        # Directly redirect to frontend with tokens in URL params
        return RedirectResponse(url=f"{frontend_url}{redirect_params}")
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"🔍 OAuth callback error: {str(e)}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
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
