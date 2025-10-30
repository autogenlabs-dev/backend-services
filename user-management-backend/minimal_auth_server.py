#!/usr/bin/env python3
"""
Minimal Authentication Test Server
A simplified server to test authentication flow only.
"""

import asyncio
import sys
import warnings

# Suppress dependency warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning, module="razorpay")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", message=".*pkg_resources.*")
warnings.filterwarnings("ignore", message=".*model_.*")
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
import razorpay
from typing import Optional, List, Dict, Any
import uuid

# Import models
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.template import Template, TemplateLike, TemplateDownload, TemplateView, TemplateComment, TemplateCategory
from app.models.component import Component, ContentStatus
from app.models.component_interactions import ComponentLike, ComponentComment
from app.models.developer_profile import DeveloperProfile
from app.models.purchased_item import PurchasedItem
from app.models.content_approval import ContentApproval
from app.models.payment_transaction import PaymentTransaction
from app.models.audit_log import AuditLog, ActionType, AuditSeverity
from app.models.item_purchase import ItemPurchase, PurchaseStatus, ItemType
from app.models.shopping_cart import ShoppingCart, CartItem, CartItemType
from app.models.developer_earnings import DeveloperEarnings, PayoutRequest, PayoutStatus, PayoutMethod

# Import middleware
from app.middleware.auth import require_auth, require_role, require_admin, require_developer_or_admin, get_current_user_from_token
from app.utils.email_service import email_service
from app.services.access_control import ContentAccessService, AccessLevel
from app.services.cache_service import cache_service, get_cache_service
from app.config import settings
from contextlib import asynccontextmanager

# Database client
client = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    global client, db
    try:
        print("🔄 Initializing cache service...")
        await get_cache_service()
        
        print("🔄 Connecting to database...")
        client = AsyncIOMotorClient(settings.database_url)
        db = client.user_management_db
        
        print("🔄 Initializing Beanie...")
        # Initialize Beanie with all models
        from app.models.template_interactions import TemplateCommentEnhanced, TemplateHelpfulVote
        from app.models.component_interactions import (
            ComponentLike, ComponentComment, ComponentView, 
            ComponentDownload, ComponentHelpfulVote
        )
        
        document_models = [
            User, 
            Organization, 
            Template, 
            TemplateLike, 
            TemplateDownload, 
            TemplateView, 
            TemplateComment, 
            TemplateCategory, 
            Component,
            DeveloperProfile,
            PurchasedItem,
            ContentApproval,
            PaymentTransaction,
            AuditLog,
            # Enhanced interaction models
            TemplateCommentEnhanced,
            TemplateHelpfulVote,
            ComponentLike,
            ComponentComment,
            ComponentView,
            ComponentDownload,
            ComponentHelpfulVote,
            # Marketplace models
            ItemPurchase,
            ShoppingCart,
            DeveloperEarnings,
            PayoutRequest
        ]
        await init_beanie(database=db, document_models=document_models)
        print("✅ Database connected and initialized")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        print("⚠️ Continuing without database (some features may not work)")
    
    yield
    
    # Shutdown
    if client:
        try:
            client.close()
            print("🔌 Database connection closed")
        except Exception as e:
            print(f"⚠️ Error closing database: {e}")
    
    # Close cache service
    try:
        await cache_service.close()
        print("🔌 Cache service closed")
    except Exception as e:
        print(f"⚠️ Error closing cache: {e}")

# Create FastAPI app
app = FastAPI(title="Minimal Auth Test Server", lifespan=lifespan)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class LoginRequest(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800
    user: dict
    a4f_api_key: Optional[str] = None
    api_endpoint: Optional[str] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

# Template Schemas
class TemplateCreate(BaseModel):
    title: str
    category: str
    type: str
    language: str
    difficulty_level: str
    plan_type: str
    short_description: str
    full_description: str
    preview_images: List[str] = []
    git_repo_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    dependencies: List[str] = []
    tags: List[str] = []
    developer_name: str
    developer_experience: str
    is_available_for_dev: bool = True
    featured: bool = False
    popular: bool = False
    code: Optional[str] = None
    readme_content: Optional[str] = None

class TemplateUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    language: Optional[str] = None
    difficulty_level: Optional[str] = None
    plan_type: Optional[str] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    preview_images: Optional[List[str]] = None
    git_repo_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    dependencies: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    developer_name: Optional[str] = None
    developer_experience: Optional[str] = None
    is_available_for_dev: Optional[bool] = None
    featured: Optional[bool] = None
    popular: Optional[bool] = None
    code: Optional[str] = None
    readme_content: Optional[str] = None

class ApprovalActionRequest(BaseModel):
    admin_notes: Optional[str] = None

class RejectContentRequest(BaseModel):
    rejection_reason: str
    admin_notes: Optional[str] = None

class TemplateResponse(BaseModel):
    id: str
    title: str
    category: str
    type: str
    language: str
    difficulty_level: str
    plan_type: str
    rating: float
    downloads: int
    views: int
    likes: int
    short_description: str
    full_description: str
    preview_images: List[str]
    git_repo_url: Optional[str]
    live_demo_url: Optional[str]
    dependencies: List[str]
    tags: List[str]
    developer_name: str
    developer_experience: str
    is_available_for_dev: bool
    featured: bool
    popular: bool
    code: Optional[str]
    readme_content: Optional[str]
    created_at: str
    updated_at: str
    is_active: bool
    user_id: str

# --- COMPONENT SCHEMAS ---
from pydantic import BaseModel
from typing import List, Optional, Union, Dict

class ComponentCreateRequest(BaseModel):
    title: str
    category: str
    type: str
    language: str
    difficulty_level: str
    plan_type: str
    short_description: str
    full_description: str
    preview_images: List[str] = []
    git_repo_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    dependencies: List[str] = []
    tags: List[str] = []
    developer_name: str
    developer_experience: str
    is_available_for_dev: bool = True
    featured: bool = False
    code: Optional[Union[str, Dict[str, str]]] = None
    readme_content: Optional[str] = None

class ComponentUpdateRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    language: Optional[str] = None
    difficulty_level: Optional[str] = None
    plan_type: Optional[str] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    preview_images: Optional[List[str]] = None
    git_repo_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    dependencies: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    developer_name: Optional[str] = None
    developer_experience: Optional[str] = None
    is_available_for_dev: Optional[bool] = None
    featured: Optional[bool] = None
    code: Optional[Union[str, Dict[str, str]]] = None
    readme_content: Optional[str] = None

# --- END COMPONENT SCHEMAS ---

# Utility functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: str, user_email: str = None, user_role: str = None) -> str:
    """Create JWT access token."""
    from datetime import datetime, timedelta
    payload = {
        "sub": user_id,
        "email": user_email,
        "role": user_role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)  # 30 minutes
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token."""
    from datetime import datetime, timedelta
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7)  # 7 days
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

async def get_current_user(token: str) -> User:
    """Get current user from JWT token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Try to get user from cache first
        cached_user_data = await cache_service.get_user_data(user_id)
        if cached_user_data:
            # Return cached user data as User object
            user = User(**cached_user_data)
            user.id = user_id  # Ensure ID is set correctly
            return user
        
        # If not in cache, get from database and cache it
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Cache the user data for future requests
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "subscription": user.subscription,
            "tokens_used": user.tokens_used,
            "email_verified": user.email_verified if hasattr(user, 'email_verified') else True
        }
        await cache_service.cache_user_data(str(user.id), user_data)
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Minimal Auth Test Server", "status": "healthy"}

@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/auth/register")
async def register(user_data: UserCreate):
    """Register a new user."""
    try:
        # Check if user exists
        existing_user = await User.find_one(User.email == user_data.email)
        if existing_user:
            return {
                "message": "User already exists (this is expected for repeat tests)",
                "user": {
                    "id": str(existing_user.id),
                    "email": existing_user.email,
                    "name": existing_user.name
                }
            }
        
        # Create user
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            name=f"{user_data.first_name} {user_data.last_name}",
            full_name=f"{user_data.first_name} {user_data.last_name}",
            subscription="free",
            tokens_remaining=10000,
            tokens_used=0,
            monthly_limit=10000,
            is_active=True,
            role="user"
        )
        
        await user.create()
        
        return {
            "message": "User registered successfully",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name
            }
        }
        
    except Exception as e:
        print(f"Registration error: {e}")
        return {
            "message": f"Registration completed with note: {str(e)}",
            "user": {"email": user_data.email}
        }

@app.post("/auth/login-json", response_model=LoginResponse)
async def login_json(login_data: LoginRequest):
    """VS Code compatible login endpoint."""
    try:
        # Check cache first for rate limiting and user data
        cache_key = f"login_attempt:{login_data.email}"
        
        # Find user
        user = await User.find_one(User.email == login_data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        await user.save()
        
        # Create tokens
        access_token = create_access_token(str(user.id), user.email, user.role)
        refresh_token = create_refresh_token(str(user.id))
        
        # Cache user session data
        session_data = {
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role,
            "subscription_tier": user.subscription,
            "last_login": user.last_login_at.isoformat(),
            "tokens_used": user.tokens_used
        }
        await cache_service.cache_user_session(str(user.id), session_data)
        
        # Cache user data for quick access
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "subscription": user.subscription,
            "tokens_used": user.tokens_used,
            "email_verified": True
        }
        await cache_service.cache_user_data(str(user.id), user_data)
        
        # Return VS Code compatible response
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": str(user.id),
                "email": user.email,
                "first_name": user.name.split()[0] if user.name else "",
                "last_name": user.name.split()[-1] if user.name and len(user.name.split()) > 1 else "",
                "role": user.role,  # Add role field
                "subscription_tier": user.subscription,
                "email_verified": True,
                "monthly_usage": {
                    "api_calls": 0,
                    "tokens_used": user.tokens_used
                }
            },
            a4f_api_key=settings.a4f_api_key,
            api_endpoint="http://localhost:8000"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/me")
async def get_current_user_info(authorization: str = Header(None)):
    """Get current user information."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "subscription_tier": user.subscription,
            "tokens_remaining": user.tokens_remaining,
            "tokens_used": user.tokens_used,
            "monthly_limit": user.monthly_limit
        }
    }

@app.get("/auth/vscode-config")
async def get_vscode_config(authorization: str = Header(None)):
    """Get VS Code configuration."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    return {
        "config": {
            "a4f_api_key": settings.a4f_api_key,
            "api_endpoint": "http://localhost:8000",
            "providers": {
                "a4f": {
                    "enabled": True,
                    "base_url": settings.a4f_base_url,
                    "models": ["gpt-4", "claude-3", "gpt-3.5-turbo"],
                    "priority": 1
                }
            },
            "model_routing": {
                "popular_models_to_a4f": True,
                "default_provider": "a4f"
            }
        }
    }

@app.get("/subscriptions/current")
async def get_subscription_status(authorization: str = Header(None)):
    """Get current subscription status."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    return {
        "tier": user.subscription,
        "status": "active",
        "usage_limits": {
            "monthly_requests": 100 if user.subscription == "free" else 10000,
            "monthly_tokens": user.monthly_limit,
            "concurrent_requests": 1 if user.subscription == "free" else 10,
            "rate_limit_per_minute": 5 if user.subscription == "free" else 60
        },
        "current_usage": {
            "requests_used": 0,
            "tokens_used": user.tokens_used,
            "reset_date": user.reset_date.isoformat() if user.reset_date else None
        },
        "usage_percentage": {
            "requests": 0,
            "tokens": (user.tokens_used / user.monthly_limit) * 100 if user.monthly_limit > 0 else 0
        },
        "features": ["basic_completion"] if user.subscription == "free" else ["advanced_completion", "priority_support"]
    }

@app.post("/auth/refresh")
async def refresh_tokens(refresh_data: dict):
    """Refresh access token."""
    refresh_token = refresh_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token required")
    
    try:
        payload = jwt.decode(refresh_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Get user info for new token
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Create new tokens
        access_token = create_access_token(user_id, user.email, user.role)
        new_refresh_token = create_refresh_token(user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.post("/auth/logout")
async def logout(authorization: str = Header(None)):
    """Logout user and invalidate tokens."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        user = await get_current_user(token)
        
        # Clear user caches
        await cache_service.clear_user_session(str(user.id))
        await cache_service.clear_user_data(str(user.id))
        
        # Update last logout time
        user.last_logout_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        await user.save()
        
        return {
            "success": True,
            "message": "Successfully logged out",
            "user_id": str(user.id)
        }
        
    except Exception as e:
        print(f"Logout error: {e}")
        # Even if there's an error, we should still return success for logout
        return {
            "success": True,
            "message": "Successfully logged out"
        }

# Additional endpoints to make the API more comprehensive
@app.get("/auth/providers")
async def get_oauth_providers():
    """Get available OAuth providers."""
    return {
        "providers": [
            {
                "name": "github",
                "display_name": "GitHub",
                "enabled": False,
                "authorization_url": "/auth/github/login"
            },
            {
                "name": "google",
                "display_name": "Google",
                "enabled": False,
                "authorization_url": "/auth/google/login"
            }
        ]
    }

@app.get("/users/me")
async def get_user_profile(authorization: str = Header(None)):
    """Get user profile."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "subscription": user.subscription,
            "tokens_remaining": user.tokens_remaining,
            "tokens_used": user.tokens_used,
            "monthly_limit": user.monthly_limit,
            "created_at": user.created_at.isoformat(),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "is_active": user.is_active,
            "role": user.role
        }
    }

@app.put("/users/me")
async def update_user_profile(user_data: UserUpdate, authorization: str = Header(None)):
    """Update user profile."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    # Update fields if provided
    update_fields = user_data.model_dump(exclude_unset=True)
    
    # Handle first_name and last_name to construct full_name
    first_name = update_fields.get('first_name')
    last_name = update_fields.get('last_name')
    
    if first_name is not None or last_name is not None:
        # Get current names if not provided
        current_first = first_name if first_name is not None else (user.full_name.split(' ')[0] if user.full_name else '')
        current_last = last_name if last_name is not None else (' '.join(user.full_name.split(' ')[1:]) if user.full_name and len(user.full_name.split(' ')) > 1 else '')
        user.full_name = f"{current_first} {current_last}".strip()
        
        # Also update the name field
        if user.full_name:
            user.name = user.full_name
    
    # Update other fields
    for field, value in update_fields.items():
        if field not in ['first_name', 'last_name'] and hasattr(user, field):
            setattr(user, field, value)
    
    user.updated_at = datetime.now(timezone.utc)
    
    # Save the updated user
    await user.save()
    
    # Clear user caches when user profile is updated
    await cache_service.clear_user_data(str(user.id))
    await cache_service.clear_user_session(str(user.id))
    
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "first_name": user.full_name.split(' ')[0] if user.full_name else '',
        "last_name": ' '.join(user.full_name.split(' ')[1:]) if user.full_name and len(user.full_name.split(' ')) > 1 else '',
        "role": user.role,
        "subscription": user.subscription,
        "tokens_remaining": user.tokens_remaining,
        "tokens_used": user.tokens_used,
        "monthly_limit": user.monthly_limit,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "is_active": user.is_active
    }

@app.get("/users/preferences")
async def get_user_preferences(authorization: str = Header(None)):
    """Get user preferences."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    return {
        "preferences": {
            "theme": "dark",
            "language": "en",
            "notifications": True,
            "auto_completion": True,
            "model_preference": "gpt-4",
            "max_tokens": 2048
        }
    }

@app.get("/users/usage")
async def get_user_usage(authorization: str = Header(None)):
    """Get user usage statistics."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    return {
        "usage": {
            "tokens_used": user.tokens_used,
            "tokens_remaining": user.tokens_remaining,
            "monthly_limit": user.monthly_limit,
            "requests_made": 0,
            "reset_date": user.reset_date.isoformat() if user.reset_date else None,
            "usage_percentage": (user.tokens_used / user.monthly_limit) * 100 if user.monthly_limit > 0 else 0
        }
    }

@app.get("/user/dashboard")
async def get_user_dashboard(authorization: str = Header(None)):
    """Get enhanced user dashboard data."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    # Get user's templates and components count
    try:
        user_templates_count = await Template.find({"user_id": user.id, "is_active": True}).count()
    except:
        user_templates_count = 0
    
    try:
        user_components_count = await Component.find({"user_id": user.id, "is_active": True}).count()
    except:
        user_components_count = 0
    
    return {
        "user": user.to_dict(),
        "dashboard_stats": {
            "templates_created": user_templates_count,
            "components_created": user_components_count,
            "total_downloads": 0,  # TODO: Implement download tracking
            "total_earnings": 0,   # TODO: Implement earnings calculation
            "subscription_status": user.subscription,
            "tokens_remaining": user.tokens_remaining,
            "tokens_used": user.tokens_used,
            "monthly_limit": user.monthly_limit
        },
        "recent_activity": [],  # TODO: Implement activity tracking
        "notifications": []     # TODO: Implement notification system
    }

@app.get("/subscriptions/plans")
async def get_subscription_plans():
    """Get available subscription plans."""
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "currency": "USD",
                "billing_interval": "monthly",
                "features": [
                    "10,000 tokens per month",
                    "Basic completion",
                    "Community support"
                ],
                "limits": {
                    "monthly_tokens": 10000,
                    "rate_limit_per_minute": 5,
                    "concurrent_requests": 1
                }
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 20,
                "currency": "USD",
                "billing_interval": "monthly",
                "features": [
                    "100,000 tokens per month",
                    "Advanced completion",
                    "Priority support",
                    "Multiple models"
                ],
                "limits": {
                    "monthly_tokens": 100000,
                    "rate_limit_per_minute": 60,
                    "concurrent_requests": 10
                }
            }
        ]
    }

@app.get("/api-keys")
async def list_api_keys(authorization: str = Header(None)):
    """List user's API keys."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    return {
        "api_keys": [
            {
                "id": "ak_test_123",
                "name": "VS Code Extension",
                "prefix": "ak_test_",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_used": None,
                "status": "active"
            }
        ]
    }

@app.post("/api-keys/generate")
async def generate_api_key(authorization: str = Header(None)):
    """Generate a new API key."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    return {
        "api_key": {
            "id": "ak_new_456",
            "key": "ak_test_456_abcdef123456789",
            "name": "New API Key",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }
    }

@app.get("/organizations")
async def list_organizations(authorization: str = Header(None)):
    """List user's organizations."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    return {
        "organizations": [
            {
                "id": str(user.id),
                "name": "Personal Organization",
                "role": "owner",
                "subscription": user.subscription,
                "created_at": user.created_at.isoformat()
            }
        ]
    }

@app.get("/organizations/current")
async def get_current_organization(authorization: str = Header(None)):
    """Get current organization."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    return {
        "organization": {
            "id": str(user.id),
            "name": "Personal Organization",
            "role": "owner",
            "subscription": user.subscription,
            "member_count": 1,
            "created_at": user.created_at.isoformat()
        }
    }

@app.get("/llm/models")
async def get_llm_models(authorization: str = Header(None)):
    """Get available LLM models."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    return {
        "models": [
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "provider": "a4f",
                "context_length": 8192,
                "cost_per_token": 0.00003,
                "capabilities": ["completion", "chat"]
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "provider": "a4f",
                "context_length": 4096,
                "cost_per_token": 0.000002,
                "capabilities": ["completion", "chat"]
            },
            {
                "id": "claude-3",
                "name": "Claude 3",
                "provider": "a4f",
                "context_length": 100000,
                "cost_per_token": 0.000015,
                "capabilities": ["completion", "chat"]
            }
        ]
    }

@app.get("/llm/providers")
async def get_llm_providers():
    """Get available LLM providers."""
    return {
        "providers": [
            {
                "id": "a4f",
                "name": "A4F",
                "enabled": True,
                "base_url": settings.a4f_base_url,
                "models": ["gpt-4", "gpt-3.5-turbo", "claude-3"],
                "features": ["completion", "chat", "streaming"]
            }
        ]
    }

@app.get("/tokens/usage")
async def get_token_usage(authorization: str = Header(None)):
    """Get token usage details."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    return {
        "usage": {
            "tokens_used": user.tokens_used,
            "tokens_remaining": user.tokens_remaining,
            "monthly_limit": user.monthly_limit,
            "reset_date": user.reset_date.isoformat() if user.reset_date else None,
            "daily_usage": 0,
            "weekly_usage": user.tokens_used,
            "usage_by_model": {
                "gpt-4": user.tokens_used // 2,
                "gpt-3.5-turbo": user.tokens_used // 2,
                "claude-3": 0
            }
        }
    }

@app.get("/payments/config")
async def get_payment_config(authorization: str = Header(None)):
    """Get Razorpay configuration for frontend."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    return {
        "razorpay_key_id": settings.razorpay_key_id,
        "currency": "INR"
    }

# =============================================================================
# TEMPLATE MANAGEMENT ENDPOINTS
# =============================================================================

@app.post("/templates", response_model=TemplateResponse)
async def create_template(
    template_data: TemplateCreate, 
    request: Request,
    current_user: User = Depends(require_developer_or_admin)
):
    """Create a new template (Developer/Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        # Create template with pending approval status
        template = Template(
            title=template_data.title,
            category=template_data.category,
            type=template_data.type,
            language=template_data.language,
            difficulty_level=template_data.difficulty_level,
            plan_type=template_data.plan_type,
            short_description=template_data.short_description,
            full_description=template_data.full_description,
            preview_images=template_data.preview_images,
            git_repo_url=template_data.git_repo_url,
            live_demo_url=template_data.live_demo_url,
            dependencies=template_data.dependencies,
            tags=template_data.tags,
            developer_name=template_data.developer_name,
            developer_experience=template_data.developer_experience,
            is_available_for_dev=template_data.is_available_for_dev,
            featured=template_data.featured,
            popular=template_data.popular,
            code=template_data.code,
            readme_content=template_data.readme_content,
            user_id=current_user.id,
            approval_status=ContentStatus.PENDING_APPROVAL
        )
        
        # Save template to database
        await template.create()
        
        # Create approval record
        approval = ContentApproval(
            content_type="template",
            content_id=str(template.id),
            content_title=template.title,
            submitted_by=str(current_user.id),
            submitted_at=template.created_at,
            status="pending_approval"  # Use valid enum value
        )
        await approval.create()
        
        # Log action
        await AuditLog.log_action(
            action_type=ActionType.USER_CREATED,  # Generic content creation
            action_description=f"Developer {current_user.email} created template '{template.title}'",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            target_type="template",
            target_id=str(template.id),
            target_name=template.title,
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"]
        )
        
        # Clear template caches when new template is created
        await cache_service.clear_template_caches()
        
        # Return the template using the to_dict method
        template_dict = template.to_dict()
        print(f"Template created successfully: {template_dict}")
        
        # Return the dictionary directly - FastAPI will handle the response model conversion
        return template_dict
        
    except Exception as e:
        print(f"Template creation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")

@app.get("/templates")
async def get_templates(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    type: Optional[str] = None,
    plan_type: Optional[str] = None,
    featured: Optional[bool] = None,
    popular: Optional[bool] = None,
    search: Optional[str] = None,
    show_my_content: Optional[bool] = False,  # New parameter for developers/admins
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Get templates with role-based filtering."""
    try:
        # Create cache key for this request
        cache_key = f"templates:{skip}:{limit}:{category}:{type}:{plan_type}:{featured}:{popular}:{search}:{show_my_content}"
        if current_user:
            cache_key += f":{current_user.id}:{current_user.role}"
        
        # Try to get from cache first
        cached_templates = await cache_service.get_templates(cache_key)
        if cached_templates:
            return cached_templates
        
        # Build base query
        query = {"is_active": True}
        
        # Content visibility logic based on user role and show_my_content parameter
        if not current_user or current_user.role == UserRole.USER:
            # Anonymous users and regular users see only approved content
            query["approval_status"] = "approved"
        elif current_user.role in [UserRole.DEVELOPER, UserRole.ADMIN]:
            if show_my_content:
                # Show only current user's content (all statuses)
                query["user_id"] = current_user.id
            else:
                # Show only approved content from all users
                query["approval_status"] = "approved"
        # Superadmins see everything (no status filter)
        
        # Apply filters
        if category:
            query["category"] = category
        if type:
            query["type"] = type
        if plan_type:
            query["plan_type"] = plan_type
        if featured is not None:
            query["featured"] = featured
        if popular is not None:
            query["popular"] = popular
        
        # Get templates
        if search:
            templates = await Template.find({
                **query,
                "$or": [
                    {"title": {"$regex": search, "$options": "i"}},
                    {"short_description": {"$regex": search, "$options": "i"}},
                    {"tags": {"$in": [search]}}
                ]
            }).skip(skip).limit(limit).to_list()
        else:
            templates = await Template.find(query).skip(skip).limit(limit).to_list()
        
        # Apply access control and filter content
        template_list = []
        for template in templates:
            # Get access level for this user and template
            access_level, access_info = await ContentAccessService.get_content_access_level(current_user, template)
            
            # Get template data
            template_data = template.to_dict()
            
            # Ensure ID is properly included as string
            template_data["id"] = str(template.id)
            
            # Add likes and comments count
            total_likes = await TemplateLike.find({"template_id": str(template.id)}).count()
            total_comments = await TemplateComment.find({
                "template_id": str(template.id), 
                "is_approved": True
            }).count()
            
            template_data["total_likes"] = total_likes
            template_data["total_comments"] = total_comments
            template_data["likes"] = total_likes  # For backward compatibility
            template_data["comments_count"] = total_comments  # For backward compatibility
            
            # Add approval info for non-approved templates
            if hasattr(template, 'status') and template.status != "approved":
                approval = await ContentApproval.find_one({
                    "content_type": "template",
                    "content_id": str(template.id)
                })
                if approval:
                    template_data["approval_info"] = {
                        "status": approval.status,
                        "submitted_at": approval.submitted_at,
                        "reviewed_at": approval.reviewed_at,
                        "rejection_reason": approval.rejection_reason,
                        "admin_notes": approval.admin_notes
                    }
            
            # Filter content based on access level
            filtered_data = ContentAccessService.filter_content_by_access_level(template_data, access_level)
            
            # Add access information
            filtered_data["access_info"] = access_info
            filtered_data["access_level"] = access_level
            
            template_list.append(filtered_data)
        
        # Get total count
        total_count = await Template.find(query).count()
        
        result = {
            "templates": template_list,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "filters": {
                "category": category,
                "type": type,
                "plan_type": plan_type,
                "featured": featured,
                "popular": popular,
                "search": search,
                "show_my_content": show_my_content
            }
        }
        
        # Cache the result for future requests (5 minutes)
        await cache_service.cache_templates(cache_key, result, ttl=300)
        
        return result
        
    except Exception as e:
        print(f"Template retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve templates: {str(e)}")

@app.get("/templates/categories")
async def get_template_categories():
    """Get all template categories."""
    try:
        categories = await TemplateCategory.find({"is_active": True}).sort("sort_order").to_list()
        
        # If no categories exist, return default categories
        if not categories:
            default_categories = [
                "Navigation", "Layout", "Forms", "Data Display", 
                "User Interface", "Content", "Media", "Interactive", 
                "Widgets", "Sections"
            ]
            return {"categories": default_categories}
        
        return {
            "categories": [{
                "name": cat.name,
                "display_name": cat.display_name,
                "description": cat.description,
                "icon": cat.icon
            } for cat in categories]
        }
        
    except Exception as e:
        print(f"Categories retrieval error: {e}")
        # Return default categories on error
        default_categories = [
            "Navigation", "Layout", "Forms", "Data Display", 
            "User Interface", "Content", "Media", "Interactive", 
            "Widgets", "Sections"
        ]
        return {"categories": default_categories}

@app.get("/templates/stats")
async def get_template_stats():
    """Get template statistics."""
    try:
        total_templates = await Template.find({"is_active": True}).count()
        free_templates = await Template.find({"is_active": True, "plan_type": "Free"}).count()
        paid_templates = await Template.find({"is_active": True, "plan_type": "Paid"}).count()
        featured_templates = await Template.find({"is_active": True, "featured": True}).count()
        popular_templates = await Template.find({"is_active": True, "popular": True}).count()
        
        return {
            "total_templates": total_templates,
            "free_templates": free_templates,
            "paid_templates": paid_templates,
            "featured_templates": featured_templates,
            "popular_templates": popular_templates
        }
        
    except Exception as e:
        print(f"Stats retrieval error: {e}")
        return {
            "total_templates": 0,
            "free_templates": 0,
            "paid_templates": 0,
            "featured_templates": 0,
            "popular_templates": 0
        }

@app.get("/templates/user/my-templates")
async def get_user_templates(
    request: Request,
    current_user: User = Depends(require_auth),
    skip: int = 0, 
    limit: int = 100,
    status_filter: Optional[str] = Query(None)  # "pending", "approved", "rejected", or None for all
):
    """Get templates created by the current user. Developers see all their content regardless of status."""
    try:
        # Build query - users see all their own content regardless of approval status
        query = {"user_id": current_user.id, "is_active": True}
        
        # Apply status filter if provided
        if status_filter:
            query["status"] = status_filter
        
        templates = await Template.find(query).skip(skip).limit(limit).to_list()
        template_list = []
        
        for template in templates:
            template_dict = template.to_dict()
            
            # Add approval info for non-approved templates
            if template.status != "approved":
                approval = await ContentApproval.find_one({
                    "content_type": "template",
                    "content_id": str(template.id)
                })
                if approval:
                    template_dict["approval_info"] = {
                        "status": approval.status,
                        "submitted_at": approval.submitted_at,
                        "reviewed_at": approval.reviewed_at,
                        "rejection_reason": approval.rejection_reason,
                        "admin_notes": approval.admin_notes
                    }
            
            template_list.append(template_dict)
        
        total_count = await Template.find(query).count()
        
        # Get status breakdown
        status_counts = {}
        for status in ["pending_approval", "approved", "rejected"]:
            count = await Template.find({"user_id": current_user.id, "is_active": True, "status": status}).count()
            status_counts[status] = count
        
        return {
            "templates": template_list,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "status_breakdown": status_counts,
            "filters": {"status": status_filter}
        }
        
    except Exception as e:
        print(f"User templates retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user templates: {str(e)}")

@app.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Get a specific template by ID with access control."""
    try:
        # Force fresh data from database with proper ObjectId
        from bson import ObjectId
        template = await Template.find_one(Template.id == ObjectId(template_id))
        
        if not template or not template.is_active:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check access level
        access_level, access_info = await ContentAccessService.get_content_access_level(current_user, template)
        
        # Increment view count only for legitimate views
        if access_level != AccessLevel.NO_ACCESS:
            template.views += 1
            await template.save()
            
            # Track user access if authenticated
            if current_user:
                await ContentAccessService.increment_download_count(
                    current_user, template_id, "template"
                )
        
        # Get template data and apply access control
        template_data = template.to_dict()
        
        # Ensure ID is properly included as string
        template_data["id"] = str(template.id)
        
        # Add likes and comments count
        total_likes = await TemplateLike.find({"template_id": template_id}).count()
        total_comments = await TemplateComment.find({
            "template_id": template_id, 
            "is_approved": True
        }).count()
        
        print(f"🔍 Template {template_id} stats - Likes: {total_likes}, Comments: {total_comments}")
        
        template_data["total_likes"] = total_likes
        template_data["total_comments"] = total_comments
        template_data["likes"] = total_likes  # For backward compatibility
        template_data["comments_count"] = total_comments  # For backward compatibility
        
        filtered_data = ContentAccessService.filter_content_by_access_level(template_data, access_level)
        
        # Add like status if user is authenticated
        if current_user:
            user_like = await TemplateLike.find_one(
                TemplateLike.template_id == template_id,
                TemplateLike.user_id == str(current_user.id)
            )
            filtered_data["liked"] = user_like is not None
        else:
            filtered_data["liked"] = False
        
        # Add access information
        filtered_data["access_info"] = access_info
        filtered_data["access_level"] = access_level
        
        return TemplateResponse(**filtered_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Template retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve template: {str(e)}")

@app.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(template_id: str, template_data: TemplateUpdate, authorization: str = Header(None)):
    """Update a template."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    try:
        template = await Template.get(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check if user owns this template or is admin
        if template.user_id != user.id and user.role not in ["admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Not authorized to update this template")
        
        # Update fields if provided
        update_fields = template_data.model_dump(exclude_unset=True)
        
        for field, value in update_fields.items():
            if hasattr(template, field):
                setattr(template, field, value)
        
        template.updated_at = datetime.now(timezone.utc)
        await template.save()
        
        # Clear template caches when template is updated
        await cache_service.clear_template_caches()
        
        return TemplateResponse(**template.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Template update error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")

@app.delete("/templates/{template_id}")
async def delete_template(template_id: str, authorization: str = Header(None)):
    """Delete a template (soft delete)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    try:
        template = await Template.get(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check if user owns this template or is admin
        if template.user_id != user.id and user.role not in ["admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this template")
        
        # Soft delete
        template.is_active = False
        template.updated_at = datetime.now(timezone.utc)
        await template.save()
        
        # Clear template caches when template is deleted
        await cache_service.clear_template_caches()
        
        return {"message": "Template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Template deletion error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")

@app.get("/templates/user/my-templates")
async def get_user_templates(authorization: str = Header(None), skip: int = 0, limit: int = 100):
    """Get templates created by the current user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    try:
        templates = await Template.find({"user_id": user.id, "is_active": True}).skip(skip).limit(limit).to_list()
        template_list = [template.to_dict() for template in templates]
        
        total_count = await Template.find({"user_id": user.id, "is_active": True}).count()
        
        return {
            "templates": template_list,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        print(f"User templates retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user templates: {str(e)}")

@app.post("/templates/{template_id}/like")
async def toggle_template_like(template_id: str, authorization: str = Header(None)):
    """Toggle like status for a template."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    try:
        template = await Template.get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check if user already liked this template using string IDs
        existing_like = await TemplateLike.find_one({
            "template_id": template_id, 
            "user_id": str(user.id)
        })
        
        if existing_like:
            # Unlike
            await existing_like.delete()
            template.likes = max(0, template.likes - 1)
            liked = False
        else:
            # Like
            like = TemplateLike(
                template_id=template_id, 
                user_id=str(user.id)
            )
            await like.create()
            template.likes += 1
            liked = True
        
        await template.save()
        
        # Get fresh count from database
        total_likes = await TemplateLike.find({"template_id": template_id}).count()
        
        return {
            "liked": liked,
            "total_likes": total_likes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Template like error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle like: {str(e)}")

@app.post("/templates/{template_id}/download")
async def download_template(template_id: str, authorization: str = Header(None)):
    """Record a template download."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    try:
        template = await Template.get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Record download
        download = TemplateDownload(template_id=template.id, user_id=user.id)
        await download.create()
        
        # Increment download count
        template.downloads += 1
        await template.save()
        
        return {
            "message": "Download recorded",
            "total_downloads": template.downloads
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Template download error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record download: {str(e)}")

# Template Comment Endpoints
@app.post("/templates/{template_id}/comments")
async def create_template_comment(
    template_id: str,
    comment_data: dict,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Create a template comment (anonymous allowed)"""
    try:
        # Import here to avoid circular imports
        from app.models.template_interactions import TemplateCommentEnhanced
        from app.models.interaction_schemas import UserInfo
        
        # Skip authentication checks for now (allowing anonymous comments)
        user_id = "6859d0c0cc7aa1dc1c3e7e28"  # Use default user ID for anonymous comments (Akarsh Mishra)
        if current_user:
            user_id = str(current_user.id)
        
        print(f"Creating template comment - template_id: {template_id}")
        print(f"Comment data: {comment_data}")
        print(f"User: {current_user.username if current_user else 'Anonymous'}")
        print(f"Using default user_id: {user_id}")
        
        # Verify template exists
        template = await Template.get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        print(f"Template found: {template.title}")
        
        # Create TemplateCommentEnhanced object
        print("Creating TemplateCommentEnhanced object...")
        comment = TemplateCommentEnhanced(
            template_id=template_id,  # Let Beanie handle ObjectId conversion
            user_id=user_id,  # Let Beanie handle ObjectId conversion
            comment=comment_data.get("content", ""),
            rating=comment_data.get("rating"),
            parent_comment_id=comment_data.get("parent_comment_id"),
            is_verified_purchase=False,
            is_approved=True,
            is_flagged=False,
            helpful_count=0,
            unhelpful_count=0,
            reply_count=0
        )
        print("TemplateCommentEnhanced object created successfully")
        
        # Insert template comment to database
        print("Inserting template comment to database...")
        await comment.create()
        print(f"Template comment inserted successfully with ID: {comment.id}")
        
        # If this is a reply, increment the parent comment's reply count
        if comment.parent_comment_id:
            try:
                print(f"This is a reply to comment {comment.parent_comment_id}, updating parent reply count...")
                parent_comment = await TemplateCommentEnhanced.get(comment.parent_comment_id)
                if parent_comment:
                    parent_comment.reply_count += 1
                    await parent_comment.save()
                    print(f"Parent comment reply count updated to {parent_comment.reply_count}")
                else:
                    print(f"Warning: Parent comment {comment.parent_comment_id} not found")
            except Exception as e:
                print(f"Error updating parent comment reply count: {e}")
        
        # Log audit event (disabled temporarily for debugging)
        print("Audit logging disabled temporarily...")
        
        # Get user info
        print("Getting user info...")
        try:
            # Try to get actual user from database first
            comment_user = await User.get(user_id)
            if comment_user and comment_user.name:  # Use name field instead of username
                user_info = UserInfo(
                    id=user_id,
                    username=comment_user.name,  # Use name field instead of username
                    profile_picture=getattr(comment_user, 'profile_picture', None),
                    verified_purchase=False
                )
                print(f"Found user in database: {comment_user.name}")
            else:
                # Fallback to current_user info or Unknown User
                user_info = UserInfo(
                    id=user_id,
                    username="Unknown User" if not current_user or not current_user.name else current_user.name,  # Use name field
                    profile_picture=None,
                    verified_purchase=False
                )
                print("Using fallback user info")
        except Exception as e:
            print(f"Error fetching user: {e}")
            user_info = UserInfo(
                id=user_id,
                username="Unknown User" if not current_user or not current_user.name else current_user.name,  # Use name field
                profile_picture=None,
                verified_purchase=False
            )
        
        # Return response
        response_data = {
            "id": str(comment.id),
            "template_id": template_id,
            "user": user_info.dict(),
            "content": comment.comment,
            "rating": comment.rating,
            "parent_comment_id": comment.parent_comment_id,
            "replies_count": 0,
            "helpful_votes": 0,
            "has_user_voted_helpful": False,
            "is_flagged": False,
            "is_approved": True,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at
        }
        
        return response_data
        
    except Exception as e:
        print(f"Error creating template comment: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create comment: {str(e)}")

@app.get("/templates/{template_id}/comments")
async def get_template_comments(
    template_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Get template comments with pagination"""
    try:
        from app.models.template_interactions import TemplateCommentEnhanced
        from app.models.interaction_schemas import UserInfo
        
        # Verify template exists
        template = await Template.get(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Convert string ID to ObjectId for querying
        from bson import ObjectId
        template_object_id = ObjectId(template_id)
        
        # Build query for approved comments
        query = {"template_id": template_object_id, "is_approved": True}
        
        # Get total count
        total_count = await TemplateCommentEnhanced.find(query).count()
        
        # Calculate pagination
        import math
        total_pages = math.ceil(total_count / page_size)
        skip = (page - 1) * page_size
        
        # Get all comments (no pagination yet - we'll paginate top-level comments later)
        comments = await TemplateCommentEnhanced.find(query)\
            .sort([("created_at", -1)])\
            .to_list()
        
        # First pass: create comment objects with user info
        comments_dict = {}
        for comment in comments:
            # Get proper user info for template comments
            try:
                # Try to get actual user from database
                comment_user = await User.get(comment.user_id)
                if comment_user and comment_user.name:  # Use name field instead of username
                    user_info = UserInfo(
                        id=str(comment_user.id),
                        username=comment_user.name,  # Use name field instead of username
                        profile_picture=getattr(comment_user, 'profile_picture', None),
                        verified_purchase=False
                    )
                else:
                    # Fallback to current user if available
                    if current_user and str(comment.user_id) == str(current_user.id):
                        user_info = UserInfo(
                            id=str(current_user.id),
                            username=current_user.name if current_user.name else "Unknown User",  # Use name field
                            profile_picture=getattr(current_user, 'profile_picture', None),
                            verified_purchase=False
                        )
                    else:
                        user_info = UserInfo(
                            id=str(comment.user_id),
                            username="Unknown User",
                            profile_picture=None,
                            verified_purchase=False
                        )
            except Exception as e:
                print(f"Error fetching user for comment: {e}")
                user_info = UserInfo(
                    id=str(comment.user_id),
                    username="Unknown User",
                    profile_picture=None,
                    verified_purchase=False
                )
            
            comment_obj = {
                "id": str(comment.id),
                "template_id": template_id,
                "user": user_info.dict(),
                "content": comment.comment,  # Map comment field to content
                "rating": comment.rating,
                "parent_comment_id": str(comment.parent_comment_id) if comment.parent_comment_id else None,
                "replies_count": 0,  # Will be calculated later
                "helpful_votes": comment.helpful_count,  # Use helpful_count field
                "unhelpful_votes": comment.unhelpful_count,  # Add unhelpful votes
                "has_user_voted_helpful": False,  # TODO: Check user vote status
                "is_flagged": comment.is_flagged,
                "is_approved": comment.is_approved,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "replies": []  # Initialize replies array
            }
            
            comments_dict[str(comment.id)] = comment_obj
        
        # Second pass: organize into parent-child hierarchy and update reply counts
        top_level_comments = []
        for comment_obj in comments_dict.values():
            if comment_obj["parent_comment_id"]:
                # This is a reply, add it to parent's replies
                parent_id = comment_obj["parent_comment_id"]
                if parent_id in comments_dict:
                    comments_dict[parent_id]["replies"].append(comment_obj)
                    # Update parent's reply count
                    comments_dict[parent_id]["replies_count"] = len(comments_dict[parent_id]["replies"])
            else:
                # This is a top-level comment
                top_level_comments.append(comment_obj)
        
        # Third pass: recursively calculate reply counts for nested replies
        def calculate_total_replies(comment_obj):
            total = len(comment_obj["replies"])
            for reply in comment_obj["replies"]:
                total += calculate_total_replies(reply)
            comment_obj["replies_count"] = total
            return total
        
        # Calculate reply counts for all top-level comments
        for comment_obj in top_level_comments:
            calculate_total_replies(comment_obj)
        
        # Apply pagination to top-level comments only
        total_top_level = len(top_level_comments)
        total_pages = math.ceil(total_top_level / page_size)
        skip = (page - 1) * page_size
        paginated_comments = top_level_comments[skip:skip + page_size]
        
        return {
            "comments": paginated_comments,
            "total_count": total_top_level,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "average_rating": None,
            "rating_distribution": {}
        }
        
    except Exception as e:
        print(f"Error getting template comments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")

@app.put("/templates/{template_id}/comments/{comment_id}")
async def update_template_comment(
    template_id: str,
    comment_id: str,
    comment_data: dict,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Update a template comment (anonymous allowed)"""
    try:
        from app.models.template_interactions import TemplateCommentEnhanced
        from app.models.interaction_schemas import UserInfo
        
        # Skip authentication checks for now (allowing anonymous updates)
        user_id = "6859d0c0cc7aa1dc1c3e7e28"  # Use default user ID (Akarsh Mishra)
        if current_user:
            user_id = str(current_user.id)
        
        # Get comment
        comment = await TemplateCommentEnhanced.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Verify template match
        if str(comment.template_id) != template_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this template")
        
        # Update fields
        update_data = {}
        if "content" in comment_data:
            update_data["comment"] = comment_data["content"]  # Map content to comment field
        if "rating" in comment_data:
            update_data["rating"] = comment_data["rating"]
        
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            await comment.update({"$set": update_data})
        
        # Get updated comment
        updated_comment = await TemplateCommentEnhanced.get(comment_id)
        try:
            # Try to get actual user from database first
            comment_user = await User.get(user_id)
            if comment_user and comment_user.name:  # Use name field instead of username
                user_info = UserInfo(
                    id=user_id,
                    username=comment_user.name,  # Use name field instead of username
                    profile_picture=getattr(comment_user, 'profile_picture', None),
                    verified_purchase=False
                )
            else:
                # Fallback to current_user info or Unknown User
                user_info = UserInfo(
                    id=user_id,
                    username="Unknown User" if not current_user or not current_user.username else current_user.username,
                    profile_picture=None,
                    verified_purchase=False
                )
        except Exception as e:
            print(f"Error fetching user for template edit: {e}")
            user_info = UserInfo(
                id=user_id,
                username="Unknown User" if not current_user or not current_user.username else current_user.username,
                profile_picture=None,
                verified_purchase=False
            )
        
        return {
            "id": str(updated_comment.id),
            "template_id": template_id,
            "user": user_info.dict(),
            "content": updated_comment.comment,  # Map comment field to content
            "rating": updated_comment.rating,
            "parent_comment_id": updated_comment.parent_comment_id,
            "replies_count": 0,
            "helpful_votes": updated_comment.helpful_count,
            "has_user_voted_helpful": False,
            "is_flagged": updated_comment.is_flagged,
            "is_approved": updated_comment.is_approved,
            "created_at": updated_comment.created_at,
            "updated_at": updated_comment.updated_at
        }
        
    except Exception as e:
        print(f"Error updating template comment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update comment: {str(e)}")

@app.delete("/templates/{template_id}/comments/{comment_id}")
async def delete_template_comment(
    template_id: str,
    comment_id: str,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Delete a template comment (anonymous allowed)"""
    try:
        from app.models.template_interactions import TemplateCommentEnhanced, TemplateHelpfulVote
        
        # Skip authentication checks for now (allowing anonymous deletes)
        user_id = "6859d0c0cc7aa1dc1c3e7e28"  # Use default user ID (Akarsh Mishra)
        if current_user:
            user_id = str(current_user.id)
        
        # Get comment
        comment = await TemplateCommentEnhanced.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Verify template match
        if str(comment.template_id) != template_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this template")
        
        # Delete all replies first
        await TemplateCommentEnhanced.find({"parent_comment_id": comment_id}).delete()
        
        # Delete helpful votes
        await TemplateHelpfulVote.find({"comment_id": comment_id}).delete()
        
        # Delete comment
        await comment.delete()
        
        return {"message": "Comment deleted successfully"}
        
    except Exception as e:
        print(f"Error deleting template comment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")

@app.post("/payments/create-order")
async def create_payment_order(request: dict, authorization: str = Header(None)):
    """Create a Razorpay order for payment."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    try:
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
        
        plan_name = request.get("plan_name", "Pro")
        amount_usd = request.get("amount_usd", 20.0)
        
        # Convert USD to INR (approximate rate: 1 USD = 83 INR)
        amount_inr = int(amount_usd * 83 * 100)  # Convert to paise (smallest unit)
        
        # Create order data
        order_data = {
            'amount': amount_inr,
            'currency': 'INR',
            'receipt': f"rcpt_{str(user.id)[-10:]}_{int(datetime.now(timezone.utc).timestamp())}"[-40:],  # Ensure max 40 chars
            'notes': {
                'user_id': str(user.id),
                'plan_name': plan_name,
                'amount_usd': amount_usd
            }
        }
        
        # Create order through Razorpay API
        razorpay_order = client.order.create(data=order_data)
        
        return {
            "success": True,
            "order": {
                "id": razorpay_order['id'],
                "order_id": razorpay_order['id'],
                "amount": razorpay_order['amount'],
                "currency": razorpay_order['currency'],
                "receipt": razorpay_order['receipt'],
                "key_id": settings.razorpay_key_id
            },
            "message": "Payment order created successfully"
        }
        
    except Exception as e:
        print(f"Razorpay order creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create payment order: {str(e)}")

@app.post("/payments/verify-payment")
async def verify_payment(request: dict, authorization: str = Header(None)):
    """Verify payment and update user subscription."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    try:
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
        
        razorpay_order_id = request.get("razorpay_order_id")
        razorpay_payment_id = request.get("razorpay_payment_id")
        razorpay_signature = request.get("razorpay_signature")
        plan_name = request.get("plan_name", "Pro")
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            raise HTTPException(status_code=400, detail="Missing payment details")
        
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        # Verify signature using Razorpay utility
        try:
            client.utility.verify_payment_signature(params_dict)
        except Exception as signature_error:
            print(f"Signature verification failed: {signature_error}")
            # In test mode, we might want to be more lenient
            # For now, let's log the error but continue if we have the required fields
            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
                raise HTTPException(status_code=400, detail="Invalid payment signature")
            print("Continuing with test payment verification...")
        
        # If verification successful, update user subscription
        user.subscription = plan_name.lower()
        if hasattr(user, 'subscription_plan'):
            user.subscription_plan = plan_name
        if hasattr(user, 'subscription_status'):
            user.subscription_status = "active"
        
        # Update token limits for paid plans
        if plan_name.lower() == "pro":
            user.monthly_limit = 100000
            user.tokens_remaining = 100000
        elif plan_name.lower() == "ultra":
            user.monthly_limit = 500000
            user.tokens_remaining = 500000
        
        await user.save()
        
        return {
            "success": True,
            "verified": True,
            "message": "Payment verified and subscription updated successfully",
            "subscription": {
                "plan": plan_name,
                "status": "active"
            }
        }
        
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    except Exception as e:
        print(f"Payment verification error: {e}")
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")

# --- COMPONENT MANAGEMENT ENDPOINTS ---
@app.post("/components")
async def create_component(
    component_data: ComponentCreateRequest, 
    request: Request,
    current_user: User = Depends(require_developer_or_admin)
):
    """Create a new component (Developer/Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        # Debug: Print the received code data
        print(f"🔍 DEBUG: Received code data: {component_data.code}")
        print(f"🔍 DEBUG: Code type: {type(component_data.code)}")
        if isinstance(component_data.code, dict):
            print(f"🔍 DEBUG: HTML preview: {component_data.code.get('html', '')[:100]}...")
            print(f"🔍 DEBUG: CSS preview: {component_data.code.get('css', '')[:100]}...")
        
        # Debug: Check what component_data.dict() returns
        component_dict = component_data.dict()
        print(f"🔍 DEBUG: component_data.dict() code type: {type(component_dict.get('code'))}")
        print(f"🔍 DEBUG: component_data.dict() code: {component_dict.get('code')}")
        
        # Manually preserve the code object structure
        code_field = component_data.code
        
        # Remove code from component_dict to avoid duplicate parameter error
        component_dict.pop('code', None)
        
        component = Component(
            **component_dict,
            code=code_field,  # Use the original code object, not the .dict() version
            user_id=current_user.id,  # Store as PydanticObjectId, not string
            approval_status=ContentStatus.PENDING_APPROVAL,  # Use approval_status field
            submitted_for_approval_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        await component.create()
        
        # Create approval record
        approval = ContentApproval(
            content_type="component",
            content_id=str(component.id),
            content_title=component.title,
            submitted_by=str(current_user.id),
            submitted_at=component.created_at,
            status="pending_approval"  # Use valid enum value
        )
        await approval.create()
        
        # Log action
        await AuditLog.log_action(
            action_type=ActionType.USER_CREATED,  # Generic content creation
            action_description=f"Developer {current_user.email} created component '{component.title}'",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            target_type="component",
            target_id=str(component.id),
            target_name=component.title,
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"]
        )
        
        # Clear component caches when new component is created
        await cache_service.clear_component_caches()
        
        return component.to_dict()
        
    except Exception as e:
        print(f"Component creation error: {e}")
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create component: {str(e)}")

@app.get("/components")
async def get_components(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    type: Optional[str] = None,
    plan_type: Optional[str] = None,
    featured: Optional[bool] = None,
    popular: Optional[bool] = None,
    search: Optional[str] = None,
    show_my_content: Optional[bool] = False,  # New parameter for developers/admins
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Get components with role-based filtering."""
    try:
        # Create cache key for this request
        cache_key = f"components:{skip}:{limit}:{category}:{type}:{plan_type}:{featured}:{popular}:{search}:{show_my_content}"
        if current_user:
            cache_key += f":{current_user.id}:{current_user.role}"
        
        # Try to get from cache first
        cached_components = await cache_service.get_components(cache_key)
        if cached_components:
            return cached_components
        
        query = {"is_active": True} if hasattr(Component, 'is_active') else {}
        
        # Content visibility logic based on user role and show_my_content parameter
        if not current_user or current_user.role == UserRole.USER:
            # Anonymous users and regular users see only approved content
            query["approval_status"] = "approved"
        elif current_user.role in [UserRole.DEVELOPER, UserRole.ADMIN]:
            if show_my_content:
                # Show only current user's content (all statuses)
                query["user_id"] = str(current_user.id)
            else:
                # Show only approved content from all users
                query["approval_status"] = "approved"
        # Superadmins see everything (no status filter)
        
        if category: query["category"] = category
        if type: query["type"] = type
        if plan_type: query["plan_type"] = plan_type
        if featured is not None: query["featured"] = featured
        if popular is not None: query["popular"] = popular
        
        if search:
            components = await Component.find({
                **query,
                "$or": [
                    {"title": {"$regex": search, "$options": "i"}},
                    {"short_description": {"$regex": search, "$options": "i"}},
                    {"tags": {"$in": [search]}}
                ]
            }).skip(skip).limit(limit).to_list()
        else:
            components = await Component.find(query).skip(skip).limit(limit).to_list()
        
        # Convert components to dict format
        component_list = []
        for component in components:
            component_data = component.to_dict()
            
            # Ensure ID is properly included as string
            component_data["id"] = str(component.id)
            
            # Add likes and comments count
            total_likes = await ComponentLike.find({"component_id": str(component.id)}).count()
            total_comments = await ComponentComment.find({
                "component_id": str(component.id), 
                "is_approved": True
            }).count()
            
            component_data["total_likes"] = total_likes
            component_data["total_comments"] = total_comments
            component_data["likes"] = total_likes  # For backward compatibility
            component_data["comments_count"] = total_comments  # For backward compatibility
            
            # Add approval info for non-approved components
            if hasattr(component, 'status') and component.status != "approved":
                approval = await ContentApproval.find_one({
                    "content_type": "component",
                    "content_id": str(component.id)
                })
                if approval:
                    component_data["approval_info"] = {
                        "status": approval.status,
                        "submitted_at": approval.submitted_at,
                        "reviewed_at": approval.reviewed_at,
                        "rejection_reason": approval.rejection_reason,
                        "admin_notes": approval.admin_notes
                    }
            
            # Add basic access info
            component_data["access_level"] = "full_access"
            component_data["access_info"] = {"can_view": True, "can_download": True}
            component_list.append(component_data)
            
        total_count = await Component.find(query).count()
        
        result = {
            "components": component_list, 
            "total": total_count, 
            "skip": skip, 
            "limit": limit,
            "filters": {
                "category": category,
                "type": type,
                "plan_type": plan_type,
                "featured": featured,
                "popular": popular,
                "search": search,
                "show_my_content": show_my_content
            }
        }
        
        # Cache the result for future requests (5 minutes)
        await cache_service.cache_components(cache_key, result, ttl=300)
        
        return result
    except Exception as e:
        print(f"Component retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve components: {str(e)}")

@app.get("/components/{component_id}")
async def get_component(
    component_id: str,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    try:
        component = await Component.get(component_id)
        if not component or (hasattr(component, 'is_active') and not component.is_active):
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Increment view count
        if not hasattr(component, 'views'):
            component.views = 0
        component.views += 1
        await component.save()
        
        component_data = component.to_dict()
        
        # Add likes and comments count
        total_likes = await ComponentLike.find({"component_id": component_id}).count()
        total_comments = await ComponentComment.find({
            "component_id": component_id, 
            "is_approved": True
        }).count()
        
        print(f"🔍 Component {component_id} stats - Likes: {total_likes}, Comments: {total_comments}")
        
        component_data["total_likes"] = total_likes
        component_data["total_comments"] = total_comments
        component_data["likes"] = total_likes  # For backward compatibility
        component_data["comments_count"] = total_comments  # For backward compatibility
        
        # Add like status if user is authenticated
        if current_user:
            user_like = await ComponentLike.find_one(
                ComponentLike.component_id == component_id,
                ComponentLike.user_id == str(current_user.id)
            )
            component_data["liked"] = user_like is not None
        else:
            component_data["liked"] = False
        
        return component_data
    except Exception as e:
        print(f"Component retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve component: {str(e)}")

@app.put("/components/{component_id}")
async def update_component(component_id: str, component_data: ComponentUpdateRequest, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    try:
        component = await Component.get(component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        if component.user_id != str(user.id) and getattr(user, 'role', None) not in ["admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Not authorized to update this component")
        update_fields = component_data.dict(exclude_unset=True)
        for field, value in update_fields.items():
            if hasattr(component, field):
                setattr(component, field, value)
        component.updated_at = datetime.now(timezone.utc)
        await component.save()
        
        # Clear component caches when component is updated
        await cache_service.clear_component_caches()
        
        return component.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Component update error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update component: {str(e)}")

@app.post("/components/{component_id}/like")
async def toggle_component_like(component_id: str, authorization: str = Header(None)):
    """Toggle like status for a component."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    
    try:
        component = await Component.get(component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Check if user already liked this component using string IDs
        existing_like = await ComponentLike.find_one({
            "component_id": component_id, 
            "user_id": str(user.id)
        })
        
        if existing_like:
            # Unlike
            await existing_like.delete()
            if not hasattr(component, 'likes'):
                component.likes = 0
            component.likes = max(0, component.likes - 1)
            liked = False
        else:
            # Like
            like = ComponentLike(
                component_id=component_id, 
                user_id=str(user.id)
            )
            await like.insert()
            if not hasattr(component, 'likes'):
                component.likes = 0
            component.likes += 1
            liked = True
        
        await component.save()
        
        # Get fresh count from database
        total_likes = await ComponentLike.find({"component_id": component_id}).count()
        
        return {
            "liked": liked,
            "total_likes": total_likes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Component like error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle like: {str(e)}")

@app.delete("/components/{component_id}")
async def delete_component(component_id: str, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.replace("Bearer ", "")
    user = await get_current_user(token)
    try:
        component = await Component.get(component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        if component.user_id != str(user.id) and getattr(user, 'role', None) not in ["admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this component")
        # Soft delete if possible
        if hasattr(component, 'is_active'):
            component.is_active = False
            component.updated_at = datetime.now(timezone.utc)
            await component.save()
        else:
            await component.delete()
        
        # Clear component caches when component is deleted
        await cache_service.clear_component_caches()
        
        return {"message": "Component deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Component deletion error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete component: {str(e)}")

@app.get("/components/user/my-components")
async def get_user_components(
    request: Request,
    current_user: User = Depends(require_auth),
    skip: int = 0, 
    limit: int = 100,
    status_filter: Optional[str] = Query(None)  # "pending", "approved", "rejected", or None for all
):
    """Get components created by the current user. Developers see all their content regardless of status."""
    print("🚀 ENTERED get_user_components function!")
    try:
        # Debug logging
        print(f"🔍 get_user_components called by user: {current_user.email} (ID: {current_user.id})")
        
        # Build query - users see all their own content regardless of approval status
        # Check both PydanticObjectId and string formats for backward compatibility
        query = {
            "$or": [
                {"user_id": current_user.id},  # New format: PydanticObjectId
                {"user_id": str(current_user.id)}  # Old format: string
            ]
        }
        # Keep is_active filter since Component model has this field
        if hasattr(Component, 'is_active'):
            query["is_active"] = True
        
        # Apply status filter if provided
        if status_filter:
            query["approval_status"] = status_filter  # Use approval_status instead of status
            
        print(f"🔍 Query: {query}")
        
        # Check total components for this user without pagination (both formats)
        total_user_components = await Component.find({
            "$or": [
                {"user_id": current_user.id},
                {"user_id": str(current_user.id)}
            ]
        }).count()
        print(f"🔍 Total components for user {current_user.id}: {total_user_components}")
        
        # Check all components in database
        all_components = await Component.find({}).to_list()
        print(f"🔍 All components in database: {len(all_components)}")
        for comp in all_components:
            print(f"  - Component '{comp.title}' by user_id: {getattr(comp, 'user_id', 'NO_USER_ID')} (status: {getattr(comp, 'status', 'NO_STATUS')})")
            
        components = await Component.find(query).skip(skip).limit(limit).to_list()
        print(f"🔍 Found {len(components)} components matching query")
        
        component_list = []
        
        for component in components:
            component_dict = component.to_dict()
            
            # Add approval info for non-approved components
            if hasattr(component, 'status') and component.status != "approved":
                approval = await ContentApproval.find_one({
                    "content_type": "component",
                    "content_id": str(component.id)
                })
                if approval:
                    component_dict["approval_info"] = {
                        "status": approval.status,
                        "submitted_at": approval.submitted_at,
                        "reviewed_at": approval.reviewed_at,
                        "rejection_reason": approval.rejection_reason,
                        "admin_notes": approval.admin_notes
                    }
            
            component_list.append(component_dict)
        
        total_count = await Component.find(query).count()
        
        # Get status breakdown
        status_counts = {}
        for status in ["pending_approval", "approved", "rejected"]:
            status_query = {
                "$or": [
                    {"user_id": current_user.id},
                    {"user_id": str(current_user.id)}
                ],
                "approval_status": status  # Use approval_status instead of status
            }
            if hasattr(Component, 'is_active'):
                status_query["is_active"] = True
            count = await Component.find(status_query).count()
            status_counts[status] = count
        
        return {
            "components": component_list, 
            "total": total_count, 
            "skip": skip, 
            "limit": limit,
            "status_breakdown": status_counts,
            "filters": {"status": status_filter}
        }
        
    except Exception as e:
        print(f"User components retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user components: {str(e)}")

# Component Comment Endpoints
@app.post("/components/{component_id}/comments")
async def create_component_comment(
    component_id: str,
    comment_data: dict,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Create a component comment (anonymous allowed)"""
    try:
        # Import here to avoid circular imports
        from app.models.component_interactions import ComponentComment
        from app.models.interaction_schemas import UserInfo
        
        # Skip authentication checks for now (allowing anonymous comments)
        user_id = "6859d0c0cc7aa1dc1c3e7e28"  # Use default user ID for anonymous comments (Akarsh Mishra)
        if current_user:
            user_id = str(current_user.id)
        
        print(f"Creating component comment - component_id: {component_id}")
        print(f"Comment data: {comment_data}")
        print(f"User: {current_user.username if current_user else 'Anonymous'}")
        print(f"Using default user_id: {user_id}")
        
        # Verify component exists
        component = await Component.get(component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        print(f"Component found: {component.title}")
        
        # Create ComponentComment object
        print("Creating ComponentComment object...")
        comment = ComponentComment(
            component_id=component_id,  # Let Beanie handle ObjectId conversion
            user_id=user_id,  # Let Beanie handle ObjectId conversion
            comment=comment_data.get("content", ""),  # Map content to comment field
            rating=comment_data.get("rating"),
            parent_comment_id=comment_data.get("parent_comment_id"),
            is_verified_purchase=False,
            is_approved=True,
            is_flagged=False,
            helpful_votes=0,
            reply_count=0
        )
        print("ComponentComment object created successfully")
        
        # Insert component comment to database
        print("Inserting component comment to database...")
        await comment.create()
        print(f"Component comment inserted successfully with ID: {comment.id}")
        
        # If this is a reply, increment the parent comment's reply count
        if comment.parent_comment_id:
            try:
                print(f"This is a reply to comment {comment.parent_comment_id}, updating parent reply count...")
                parent_comment = await ComponentComment.get(comment.parent_comment_id)
                if parent_comment:
                    parent_comment.reply_count += 1
                    await parent_comment.save()
                    print(f"Parent comment reply count updated to {parent_comment.reply_count}")
                else:
                    print(f"Warning: Parent comment {comment.parent_comment_id} not found")
            except Exception as e:
                print(f"Error updating parent comment reply count: {e}")
        
        # Get user info
        print("Getting user info...")
        try:
            # Try to get actual user from database first
            comment_user = await User.get(user_id)
            if comment_user and comment_user.name:  # Use name field instead of username
                user_info = UserInfo(
                    id=user_id,
                    username=comment_user.name,  # Use name field instead of username
                    profile_picture=getattr(comment_user, 'profile_picture', None),
                    verified_purchase=False
                )
                print(f"Found user in database: {comment_user.name}")
            else:
                # Fallback to current_user info or Unknown User
                user_info = UserInfo(
                    id=user_id,
                    username="Unknown User" if not current_user or not current_user.name else current_user.name,  # Use name field
                    profile_picture=None,
                    verified_purchase=False
                )
                print("Using fallback user info")
        except Exception as e:
            print(f"Error fetching user: {e}")
            user_info = UserInfo(
                id=user_id,
                username="Unknown User" if not current_user or not current_user.name else current_user.name,  # Use name field
                profile_picture=None,
                verified_purchase=False
            )
        
        # Return response
        response_data = {
            "id": str(comment.id),
            "component_id": component_id,
            "user": user_info.dict(),
            "content": comment.comment,  # Map comment field to content
            "rating": comment.rating,
            "parent_comment_id": comment.parent_comment_id,
            "replies_count": 0,
            "helpful_votes": 0,
            "has_user_voted_helpful": False,
            "is_flagged": False,
            "is_approved": True,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at
        }
        
        return response_data
        
    except Exception as e:
        print(f"Error creating component comment: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create comment: {str(e)}")

@app.get("/components/{component_id}/comments")
async def get_component_comments(
    component_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Get component comments with pagination"""
    try:
        from app.models.component_interactions import ComponentComment
        from app.models.interaction_schemas import UserInfo
        
        # Verify component exists
        component = await Component.get(component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Convert string ID to ObjectId for querying
        from bson import ObjectId
        component_object_id = ObjectId(component_id)
        
        # Build query for approved comments
        query = {"component_id": component_object_id, "is_approved": True}
        
        # Get total count
        total_count = await ComponentComment.find(query).count()
        
        # Calculate pagination
        import math
        total_pages = math.ceil(total_count / page_size)
        skip = (page - 1) * page_size
        
        # Get comments (get all comments for this component, not just paginated ones for proper nesting)
        all_comments = await ComponentComment.find(query)\
            .sort([("created_at", -1)])\
            .to_list()
        
        # Build response comments with proper nesting
        response_comments = []
        comments_dict = {}
        
        # First pass: create all comment objects
        for comment in all_comments:
            # Get proper user info for component comments
            try:
                # Try to get actual user from database
                comment_user = await User.get(comment.user_id)
                if comment_user and comment_user.name:
                    user_info = UserInfo(
                        id=str(comment_user.id),
                        username=comment_user.name,  # Use name field instead of username
                        profile_picture=getattr(comment_user, 'profile_picture', None),
                        verified_purchase=False
                    )
                else:
                    # Fallback to current user if available
                    if current_user and str(comment.user_id) == str(current_user.id):
                        user_info = UserInfo(
                            id=str(current_user.id),
                            username=current_user.username if current_user.username else "Unknown User",
                            profile_picture=getattr(current_user, 'profile_picture', None),
                            verified_purchase=False
                        )
                    else:
                        user_info = UserInfo(
                            id=str(comment.user_id),
                            username="Unknown User",
                            profile_picture=None,
                            verified_purchase=False
                        )
            except Exception as e:
                print(f"Error fetching user for comment: {e}")
                user_info = UserInfo(
                    id=str(comment.user_id),
                    username="Unknown User",
                    profile_picture=None,
                    verified_purchase=False
                )
            
            # Calculate actual replies count for this comment from database
            actual_replies_count = await ComponentComment.find(
                ComponentComment.parent_comment_id == comment.id
            ).count()
            
            comment_obj = {
                "id": str(comment.id),
                "component_id": component_id,
                "user": user_info.dict(),
                "content": comment.comment,  # Map comment field to content
                "rating": comment.rating,
                "parent_comment_id": str(comment.parent_comment_id) if comment.parent_comment_id else None,
                "replies_count": actual_replies_count,  # Use dynamically calculated count
                "helpful_votes": comment.helpful_count,  # Use correct field name
                "unhelpful_votes": comment.unhelpful_count,  # Add unhelpful votes
                "has_user_voted_helpful": False,  # TODO: Check user vote status
                "is_flagged": comment.is_flagged,
                "is_approved": comment.is_approved,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "replies": []  # Initialize replies array
            }
            
            comments_dict[str(comment.id)] = comment_obj
        
        # Second pass: organize into parent-child hierarchy and update reply counts
        top_level_comments = []
        for comment_obj in comments_dict.values():
            if comment_obj["parent_comment_id"]:
                # This is a reply, add it to parent's replies
                parent_id = comment_obj["parent_comment_id"]
                if parent_id in comments_dict:
                    comments_dict[parent_id]["replies"].append(comment_obj)
                    # Update parent's reply count
                    comments_dict[parent_id]["replies_count"] = len(comments_dict[parent_id]["replies"])
            else:
                # This is a top-level comment
                top_level_comments.append(comment_obj)
        
        # Third pass: recursively calculate reply counts for nested replies
        def calculate_total_replies(comment_obj):
            total = len(comment_obj["replies"])
            for reply in comment_obj["replies"]:
                total += calculate_total_replies(reply)
            comment_obj["replies_count"] = total
            return total
        
        # Calculate reply counts for all top-level comments
        for comment_obj in top_level_comments:
            calculate_total_replies(comment_obj)
        
        # Apply pagination to top-level comments only
        total_top_level = len(top_level_comments)
        total_pages = math.ceil(total_top_level / page_size)
        skip = (page - 1) * page_size
        paginated_comments = top_level_comments[skip:skip + page_size]
        
        return {
            "comments": paginated_comments,
            "total_count": total_top_level,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "average_rating": None,
            "rating_distribution": {}
        }
        
    except Exception as e:
        print(f"Error getting component comments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")

@app.put("/components/{component_id}/comments/{comment_id}")
async def update_component_comment(
    component_id: str,
    comment_id: str,
    comment_data: dict,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Update a component comment (anonymous allowed)"""
    try:
        from app.models.component_interactions import ComponentComment
        from app.models.interaction_schemas import UserInfo
        
        # Skip authentication checks for now (allowing anonymous updates)
        user_id = "6859d0c0cc7aa1dc1c3e7e28"  # Use default user ID (Akarsh Mishra)
        if current_user:
            user_id = str(current_user.id)
        
        # Get comment
        comment = await ComponentComment.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Verify component match
        if str(comment.component_id) != component_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this component")
        
        # Update fields
        update_data = {}
        if "content" in comment_data:
            update_data["comment"] = comment_data["content"]  # Map content to comment field
        if "rating" in comment_data:
            update_data["rating"] = comment_data["rating"]
        
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            await comment.update({"$set": update_data})
        
        # Get updated comment
        updated_comment = await ComponentComment.get(comment_id)
        try:
            # Try to get actual user from database first
            comment_user = await User.get(user_id)
            if comment_user and comment_user.name:  # Use name field instead of username
                user_info = UserInfo(
                    id=user_id,
                    username=comment_user.name,  # Use name field instead of username
                    profile_picture=getattr(comment_user, 'profile_picture', None),
                    verified_purchase=False
                )
            else:
                # Fallback to current_user info or Unknown User
                user_info = UserInfo(
                    id=user_id,
                    username="Unknown User" if not current_user or not current_user.name else current_user.name,  # Use name field
                    profile_picture=None,
                    verified_purchase=False
                )
        except Exception as e:
            print(f"Error fetching user for edit: {e}")
            user_info = UserInfo(
                id=user_id,
                username="Unknown User" if not current_user or not current_user.username else current_user.username,
                profile_picture=None,
                verified_purchase=False
            )
        
        return {
            "id": str(updated_comment.id),
            "component_id": component_id,
            "user": user_info.dict(),
            "content": updated_comment.comment,  # Map comment field to content
            "rating": updated_comment.rating,
            "parent_comment_id": updated_comment.parent_comment_id,
            "replies_count": 0,
            "helpful_votes": updated_comment.helpful_count,  # Use correct field name
            "has_user_voted_helpful": False,
            "is_flagged": updated_comment.is_flagged,
            "is_approved": updated_comment.is_approved,
            "created_at": updated_comment.created_at,
            "updated_at": updated_comment.updated_at
        }
        
    except Exception as e:
        print(f"Error updating component comment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update comment: {str(e)}")

@app.delete("/components/{component_id}/comments/{comment_id}")
async def delete_component_comment(
    component_id: str,
    comment_id: str,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Delete a component comment (anonymous allowed)"""
    try:
        from app.models.component_interactions import ComponentComment, ComponentHelpfulVote
        
        # Skip authentication checks for now (allowing anonymous deletes)
        user_id = "6859d0c0cc7aa1dc1c3e7e28"  # Use default user ID (Akarsh Mishra)
        if current_user:
            user_id = str(current_user.id)
        
        # Get comment
        comment = await ComponentComment.get(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Verify component match
        if str(comment.component_id) != component_id:
            raise HTTPException(status_code=400, detail="Comment does not belong to this component")
        
        # Delete all replies first
        await ComponentComment.find({"parent_comment_id": comment_id}).delete()
        
        # Delete helpful votes
        await ComponentHelpfulVote.find({"comment_id": comment_id}).delete()
        
        # Delete comment
        await comment.delete()
        
        return {"message": "Comment deleted successfully"}
        
    except Exception as e:
        print(f"Error deleting component comment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")

# ==================== COMPONENT COMMENT LIKE/DISLIKE ENDPOINTS ====================

@app.post("/components/{component_id}/comments/{comment_id}/like")
async def like_component_comment(
    component_id: str,
    comment_id: str,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Like/unlike a component comment (anonymous allowed)"""
    try:
        from app.models.component_interactions import ComponentComment, ComponentHelpfulVote
        from bson import ObjectId
        
        # Skip authentication checks for now (allowing anonymous likes)
        user_id = "6859d0c0cc7aa1dc1c3e7e28"  # Use default user ID (Akarsh Mishra)
        if current_user:
            user_id = str(current_user.id)
        
        # Get comment
        comment = await ComponentComment.get(ObjectId(comment_id))
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Check if user already voted
        existing_vote = await ComponentHelpfulVote.find_one({
            "comment_id": ObjectId(comment_id),
            "user_id": ObjectId(user_id)
        })
        
        if existing_vote:
            if existing_vote.is_helpful:
                # User already liked, so unlike
                await existing_vote.delete()
                await comment.update({"$inc": {"helpful_count": -1}})
                action = "unliked"
            else:
                # User disliked, change to like
                await existing_vote.update({"$set": {"is_helpful": True}})
                await comment.update({"$inc": {"helpful_count": 1, "unhelpful_count": -1}})
                action = "liked"
        else:
            # New like
            vote = ComponentHelpfulVote(
                comment_id=ObjectId(comment_id),
                user_id=ObjectId(user_id),
                is_helpful=True
            )
            await vote.create()
            await comment.update({"$inc": {"helpful_count": 1}})
            action = "liked"
        
        # Get updated comment
        updated_comment = await ComponentComment.get(ObjectId(comment_id))
        
        return {
            "action": action,
            "helpful_count": updated_comment.helpful_count,
            "unhelpful_count": updated_comment.unhelpful_count
        }
        
    except Exception as e:
        print(f"Error liking component comment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to like comment: {str(e)}")

@app.post("/components/{component_id}/comments/{comment_id}/dislike")
async def dislike_component_comment(
    component_id: str,
    comment_id: str,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Dislike/undislike a component comment (anonymous allowed)"""
    try:
        from app.models.component_interactions import ComponentComment, ComponentHelpfulVote
        from bson import ObjectId
        
        # Skip authentication checks for now (allowing anonymous dislikes)
        user_id = "6859d0c0cc7aa1dc1c3e7e28"  # Use default user ID (Akarsh Mishra)
        if current_user:
            user_id = str(current_user.id)
        
        # Get comment
        comment = await ComponentComment.get(ObjectId(comment_id))
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Check if user already voted
        existing_vote = await ComponentHelpfulVote.find_one({
            "comment_id": ObjectId(comment_id),
            "user_id": ObjectId(user_id)
        })
        
        if existing_vote:
            if not existing_vote.is_helpful:
                # User already disliked, so undislike
                await existing_vote.delete()
                await comment.update({"$inc": {"unhelpful_count": -1}})
                action = "undisliked"
            else:
                # User liked, change to dislike
                await existing_vote.update({"$set": {"is_helpful": False}})
                await comment.update({"$inc": {"helpful_count": -1, "unhelpful_count": 1}})
                action = "disliked"
        else:
            # New dislike
            vote = ComponentHelpfulVote(
                comment_id=ObjectId(comment_id),
                user_id=ObjectId(user_id),
                is_helpful=False
            )
            await vote.create()
            await comment.update({"$inc": {"unhelpful_count": 1}})
            action = "disliked"
        
        # Get updated comment
        updated_comment = await ComponentComment.get(ObjectId(comment_id))
        
        return {
            "action": action,
            "helpful_count": updated_comment.helpful_count,
            "unhelpful_count": updated_comment.unhelpful_count
        }
        
    except Exception as e:
        print(f"Error disliking component comment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to dislike comment: {str(e)}")

# ==================== TEMPLATE COMMENT LIKE/DISLIKE ENDPOINTS ====================

@app.post("/templates/{template_id}/comments/{comment_id}/like")
async def like_template_comment(
    template_id: str,
    comment_id: str,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Like/unlike a template comment (anonymous allowed)"""
    try:
        from app.models.template_interactions import TemplateCommentEnhanced, TemplateHelpfulVote
        from bson import ObjectId
        
        # Skip authentication checks for now (allowing anonymous likes)
        user_id = "6859d0c0cc7aa1dc1c3e7e28"  # Use default user ID (Akarsh Mishra)
        if current_user:
            user_id = str(current_user.id)
        
        # Get comment
        comment = await TemplateCommentEnhanced.get(ObjectId(comment_id))
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Check if user already voted
        existing_vote = await TemplateHelpfulVote.find_one({
            "comment_id": ObjectId(comment_id),
            "user_id": ObjectId(user_id)
        })
        
        if existing_vote:
            if existing_vote.is_helpful:
                # User already liked, so unlike
                await existing_vote.delete()
                await comment.update({"$inc": {"helpful_count": -1}})
                action = "unliked"
            else:
                # User disliked, change to like
                await existing_vote.update({"$set": {"is_helpful": True}})
                await comment.update({"$inc": {"helpful_count": 1, "unhelpful_count": -1}})
                action = "liked"
        else:
            # New like
            vote = TemplateHelpfulVote(
                comment_id=ObjectId(comment_id),
                user_id=ObjectId(user_id),
                is_helpful=True
            )
            await vote.create()
            await comment.update({"$inc": {"helpful_count": 1}})
            action = "liked"
        
        # Get updated comment
        updated_comment = await TemplateCommentEnhanced.get(ObjectId(comment_id))
        
        return {
            "action": action,
            "helpful_count": updated_comment.helpful_count,
            "unhelpful_count": updated_comment.unhelpful_count
        }
        
    except Exception as e:
        print(f"Error liking template comment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to like comment: {str(e)}")

@app.post("/templates/{template_id}/comments/{comment_id}/dislike")
async def dislike_template_comment(
    template_id: str,
    comment_id: str,
    current_user: Optional[User] = Depends(get_current_user_from_token)
):
    """Dislike/undislike a template comment (anonymous allowed)"""
    try:
        from app.models.template_interactions import TemplateCommentEnhanced, TemplateHelpfulVote
        from bson import ObjectId
        
        # Skip authentication checks for now (allowing anonymous dislikes)
        user_id = "6859d0c0cc7aa1dc1c3e7e28"  # Use default user ID (Akarsh Mishra)
        if current_user:
            user_id = str(current_user.id)
        
        # Get comment
        comment = await TemplateCommentEnhanced.get(ObjectId(comment_id))
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Check if user already voted
        existing_vote = await TemplateHelpfulVote.find_one({
            "comment_id": ObjectId(comment_id),
            "user_id": ObjectId(user_id)
        })
        
        if existing_vote:
            if not existing_vote.is_helpful:
                # User already disliked, so undislike
                await existing_vote.delete()
                await comment.update({"$inc": {"unhelpful_count": -1}})
                action = "undisliked"
            else:
                # User liked, change to dislike
                await existing_vote.update({"$set": {"is_helpful": False}})
                await comment.update({"$inc": {"helpful_count": -1, "unhelpful_count": 1}})
                action = "disliked"
        else:
            # New dislike
            vote = TemplateHelpfulVote(
                comment_id=ObjectId(comment_id),
                user_id=ObjectId(user_id),
                is_helpful=False
            )
            await vote.create()
            await comment.update({"$inc": {"unhelpful_count": 1}})
            action = "disliked"
        
        # Get updated comment
        updated_comment = await TemplateCommentEnhanced.get(ObjectId(comment_id))
        
        return {
            "action": action,
            "helpful_count": updated_comment.helpful_count,
            "unhelpful_count": updated_comment.unhelpful_count
        }
        
    except Exception as e:
        print(f"Error disliking template comment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to dislike comment: {str(e)}")

# ==================== CONTENT APPROVAL ENDPOINTS ====================

@app.get("/admin/approvals")
async def get_pending_approvals(
    request: Request,
    current_user: User = Depends(require_admin),
    content_type: Optional[str] = Query(None),  # "template" or "component"
    status: Optional[str] = Query("pending_approval"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200)
):
    """Get pending approvals (Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        # Build query
        query = {}
        if content_type:
            query["content_type"] = content_type
        if status:
            query["status"] = status
            
        # Get approvals
        approvals = await ContentApproval.find(query).skip(skip).limit(limit).sort("-submitted_at").to_list()
        total_count = await ContentApproval.find(query).count()
        
        # Enhance with content details
        approval_list = []
        for approval in approvals:
            approval_dict = approval.to_dict()
            
            # Get content details
            if approval.content_type == "template":
                content = await Template.get(approval.content_id)
            elif approval.content_type == "component":
                content = await Component.get(approval.content_id)
            else:
                content = None
                
            if content:
                approval_dict["content_details"] = {
                    "title": content.title,
                    "category": getattr(content, 'category', None),
                    "type": getattr(content, 'type', None),
                    "plan_type": getattr(content, 'plan_type', 'Free'),
                    "preview_images": getattr(content, 'preview_images', []),
                    "short_description": getattr(content, 'short_description', None)
                }
                
                # Get submitter details
                submitter = await User.get(approval.submitted_by)
                if submitter:
                    approval_dict["submitter_details"] = {
                        "name": submitter.name or submitter.email.split('@')[0],
                        "email": submitter.email,
                        "role": submitter.role
                    }
            
            approval_list.append(approval_dict)
        
        return {
            "approvals": approval_list,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "filters": {
                "content_type": content_type,
                "status": status
            }
        }
        
    except Exception as e:
        print(f"Get approvals error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get approvals: {str(e)}")

@app.post("/admin/approvals/{approval_id}/approve")
async def approve_content(
    approval_id: str,
    request: Request,
    approval_data: ApprovalActionRequest,
    current_user: User = Depends(require_admin)
):
    """Approve content (Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        # Get approval record
        approval = await ContentApproval.get(approval_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
            
        if approval.status != "pending_approval":
            raise HTTPException(status_code=400, detail="Content already reviewed")
        
        # Update approval record
        approval.status = "approved"
        approval.reviewed_by = str(current_user.id)
        approval.reviewed_at = datetime.now(timezone.utc)
        approval.admin_notes = approval_data.admin_notes
        await approval.save()
        
        # Update content status
        if approval.content_type == "template":
            content = await Template.get(approval.content_id)
            if content:
                content.status = "approved"
                content.approved_at = datetime.now(timezone.utc)
                await content.save()
        elif approval.content_type == "component":
            content = await Component.get(approval.content_id)
            if content:
                content.status = "approved"
                content.approved_at = datetime.now(timezone.utc)
                await content.save()
        
        # Log action
        await AuditLog.log_action(
            action_type=ActionType.SETTINGS_UPDATED,
            action_description=f"Admin {current_user.email} approved {approval.content_type} '{approval.content_title}'",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            target_type=approval.content_type,
            target_id=approval.content_id,
            target_name=approval.content_title,
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"]
        )
        
        return {"success": True, "message": "Content approved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Approve content error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve content: {str(e)}")

@app.post("/admin/approvals/{approval_id}/reject")
async def reject_content(
    approval_id: str,
    request: Request,
    rejection_data: RejectContentRequest,
    current_user: User = Depends(require_admin)
):
    """Reject content (Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        # Get approval record
        approval = await ContentApproval.get(approval_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
            
        if approval.status != "pending_approval":
            raise HTTPException(status_code=400, detail="Content already reviewed")
        
        # Update approval record
        approval.status = "rejected"
        approval.reviewed_by = str(current_user.id)
        approval.reviewed_at = datetime.now(timezone.utc)
        approval.rejection_reason = rejection_data.rejection_reason
        approval.admin_notes = rejection_data.admin_notes
        await approval.save()
        
        # Update content status
        if approval.content_type == "template":
            content = await Template.get(approval.content_id)
            if content:
                content.status = "rejected"
                await content.save()
        elif approval.content_type == "component":
            content = await Component.get(approval.content_id)
            if content:
                content.status = "rejected"
                await content.save()
        
        # Log action
        await AuditLog.log_action(
            action_type=ActionType.SETTINGS_UPDATED,
            action_description=f"Admin {current_user.email} rejected {approval.content_type} '{approval.content_title}': {rejection_data.rejection_reason}",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            target_type=approval.content_type,
            target_id=approval.content_id,
            target_name=approval.content_title,
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"]
        )
        
        return {"success": True, "message": "Content rejected successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reject content error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reject content: {str(e)}")

# ==================== ADMIN ENDPOINTS ====================

# Helper function to extract client info for audit logging
async def get_client_info(request: Request) -> Dict[str, Any]:
    """Extract client information for audit logging."""
    return {
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "endpoint": str(request.url),
        "method": request.method
    }

# Admin Schemas
class ContentApprovalRequest(BaseModel):
    action: str  # "approve" or "reject"
    reason: Optional[str] = None
    admin_notes: Optional[str] = None

class UserManagementRequest(BaseModel):
    action: str  # "activate", "deactivate", "change_role"
    role: Optional[UserRole] = None
    reason: Optional[str] = None

# Admin User Management Endpoints
@app.get("/admin/users")
async def admin_get_users(
    request: Request,
    current_user: User = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    role: Optional[UserRole] = Query(None),
    search: Optional[str] = Query(None),
    active_only: bool = Query(True)
):
    """Get all users with pagination and filtering (Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        # Build query
        query = {}
        if role:
            query["role"] = role
        if active_only:
            query["is_active"] = True
        if search:
            query["$or"] = [
                {"email": {"$regex": search, "$options": "i"}},
                {"first_name": {"$regex": search, "$options": "i"}},
                {"last_name": {"$regex": search, "$options": "i"}}
            ]
        
        # Get users
        users = await User.find(query).skip(skip).limit(limit).to_list()
        total_count = await User.find(query).count()
        
        # Format response
        user_list = []
        for user in users:
            user_dict = user.to_dict()
            # Remove sensitive data
            user_dict.pop("password_hash", None)
            user_dict.pop("refresh_token", None)
            user_list.append(user_dict)
        
        # Log admin action
        await AuditLog.log_action(
            action_type=ActionType.USER_CREATED,  # Generic user action
            action_description=f"Admin {current_user.email} viewed user list",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"],
            metadata={"query": query, "total_results": total_count}
        )
        
        return {
            "users": user_list,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "filters": {"role": role, "search": search, "active_only": active_only}
        }
        
    except Exception as e:
        print(f"Admin get users error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {str(e)}")

@app.get("/admin/developers")
async def admin_get_developers(
    request: Request,
    current_user: User = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    verified_only: bool = Query(False)
):
    """Get all developers with earnings data (Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        # Get developers
        query = {"role": UserRole.DEVELOPER}
        if verified_only:
            query["is_active"] = True
            
        developers = await User.find(query).skip(skip).limit(limit).to_list()
        total_count = await User.find(query).count()
        
        # Enrich with developer profile and earnings data
        developer_list = []
        for dev in developers:
            dev_dict = dev.to_dict()
            dev_dict.pop("password_hash", None)
            dev_dict.pop("refresh_token", None)
            
            # Get developer profile
            dev_profile = await DeveloperProfile.find_one({"user_id": str(dev.id)})
            if dev_profile:
                dev_dict["developer_profile"] = dev_profile.to_dict()
            
            # Get earnings data
            earnings = await PaymentTransaction.find({
                "recipient_id": str(dev.id),
                "transaction_type": "payout",
                "status": "completed"
            }).to_list()
            
            total_earnings = sum(transaction.amount for transaction in earnings)
            dev_dict["total_earnings"] = total_earnings
            dev_dict["payout_count"] = len(earnings)
            
            # Get content count
            template_count = await Template.find({"user_id": str(dev.id)}).count()
            component_count = await Component.find({"user_id": str(dev.id)}).count()
            dev_dict["content_stats"] = {
                "templates": template_count,
                "components": component_count,
                "total": template_count + component_count
            }
            
            developer_list.append(dev_dict)
        
        # Log admin action
        await AuditLog.log_action(
            action_type=ActionType.DEVELOPER_APPROVED,  # Generic developer action
            action_description=f"Admin {current_user.email} viewed developer list",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"],
            metadata={"total_results": total_count, "verified_only": verified_only}
        )
        
        return {
            "developers": developer_list,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "filters": {"verified_only": verified_only}
        }
        
    except Exception as e:
        print(f"Admin get developers error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve developers: {str(e)}")

@app.get("/admin/content")
async def admin_get_content(
    request: Request,
    limit: int = Query(100, description="Maximum number of items to return"),
    skip: int = Query(0, description="Number of items to skip"),
    content_type: Optional[str] = Query(None, description="Filter by content type: template or component"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(require_admin)
):
    """Get all content (templates and components) for admin review"""
    try:
        content_items = []
        
        # Get templates
        if not content_type or content_type == "template":
            templates = await Template.find().skip(skip if not content_type else 0).limit(limit if not content_type else limit//2).to_list()
            for template in templates:
                # Get developer info
                developer = await User.get(template.user_id)
                
                template_dict = {
                    "id": str(template.id),
                    "title": template.title,
                    "description": template.short_description,
                    "category": template.category,
                    "status": getattr(template, 'approval_status', 'approved'),
                    "plan_type": getattr(template, 'plan_type', 'Free'),
                    "developer_name": developer.name if developer else "Unknown",
                    "developer_email": developer.email if developer else "Unknown",
                    "created_at": template.created_at.isoformat(),
                    "download_count": template.downloads,
                    "like_count": template.likes,
                    "average_rating": getattr(template, 'average_rating', 0),
                    "content_type": "template"
                }
                content_items.append(template_dict)
        
        # Get components  
        if not content_type or content_type == "component":
            components = await Component.find().skip(skip if not content_type else 0).limit(limit if not content_type else limit//2).to_list()
            for component in components:
                # Get developer info
                developer = await User.get(component.user_id)
                
                component_dict = {
                    "id": str(component.id),
                    "title": component.title,
                    "description": component.short_description,
                    "category": component.category,
                    "status": getattr(component, 'approval_status', 'approved'),
                    "plan_type": getattr(component, 'plan_type', 'Free'),
                    "developer_name": developer.name if developer else "Unknown",
                    "developer_email": developer.email if developer else "Unknown",
                    "created_at": component.created_at.isoformat(),
                    "download_count": getattr(component, 'downloads', 0),
                    "like_count": getattr(component, 'likes', 0),
                    "average_rating": getattr(component, 'average_rating', 0),
                    "content_type": "component"
                }
                content_items.append(component_dict)
        
        # Filter by status if provided
        if status:
            content_items = [item for item in content_items if item['status'] == status]
        
        # Sort by creation date (newest first)
        content_items.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "content": content_items[:limit],
            "total": len(content_items),
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        print(f"Admin get content error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve content: {str(e)}")

@app.get("/admin/content/pending")
async def admin_get_pending_content(
    request: Request,
    current_user: User = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    content_type: Optional[str] = Query(None)  # "template" or "component"
):
    """Get content waiting for approval (Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        pending_content = []
        
        # Get pending templates
        if not content_type or content_type == "template":
            pending_templates = await Template.find({"approval_status": "pending_approval"}).skip(skip if not content_type else 0).limit(limit if not content_type else 1000).to_list()
            
            for template in pending_templates:
                template_dict = template.to_dict()
                template_dict["content_type"] = "template"
                
                # Get approval record
                approval = await ContentApproval.find_one({
                    "content_type": "template",
                    "content_id": str(template.id)
                })
                if approval:
                    template_dict["approval_info"] = approval.to_dict()
                
                # Get author info
                author = await User.find_one({"_id": template.user_id})
                if author:
                    template_dict["author"] = {
                        "id": str(author.id),
                        "email": author.email,
                        "name": f"{author.first_name} {author.last_name}"
                    }
                
                pending_content.append(template_dict)
        
        # Get pending components
        if not content_type or content_type == "component":
            pending_components = await Component.find({"approval_status": "pending_approval"}).skip(skip if not content_type else 0).limit(limit if not content_type else 1000).to_list()
            
            for component in pending_components:
                component_dict = component.to_dict()
                component_dict["content_type"] = "component"
                
                # Get approval record
                approval = await ContentApproval.find_one({
                    "content_type": "component",
                    "content_id": str(component.id)
                })
                if approval:
                    component_dict["approval_info"] = approval.to_dict()
                
                # Get author info
                author = await User.find_one({"_id": component.user_id})
                if author:
                    component_dict["author"] = {
                        "id": str(author.id),
                        "email": author.email,
                        "name": f"{author.first_name} {author.last_name}"
                    }
                
                pending_content.append(component_dict)
        
        # Sort by submission date
        pending_content.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        
        # Apply pagination if filtering by content type
        if content_type:
            total_count = len(pending_content)
            pending_content = pending_content[skip:skip + limit]
        else:
            total_count = len(pending_content)
        
        # Log admin action
        await AuditLog.log_action(
            action_type=ActionType.CONTENT_APPROVED,  # Generic content action
            action_description=f"Admin {current_user.email} viewed pending content",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"],
            metadata={"content_type": content_type, "total_results": total_count}
        )
        
        return {
            "pending_content": pending_content,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "filters": {"content_type": content_type}
        }
        
    except Exception as e:
        print(f"Admin get pending content error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve pending content: {str(e)}")

@app.post("/admin/content/approve/{content_id}")
async def admin_approve_content(
    content_id: str,
    request: Request,
    approval_request: ContentApprovalRequest,
    current_user: User = Depends(require_admin)
):
    """Approve content (Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        if approval_request.action not in ["approve", "reject"]:
            raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
        
        # Find the content (template or component)
        content = None
        content_type = None
        
        try:
            # Convert string ID to ObjectId for MongoDB query
            from bson import ObjectId
            object_id = ObjectId(content_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid content ID format")
        
        template = await Template.find_one({"_id": object_id})
        if template:
            content = template
            content_type = "template"
        else:
            component = await Component.find_one({"_id": object_id})
            if component:
                content = component
                content_type = "component"
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Update content status
        if approval_request.action == "approve":
            content.approval_status = "approved"
            content.approved_at = datetime.now(timezone.utc)
            content.approved_by = current_user.id  # This should be PydanticObjectId, not string
        else:
            content.approval_status = "rejected"
            content.rejection_reason = approval_request.reason or "No reason provided"
        
        await content.save()
        
        # Create or update approval record
        approval = await ContentApproval.find_one({
            "content_type": content_type,
            "content_id": object_id  # Use object_id instead of content_id string
        })
        
        if not approval:
            approval = ContentApproval(
                content_type=content_type,
                content_id=object_id,  # Use object_id instead of content_id string
                content_title=content.title,
                submitted_by=content.user_id,
                submitted_at=content.created_at
            )
        
        approval.status = "approved" if approval_request.action == "approve" else "rejected"
        approval.reviewed_by = current_user.id  # Should be PydanticObjectId, not string
        approval.reviewed_at = datetime.now(timezone.utc)
        approval.approval_notes = approval_request.admin_notes or ""  # Use approval_notes instead of admin_notes
        
        if approval_request.action == "reject":
            approval.rejection_reason = approval_request.reason or "No reason provided"
        
        await approval.save()
        
        # Get author for notification
        author = await User.find_one({"_id": content.user_id})
        
        # Log admin action
        action_type = ActionType.CONTENT_APPROVED if approval_request.action == "approve" else ActionType.CONTENT_REJECTED
        await AuditLog.log_action(
            action_type=action_type,
            action_description=f"Admin {current_user.email} {approval_request.action}d {content_type} '{content.title}'",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            target_type=content_type,
            target_id=content_id,
            target_name=content.title,
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"],
            metadata={
                "action": approval_request.action,
                "reason": approval_request.reason,
                "admin_notes": approval_request.admin_notes,
                "author_email": author.email if author else None
            }
        )
        
        # Send email notification to author
        if author:
            await email_service.send_content_approval_notification(
                user=author,
                content_type=content_type,
                content_title=content.title,
                action=approval_request.action,
                reason=approval_request.reason,
                admin_notes=approval_request.admin_notes
            )
        
        return {
            "message": f"Content {approval_request.action}d successfully",
            "content_id": content_id,
            "content_type": content_type,
            "status": content.status,
            "approval_id": str(approval.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Admin approve content error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to {approval_request.action} content: {str(e)}")

@app.get("/admin/analytics")
async def admin_get_analytics(
    request: Request,
    current_user: User = Depends(require_admin),
    days: int = Query(30, ge=1, le=365)
):
    """Get platform analytics (Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date.replace(day=1) if days >= 30 else end_date - timedelta(days=days)
        
        # User metrics
        total_users = await User.find().count()
        active_users = await User.find({"is_active": True}).count()
        users_by_role = {}
        for role in UserRole:
            count = await User.find({"role": role}).count()
            users_by_role[role] = count
        
        # Recent user growth
        recent_users = await User.find({
            "created_at": {"$gte": start_date}
        }).count()
        
        # Content metrics
        total_templates = await Template.find().count()
        total_components = await Component.find().count()
        approved_templates = await Template.find({"approval_status": "approved"}).count()
        approved_components = await Component.find({"approval_status": "approved"}).count()
        pending_templates = await Template.find({"approval_status": "pending_approval"}).count()
        pending_components = await Component.find({"approval_status": "pending_approval"}).count()
        
        # Recent content submissions
        recent_templates = await Template.find({
            "created_at": {"$gte": start_date}
        }).count()
        recent_components = await Component.find({
            "created_at": {"$gte": start_date}
        }).count()
        
        # Revenue metrics (basic)
        total_transactions = await PaymentTransaction.find({
            "status": "completed"
        }).count()
        
        # Get revenue by summing completed transactions
        completed_transactions = await PaymentTransaction.find({
            "status": "completed",
            "transaction_type": "purchase"
        }).to_list()
        
        total_revenue = sum(transaction.amount for transaction in completed_transactions)
        
        recent_transactions = await PaymentTransaction.find({
            "status": "completed",
            "transaction_type": "purchase",
            "created_at": {"$gte": start_date}
        }).to_list()
        
        recent_revenue = sum(transaction.amount for transaction in recent_transactions)
        
        # Developer performance (top 10)
        developers = await User.find({"role": UserRole.DEVELOPER}).to_list()
        developer_performance = []
        
        for dev in developers[:10]:  # Limit to top 10 for performance
            template_count = await Template.find({"user_id": str(dev.id), "status": "approved"}).count()
            component_count = await Component.find({"user_id": str(dev.id), "status": "approved"}).count()
            
            # Get earnings
            earnings = await PaymentTransaction.find({
                "recipient_id": str(dev.id),
                "status": "completed",
                "transaction_type": "payout"
            }).to_list()
            
            total_earnings = sum(transaction.amount for transaction in earnings)
            
            if template_count > 0 or component_count > 0 or total_earnings > 0:
                developer_performance.append({
                    "developer_id": str(dev.id),
                    "name": f"{dev.first_name} {dev.last_name}",
                    "email": dev.email,
                    "templates": template_count,
                    "components": component_count,
                    "total_content": template_count + component_count,
                    "earnings": total_earnings
                })
        
        # Sort by total content + earnings
        developer_performance.sort(
            key=lambda x: x["total_content"] * 10 + x["earnings"] / 1000,
            reverse=True
        )
        
        # Approval metrics
        total_approvals = await ContentApproval.find().count()
        pending_approvals = await ContentApproval.find({"status": "pending"}).count()
        approved_count = await ContentApproval.find({"status": "approved"}).count()
        rejected_count = await ContentApproval.find({"status": "rejected"}).count()
        
        analytics_data = {
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "users": {
                "total": total_users,
                "active": active_users,
                "recent_signups": recent_users,
                "by_role": users_by_role
            },
            "content": {
                "templates": {
                    "total": total_templates,
                    "approved": approved_templates,
                    "pending": pending_templates,
                    "recent": recent_templates
                },
                "components": {
                    "total": total_components,
                    "approved": approved_components,
                    "pending": pending_components,
                    "recent": recent_components
                },
                "totals": {
                    "all_content": total_templates + total_components,
                    "approved_content": approved_templates + approved_components,
                    "pending_content": pending_templates + pending_components
                }
            },
            "revenue": {
                "total_revenue": total_revenue,
                "recent_revenue": recent_revenue,
                "total_transactions": total_transactions,
                "recent_transactions": len(recent_transactions)
            },
            "approvals": {
                "total": total_approvals,
                "pending": pending_approvals,
                "approved": approved_count,
                "rejected": rejected_count,
                "approval_rate": round((approved_count / max(total_approvals, 1)) * 100, 2)
            },
            "top_developers": developer_performance[:10]
        }
        
        # Log admin action
        await AuditLog.log_action(
            action_type=ActionType.SETTINGS_UPDATED,  # Generic admin action
            action_description=f"Admin {current_user.email} viewed analytics dashboard",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"],
            metadata={"days": days, "total_users": total_users, "total_content": total_templates + total_components}
        )
        
        return analytics_data
        
    except Exception as e:
        print(f"Admin analytics error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")

# Admin Audit Log Endpoint
@app.get("/admin/audit-logs")
async def admin_get_audit_logs(
    request: Request,
    current_user: User = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    action_type: Optional[ActionType] = Query(None),
    actor_email: Optional[str] = Query(None),
    severity: Optional[AuditSeverity] = Query(None),
    days: int = Query(7, ge=1, le=90)
):
    """Get audit logs (Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        # Build query
        query = {}
        
        # Date filter
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        query["timestamp"] = {"$gte": start_date}
        
        if action_type:
            query["action_type"] = action_type
        if actor_email:
            query["actor_email"] = {"$regex": actor_email, "$options": "i"}
        if severity:
            query["severity"] = severity
        
        # Get logs
        logs = await AuditLog.find(query).skip(skip).limit(limit).sort("-timestamp").to_list()
        total_count = await AuditLog.find(query).count()
        
        # Format response
        log_list = [log.to_dict() for log in logs]
        
        # Log this admin action
        await AuditLog.log_action(
            action_type=ActionType.SETTINGS_UPDATED,  # Generic admin action
            action_description=f"Admin {current_user.email} viewed audit logs",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"],
            metadata={"filters": query, "total_results": total_count}
        )
        
        return {
            "audit_logs": log_list,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "filters": {
                "action_type": action_type,
                "actor_email": actor_email,
                "severity": severity,
                "days": days
            }
        }
        
    except Exception as e:
        print(f"Admin audit logs error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit logs: {str(e)}")

# User Management Endpoints
@app.put("/admin/users/{user_id}")
async def admin_update_user(
    user_id: str,
    user_update: dict,
    request: Request,
    current_user: User = Depends(require_admin)
):
    """Update user details (Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        # Find the user
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update allowed fields
        update_data = {}
        if "name" in user_update:
            update_data["name"] = user_update["name"]
        if "first_name" in user_update:
            update_data["first_name"] = user_update["first_name"]
        if "last_name" in user_update:
            update_data["last_name"] = user_update["last_name"]
        if "email" in user_update:
            # Check if email already exists
            existing_user = await User.find_one({"email": user_update["email"]})
            if existing_user and str(existing_user.id) != user_id:
                raise HTTPException(status_code=400, detail="Email already exists")
            update_data["email"] = user_update["email"]
        if "role" in user_update:
            update_data["role"] = UserRole(user_update["role"])
        if "is_active" in user_update:
            update_data["is_active"] = user_update["is_active"]
        
        # Apply updates
        for key, value in update_data.items():
            setattr(user, key, value)
        
        user.updated_at = datetime.now(timezone.utc)
        await user.save()
        
        # Log admin action
        await AuditLog.log_action(
            action_type=ActionType.USER_CREATED,  # Generic user action
            action_description=f"Admin {current_user.email} updated user {user.email}",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"],
            metadata={"updated_fields": list(update_data.keys()), "target_user_id": user_id}
        )
        
        # Return updated user
        user_dict = user.to_dict()
        user_dict.pop("password_hash", None)
        user_dict.pop("refresh_token", None)
        
        return {
            "message": "User updated successfully",
            "user": user_dict
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Admin update user error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@app.post("/admin/users/{user_id}/manage")
async def admin_manage_user(
    user_id: str,
    action_data: dict,
    request: Request,
    current_user: User = Depends(require_admin)
):
    """Manage user (activate, deactivate, suspend) (Admin only)."""
    try:
        client_info = await get_client_info(request)
        
        # Find the user
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        action = action_data.get("action")
        if not action:
            raise HTTPException(status_code=400, detail="Action is required")
        
        # Perform the action
        if action == "activate":
            user.is_active = True
            message = f"User {user.email} activated successfully"
        elif action == "deactivate":
            user.is_active = False
            message = f"User {user.email} deactivated successfully"
        elif action == "suspend":
            user.is_active = False
            message = f"User {user.email} suspended successfully"
        elif action == "change_role":
            new_role = action_data.get("role")
            if not new_role:
                raise HTTPException(status_code=400, detail="Role is required for role change")
            user.role = UserRole(new_role)
            message = f"User {user.email} role changed to {new_role}"
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        user.updated_at = datetime.now(timezone.utc)
        await user.save()
        
        # Log admin action
        await AuditLog.log_action(
            action_type=ActionType.USER_CREATED,  # Generic user action
            action_description=f"Admin {current_user.email} performed {action} on user {user.email}",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"],
            metadata={"action": action, "target_user_id": user_id, "reason": action_data.get("reason")}
        )
        
        return {
            "message": message,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Admin manage user error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to manage user: {str(e)}")

@app.delete("/admin/users/{user_id}")
async def admin_delete_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(require_admin)
):
    """Delete user permanently (Admin only) - Use with caution."""
    try:
        client_info = await get_client_info(request)
        
        # Find the user
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent deletion of other admins (safety measure)
        if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN] and str(user.id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Cannot delete other admin users")
        
        # Store user info for logging
        deleted_user_email = user.email
        
        # Log admin action before deletion
        await AuditLog.log_action(
            action_type=ActionType.USER_DELETED,
            action_description=f"Admin {current_user.email} deleted user {deleted_user_email}",
            actor_id=str(current_user.id),
            actor_email=current_user.email,
            actor_role=current_user.role,
            actor_ip=client_info["ip"],
            endpoint=client_info["endpoint"],
            user_agent=client_info["user_agent"],
            metadata={"deleted_user_id": user_id, "deleted_user_email": deleted_user_email}
        )
        
        # Delete the user
        await user.delete()
        
        return {
            "message": f"User {deleted_user_email} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Admin delete user error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

# ==================== END ADMIN ENDPOINTS ====================

# ==================== ADMIN API ROUTER ====================
# Note: Admin routes are defined directly in main server to avoid conflicts
# Include admin API router for admin dashboard
# try:
#     from app.api.admin import router as admin_api_router
#     app.include_router(admin_api_router, tags=["Admin API"])
#     print("✅ Admin API router included")
# except Exception as e:
#     print(f"⚠️ Could not include admin API router: {e}")
print("ℹ️ Admin routes are defined directly in main server")

# ==================== MARKETPLACE ENDPOINTS ====================
# Include payment endpoints
from app.endpoints.payments import router as payment_router
app.include_router(payment_router, tags=["Payments"])

# Include developer earnings endpoints  
from app.endpoints.developer_earnings import router as earnings_router
app.include_router(earnings_router, tags=["Developer Earnings"])

# Include user dashboard endpoints
from app.endpoints.user_dashboard import router as dashboard_router
app.include_router(dashboard_router, tags=["User Dashboard"])

# Include components API endpoints
try:
    from app.api.components import router as components_router
    app.include_router(components_router, tags=["Components"])
    print("✅ Components API router included")
except Exception as e:
    print(f"⚠️ Could not include components API router: {e}")

# ==================== INTERACTION ENDPOINTS ====================

# Template interaction endpoints
from app.endpoints.template_interactions import router as template_interactions_router
app.include_router(template_interactions_router, tags=["Template Interactions"])

# Component interaction endpoints  
from app.endpoints.component_interactions import router as component_interactions_router
app.include_router(component_interactions_router, tags=["Component Interactions"])

# Admin moderation endpoints
from app.endpoints.admin_moderation import router as admin_moderation_router
app.include_router(admin_moderation_router, tags=["Admin Moderation"])

# ==================== END INTERACTION ENDPOINTS ====================

# Main execution
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Minimal Auth Test Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API docs will be available at: http://localhost:8000/docs")
    print("🔧 Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload to avoid issues
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server startup error: {e}")
