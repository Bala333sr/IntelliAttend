#!/usr/bin/env python3
"""
IntelliAttend Security Enhancements
==================================

This module provides critical security enhancements for the IntelliAttend system.
It addresses the key security vulnerabilities identified in the security analysis.
"""

import re
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from flask import request, jsonify
from werkzeug.utils import secure_filename
import logging

# Configure security logging
security_logger = logging.getLogger('security')
security_handler = logging.FileHandler('./logs/security.log')
security_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
security_handler.setFormatter(security_formatter)
security_logger.addHandler(security_handler)
security_logger.setLevel(logging.INFO)

class PasswordValidator:
    """Enhanced password validation with security policies"""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    @classmethod
    def validate_strength(cls, password):
        """
        Validate password strength against security policy
        Returns: (is_valid, error_message, strength_score)
        """
        if not password:
            return False, "Password is required", 0
        
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters long", 0
        
        if len(password) > cls.MAX_LENGTH:
            return False, f"Password must not exceed {cls.MAX_LENGTH} characters", 0
        
        strength_score = 0
        errors = []
        
        # Check for uppercase letters
        if not re.search(r'[A-Z]', password):
            errors.append("at least one uppercase letter")
        else:
            strength_score += 1
        
        # Check for lowercase letters
        if not re.search(r'[a-z]', password):
            errors.append("at least one lowercase letter")
        else:
            strength_score += 1
        
        # Check for digits
        if not re.search(r'\d', password):
            errors.append("at least one number")
        else:
            strength_score += 1
        
        # Check for special characters
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("at least one special character (!@#$%^&*(),.?\":{}|<>)")
        else:
            strength_score += 1
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin123', 'letmein', 'welcome', 'monkey'
        ]
        
        if password.lower() in weak_passwords:
            errors.append("password is too common")
            strength_score = max(0, strength_score - 2)
        
        # Check for sequential characters
        if cls._has_sequential_chars(password):
            errors.append("avoid sequential characters")
            strength_score = max(0, strength_score - 1)
        
        if errors:
            error_msg = f"Password must contain {', '.join(errors)}"
            return False, error_msg, strength_score
        
        return True, "Password meets security requirements", strength_score
    
    @classmethod
    def _has_sequential_chars(cls, password):
        """Check for sequential characters (abc, 123, qwe, etc.)"""
        sequences = [
            'abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 'hij', 'ijk', 'jkl',
            'klm', 'lmn', 'mno', 'nop', 'opq', 'pqr', 'qrs', 'rst', 'stu', 'tuv',
            'uvw', 'vwx', 'wxy', 'xyz', '123', '234', '345', '456', '567', '678',
            '789', 'qwe', 'wer', 'ert', 'rty', 'tyu', 'yui', 'uio', 'iop', 'asd',
            'sdf', 'dfg', 'fgh', 'ghj', 'hjk', 'jkl', 'zxc', 'xcv', 'cvb', 'vbn', 'bnm'
        ]
        
        password_lower = password.lower()
        for seq in sequences:
            if seq in password_lower or seq[::-1] in password_lower:
                return True
        return False

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    @classmethod
    def validate_email(cls, email):
        """Validate email format"""
        if not email:
            return False, "Email is required"
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        if len(email) > 254:
            return False, "Email address too long"
        
        return True, "Valid email"
    
    @classmethod
    def validate_name(cls, name, field_name="Name"):
        """Validate name fields"""
        if not name or not name.strip():
            return False, f"{field_name} is required"
        
        name = name.strip()
        
        if len(name) > 100:
            return False, f"{field_name} must not exceed 100 characters"
        
        # Allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            return False, f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, cls.sanitize_text(name)
    
    @classmethod
    def validate_student_code(cls, code):
        """Validate student code format"""
        if not code:
            return False, "Student code is required"
        
        # Assuming format: letters followed by numbers (e.g., ST2021001)
        if not re.match(r'^[A-Z]{2}\d{4}\d{3}$', code.upper()):
            return False, "Invalid student code format (expected: AA0000000)"
        
        return True, code.upper()
    
    @classmethod
    def sanitize_text(cls, text):
        """Sanitize text input to prevent XSS"""
        if not text:
            return ""
        
        # Remove or escape dangerous characters
        dangerous_chars = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;',
            '/': '&#x2F;'
        }
        
        sanitized = text
        for char, escape in dangerous_chars.items():
            sanitized = sanitized.replace(char, escape)
        
        return sanitized.strip()
    
    @classmethod
    def validate_file_upload(cls, file, allowed_extensions=None, max_size_mb=5):
        """Validate file uploads securely"""
        if not file or not file.filename:
            return False, "No file selected"
        
        # Secure filename
        filename = secure_filename(file.filename)
        if not filename:
            return False, "Invalid filename"
        
        # Check file extension
        allowed_extensions = allowed_extensions or {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
        if not cls._allowed_file_extension(filename, allowed_extensions):
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        
        # Check file size (if available)
        if hasattr(file, 'content_length') and file.content_length:
            max_size_bytes = max_size_mb * 1024 * 1024
            if file.content_length > max_size_bytes:
                return False, f"File too large. Maximum size: {max_size_mb}MB"
        
        # Generate secure filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = secrets.token_hex(8)
        name, ext = os.path.splitext(filename)
        secure_name = f"{name[:30]}_{timestamp}_{random_suffix}{ext}"
        
        return True, secure_name
    
    @classmethod
    def _allowed_file_extension(cls, filename, allowed_extensions):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

class SecurityAuditor:
    """Security event logging and monitoring"""
    
    @classmethod
    def log_security_event(cls, event_type, user_id=None, ip_address=None, details=None):
        """Log security-related events"""
        try:
            event_data = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'user_id': user_id,
                'ip_address': ip_address or request.remote_addr if request else None,
                'user_agent': request.headers.get('User-Agent') if request else None,
                'details': details or {}
            }
            
            security_logger.info(f"SECURITY_EVENT: {event_data}")
            
        except Exception as e:
            # Fallback logging if security logger fails
            print(f"Security logging failed: {e}")
    
    @classmethod
    def log_failed_login(cls, username, ip_address, reason):
        """Log failed login attempts"""
        cls.log_security_event(
            'FAILED_LOGIN',
            user_id=username,
            ip_address=ip_address,
            details={'reason': reason}
        )
    
    @classmethod
    def log_successful_login(cls, user_id, user_type, ip_address):
        """Log successful login"""
        cls.log_security_event(
            'SUCCESSFUL_LOGIN',
            user_id=user_id,
            ip_address=ip_address,
            details={'user_type': user_type}
        )
    
    @classmethod
    def log_permission_violation(cls, user_id, resource, action):
        """Log unauthorized access attempts"""
        cls.log_security_event(
            'PERMISSION_VIOLATION',
            user_id=user_id,
            details={'resource': resource, 'action': action}
        )

class CSRFProtection:
    """CSRF protection implementation"""
    
    @classmethod
    def generate_csrf_token(cls, user_id):
        """Generate CSRF token for user"""
        timestamp = str(int(datetime.now().timestamp()))
        data = f"{user_id}:{timestamp}:{secrets.token_hex(16)}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    @classmethod
    def validate_csrf_token(cls, token, user_id, max_age_hours=24):
        """Validate CSRF token"""
        if not token:
            return False
        
        try:
            # In production, store tokens in Redis or database
            # For now, we'll implement basic validation
            return len(token) == 32 and token.isalnum()
        except Exception:
            return False

class AccountLockout:
    """Account lockout mechanism for failed login attempts"""
    
    # In production, use Redis or database
    failed_attempts = {}
    locked_accounts = {}
    
    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    @classmethod
    def record_failed_attempt(cls, username, ip_address):
        """Record a failed login attempt"""
        key = f"{username}:{ip_address}"
        now = datetime.now()
        
        if key not in cls.failed_attempts:
            cls.failed_attempts[key] = []
        
        # Remove old attempts (older than 1 hour)
        cls.failed_attempts[key] = [
            attempt for attempt in cls.failed_attempts[key]
            if now - attempt < timedelta(hours=1)
        ]
        
        cls.failed_attempts[key].append(now)
        
        # Check if account should be locked
        if len(cls.failed_attempts[key]) >= cls.MAX_ATTEMPTS:
            cls.locked_accounts[key] = now + timedelta(minutes=cls.LOCKOUT_DURATION_MINUTES)
            SecurityAuditor.log_security_event(
                'ACCOUNT_LOCKED',
                user_id=username,
                ip_address=ip_address,
                details={'attempts': len(cls.failed_attempts[key])}
            )
            return True
        
        return False
    
    @classmethod
    def is_account_locked(cls, username, ip_address):
        """Check if account is currently locked"""
        key = f"{username}:{ip_address}"
        
        if key in cls.locked_accounts:
            if datetime.now() < cls.locked_accounts[key]:
                return True
            else:
                # Lockout expired, remove it
                del cls.locked_accounts[key]
                if key in cls.failed_attempts:
                    del cls.failed_attempts[key]
        
        return False
    
    @classmethod
    def clear_failed_attempts(cls, username, ip_address):
        """Clear failed attempts on successful login"""
        key = f"{username}:{ip_address}"
        cls.failed_attempts.pop(key, None)
        cls.locked_accounts.pop(key, None)

# Security headers middleware
def add_security_headers(response):
    """Add security headers to responses"""
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'"
    )
    
    # Other security headers
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(self), camera=(), microphone=()'
    
    # Remove server information
    response.headers.pop('Server', None)
    response.headers['Server'] = 'IntelliAttend/1.0'
    
    return response

# Rate limiting enhancements
class EnhancedRateLimiter:
    """Enhanced rate limiting with progressive delays"""
    
    # Store in Redis in production
    rate_limit_data = {}
    
    @classmethod
    def check_rate_limit(cls, key, limit, window_minutes=1):
        """Check if rate limit is exceeded"""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        if key not in cls.rate_limit_data:
            cls.rate_limit_data[key] = []
        
        # Remove old requests
        cls.rate_limit_data[key] = [
            timestamp for timestamp in cls.rate_limit_data[key]
            if timestamp > window_start
        ]
        
        # Check if limit exceeded
        if len(cls.rate_limit_data[key]) >= limit:
            return False, cls._calculate_delay(len(cls.rate_limit_data[key]) - limit)
        
        # Record this request
        cls.rate_limit_data[key].append(now)
        return True, 0
    
    @classmethod
    def _calculate_delay(cls, excess_requests):
        """Calculate progressive delay based on excess requests"""
        # Progressive delay: 2^excess seconds, max 300 seconds
        delay = min(2 ** excess_requests, 300)
        return delay

def create_secure_response(success, data=None, error=None, message=None, status_code=200):
    """Create standardized secure response"""
    response_data = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
    }
    
    if success and data:
        response_data["data"] = data
    
    if message:
        response_data["message"] = message
    
    if not success and error:
        # Sanitize error message to prevent information leakage
        if isinstance(error, str):
            response_data["error"] = InputValidator.sanitize_text(error)
        else:
            response_data["error"] = "An error occurred"
    
    response = jsonify(response_data)
    response.status_code = status_code
    
    return add_security_headers(response)

# Usage examples for integration:
"""
# In your main app.py file:

from security_enhancements import (
    PasswordValidator, InputValidator, SecurityAuditor, 
    AccountLockout, create_secure_response, add_security_headers
)

# Add security headers to all responses
@app.after_request
def after_request(response):
    return add_security_headers(response)

# Enhanced login endpoint example:
@app.route('/api/admin/login', methods=['POST'])
@limiter.limit("5 per minute")
def enhanced_admin_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        ip_address = request.remote_addr
        
        # Check account lockout
        if AccountLockout.is_account_locked(username, ip_address):
            SecurityAuditor.log_failed_login(username, ip_address, "Account locked")
            return create_secure_response(
                success=False,
                error='Account temporarily locked due to multiple failed attempts',
                status_code=423
            )
        
        # Validate input
        if not username or not password:
            SecurityAuditor.log_failed_login(username, ip_address, "Missing credentials")
            return create_secure_response(
                success=False,
                error='Username and password required',
                status_code=400
            )
        
        # Sanitize inputs
        username = InputValidator.sanitize_text(username)
        
        # Authenticate user
        admin = Admin.query.filter_by(username=username, is_active=True).first()
        
        if admin and check_password(password, admin.password_hash):
            # Clear failed attempts on success
            AccountLockout.clear_failed_attempts(username, ip_address)
            SecurityAuditor.log_successful_login(admin.admin_id, 'admin', ip_address)
            
            # Generate token and return success
            access_token = create_access_token(...)
            return create_secure_response(
                success=True,
                data={'access_token': access_token, 'admin': admin_data},
                message='Login successful'
            )
        else:
            # Record failed attempt
            is_locked = AccountLockout.record_failed_attempt(username, ip_address)
            SecurityAuditor.log_failed_login(username, ip_address, "Invalid credentials")
            
            error_msg = 'Account locked due to multiple failed attempts' if is_locked else 'Invalid credentials'
            status_code = 423 if is_locked else 401
            
            return create_secure_response(
                success=False,
                error=error_msg,
                status_code=status_code
            )
            
    except Exception as e:
        SecurityAuditor.log_security_event('LOGIN_ERROR', details={'error': str(e)})
        return create_secure_response(
            success=False,
            error='An error occurred during login',
            status_code=500
        )
"""