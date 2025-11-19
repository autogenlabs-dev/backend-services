"""Sub-user management service."""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.user import User, SubscriptionPlan
from ..auth.jwt import get_password_hash


def create_sub_user(
    db: Session, 
    parent_user_id: str, 
    email: str, 
    password: str, 
    name: str, 
    permissions: Dict[str, Any],
    limits: Dict[str, Any]
) -> User:
    """Create a new sub-user under a parent user."""
    # Check if email is already in use
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise ValueError("Email already in use")
    
    # Create hashed password
    hashed_password = get_password_hash(password)
    
    # Create sub-user
    sub_user = User(
        id=str(uuid4()),
        email=email,
        password_hash=hashed_password,
        name=name,
        is_active=True,
        is_sub_user=True,
        parent_user_id=parent_user_user_id,
        sub_user_permissions=permissions,
        sub_user_limits=limits,
        subscription=SubscriptionPlan.FREE,
        tokens_remaining=limits.get("token_limit", 1000),
        tokens_used=0,
        monthly_limit=limits.get("token_limit", 1000),
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(sub_user)
    db.commit()
    db.refresh(sub_user)
    return sub_user


def get_sub_users(db: Session, parent_user_id: str) -> List[User]:
    """Get all sub-users for a parent user."""
    return db.query(User).filter(
        and_(
            User.parent_user_id == parent_user_id,
            User.is_sub_user == True
        )
    ).all()


def get_sub_user_by_id(db: Session, parent_user_id: str, sub_user_id: str) -> Optional[User]:
    """Get a specific sub-user by ID."""
    return db.query(User).filter(
        and_(
            User.id == sub_user_id,
            User.parent_user_id == parent_user_id,
            User.is_sub_user == True
        )
    ).first()


def update_sub_user(
    db: Session, 
    parent_user_id: str, 
    sub_user_id: str, 
    name: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    permissions: Optional[Dict[str, Any]] = None,
    limits: Optional[Dict[str, Any]] = None,
    is_active: Optional[bool] = None
) -> Optional[User]:
    """Update a sub-user's information."""
    sub_user = get_sub_user_by_id(db, parent_user_id, sub_user_id)
    if not sub_user:
        return None
    
    if name is not None:
        sub_user.name = name
        
    if email is not None:
        # Check if new email is already in use by another user
        existing_user = db.query(User).filter(
            and_(
                User.email == email,
                User.id != sub_user_id
            )
        ).first()
        if existing_user:
            raise ValueError("Email already in use")
        sub_user.email = email
        
    if password is not None:
        sub_user.password_hash = get_password_hash(password)
        
    if permissions is not None:
        sub_user.sub_user_permissions = permissions
        
    if limits is not None:
        sub_user.sub_user_limits = limits
        # Update token limits if they exist in the new limits
        token_limit = limits.get("token_limit", sub_user.monthly_limit)
        sub_user.monthly_limit = token_limit
        sub_user.tokens_remaining = max(0, token_limit - sub_user.tokens_used)
        
    if is_active is not None:
        sub_user.is_active = is_active
    
    sub_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(sub_user)
    return sub_user


def delete_sub_user(db: Session, parent_user_id: str, sub_user_id: str) -> bool:
    """Delete a sub-user."""
    sub_user = get_sub_user_by_id(db, parent_user_id, sub_user_id)
    if not sub_user:
        return False
        
    db.delete(sub_user)
    db.commit()
    return True
