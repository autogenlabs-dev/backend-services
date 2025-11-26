from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import settings
from .auth.oauth import register_oauth_clients
from .middleware.rate_limiting import rate_limit_middleware, add_rate_limit_headers
from .api import auth, users, subscriptions, tokens, llm, admin, api_keys, payments, templates, extension_auth
from .api import (
    auth,
    users,
    subscriptions,
    tokens,
    llm,
    admin,
    api_keys,
    payments,
    templates,
    components,
    extension_auth,
)
from .api import debug
from .api import verify
from typing import Callable, Dict, Any
import time
import uvicorn

# Import all models that need to be registered with Beanie
from app.models.user import (
    User,
    UserOAuthAccount,
    UserSubscription,
    SubscriptionPlanModel,
    OAuthProvider,
    TokenUsageLog,
    ApiKey
)
from app.models.template import (
    Template,
    TemplateCategory,
    TemplateLike,
    TemplateDownload,
    TemplateView,
    TemplateComment
)
from app.models.component import (
    Component,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Initialize database and Beanie
    print("🔄 Connecting to database...")
    client = AsyncIOMotorClient(settings.database_url)
    database = client["user_management_db"]  # Extract database name from URL
    
    print("🔄 Initializing Beanie...")
    # Only import models that exist
    try:
        await init_beanie(
            database=database,
            document_models=[
                User,
                UserOAuthAccount,
                UserSubscription,
                SubscriptionPlanModel,
                OAuthProvider,
                TokenUsageLog,
                ApiKey,
                Template,
                TemplateCategory,
                TemplateLike,
                TemplateDownload,
                TemplateView,
                TemplateComment
                    ,
                    Component
            ]
        )
        print("✅ Database connected and initialized")
    except Exception as e:
        print(f"❌ Error initializing Beanie: {e}")
        raise
    
    yield
    
    # Shutdown: Close database connection
    print("🔄 Closing database connection...")
    client.close()
    print("✅ Database connection closed")


# Create FastAPI instance with lifespan
# Updated: Sept 2, 2025 - Corrected port configuration to 8000 for production deployment
# Updated: Oct 9, 2025 - Added lifespan context manager for Beanie initialization
app = FastAPI(
    title=settings.app_name,
    description="User Management System with Paid Plans for VS Code Extension",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add session middleware for OAuth
app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.jwt_secret_key
)

# Add CORS middleware with explicit origins and regex
# Explicit origins for production domains
allowed_origins = [
    "https://codemurf.com",
    "https://www.codemurf.com",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Explicit origins
    allow_origin_regex=r"vscode-webview://.*",  # Allow vscode-webview
    allow_credentials=True,  # Allow credentials for authenticated requests  
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Custom middleware for performance monitoring and rate limit headers
class PerformanceAndRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> JSONResponse:
        # Debug logging for /api/users/me
        if request.url.path == "/api/users/me":
            print(f"DEBUG [middleware]: Request to /api/users/me")
            print(f"DEBUG [middleware]: Authorization header: {request.headers.get('authorization', 'NOT PRESENT')}")
            print(f"DEBUG [middleware]: All headers: {dict(request.headers)}")
        
        # Track request timing
        start_time = time.time()
        
        # Apply rate limiting for non-health endpoints
        if not request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            try:
                from .database import get_database
                from .middleware.rate_limiting import rate_limit_middleware
                
                # Get database instance
                db = get_database()
                
                try:
                    # Check rate limits
                    rate_info = await rate_limit_middleware.check_rate_limit(request, db)
                    request.state.rate_limit_info = rate_info
                except Exception as e:
                    # If rate limiting fails, allow request but log error
                    print(f"Rate limiting error: {e}")
                    request.state.rate_limit_info = {
                        "limit": 100,
                        "remaining": 99,
                        "reset": int(time.time()) + 3600,
                        "tier": "fallback"
                    }
            except Exception as e:
                print(f"Rate limiting initialization error: {e}")
        
        # Process the request
        response = await call_next(request)
        
        # Add request processing time header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Add rate limit headers if present in request state
        if hasattr(request.state, "rate_limit_info"):
            add_rate_limit_headers(response, request.state.rate_limit_info)
        
        # Return the response
        return response

# Add custom middleware
app.add_middleware(PerformanceAndRateLimitMiddleware)

# Register OAuth clients
register_oauth_clients()

# Mount static files BEFORE including routers
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
try:
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        print(f"✅ Static files mounted from {static_dir}")
    else:
        print(f"⚠️ Static directory not found: {static_dir}")
except Exception as e:
    print(f"❌ Error mounting static files: {e}")

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(tokens.router, prefix="/api")
app.include_router(llm.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(api_keys.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(components.router, prefix="/api")
# Extension authentication endpoints (Clerk-compatible API)
app.include_router(extension_auth.router, prefix="/api")
app.include_router(debug.router, prefix="/api")
app.include_router(verify.router, prefix="/api")

# Backward compatibility: Mount components router without /api prefix for frontend
# This allows frontend to call /components directly
app.include_router(components.router, tags=["Components (Legacy)"])

# Import interaction routers
try:
    from .endpoints import template_interactions, component_interactions, admin_moderation
    app.include_router(template_interactions.router, prefix="/api", tags=["Template Interactions"])
    app.include_router(component_interactions.router, prefix="/api", tags=["Component Interactions"])
    app.include_router(admin_moderation.router, prefix="/api", tags=["Admin Moderation"])
except ImportError as e:
    print(f"Warning: Could not import interaction routers: {e}")

# Import and include sub-users router
try:
    from .api import sub_users, sub_user_dashboard
    app.include_router(sub_users.router)
    app.include_router(sub_user_dashboard.router)
except ImportError:
    print("Warning: Sub-users router not available")

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "User Management Backend API", "status": "healthy"}

@app.get("/health")
@app.head("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

# Backward compatibility endpoint for /auth/me
@app.get("/auth/me")
async def auth_me_backward_compatibility(request: Request):
    """Backward compatibility endpoint for /auth/me - forwards internally instead of redirecting"""
    from .api.auth import get_current_user_unified
    try:
        user = await get_current_user_unified(request)
        return {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login_at": user.last_login_at
        }
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=401, content={"detail": str(e)})

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc) if settings.debug else "Server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
