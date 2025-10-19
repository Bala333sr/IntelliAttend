"""
Admin APIs for Faculty Management
Handles CRUD operations for faculty members
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from models import Users, Faculty, Classrooms
from werkzeug.security import generate_password_hash
from utils.audit_helpers import log_registration_action
import re

admin_faculty_bp = Blueprint('admin_faculty', __name__, url_prefix='/api/admin/faculty')


def require_admin_role():
    """Verify that the current user is an admin"""
    user_id = get_jwt_identity()
    user = Users.query.get(user_id)
    
    if not user or user.role != 'admin':
        return jsonify({
            'success': False,
            'error': 'Admin access required'
        }), 403
    
    return None


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number format (10 digits)"""
    if not phone:
        return True  # Phone is optional
    pattern = r'^\d{10}$'
    return re.match(pattern, phone) is not None


# ==================== CREATE FACULTY ====================

@admin_faculty_bp.route('', methods=['POST'])
@jwt_required()
def create_faculty():
    """
    Create a new faculty member
    
    Request body:
        - faculty_code (required): unique faculty identifier
        - email (required): must be unique
        - first_name (required)
        - last_name (required)
        - password (required): will be hashed
        - department (optional)
        - phone (optional): 10 digit number
        - designation (optional): e.g., Professor, Assistant Professor
    """
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    admin_id = get_jwt_identity()
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': 'Request body is required'
        }), 400
    
    # Required fields
    required_fields = ['faculty_code', 'email', 'first_name', 'last_name', 'password']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400
    
    faculty_code = data['faculty_code'].strip()
    email = data['email'].strip().lower()
    first_name = data['first_name'].strip()
    last_name = data['last_name'].strip()
    password = data['password']
    department = data.get('department', '').strip()
    phone = data.get('phone', '').strip()
    designation = data.get('designation', '').strip()
    
    # Validate email format
    if not validate_email(email):
        return jsonify({
            'success': False,
            'error': 'Invalid email format'
        }), 400
    
    # Validate phone if provided
    if phone and not validate_phone(phone):
        return jsonify({
            'success': False,
            'error': 'Invalid phone number format. Must be 10 digits.'
        }), 400
    
    # Check if faculty_code already exists
    existing_faculty = Faculty.query.filter_by(faculty_code=faculty_code).first()
    if existing_faculty:
        return jsonify({
            'success': False,
            'error': f'Faculty with code {faculty_code} already exists'
        }), 409
    
    # Check if email already exists
    existing_user = Users.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({
            'success': False,
            'error': f'Email {email} is already registered'
        }), 409
    
    try:
        # Create user account
        user = Users(
            email=email,
            password_hash=generate_password_hash(password),
            role='faculty',
            is_active=True
        )
        db.session.add(user)
        db.session.flush()
        
        # Create faculty record
        faculty = Faculty(
            user_id=user.user_id,
            faculty_code=faculty_code,
            first_name=first_name,
            last_name=last_name,
            email=email,
            department=department if department else None,
            phone=phone if phone else None,
            designation=designation if designation else None
        )
        db.session.add(faculty)
        db.session.flush()
        
        # Log action
        log_registration_action(
            admin_id=admin_id,
            action='faculty_created',
            entity_type='faculty',
            entity_id=faculty.faculty_id,
            entity_code=faculty_code,
            details={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'department': department
            }
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Faculty member created successfully',
            'faculty': {
                'faculty_id': faculty.faculty_id,
                'faculty_code': faculty.faculty_code,
                'first_name': faculty.first_name,
                'last_name': faculty.last_name,
                'email': faculty.email,
                'department': faculty.department,
                'phone': faculty.phone,
                'designation': faculty.designation,
                'user_id': user.user_id,
                'created_at': faculty.created_at.isoformat()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to create faculty: {str(e)}'
        }), 500


# ==================== GET FACULTY ====================

@admin_faculty_bp.route('', methods=['GET'])
@jwt_required()
def get_all_faculty():
    """
    Get all faculty members with pagination and filtering
    
    Query params:
        - page: page number (default: 1)
        - per_page: items per page (default: 20)
        - department: filter by department
        - search: search in name, email, or faculty_code
        - is_active: filter by active status (true/false)
    """
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    # Query parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    department = request.args.get('department')
    search = request.args.get('search')
    is_active = request.args.get('is_active')
    
    # Build query with join to Users table
    query = db.session.query(Faculty, Users).join(
        Users, Faculty.user_id == Users.user_id
    )
    
    # Apply filters
    if department:
        query = query.filter(Faculty.department.ilike(f'%{department}%'))
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Faculty.first_name.ilike(search_term),
                Faculty.last_name.ilike(search_term),
                Faculty.email.ilike(search_term),
                Faculty.faculty_code.ilike(search_term)
            )
        )
    
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        query = query.filter(Users.is_active == is_active_bool)
    
    # Order by created_at descending
    query = query.order_by(Faculty.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Format results
    results = []
    for faculty, user in pagination.items:
        # Get assigned classrooms count
        classrooms_count = Classrooms.query.filter_by(faculty_id=faculty.faculty_id).count()
        
        results.append({
            'faculty_id': faculty.faculty_id,
            'faculty_code': faculty.faculty_code,
            'first_name': faculty.first_name,
            'last_name': faculty.last_name,
            'email': faculty.email,
            'department': faculty.department,
            'phone': faculty.phone,
            'designation': faculty.designation,
            'is_active': user.is_active,
            'classrooms_count': classrooms_count,
            'created_at': faculty.created_at.isoformat(),
            'updated_at': faculty.updated_at.isoformat() if faculty.updated_at else None
        })
    
    return jsonify({
        'success': True,
        'faculty': results,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@admin_faculty_bp.route('/<string:faculty_code>', methods=['GET'])
@jwt_required()
def get_faculty_by_code(faculty_code):
    """Get detailed information about a specific faculty member"""
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    faculty = Faculty.query.filter_by(faculty_code=faculty_code).first()
    if not faculty:
        return jsonify({
            'success': False,
            'error': 'Faculty not found'
        }), 404
    
    user = Users.query.get(faculty.user_id)
    
    # Get assigned classrooms
    classrooms = Classrooms.query.filter_by(faculty_id=faculty.faculty_id).all()
    
    return jsonify({
        'success': True,
        'faculty': {
            'faculty_id': faculty.faculty_id,
            'faculty_code': faculty.faculty_code,
            'first_name': faculty.first_name,
            'last_name': faculty.last_name,
            'email': faculty.email,
            'department': faculty.department,
            'phone': faculty.phone,
            'designation': faculty.designation,
            'is_active': user.is_active if user else False,
            'created_at': faculty.created_at.isoformat(),
            'updated_at': faculty.updated_at.isoformat() if faculty.updated_at else None,
            'classrooms': [{
                'classroom_id': classroom.classroom_id,
                'classroom_code': classroom.classroom_code,
                'classroom_name': classroom.classroom_name,
                'building': classroom.building,
                'room_number': classroom.room_number
            } for classroom in classrooms]
        }
    }), 200


# ==================== UPDATE FACULTY ====================

@admin_faculty_bp.route('/<string:faculty_code>', methods=['PUT'])
@jwt_required()
def update_faculty(faculty_code):
    """
    Update faculty member information
    
    Request body (all fields optional):
        - first_name
        - last_name
        - email
        - department
        - phone
        - designation
        - is_active
        - password (if provided, will be hashed and updated)
    """
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    admin_id = get_jwt_identity()
    
    faculty = Faculty.query.filter_by(faculty_code=faculty_code).first()
    if not faculty:
        return jsonify({
            'success': False,
            'error': 'Faculty not found'
        }), 404
    
    user = Users.query.get(faculty.user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': 'User account not found'
        }), 404
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': 'Request body is required'
        }), 400
    
    changes = {}
    
    # Update first_name
    if 'first_name' in data and data['first_name']:
        new_value = data['first_name'].strip()
        if new_value != faculty.first_name:
            changes['first_name'] = {'old': faculty.first_name, 'new': new_value}
            faculty.first_name = new_value
    
    # Update last_name
    if 'last_name' in data and data['last_name']:
        new_value = data['last_name'].strip()
        if new_value != faculty.last_name:
            changes['last_name'] = {'old': faculty.last_name, 'new': new_value}
            faculty.last_name = new_value
    
    # Update email
    if 'email' in data and data['email']:
        new_email = data['email'].strip().lower()
        if not validate_email(new_email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        if new_email != faculty.email:
            # Check if new email is already taken
            existing = Users.query.filter(
                Users.email == new_email,
                Users.user_id != user.user_id
            ).first()
            
            if existing:
                return jsonify({
                    'success': False,
                    'error': f'Email {new_email} is already registered'
                }), 409
            
            changes['email'] = {'old': faculty.email, 'new': new_email}
            faculty.email = new_email
            user.email = new_email
    
    # Update department
    if 'department' in data:
        new_value = data['department'].strip() if data['department'] else None
        if new_value != faculty.department:
            changes['department'] = {'old': faculty.department, 'new': new_value}
            faculty.department = new_value
    
    # Update phone
    if 'phone' in data:
        new_phone = data['phone'].strip() if data['phone'] else None
        if new_phone and not validate_phone(new_phone):
            return jsonify({
                'success': False,
                'error': 'Invalid phone number format. Must be 10 digits.'
            }), 400
        
        if new_phone != faculty.phone:
            changes['phone'] = {'old': faculty.phone, 'new': new_phone}
            faculty.phone = new_phone
    
    # Update designation
    if 'designation' in data:
        new_value = data['designation'].strip() if data['designation'] else None
        if new_value != faculty.designation:
            changes['designation'] = {'old': faculty.designation, 'new': new_value}
            faculty.designation = new_value
    
    # Update is_active
    if 'is_active' in data:
        new_value = bool(data['is_active'])
        if new_value != user.is_active:
            changes['is_active'] = {'old': user.is_active, 'new': new_value}
            user.is_active = new_value
    
    # Update password if provided
    if 'password' in data and data['password']:
        user.password_hash = generate_password_hash(data['password'])
        changes['password'] = 'updated'
    
    if not changes:
        return jsonify({
            'success': True,
            'message': 'No changes detected',
            'faculty': {
                'faculty_id': faculty.faculty_id,
                'faculty_code': faculty.faculty_code,
                'first_name': faculty.first_name,
                'last_name': faculty.last_name,
                'email': faculty.email
            }
        }), 200
    
    try:
        faculty.updated_at = datetime.utcnow()
        
        # Log action
        log_registration_action(
            admin_id=admin_id,
            action='faculty_updated',
            entity_type='faculty',
            entity_id=faculty.faculty_id,
            entity_code=faculty_code,
            details={'changes': changes}
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Faculty member updated successfully',
            'faculty': {
                'faculty_id': faculty.faculty_id,
                'faculty_code': faculty.faculty_code,
                'first_name': faculty.first_name,
                'last_name': faculty.last_name,
                'email': faculty.email,
                'department': faculty.department,
                'phone': faculty.phone,
                'designation': faculty.designation,
                'is_active': user.is_active,
                'updated_at': faculty.updated_at.isoformat()
            },
            'changes': changes
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to update faculty: {str(e)}'
        }), 500


# ==================== DELETE FACULTY ====================

@admin_faculty_bp.route('/<string:faculty_code>', methods=['DELETE'])
@jwt_required()
def delete_faculty(faculty_code):
    """
    Delete a faculty member (soft delete by deactivating the account)
    
    Note: This performs a soft delete by setting is_active to False.
    To permanently delete, use ?permanent=true (use with caution)
    """
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    admin_id = get_jwt_identity()
    permanent = request.args.get('permanent', 'false').lower() == 'true'
    
    faculty = Faculty.query.filter_by(faculty_code=faculty_code).first()
    if not faculty:
        return jsonify({
            'success': False,
            'error': 'Faculty not found'
        }), 404
    
    user = Users.query.get(faculty.user_id)
    
    # Check if faculty has assigned classrooms
    classrooms_count = Classrooms.query.filter_by(faculty_id=faculty.faculty_id).count()
    
    if classrooms_count > 0 and permanent:
        return jsonify({
            'success': False,
            'error': f'Cannot permanently delete faculty with {classrooms_count} assigned classroom(s). Please reassign or remove classrooms first.'
        }), 400
    
    try:
        if permanent:
            # Permanent deletion
            db.session.delete(faculty)
            if user:
                db.session.delete(user)
            
            log_registration_action(
                admin_id=admin_id,
                action='faculty_deleted_permanent',
                entity_type='faculty',
                entity_id=faculty.faculty_id,
                entity_code=faculty_code,
                details={
                    'name': f'{faculty.first_name} {faculty.last_name}',
                    'email': faculty.email
                }
            )
            
            message = 'Faculty member permanently deleted'
        else:
            # Soft delete (deactivate)
            if user:
                user.is_active = False
            
            log_registration_action(
                admin_id=admin_id,
                action='faculty_deactivated',
                entity_type='faculty',
                entity_id=faculty.faculty_id,
                entity_code=faculty_code,
                details={
                    'name': f'{faculty.first_name} {faculty.last_name}',
                    'email': faculty.email,
                    'classrooms_count': classrooms_count
                }
            )
            
            message = 'Faculty member deactivated successfully'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'faculty_code': faculty_code
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to delete faculty: {str(e)}'
        }), 500


# ==================== BULK OPERATIONS ====================

@admin_faculty_bp.route('/bulk/activate', methods=['POST'])
@jwt_required()
def bulk_activate_faculty():
    """
    Activate multiple faculty members
    
    Request body:
        - faculty_codes: list of faculty codes to activate
    """
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    admin_id = get_jwt_identity()
    
    data = request.get_json()
    if not data or not data.get('faculty_codes'):
        return jsonify({
            'success': False,
            'error': 'faculty_codes list is required'
        }), 400
    
    faculty_codes = data['faculty_codes']
    
    try:
        # Get all faculty and their users
        faculty_list = Faculty.query.filter(Faculty.faculty_code.in_(faculty_codes)).all()
        
        if not faculty_list:
            return jsonify({
                'success': False,
                'error': 'No faculty found with the provided codes'
            }), 404
        
        activated_count = 0
        for faculty in faculty_list:
            user = Users.query.get(faculty.user_id)
            if user and not user.is_active:
                user.is_active = True
                activated_count += 1
        
        # Log action
        log_registration_action(
            admin_id=admin_id,
            action='faculty_bulk_activated',
            entity_type='faculty',
            entity_id=None,
            entity_code=None,
            details={
                'count': activated_count,
                'faculty_codes': faculty_codes
            }
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{activated_count} faculty member(s) activated successfully',
            'activated_count': activated_count,
            'total_requested': len(faculty_codes)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to activate faculty: {str(e)}'
        }), 500


@admin_faculty_bp.route('/bulk/deactivate', methods=['POST'])
@jwt_required()
def bulk_deactivate_faculty():
    """
    Deactivate multiple faculty members
    
    Request body:
        - faculty_codes: list of faculty codes to deactivate
    """
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    admin_id = get_jwt_identity()
    
    data = request.get_json()
    if not data or not data.get('faculty_codes'):
        return jsonify({
            'success': False,
            'error': 'faculty_codes list is required'
        }), 400
    
    faculty_codes = data['faculty_codes']
    
    try:
        # Get all faculty and their users
        faculty_list = Faculty.query.filter(Faculty.faculty_code.in_(faculty_codes)).all()
        
        if not faculty_list:
            return jsonify({
                'success': False,
                'error': 'No faculty found with the provided codes'
            }), 404
        
        deactivated_count = 0
        for faculty in faculty_list:
            user = Users.query.get(faculty.user_id)
            if user and user.is_active:
                user.is_active = False
                deactivated_count += 1
        
        # Log action
        log_registration_action(
            admin_id=admin_id,
            action='faculty_bulk_deactivated',
            entity_type='faculty',
            entity_id=None,
            entity_code=None,
            details={
                'count': deactivated_count,
                'faculty_codes': faculty_codes
            }
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{deactivated_count} faculty member(s) deactivated successfully',
            'deactivated_count': deactivated_count,
            'total_requested': len(faculty_codes)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to deactivate faculty: {str(e)}'
        }), 500
