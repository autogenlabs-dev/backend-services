# Audit logging utility functions
from datetime import datetime
from typing import Optional, Dict, Any
import traceback

from app.models.audit_log import AuditLog, ActionType, AuditSeverity


async def log_audit_event(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    details: Optional[Dict[str, Any]] = None,
    severity: str = "info",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditLog:
    """
    Log an audit event to the database.
    
    Args:
        user_id: ID of the user performing the action
        action: Action being performed (e.g., "CREATE_TEMPLATE_COMMENT")
        resource_type: Type of resource being acted upon (e.g., "template_comment")
        resource_id: ID of the specific resource
        details: Additional details about the action
        severity: AuditSeverity level (info, warning, error, critical)
        ip_address: IP address of the user (optional)
        user_agent: User agent string (optional)
    
    Returns:
        The created AuditLog instance
    """
    try:
        # Convert action string to ActionType enum if possible
        action_type = None
        try:
            action_type = ActionType(action.lower())
        except ValueError:
            # If action doesn't match enum, use the string as-is
            action_type = action
        
        # Convert severity string to AuditSeverity enum
        severity_enum = AuditSeverity.INFO
        try:
            severity_enum = AuditSeverity(severity.lower())
        except ValueError:
            pass  # Default to INFO if invalid severity
        
        # Create audit log entry
        audit_log = AuditLog(
            user_id=user_id,
            action=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            severity=severity_enum,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        
        await audit_log.insert()
        return audit_log
        
    except Exception as e:
        # If audit logging fails, print error but don't raise exception
        # to avoid breaking the main application flow
        print(f"Failed to log audit event: {e}")
        print(f"Action: {action}, User: {user_id}, Resource: {resource_type}/{resource_id}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Return a mock audit log for consistency
        return AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            severity=severity_enum,
            timestamp=datetime.utcnow()
        )


async def log_user_action(
    user_id: str,
    action: str,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Log a user action (convenience function).
    
    Args:
        user_id: ID of the user performing the action
        action: Action being performed
        details: Additional details about the action
        ip_address: IP address of the user
    
    Returns:
        The created AuditLog instance
    """
    return await log_audit_event(
        user_id=user_id,
        action=action,
        resource_type="user",
        resource_id=user_id,
        details=details,
        ip_address=ip_address
    )


async def log_admin_action(
    admin_user_id: str,
    action: str,
    target_resource_type: str,
    target_resource_id: str,
    details: Optional[Dict[str, Any]] = None,
    severity: str = "info"
) -> AuditLog:
    """
    Log an admin action (convenience function).
    
    Args:
        admin_user_id: ID of the admin user performing the action
        action: Action being performed
        target_resource_type: Type of resource being acted upon
        target_resource_id: ID of the target resource
        details: Additional details about the action
        severity: AuditSeverity level
    
    Returns:
        The created AuditLog instance
    """
    return await log_audit_event(
        user_id=admin_user_id,
        action=action,
        resource_type=target_resource_type,
        resource_id=target_resource_id,
        details=details,
        severity=severity
    )


async def log_security_event(
    user_id: Optional[str],
    action: str,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    severity: str = "warning"
) -> AuditLog:
    """
    Log a security event (convenience function).
    
    Args:
        user_id: ID of the user (can be None for system events)
        action: Security action/event
        details: Additional details about the event
        ip_address: IP address involved
        severity: AuditSeverity level (typically warning or error)
    
    Returns:
        The created AuditLog instance
    """
    return await log_audit_event(
        user_id=user_id or "system",
        action=action,
        resource_type="security",
        resource_id="system",
        details=details,
        severity=severity,
        ip_address=ip_address
    )


async def log_content_action(
    user_id: str,
    action: str,
    content_type: str,
    content_id: str,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Log a content-related action (convenience function).
    
    Args:
        user_id: ID of the user performing the action
        action: Content action being performed
        content_type: Type of content (template, component, etc.)
        content_id: ID of the content
        details: Additional details about the action
    
    Returns:
        The created AuditLog instance
    """
    return await log_audit_event(
        user_id=user_id,
        action=action,
        resource_type=content_type,
        resource_id=content_id,
        details=details
    )
