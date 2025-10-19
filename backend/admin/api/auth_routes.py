"""
Admin authentication routes for IntelliAttend admin panel
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, create_access_token
from datetime import datetime
import bcrypt
import logging
import sys
import os

# Add backend path to sys.path
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Import models and components from app.py
# We'll import db within functions to avoid SQLAlchemy instance issues

# Configure logging
auth_logger = logging.getLogger(__name__)

# Auth routes blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/admin/auth')

@auth_bp.route('/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Import app components
        from app import app, Admin, check_password
        
        with app.app_context():
            admin = Admin.query.filter_by(username=username, is_active=True).first()
        
        if admin and check_password(password, admin.password_hash):
            # Import app components
            from app import app, db
            
            with app.app_context():
                # Update last login
                admin.last_login = datetime.utcnow()
                db.session.commit()
            
            with app.app_context():
                access_token = create_access_token(
                    identity=str(admin.admin_id),
                    additional_claims={'type': 'admin', 'admin_id': admin.admin_id, 'role': admin.role}
                )
            
            return jsonify({
                'success': True,
                'access_token': access_token,
                'admin': {
                    'admin_id': admin.admin_id,
                    'username': admin.username,
                    'email': admin.email,
                    'name': f"{admin.first_name} {admin.last_name}",
                    'role': admin.role
                }
            })
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        # Import app components
        from app import app, db
        with app.app_context():
            db.session.rollback()
        auth_logger.error(f"Error during admin login: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def admin_logout():
    """Admin logout endpoint"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        # Import app components
        from app import jwt_blacklist, jwt_blacklist_lock
        
        # Add token to blacklist for secure logout
        jti = claims['jti']
        with jwt_blacklist_lock:
            jwt_blacklist.add(jti)
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        auth_logger.error(f"Error during admin logout: {str(e)}")
        return jsonify({'error': str(e)}), 500