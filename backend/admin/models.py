"""
Admin models for IntelliAttend
Contains admin-specific data models and utility functions
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import bcrypt
import logging

# Configure logging
admin_models_logger = logging.getLogger(__name__)

# This file is intentionally left mostly empty as we're using the models from app.py
# This helps avoid circular imports by providing a clean interface

def get_admin_by_username(db, Admin, username):
    """Get admin by username"""
    try:
        return Admin.query.filter_by(username=username, is_active=True).first()
    except Exception as e:
        admin_models_logger.error(f"Error getting admin by username: {str(e)}")
        return None

def verify_admin_password(admin, password, check_password_func):
    """Verify admin password"""
    try:
        return check_password_func(password, admin.password_hash)
    except Exception as e:
        admin_models_logger.error(f"Error verifying admin password: {str(e)}")
        return False

def update_admin_last_login(db, admin):
    """Update admin last login timestamp"""
    try:
        from datetime import datetime
        admin.last_login = datetime.utcnow()
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        admin_models_logger.error(f"Error updating admin last login: {str(e)}")
        return False