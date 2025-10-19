"""
Student management routes for IntelliAttend admin panel
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
student_logger = logging.getLogger(__name__)

# Student routes blueprint
student_bp = Blueprint('student', __name__, url_prefix='/api/admin/students')

@student_bp.route('', methods=['GET'])
@jwt_required()
def admin_get_students_list():
    """Get list of all students"""
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
        from app import app, db, Student
        
        with app.app_context():
            # Build query
            query = Student.query
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        getattr(Student, 'first_name').like(search_filter),
                        getattr(Student, 'last_name').like(search_filter),
                        getattr(Student, 'email').like(search_filter),
                        getattr(Student, 'student_code').like(search_filter),
                        getattr(Student, 'program').like(search_filter)
                    )
                )
            
            # Paginate results
            students_pagination = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            students_list = []
            for student in students_pagination.items:
                students_list.append({
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'phone_number': student.phone_number,
                    'program': student.program,
                    'year_of_study': student.year_of_study,
                    'is_active': student.is_active,
                    'created_at': student.created_at.isoformat() if student.created_at else None,
                    'updated_at': student.updated_at.isoformat() if student.updated_at else None
                })
            
            return jsonify({
                'success': True,
                'students': students_list,
                'pagination': {
                    'page': students_pagination.page,
                    'pages': students_pagination.pages,
                    'per_page': students_pagination.per_page,
                    'total': students_pagination.total
                }
            })
        
    except Exception as e:
        student_logger.error(f"Error getting students list: {str(e)}")
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>', methods=['GET'])
@jwt_required()
def admin_get_student(student_id):
    """Get specific student details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app, Student
        
        with app.app_context():
            student = Student.query.get(student_id)
            if not student:
                return jsonify({'error': 'Student not found'}), 404
            
            return jsonify({
                'success': True,
                'student': {
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'phone_number': student.phone_number,
                    'program': student.program,
                    'year_of_study': student.year_of_study,
                    'is_active': student.is_active,
                    'created_at': student.created_at.isoformat() if student.created_at else None,
                    'updated_at': student.updated_at.isoformat() if student.updated_at else None
                }
            })
        
    except Exception as e:
        student_logger.error(f"Error getting student {student_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@student_bp.route('', methods=['POST'])
@jwt_required()
def admin_create_student():
    """Create new student"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_code', 'first_name', 'last_name', 'email', 'program', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Import app components
        from app import app, db, Student
        
        with app.app_context():
            # Check if student code or email already exists
            existing = Student.query.filter(
                or_(
                    getattr(Student, 'student_code') == data['student_code'],
                    getattr(Student, 'email') == data['email']
                )
            ).first()
            
            if existing:
                return jsonify({'error': 'Student code or email already exists'}), 400
            
            # Create new student
            student = Student(
                student_code=data['student_code'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                program=data['program'],
                password_hash=bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                phone_number=data.get('phone_number'),
                year_of_study=data.get('year_of_study'),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(student)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Student created successfully',
                'student': {
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'program': student.program,
                    'phone_number': student.phone_number,
                    'year_of_study': student.year_of_study,
                    'is_active': student.is_active
                }
            }), 201
        
    except Exception as e:
        # Import app components
        from app import app, db
        with app.app_context():
            db.session.rollback()
        student_logger.error(f"Error creating student: {str(e)}")
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>', methods=['PUT'])
@jwt_required()
def admin_update_student(student_id):
    """Update student"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app, Student, db
        
        with app.app_context():
            student = Student.query.get(student_id)
            if not student:
                return jsonify({'error': 'Student not found'}), 404
            
            data = request.get_json()
            
            # Update fields if provided
            if 'student_code' in data and data['student_code'] != student.student_code:
                # Check if new student code already exists
                existing = Student.query.filter(
                    getattr(Student, 'student_code') == data['student_code'],
                    getattr(Student, 'student_id') != student_id
                ).first()
                if existing:
                    return jsonify({'error': 'Student code already exists'}), 400
                student.student_code = data['student_code']
            
            if 'first_name' in data:
                student.first_name = data['first_name']
            
            if 'last_name' in data:
                student.last_name = data['last_name']
            
            if 'email' in data and data['email'] != student.email:
                # Check if new email already exists
                existing = Student.query.filter(
                    getattr(Student, 'email') == data['email'],
                    Student.student_id != student_id
                ).first()
                if existing:
                    return jsonify({'error': 'Email already exists'}), 400
                student.email = data['email']
            
            if 'phone_number' in data:
                student.phone_number = data['phone_number']
            
            if 'program' in data:
                student.program = data['program']
            
            if 'year_of_study' in data:
                student.year_of_study = data['year_of_study']
            
            if 'is_active' in data:
                student.is_active = data['is_active']
            
            if 'password' in data:
                student.password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            student.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Student updated successfully',
                'student': {
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'program': student.program,
                    'phone_number': student.phone_number,
                    'year_of_study': student.year_of_study,
                    'is_active': student.is_active
                }
            })
        
    except Exception as e:
        # Import app components
        from app import app, db
        with app.app_context():
            db.session.rollback()
        student_logger.error(f"Error updating student {student_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_student_permanent(student_id):
    """Delete student"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app, Student, StudentClassEnrollment, db
        
        with app.app_context():
            student = Student.query.get(student_id)
            if not student:
                return jsonify({'error': 'Student not found'}), 404
            
            # Check if student is enrolled in any classes
            enrollments = StudentClassEnrollment.query.filter_by(student_id=student_id).count()
            if enrollments > 0:
                return jsonify({'error': 'Cannot delete student enrolled in classes'}), 400
            
            db.session.delete(student)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Student deleted successfully'
            })
        
    except Exception as e:
        # Import app components
        from app import app, db
        with app.app_context():
            db.session.rollback()
        student_logger.error(f"Error deleting student {student_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500