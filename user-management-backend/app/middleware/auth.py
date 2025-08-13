"""
Role-based authentication middleware for FastAPI
"""
from functools import wraps
from typing import List, Optional
from fastapi import HTTPException, Header, Depends
import jwt
from app.models.user import User, UserRole
from app.config import settings

async def get_current_user_from_token(authorization: str = Header(None)) -> Optional[User]:
    """Get current user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await User.get(user_id)
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception):
        return None

async def require_auth(authorization: str = Header(None)) -> User:
    """Require valid authentication"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="User account is inactive")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

async def require_role(required_roles: List[UserRole], authorization: str = Header(None)) -> User:
    """Require specific user roles"""
    user = await require_auth(authorization)
    
    if user.role not in required_roles:
        raise HTTPException(
            status_code=403, 
            detail=f"Access denied. Required roles: {[role.value for role in required_roles]}"
        )
    
    return user

def require_admin(current_user: User = Depends(get_current_user_from_token)):
    """Dependency to require admin role"""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user

def require_developer_or_admin(current_user: User = Depends(get_current_user_from_token)):
    """Dependency to require developer or admin role"""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    if current_user.role not in [UserRole.DEVELOPER, UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Developer or Admin access required"
        )
    return current_user

async def require_developer(authorization: str = Header(None)) -> User:
    """Require developer role or higher"""
    return await require_role([UserRole.DEVELOPER, UserRole.ADMIN, UserRole.SUPERADMIN], authorization)

async def require_user(authorization: str = Header(None)) -> User:
    """Require any authenticated user"""
    return await require_auth(authorization)

def check_content_ownership(user: User, content_user_id: str) -> bool:
    """Check if user owns the content or is admin"""
    if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        return True
    return str(user.id) == content_user_id

def check_content_access(user: User, content) -> str:
    """
    Check user's access level to content
    Returns: 'full_access', 'limited_access', 'owner_access', 'no_access'
    """
    # Admin always has full access
    if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        return "full_access"
    
    # Owner access
    if hasattr(content, 'user_id') and str(content.user_id) == str(user.id):
        return "owner_access"
    
    # Check if content is approved for public viewing
    if hasattr(content, 'approval_status') and content.approval_status != "approved":
        return "no_access"
    
    # Free content - full access
    if hasattr(content, 'plan_type') and content.plan_type.lower() == "free":
        return "full_access"
    
    # TODO: Check if user has purchased the content
    # This will be implemented when purchase system is added
    
    # Default to limited access for paid content
    return "limited_access"

class RoleChecker:
    """Class-based role checker for dependency injection"""
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, authorization: str = Header(None)) -> User:
        return await require_role(self.allowed_roles, authorization)

# Convenience instances
AdminOnly = RoleChecker([UserRole.ADMIN, UserRole.SUPERADMIN])
DeveloperOrAdmin = RoleChecker([UserRole.DEVELOPER, UserRole.ADMIN, UserRole.SUPERADMIN])
AnyUser = RoleChecker([UserRole.USER, UserRole.DEVELOPER, UserRole.ADMIN, UserRole.SUPERADMIN])
