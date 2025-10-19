#!/usr/bin/env python3
"""
IntelliAttend - Audit Logging Helpers
Consistent audit logging for all registration and admin actions
"""

from datetime import datetime
from flask import request
from typing import Optional, Dict, Any


def log_registration_action(
    db,
    RegistrationAuditLog,
    Admin,
    action: str,
    resource_type: str,
    resource_id: int,
    admin_id: int,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log a registration action to the audit log
    
    Args:
        db: SQLAlchemy database instance
        RegistrationAuditLog: RegistrationAuditLog model class
        Admin: Admin model class
        action: Action performed ('create', 'update', 'delete', 'approve', 'reject')
        resource_type: Type of resource ('classroom', 'student', 'faculty', 'device', 'wifi', 'beacon')
        resource_id: ID of the affected resource
        admin_id: ID of the admin performing the action
        details: Optional dictionary with additional context
    
    Returns:
        RegistrationAuditLog instance
    """
    try:
        # Get admin username
        admin = Admin.query.get(admin_id)
        admin_username = admin.username if admin else "Unknown"
        
        # Get request metadata
        ip_address = request.remote_addr if request else None
        user_agent = request.user_agent.string if request and hasattr(request, 'user_agent') else None
        
        # Create audit log entry
        audit_entry = RegistrationAuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            admin_id=admin_id,
            admin_username=admin_username,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        
        db.session.add(audit_entry)
        db.session.flush()  # Flush to get the log_id without committing
        
        return audit_entry
        
    except Exception as e:
        # Log error but don't fail the main operation
        print(f"⚠️  Audit logging error: {e}")
        return None


def create_audit_details(
    operation: str,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a structured audit details dictionary
    
    Args:
        operation: Description of the operation
        old_values: Previous values (for updates)
        new_values: New values
        metadata: Additional metadata
    
    Returns:
        Dictionary with audit details
    """
    details = {
        'operation': operation,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if old_values:
        details['old_values'] = old_values
    
    if new_values:
        details['new_values'] = new_values
    
    if metadata:
        details['metadata'] = metadata
    
    return details


def sanitize_audit_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize sensitive data before logging to audit
    
    Args:
        data: Dictionary with potentially sensitive data
    
    Returns:
        Sanitized dictionary
    """
    sensitive_fields = ['password', 'password_hash', 'secret_key', 'token', 'api_key']
    
    sanitized = {}
    for key, value in data.items():
        # Check if field name contains sensitive keywords
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            sanitized[key] = '***REDACTED***'
        elif isinstance(value, dict):
            sanitized[key] = sanitize_audit_data(value)
        else:
            sanitized[key] = value
    
    return sanitized


def get_request_context() -> Dict[str, Any]:
    """
    Get request context information for audit logging
    
    Returns:
        Dictionary with request context
    """
    if not request:
        return {}
    
    return {
        'ip_address': request.remote_addr,
        'user_agent': request.user_agent.string if hasattr(request, 'user_agent') else None,
        'method': request.method,
        'endpoint': request.endpoint,
        'url': request.url,
        'referrer': request.referrer
    }
