#!/usr/bin/env python3
"""
Minimal Authentication Test Server
A simplified server to test authentication flow only.
"""

import asyncio
import sys
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pydantic import BaseModel
from datetime import datetime
import bcrypt
import jwt
from typing import Optional

# Import models
from app.models.user import User
from app.models.organization import Organization
from app.config import settings

# Create FastAPI app
app = FastAPI(title="Minimal Auth Test Server")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database client
client = None
db = None

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    global client, db
    client = AsyncIOMotorClient(settings.database_url)
    db = client.user_management_db
    
    # Initialize Beanie
    await init_beanie(database=db, document_models=[User, Organization])
    print("✅ Database connected and initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    if client:
        client.close()
        print("🔌 Database connection closed")

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

# Utility functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: str) -> str:
    """Create JWT access token."""
    from datetime import datetime, timedelta
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=30)  # 30 minutes
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token."""
    from datetime import datetime, timedelta
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=7)  # 7 days
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

async def get_current_user(token: str) -> User:
    """Get current user from JWT token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
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
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

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
        # Find user
        user = await User.find_one(User.email == login_data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        await user.save()
        
        # Create tokens
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        
        # Return VS Code compatible response
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": str(user.id),
                "email": user.email,
                "first_name": user.name.split()[0] if user.name else "",
                "last_name": user.name.split()[-1] if user.name and len(user.name.split()) > 1 else "",
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
            "api_endpoint": "http://localhost:8001",
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
        
        # Create new tokens
        access_token = create_access_token(user_id)
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
                "created_at": datetime.utcnow().isoformat(),
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
            "created_at": datetime.utcnow().isoformat(),
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
