"""
Redis Caching Service for User Management Backend
Provides caching functionality for user sessions, data, and frequently accessed information.
"""

import json
import time
import hashlib
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
import redis
from app.config import settings


class CacheService:
    """Redis-based caching service for the application"""
    
    def __init__(self):
        """Initialize Redis connection with fallback handling"""
        try:
            self.redis = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                decode_responses=True,
                socket_connect_timeout=5.0,
                socket_timeout=5.0,
                health_check_interval=30
            )
            # Test connection
            self.redis.ping()
            self.connected = True
            print("✅ Redis cache service connected successfully")
        except Exception as e:
            print(f"⚠️ Redis cache connection failed: {e}. Running without cache.")
            self.connected = False
            self.redis = None
    
    def _generate_key(self, prefix: str, identifier: str, suffix: str = "") -> str:
        """Generate consistent cache keys"""
        key = f"{prefix}:{identifier}"
        if suffix:
            key += f":{suffix}"
        return key
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data for Redis storage"""
        if isinstance(data, (dict, list)):
            return json.dumps(data, default=str)
        return str(data)
    
    def _deserialize_data(self, data: str) -> Any:
        """Deserialize data from Redis"""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Set a value in cache with TTL"""
        if not self.connected:
            return False
        
        try:
            serialized_value = self._serialize_data(value)
            return self.redis.setex(key, ttl_seconds, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        if not self.connected:
            return None
        
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            return self._deserialize_data(value)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self.connected:
            return False
        
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache"""
        if not self.connected:
            return False
        
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1, ttl_seconds: int = 3600) -> Optional[int]:
        """Increment a numeric value in cache"""
        if not self.connected:
            return None
        
        try:
            pipe = self.redis.pipeline()
            pipe.incr(key, amount)
            pipe.expire(key, ttl_seconds)
            result = pipe.execute()
            return result[0] if result else None
        except Exception as e:
            print(f"Cache increment error: {e}")
            return None
    
    # User-specific caching methods
    async def cache_user_data(self, user_id: str, user_data: Dict[str, Any], ttl_seconds: int = 1800) -> bool:
        """Cache user profile data"""
        key = self._generate_key("user_data", user_id)
        return await self.set(key, user_data, ttl_seconds)
    
    async def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user profile data"""
        key = self._generate_key("user_data", user_id)
        return await self.get(key)
    
    async def invalidate_user_data(self, user_id: str) -> bool:
        """Invalidate cached user data"""
        key = self._generate_key("user_data", user_id)
        return await self.delete(key)
    
    async def cache_user_session(self, user_id: str, session_data: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Cache user session data"""
        key = self._generate_key("user_session", user_id)
        return await self.set(key, session_data, ttl_seconds)
    
    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user session data"""
        key = self._generate_key("user_session", user_id)
        return await self.get(key)
    
    async def invalidate_user_session(self, user_id: str) -> bool:
        """Invalidate user session cache"""
        key = self._generate_key("user_session", user_id)
        return await self.delete(key)
    
    # Token blacklisting
    async def blacklist_token(self, token_jti: str, ttl_seconds: int = 86400) -> bool:
        """Add token to blacklist"""
        key = self._generate_key("blacklisted_token", token_jti)
        return await self.set(key, "blacklisted", ttl_seconds)
    
    async def is_token_blacklisted(self, token_jti: str) -> bool:
        """Check if token is blacklisted"""
        key = self._generate_key("blacklisted_token", token_jti)
        return await self.exists(key)
    
    # Template and Component caching
    async def cache_template(self, template_id: str, template_data: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Cache template data"""
        key = self._generate_key("template", template_id)
        return await self.set(key, template_data, ttl_seconds)
    
    async def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get cached template data"""
        key = self._generate_key("template", template_id)
        return await self.get(key)
    
    async def invalidate_template(self, template_id: str) -> bool:
        """Invalidate template cache"""
        key = self._generate_key("template", template_id)
        return await self.delete(key)
    
    async def cache_component(self, component_id: str, component_data: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Cache component data"""
        key = self._generate_key("component", component_id)
        return await self.set(key, component_data, ttl_seconds)
    
    async def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get cached component data"""
        key = self._generate_key("component", component_id)
        return await self.get(key)
    
    async def invalidate_component(self, component_id: str) -> bool:
        """Invalidate component cache"""
        key = self._generate_key("component", component_id)
        return await self.delete(key)
    
    # Statistics caching
    async def cache_statistics(self, stat_type: str, data: Dict[str, Any], ttl_seconds: int = 300) -> bool:
        """Cache statistics data (short TTL due to frequent updates)"""
        key = self._generate_key("stats", stat_type)
        return await self.set(key, data, ttl_seconds)
    
    async def get_statistics(self, stat_type: str) -> Optional[Dict[str, Any]]:
        """Get cached statistics"""
        key = self._generate_key("stats", stat_type)
        return await self.get(key)
    
    # Cart caching
    async def cache_user_cart(self, user_id: str, cart_data: Dict[str, Any], ttl_seconds: int = 1800) -> bool:
        """Cache user shopping cart"""
        key = self._generate_key("user_cart", user_id)
        return await self.set(key, cart_data, ttl_seconds)
    
    async def get_user_cart(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user cart"""
        key = self._generate_key("user_cart", user_id)
        return await self.get(key)
    
    async def invalidate_user_cart(self, user_id: str) -> bool:
        """Invalidate user cart cache"""
        key = self._generate_key("user_cart", user_id)
        return await self.delete(key)
    
    # Template and Component list caching methods
    async def cache_templates(self, cache_key: str, data: Any, ttl: int = 3600) -> bool:
        """Cache template list data"""
        if not self.connected:
            return False
        
        try:
            serialized_data = self._serialize_data(data)
            return bool(self.redis.setex(cache_key, ttl, serialized_data))
        except Exception as e:
            print(f"Cache templates error: {e}")
            return False
    
    async def get_templates(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get templates from cache"""
        if not self.connected:
            return None
        
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                return self._deserialize_data(cached_data)
            return None
        except Exception as e:
            print(f"Get templates cache error: {e}")
            return None
    
    async def cache_components(self, cache_key: str, data: Any, ttl: int = 3600) -> bool:
        """Cache component list data"""
        if not self.connected:
            return False
        
        try:
            serialized_data = self._serialize_data(data)
            return bool(self.redis.setex(cache_key, ttl, serialized_data))
        except Exception as e:
            print(f"Cache components error: {e}")
            return False
    
    async def get_components(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get components from cache"""
        if not self.connected:
            return None
        
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                return self._deserialize_data(cached_data)
            return None
        except Exception as e:
            print(f"Get components cache error: {e}")
            return None
    
    # Bulk operations
    async def invalidate_user_all(self, user_id: str) -> bool:
        """Invalidate all cached data for a user"""
        if not self.connected:
            return False
        
        try:
            # Get all keys related to this user
            patterns = [
                f"user_data:{user_id}",
                f"user_session:{user_id}",
                f"user_cart:{user_id}",
            ]
            
            deleted_count = 0
            for pattern in patterns:
                if self.redis.delete(pattern):
                    deleted_count += 1
            
            return deleted_count > 0
        except Exception as e:
            print(f"Cache bulk invalidation error: {e}")
            return False
    
    async def clear_all_cache(self) -> bool:
        """Clear all cache (use with caution)"""
        if not self.connected:
            return False
        
        try:
            return self.redis.flushdb()
        except Exception as e:
            print(f"Cache clear all error: {e}")
            return False
    
    async def get_cache_info(self) -> Dict[str, Any]:
        """Get cache connection and usage info"""
        if not self.connected:
            return {"connected": False, "error": "Redis not available"}
        
        try:
            info = self.redis.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "Unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}
    
    # Additional cache management methods
    
    async def clear_user_session(self, user_id: str) -> bool:
        """Clear user session cache"""
        if not self.connected:
            return False
        
        try:
            key = self._generate_key("session", user_id)
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Clear user session error: {e}")
            return False
    
    async def clear_user_data(self, user_id: str) -> bool:
        """Clear user data cache"""
        if not self.connected:
            return False
        
        try:
            key = self._generate_key("user", user_id)
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Clear user data error: {e}")
            return False
    
    async def clear_template_caches(self) -> bool:
        """Clear all template-related caches"""
        if not self.connected:
            return False
        
        try:
            # Get all template cache keys
            template_keys = self.redis.keys("templates:*")
            template_stats_keys = self.redis.keys("template_stats:*")
            
            # Delete all template-related keys
            if template_keys:
                self.redis.delete(*template_keys)
            if template_stats_keys:
                self.redis.delete(*template_stats_keys)
            
            return True
        except Exception as e:
            print(f"Clear template caches error: {e}")
            return False
    
    async def clear_component_caches(self) -> bool:
        """Clear all component-related caches"""
        if not self.connected:
            return False
        
        try:
            # Get all component cache keys
            component_keys = self.redis.keys("components:*")
            component_stats_keys = self.redis.keys("component_stats:*")
            
            # Delete all component-related keys
            if component_keys:
                self.redis.delete(*component_keys)
            if component_stats_keys:
                self.redis.delete(*component_stats_keys)
            
            return True
        except Exception as e:
            print(f"Clear component caches error: {e}")
            return False
    
    async def close(self) -> None:
        """Close Redis connection"""
        if self.redis and self.connected:
            try:
                self.redis.close()
                print("🔌 Redis connection closed")
            except Exception as e:
                print(f"⚠️ Error closing Redis connection: {e}")


# Global cache service instance
cache_service = CacheService()


# Dependency function for FastAPI
async def get_cache_service() -> CacheService:
    """FastAPI dependency to get cache service"""
    return cache_service
