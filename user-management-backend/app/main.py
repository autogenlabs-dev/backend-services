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
from .api import admin_api_keys, webhooks
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
from app.models.item_purchase import ItemPurchase
from app.models.developer_earnings import DeveloperEarnings, PayoutRequest
from app.models.shopping_cart import ShoppingCart
from app.models.audit_log import AuditLog
from app.models.api_key_pool import ApiKeyPool

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Initialize database and Beanie
    print("🔄 Connecting to database...")
    client = AsyncIOMotorClient(settings.database_url)
    database = client.get_default_database()
    
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
                TemplateComment,
                Component,
                ItemPurchase,
                DeveloperEarnings,
                PayoutRequest,
                ShoppingCart,
                AuditLog,
                ApiKeyPool
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

# Custom middleware for performance monitoring and rate limit headers
class PerformanceAndRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> JSONResponse:
        # Note: Debug logging removed for production security
        # Sensitive headers should never be logged

        # Track request timing
        start_time = time.time()
        
        # Apply rate limiting for non-health endpoints AND skip OPTIONS requests
        if request.method != "OPTIONS" and not request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
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
        
        # Prevent caching of OPTIONS preflight requests
        # This fixes CORS issues when Cloudflare caches OPTIONS with wrong origin
        if request.method == "OPTIONS":
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        # Add request processing time header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Add rate limit headers if present in request state
        if hasattr(request.state, "rate_limit_info"):
            add_rate_limit_headers(response, request.state.rate_limit_info)
        
        # Return the response
        return response

# Add custom middleware (Inner middleware)


# Add CORS middleware with explicit origins and regex (Outer middleware - runs first)
# Start with origins from config
allowed_origins = list(settings.backend_cors_origins)

# SIMPLE FIX: Add both www and non-www versions of production domains
production_domains = [
    "https://codemurf.com",
    "https://www.codemurf.com",
    "http://codemurf.com",
    "http://www.codemurf.com",
]
for domain in production_domains:
    if domain not in allowed_origins:
        allowed_origins.append(domain)

# Add common development ports if in debug mode
if settings.debug:
    dev_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:4200",  # Angular default
        "http://localhost:5173",  # Vite default
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]
    for origin in dev_origins:
        if origin not in allowed_origins:
            allowed_origins.append(origin)

# Allow environment variable to add additional origins (for production without code changes)
import os
extra_origins = os.getenv("CORS_EXTRA_ORIGINS", "")
if extra_origins:
    for origin in extra_origins.split(","):
        origin = origin.strip()
        if origin and origin not in allowed_origins:
            allowed_origins.append(origin)

# Log CORS origins for debugging
print(f"🔧 CORS Configuration:")
print(f"   - Allowed Origins: {allowed_origins}")
print(f"   - Debug Mode: {settings.debug}")

# Check if CORS middleware should be disabled (when Cloudflare handles CORS)
import os
disable_cors = os.getenv("DISABLE_CORS_MIDDLEWARE", "false").lower() == "true"

if not disable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Explicit origins only
        allow_credentials=True,  # Allow credentials for authenticated requests  
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )
    print("✅ CORS Middleware enabled")
else:
    print("⚠️ CORS Middleware DISABLED - Cloudflare handles CORS")

# Add custom middleware (Outer middleware - wraps CORS)
# This ensures we can add headers to responses generated by CORS middleware (like OPTIONS)
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
# Include item payments router (from endpoints)
from .endpoints import payments as item_payments
app.include_router(item_payments.router, prefix="/api")
# Extension authentication endpoints (Clerk-compatible API)
app.include_router(extension_auth.router, prefix="/api")

# Debug router - ONLY in debug mode
if settings.debug:
    app.include_router(debug.router, prefix="/api")

app.include_router(verify.router, prefix="/api")

# Admin API key pool management
app.include_router(admin_api_keys.router, prefix="/api")

# Webhook endpoints (no /api prefix for external access)
app.include_router(webhooks.router)

# Screenshot service for template/component previews
from .services.screenshot_service import router as screenshot_router
app.include_router(screenshot_router, prefix="/api", tags=["Screenshots"])

# Backward compatibility: Mount components router without /api prefix for frontend
# This allows frontend to call /components directly
app.include_router(components.router, tags=["Components (Legacy)"])

# Legacy routes for frontend compatibility (without /api prefix)
# Frontend calls /user/dashboard, /cart, /purchased-items directly
app.include_router(users.router, prefix="", tags=["Users (Legacy)"])
app.include_router(item_payments.router, prefix="", tags=["Payments (Legacy)"])

# Legacy routes already mounted above (users.router, item_payments.router without /api prefix)


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
