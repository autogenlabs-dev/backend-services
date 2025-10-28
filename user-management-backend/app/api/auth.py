"""Authentication API endpoints."""

from datetime import timedelta
from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_database # Changed from get_db to get_database
from ..schemas.auth import Token, TokenRefresh, OAuthCallback, UserCreate, UserLogin, UserResponse
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


@router.get("/providers")
async def list_oauth_providers() -> Dict[str, Any]:
    """List available OAuth providers."""
    from ..auth.oauth import OAUTH_PROVIDERS
    
    providers = []
    for name, config in OAUTH_PROVIDERS.items():
        if config["client_id"] and config["client_secret"]:
            providers.append({
                "name": name,
                "display_name": config["display_name"],
                "authorization_url": f"/auth/{name}/login"
            })
    return {"providers": providers}


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Any = Depends(get_database)): # Changed type hint from Session to Any, and get_db to get_database
    """Register a new user with email and password."""
    try:
        user = create_user_with_password(db, user_data)
        return UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
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
async def signup_user(user_data: UserCreate, db: Any = Depends(get_database)): # Changed type hint from Session to Any, and get_db to get_database
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
        print(traceback.format_exc())
        raise


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Any = Depends(get_database) # Changed type hint from Session to Any, and get_db to get_database
):
    """Login user with email and password."""
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    # Update last login
    update_user_last_login(db, user.id)
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
    db: Any = Depends(get_database) # Changed type hint from Session to Any, and get_db to get_database
):
    """Login user with email and password using JSON."""
    user = authenticate_user(db, user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
      # Update last login
    update_user_last_login(db, user.id)
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
        redirect_uri = str(request.url_for("oauth_callback", provider=provider))
        
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
    db: Any = Depends(get_database) # Changed type hint from Session to Any, and get_db to get_database
) -> Token:
    """Handle OAuth callback and create user session."""
    if provider not in ["openrouter", "google", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth provider"
        )
    
    try:
        client = oauth.create_client(provider)
        token = await client.authorize_access_token(request)
        
        # Get user info from provider
        config = get_provider_config(provider)
        userinfo_endpoint = config.get("userinfo_endpoint")
        
        if userinfo_endpoint:
            # Use the token to get user info
            user_info = await client.get(userinfo_endpoint, token=token)
            user_data = user_info.json()
        else:
            # Use the token directly if it contains user info
            user_data = token.get("userinfo", {})
        
        # Extract user information
        if provider == "github":
            # GitHub requires a separate call to get email
            email_response = await client.get("https://api.github.com/user/emails", token=token)
            emails = email_response.json()
            primary_email = next((email for email in emails if email.get("primary")), None)
            email = primary_email.get("email") if primary_email else user_data.get("email")
        else:
            email = user_data.get("email")

        provider_user_id = user_data.get("id") or user_data.get("sub")
        
        if not email or not provider_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract user information from OAuth provider"
            )
        
        # Get or create user
        user = get_or_create_user_by_oauth(
            db=db,
            provider_name=provider,
            provider_user_id=str(provider_user_id),
            email=email
        )
        
        # Update last login
        update_user_last_login(db, user.id)
        
        # Create tokens
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        )


@router.post("/refresh")
async def refresh_access_token(
    token_data: TokenRefresh,
    db: Any = Depends(get_database) # Changed type hint from Session to Any, and get_db to get_database
) -> Token:
    """Refresh an access token using a refresh token."""
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
    user = get_user_by_id(db, UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
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
    db: Any = Depends(get_database)
):
    """Logout the current user and invalidate tokens."""
    try:
        # Get the authorization header to extract the token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            # In a production system, you would blacklist the token here
            # For now, we'll update the user's last logout time
            from ..services.user_service import update_user_last_logout
            try:
                update_user_last_logout(db, current_user.id)
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
            "message": "Successfully logged out"
        }


@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user_unified)):
    """Get current user information."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "last_login_at": current_user.last_login_at
    }


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
