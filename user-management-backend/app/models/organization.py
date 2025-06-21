"""Organization models for enterprise features."""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database import Base


class Organization(Base):
    """Organization model for enterprise customers."""
    
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    admin_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subscription_plan = Column(String(50), default="enterprise")
    token_pool = Column(Integer, default=1000000)
    tokens_used = Column(Integer, default=0)
    monthly_limit = Column(Integer, default=1000000)
    reset_date = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    admin_user = relationship("User", foreign_keys=[admin_user_id])
    members = relationship("OrganizationMember", back_populates="organization")
    keys = relationship("OrganizationKey", back_populates="organization")


class OrganizationKey(Base):
    """Organization API keys for team access."""
    
    __tablename__ = "organization_keys"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    key_name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSON, default=lambda: {})
    monthly_limit = Column(Integer, default=100000)
    tokens_used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_used_at = Column(DateTime)
    
        
    # Relationships
    organization = relationship("Organization", back_populates="keys")
    creator = relationship("User", foreign_keys=[created_by])
    usage_logs = relationship("KeyUsageLog", back_populates="organization_key")


class OrganizationMember(Base):
    """Organization membership table."""
    
    __tablename__ = "organization_members"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member")
    assigned_key_id = Column(String(36), ForeignKey("organization_keys.id"))
    joined_at = Column(DateTime, server_default=func.now())
    invited_by = Column(String(36), ForeignKey("users.id"))
    
    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])
    assigned_key = relationship("OrganizationKey", foreign_keys=[assigned_key_id])


class KeyUsageLog(Base):
    """Log organization key usage for analytics."""
    
    __tablename__ = "key_usage_logs"
    
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    organization_key_id = Column(String(36), ForeignKey("organization_keys.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)
    model_name = Column(String(100), nullable=False)
    tokens_used = Column(Integer, nullable=False)
    cost_usd = Column(DECIMAL(10, 6))
    request_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    organization_key = relationship("OrganizationKey", back_populates="usage_logs")
    user = relationship("User")
