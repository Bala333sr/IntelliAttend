"""
Faculty management routes for IntelliAttend admin panel
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import or_
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
# We'll import these within functions to avoid circular imports

# Configure logging
faculty_logger = logging.getLogger(__name__)

# Faculty routes blueprint
faculty_bp = Blueprint('faculty', __name__, url_prefix='/api/admin/faculty')

@faculty_bp.route('', methods=['GET'])
@jwt_required()
def admin_get_faculty_list():
    """Get list of all faculty members"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get search parameter
        search = request.args.get('search', '')
        
        # Import app components
        from app import app, db, Faculty
        
        with app.app_context():
            # Build query
            query = db.session.query(Faculty)
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        getattr(Faculty, 'first_name').like(search_filter),
                        getattr(Faculty, 'last_name').like(search_filter),
                        getattr(Faculty, 'email').like(search_filter),
                        getattr(Faculty, 'faculty_code').like(search_filter)
                    )
                )
            
            # Execute query and manually paginate
            total_count = query.count()
            offset = (page - 1) * per_page
            faculty_items = query.offset(offset).limit(per_page).all()
            
            faculty_list = []
            for faculty in faculty_items:
                faculty_list.append({
                    'faculty_id': faculty.faculty_id,
                    'faculty_code': faculty.faculty_code,
                    'first_name': faculty.first_name,
                    'last_name': faculty.last_name,
                    'email': faculty.email,
                    'phone_number': faculty.phone_number,
                    'department': faculty.department,
                    'is_active': faculty.is_active,
                    'created_at': faculty.created_at.isoformat() if faculty.created_at else None,
                    'updated_at': faculty.updated_at.isoformat() if faculty.updated_at else None
                })
            
            # Calculate pagination details
            total_pages = (total_count + per_page - 1) // per_page
            
            return jsonify({
                'success': True,
                'faculty': faculty_list,
                'pagination': {
                    'page': page,
                    'pages': total_pages,
                    'per_page': per_page,
                    'total': total_count
                }
            })
        
    except Exception as e:
        faculty_logger.error(f"Error getting faculty list: {str(e)}")
        return jsonify({'error': str(e)}), 500

@faculty_bp.route('/<int:faculty_id>', methods=['GET'])
@jwt_required()
def admin_get_faculty(faculty_id):
    """Get specific faculty member details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app, Faculty
        
        with app.app_context():
            faculty = Faculty.query.get(faculty_id)
            if not faculty:
                return jsonify({'error': 'Faculty not found'}), 404
            
            return jsonify({
                'success': True,
                'faculty': {
                    'faculty_id': faculty.faculty_id,
                    'faculty_code': faculty.faculty_code,
                    'first_name': faculty.first_name,
                    'last_name': faculty.last_name,
                    'email': faculty.email,
                    'phone_number': faculty.phone_number,
                    'department': faculty.department,
                    'is_active': faculty.is_active,
                    'created_at': faculty.created_at.isoformat() if faculty.created_at else None,
                    'updated_at': faculty.updated_at.isoformat() if faculty.updated_at else None
                }
            })
        
    except Exception as e:
        faculty_logger.error(f"Error getting faculty {faculty_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@faculty_bp.route('', methods=['POST'])
@jwt_required()
def admin_create_faculty():
    """Create new faculty member"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['faculty_code', 'first_name', 'last_name', 'email', 'phone_number', 'department', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Import app components
        from app import app, db, Faculty
        
        with app.app_context():
            # Check if faculty code or email already exists
            existing = db.session.query(Faculty).filter(
                or_(
                    getattr(Faculty, 'faculty_code') == data['faculty_code'],
                    getattr(Faculty, 'email') == data['email']
                )
            ).first()
            
            if existing:
                return jsonify({'error': 'Faculty code or email already exists'}), 400
            
            # Create new faculty
            faculty = Faculty(
                faculty_code=data['faculty_code'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone_number=data['phone_number'],
                department=data['department'],
                password_hash=bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(faculty)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Faculty created successfully',
                'faculty': {
                    'faculty_id': faculty.faculty_id,
                    'faculty_code': faculty.faculty_code,
                    'first_name': faculty.first_name,
                    'last_name': faculty.last_name,
                    'email': faculty.email,
                    'phone_number': faculty.phone_number,
                    'department': faculty.department,
                    'is_active': faculty.is_active
                }
            }), 201
        
    except Exception as e:
        # Import app components
        from app import app, db
        with app.app_context():
            db.session.rollback()
        faculty_logger.error(f"Error creating faculty: {str(e)}")
        return jsonify({'error': str(e)}), 500

@faculty_bp.route('/<int:faculty_id>', methods=['PUT'])
@jwt_required()
def admin_update_faculty(faculty_id):
    """Update faculty member"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app, Faculty, db
        
        with app.app_context():
            faculty = Faculty.query.get(faculty_id)
            if not faculty:
                return jsonify({'error': 'Faculty not found'}), 404
            
            data = request.get_json()
            
            # Update fields if provided
            if 'faculty_code' in data and data['faculty_code'] != faculty.faculty_code:
                # Check if faculty code or email already exists
                existing = db.session.query(Faculty).filter(
                    or_(
                        getattr(Faculty, 'faculty_code') == data['faculty_code'],
                        getattr(Faculty, 'email') == data['email']
                    )
                ).first()
                if existing:
                    return jsonify({'error': 'Faculty code already exists'}), 400
                faculty.faculty_code = data['faculty_code']
            
            if 'first_name' in data:
                faculty.first_name = data['first_name']
            
            if 'last_name' in data:
                faculty.last_name = data['last_name']
            
            if 'email' in data and data['email'] != faculty.email:
                # Check if new email already exists
                existing = db.session.query(Faculty).filter(
                    getattr(Faculty, 'email') == data['email'],
                    Faculty.faculty_id != faculty_id
                ).first()
                if existing:
                    return jsonify({'error': 'Email already exists'}), 400
                faculty.email = data['email']
            
            if 'phone_number' in data:
                faculty.phone_number = data['phone_number']
            
            if 'department' in data:
                faculty.department = data['department']
            
            if 'is_active' in data:
                faculty.is_active = data['is_active']
            
            if 'password' in data:
                faculty.password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            faculty.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Faculty updated successfully',
                'faculty': {
                    'faculty_id': faculty.faculty_id,
                    'faculty_code': faculty.faculty_code,
                    'first_name': faculty.first_name,
                    'last_name': faculty.last_name,
                    'email': faculty.email,
                    'phone_number': faculty.phone_number,
                    'department': faculty.department,
                    'is_active': faculty.is_active
                }
            })
        
    except Exception as e:
        # Import app components
        from app import app, db
        with app.app_context():
            db.session.rollback()
        faculty_logger.error(f"Error updating faculty {faculty_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@faculty_bp.route('/<int:faculty_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_faculty(faculty_id):
    """Delete faculty member"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app, Faculty, Classes, db
        
        with app.app_context():
            faculty = Faculty.query.get(faculty_id)
            if not faculty:
                return jsonify({'error': 'Faculty not found'}), 404
            
            # Check if faculty has any classes
            classes = Classes.query.filter_by(faculty_id=faculty_id).count()
            if classes > 0:
                return jsonify({'error': 'Cannot delete faculty with associated classes'}), 400
            
            db.session.delete(faculty)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Faculty deleted successfully'
            })
        
    except Exception as e:
        # Import app components
        from app import app, db
        with app.app_context():
            db.session.rollback()
        faculty_logger.error(f"Error deleting faculty {faculty_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500