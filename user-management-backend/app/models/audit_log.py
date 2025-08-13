"""
Audit Log model for tracking admin actions and important system events.
"""

from beanie import Document
from pydantic import Field
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict
import uuid


class ActionType(str, Enum):
    """Types of actions that can be audited."""
    
    # User Management
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ROLE_CHANGED = "user_role_changed"
    USER_STATUS_CHANGED = "user_status_changed"
    
    # Content Management
    CONTENT_APPROVED = "content_approved"
    CONTENT_REJECTED = "content_rejected"
    CONTENT_DELETED = "content_deleted"
    CONTENT_FEATURED = "content_featured"
    CONTENT_UNFEATURED = "content_unfeatured"
    
    # Developer Management
    DEVELOPER_APPROVED = "developer_approved"
    DEVELOPER_REJECTED = "developer_rejected"
    DEVELOPER_SUSPENDED = "developer_suspended"
    
    # Payment Management
    PAYMENT_REFUNDED = "payment_refunded"
    PAYOUT_PROCESSED = "payout_processed"
    TRANSACTION_DISPUTED = "transaction_disputed"
    
    # System Configuration
    SETTINGS_UPDATED = "settings_updated"
    CATEGORY_CREATED = "category_created"
    CATEGORY_UPDATED = "category_updated"
    CATEGORY_DELETED = "category_deleted"
    
    # Security
    LOGIN_FAILED = "login_failed"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCOUNT_LOCKED = "account_locked"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLog(Document):
    """
    Audit log for tracking admin actions and system events.
    """
    
    # Unique identifier
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    
    # Action details
    action_type: ActionType = Field(..., description="Type of action performed")
    action_description: str = Field(..., description="Human-readable description of the action")
    severity: AuditSeverity = Field(default=AuditSeverity.MEDIUM, description="Severity of the action")
    
    # Actor information
    actor_id: Optional[str] = Field(None, description="ID of user who performed the action")
    actor_email: Optional[str] = Field(None, description="Email of user who performed the action")
    actor_role: Optional[str] = Field(None, description="Role of user who performed the action")
    actor_ip: Optional[str] = Field(None, description="IP address of the actor")
    
    # Target information
    target_type: Optional[str] = Field(None, description="Type of target (user, template, component, etc.)")
    target_id: Optional[str] = Field(None, description="ID of the target object")
    target_name: Optional[str] = Field(None, description="Name/title of the target object")
    
    # Additional context
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
    old_values: Optional[Dict[str, Any]] = Field(None, description="Previous values before change")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values after change")
    
    # Request information
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    user_agent: Optional[str] = Field(None, description="User agent string")
    endpoint: Optional[str] = Field(None, description="API endpoint that triggered the action")
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the action occurred")
    
    # Status
    success: bool = Field(default=True, description="Whether the action was successful")
    error_message: Optional[str] = Field(None, description="Error message if action failed")
    
    class Settings:
        """Beanie document settings."""
        collection = "audit_logs"
        indexes = [
            "timestamp",
            "action_type",
            "actor_id",
            "target_type",
            "target_id",
            "severity",
            ("timestamp", "action_type"),
            ("actor_id", "timestamp"),
            ("target_type", "target_id"),
        ]
        
    def __str__(self) -> str:
        return f"AuditLog({self.action_type}, {self.actor_email}, {self.timestamp})"
        
    @classmethod
    async def log_action(
        cls,
        action_type: ActionType,
        action_description: str,
        actor_id: Optional[str] = None,
        actor_email: Optional[str] = None,
        actor_role: Optional[str] = None,
        actor_ip: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        target_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        request_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> "AuditLog":
        """
        Convenience method to create and save an audit log entry.
        
        Args:
            action_type: Type of action performed
            action_description: Human-readable description
            actor_id: ID of user performing action
            actor_email: Email of user performing action
            actor_role: Role of user performing action
            actor_ip: IP address of user
            target_type: Type of target object
            target_id: ID of target object
            target_name: Name of target object
            metadata: Additional context data
            old_values: Previous values before change
            new_values: New values after change
            severity: Severity level
            request_id: Request ID for tracing
            user_agent: User agent string
            endpoint: API endpoint
            success: Whether action was successful
            error_message: Error message if failed
            
        Returns:
            Created AuditLog instance
        """
        try:
            audit_log = cls(
                action_type=action_type,
                action_description=action_description,
                severity=severity,
                actor_id=actor_id,
                actor_email=actor_email,
                actor_role=actor_role,
                actor_ip=actor_ip,
                target_type=target_type,
                target_id=target_id,
                target_name=target_name,
                metadata=metadata or {},
                old_values=old_values,
                new_values=new_values,
                request_id=request_id,
                user_agent=user_agent,
                endpoint=endpoint,
                success=success,
                error_message=error_message
            )
            
            await audit_log.insert()
            return audit_log
            
        except Exception as e:
            # Don't let audit logging failures break the main operation
            print(f"Failed to create audit log: {e}")
            return None
