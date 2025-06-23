"""
Rate limiting middleware using Redis for the FastAPI marketplace backend.
Provides request rate limiting based on user tokens, API keys, and IP addresses.
"""

import time
import redis
import json
from typing import Optional, Tuple, Dict, Any, List
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_database # Changed from get_db to get_database
from app.models.user import User, ApiKey
from app.config import settings
from app.auth.jwt import verify_token
import hashlib

# Redis client
try:
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        decode_responses=True,
        socket_connect_timeout=2.0  # Short timeout for faster fallback
    )
    # Test connection
    redis_client.ping()
    print("✅ Redis connected successfully")
except Exception as e:
    print(f"⚠️ Redis connection failed: {e}. Using fallback mode for rate limiting.")
    # Dummy Redis client for fallback
    class DummyRedis:
        def get(self, *args, **kwargs):
            return None
        
        def incr(self, *args, **kwargs):
            return 1
        
        def expire(self, *args, **kwargs):
            return True
        
        def pipeline(self, *args, **kwargs):
            return self
        
        def execute(self, *args, **kwargs):
            return [1, True]
    
    redis_client = DummyRedis()

security = HTTPBearer(auto_error=False)

class RateLimiter:
    """Redis-based rate limiter with sliding window algorithm"""
    
    def __init__(self):
        self.redis = redis_client
        
    def _get_window_key(self, identifier: str, window: str) -> str:
        """Generate Redis key for rate limiting window"""
        return f"rate_limit:{identifier}:{window}"
    
    def _get_current_window(self, window_seconds: int) -> int:
        """Get current time window"""
        return int(time.time()) // window_seconds
    
    async def check_rate_limit(
        self, 
        identifier: str, 
        limit: int, 
        window_seconds: int = 3600,
        endpoint: str = "general"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limit
        
        Args:
            identifier: Unique identifier (user_id, api_key, ip)
            limit: Maximum requests allowed in window
            window_seconds: Time window in seconds (default: 1 hour)
            endpoint: Endpoint category for granular limits
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        try:
            current_window = self._get_current_window(window_seconds)
            key = self._get_window_key(f"{identifier}:{endpoint}", str(current_window))
            
            # Get current count
            current_count = self.redis.get(key)
            current_count = int(current_count) if current_count else 0
            
            # Rate limit info
            remaining = max(0, limit - current_count)
            reset_time = (current_window + 1) * window_seconds
            
            rate_limit_info = {
                "limit": limit,
                "remaining": remaining,
                "reset": reset_time,
                "window_seconds": window_seconds
            }
            
            if current_count >= limit:
                return False, rate_limit_info
            
            # Increment counter with expiration
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            pipe.execute()
            
            # Update remaining count
            rate_limit_info["remaining"] = remaining - 1
            
            return True, rate_limit_info
            
        except Exception as e:
            # If Redis fails, allow the request but log the error
            print(f"Rate limiting error: {e}")
            return True, {
                "limit": limit,
                "remaining": limit - 1,
                "reset": int(time.time()) + window_seconds,
                "window_seconds": window_seconds,
                "error": "rate_limiter_unavailable"
            }


class RateLimitMiddleware:
    """Rate limiting middleware for FastAPI"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.rate_limits = {
            # Free tier limits (per hour)
            "free": {
                "general": 100,
                "llm": 50,
                "auth": 20
            },
            # Pro tier limits (per hour)
            "pro": {
                "general": 1000,
                "llm": 500,
                "auth": 100
            },
            # Enterprise tier limits (per hour)
            "enterprise": {
                "general": 10000,
                "llm": 5000,
                "auth": 500
            },
            # API key limits (per hour)
            "api_key": {
                "general": 2000,
                "llm": 1000,
                "auth": 200
            },
            # IP-based limits for unauthenticated requests
            "ip": {
                "general": 50,
                "llm": 0,  # No LLM access without auth
                "auth": 10
            }
        }
    
    def _get_endpoint_category(self, path: str) -> str:
        """Categorize endpoint for rate limiting"""
        if path.startswith("/api/llm/"):
            return "llm"
        elif path.startswith(("/api/auth/", "/api/users/")):
            return "auth"
        else:
            return "general"
            
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip
            
        return request.client.host if request.client else "unknown"
    
    async def _get_user_from_token(self, token: str, db: Session) -> Optional[User]:
        """Get user from JWT token"""
        try:
            payload = verify_token(token)
            if not payload:
                return None
                
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            # Convert user_id to UUID if it's a string
            import uuid
            try:
                if isinstance(user_id, str):
                    user_id = uuid.UUID(user_id)
            except (ValueError, TypeError):
                return None
                
            result = db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
            
        except Exception:
            return None
    
    async def _get_user_from_api_key(self, api_key: str, db: Session) -> Optional[Tuple[User, ApiKey]]:
        """Get user from API key"""
        try:
            # Hash the API key to match stored hash
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            result = db.execute(
                select(ApiKey).where(
                    ApiKey.key_hash == key_hash,
                    ApiKey.is_active == True
                )
            )
            api_key_obj = result.scalar_one_or_none()
            
            if not api_key_obj:
                return None, None
                  # Update last used timestamp
            from datetime import datetime
            api_key_obj.last_used_at = datetime.utcnow()
            db.commit()
            
            # Get the associated user
            import uuid
            try:
                user_id = api_key_obj.user_id
                if isinstance(user_id, str):
                    user_id = uuid.UUID(user_id)
            except (ValueError, TypeError):
                return None, None
                
            result = db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            return user, api_key_obj
            
        except Exception:
            return None, None
    
    async def check_rate_limit(
        self, 
        request: Request, 
        db: Session
    ) -> Dict[str, Any]:
        """
        Check rate limits for incoming request
        
        Returns rate limit info or raises HTTPException
        """
        endpoint_category = self._get_endpoint_category(request.url.path)
        client_ip = self._get_client_ip(request)
        
        # Try to identify user
        user = None
        api_key_obj = None
        identifier = None
        rate_limit_tier = "ip"
        
        # Check for API key in headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            user, api_key_obj = await self._get_user_from_api_key(api_key, db)
            if user and api_key_obj:
                identifier = f"api_key:{api_key_obj.id}"
                rate_limit_tier = "api_key"
        
        # Check for Bearer token
        if not user:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                user = await self._get_user_from_token(token, db)
                if user:
                    identifier = f"user:{user.id}"
                    rate_limit_tier = user.subscription
        
        # Fall back to IP-based limiting
        if not identifier:
            identifier = f"ip:{client_ip}"
            rate_limit_tier = "ip"
        
        # Get rate limits for tier and endpoint
        limits = self.rate_limits.get(rate_limit_tier, self.rate_limits["ip"])
        limit = limits.get(endpoint_category, limits["general"])
        
        # Check rate limit
        is_allowed, rate_info = await self.rate_limiter.check_rate_limit(
            identifier=identifier,
            limit=limit,
            window_seconds=3600,  # 1 hour window
            endpoint=endpoint_category
        )
        
        # Add additional metadata
        rate_info.update({
            "tier": rate_limit_tier,
            "endpoint_category": endpoint_category,
            "identifier_type": identifier.split(":")[0] if ":" in identifier else "unknown"
        })
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded for {endpoint_category} endpoints",
                    "rate_limit": rate_info
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info["reset"] - int(time.time()))
                }
            )
        
        return rate_info


# Global rate limiter instance
rate_limit_middleware = RateLimitMiddleware()

async def apply_rate_limit(
    request: Request,
    db: Any = Depends(get_database) # Changed type hint from Session to Any, and get_db to get_database
) -> Dict[str, Any]:
    """
    FastAPI dependency for applying rate limits
    Usage: rate_info = Depends(apply_rate_limit)
    """
    return await rate_limit_middleware.check_rate_limit(request, db)

def add_rate_limit_headers(response, rate_info: Dict[str, Any]):
    """Add rate limit headers to response"""
    response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
    response.headers["X-RateLimit-Tier"] = rate_info["tier"]
