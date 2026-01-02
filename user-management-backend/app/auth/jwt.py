"""JWT token utilities for authentication."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import hashlib
import secrets

from jose import JWTError, jwt
import bcrypt  # Direct bcrypt usage instead of passlib for better compatibility
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uuid

from ..config import settings
from ..database import get_database
from ..models.user import User

# Bearer token authentication scheme
security = HTTPBearer()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Supports both bcrypt (new) and SHA-256 (legacy) hashed passwords.
    This allows seamless migration from old SHA-256 hashes to bcrypt.
    """
    # Try bcrypt first (new format)
    try:
        if hashed_password.startswith("$2"):  # bcrypt hash indicator
            # Ensure bytes for bcrypt
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        pass
    
    # Fallback to SHA-256 (legacy format) for existing passwords
    sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return sha256_hash == hashed_password


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    bcrypt is designed specifically for password hashing with:
    - Built-in salt generation
    - Configurable work factor for future-proofing
    - Resistance to timing attacks
    """
    # Hash password using bcrypt (generates salt automatically)
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def needs_password_rehash(hashed_password: str) -> bool:
    """
    Check if a password hash needs to be upgraded to bcrypt.
    
    Returns True if the hash is SHA-256 (legacy) and should be 
    rehashed with bcrypt on next successful login.
    """
    return not hashed_password.startswith("$2")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Any = Depends(get_database)
) -> User:
    """Get the current authenticated user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
            
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Convert user_id to UUID if it's a string
        try:
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
        except (ValueError, TypeError):
            raise credentials_exception
        
        # MongoDB: Find user by ID
        user = await User.get(user_id)
        
        if user is None:
            raise credentials_exception
            
        return user
            
    except JWTError:
        raise credentials_exception