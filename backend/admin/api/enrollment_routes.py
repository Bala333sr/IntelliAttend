"""
Enrollment management routes for IntelliAttend admin panel
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import or_
from datetime import datetime
import logging
import sys
import os

# Add backend path to sys.path
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Configure logging
enrollment_logger = logging.getLogger(__name__)

# Enrollment routes blueprint
enrollment_bp = Blueprint('enrollment', __name__, url_prefix='/api/admin/enrollments')

@enrollment_bp.route('', methods=['POST'])
@jwt_required()
def admin_create_enrollment():
    """Create a new student enrollment"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import db, StudentClassEnrollment, Student, Classes
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_id', 'class_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if student and class exist
        student = Student.query.get(data['student_id'])
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        class_obj = Classes.query.get(data['class_id'])
        if not class_obj:
            return jsonify({'error': 'Class not found'}), 404
        
        # Check if enrollment already exists
        existing_enrollment = StudentClassEnrollment.query.filter_by(
            student_id=data['student_id'],
            class_id=data['class_id']
        ).first()
        
        if existing_enrollment:
            return jsonify({'error': 'Student already enrolled in this class'}), 400
        
        # Create new enrollment
        enrollment = StudentClassEnrollment(
            student_id=data['student_id'],
            class_id=data['class_id'],
            status=data.get('status', 'enrolled'),
            final_grade=data.get('final_grade'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        # Get related data for response
        student = Student.query.get(enrollment.student_id)
        class_obj = Classes.query.get(enrollment.class_id)
        
        return jsonify({
            'success': True,
            'message': 'Student enrolled successfully',
            'enrollment': {
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'student_name': f"{student.first_name} {student.last_name}" if student else None,
                'student_code': student.student_code if student else None,
                'class_id': enrollment.class_id,
                'class_name': class_obj.class_name if class_obj else None,
                'class_code': class_obj.class_code if class_obj else None,
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None,
                'created_at': enrollment.created_at.isoformat() if enrollment.created_at else None
            }
        }), 201
        
    except Exception as e:
        # Import app components
        from app import db
        db.session.rollback()
        enrollment_logger.error(f"Error creating enrollment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enrollment_bp.route('/<int:enrollment_id>', methods=['GET'])
@jwt_required()
def admin_get_enrollment(enrollment_id):
    """Get specific enrollment details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import db, StudentClassEnrollment, Student, Classes
        
        # Get enrollment with related data
        enrollment_data = db.session.query(StudentClassEnrollment, Student, Classes).join(
            Student, StudentClassEnrollment.student_id == Student.student_id
        ).join(
            Classes, StudentClassEnrollment.class_id == Classes.class_id
        ).filter(StudentClassEnrollment.enrollment_id == enrollment_id).first()
        
        if not enrollment_data:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        enrollment, student, class_obj = enrollment_data
        
        return jsonify({
            'success': True,
            'enrollment': {
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code,
                'student_email': student.email,
                'class_id': enrollment.class_id,
                'class_name': class_obj.class_name,
                'class_code': class_obj.class_code,
                'faculty_id': class_obj.faculty_id,
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None,
                'created_at': enrollment.created_at.isoformat() if enrollment.created_at else None,
                'updated_at': enrollment.updated_at.isoformat() if enrollment.updated_at else None
            }
        })
        
    except Exception as e:
        enrollment_logger.error(f"Error getting enrollment {enrollment_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enrollment_bp.route('', methods=['GET'])
@jwt_required()
def admin_get_enrollments_list():
    """Get list of all student enrollments"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import db, StudentClassEnrollment, Student, Classes
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get filter parameters
        student_id = request.args.get('student_id', type=int)
        class_id = request.args.get('class_id', type=int)
        status = request.args.get('status', '')
        
        # Build query with joins to get related data
        query = db.session.query(StudentClassEnrollment, Student, Classes).join(
            Student, StudentClassEnrollment.student_id == Student.student_id
        ).join(
            Classes, StudentClassEnrollment.class_id == Classes.class_id
        )
        
        # Apply filters
        if student_id:
            query = query.filter(StudentClassEnrollment.student_id == student_id)
        
        if class_id:
            query = query.filter(StudentClassEnrollment.class_id == class_id)
        
        if status:
            query = query.filter(StudentClassEnrollment.status == status)
        
        # Order by enrollment date descending
        query = query.order_by(StudentClassEnrollment.enrollment_date.desc())
        
        # Execute query and manually paginate
        total_count = query.count()
        offset = (page - 1) * per_page
        enrollments_items = query.offset(offset).limit(per_page).all()
        
        # Calculate pagination details
        total_pages = (total_count + per_page - 1) // per_page
        
        enrollments_list = []
        for enrollment, student, class_obj in enrollments_items:
            enrollments_list.append({
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code,
                'class_id': enrollment.class_id,
                'class_name': class_obj.class_name,
                'class_code': class_obj.class_code,
                'faculty_id': class_obj.faculty_id,
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None
            })
        
        return jsonify({
            'success': True,
            'enrollments': enrollments_list,
            'pagination': {
                'page': page,
                'pages': total_pages,
                'per_page': per_page,
                'total': total_count
            }
        })
        
    except Exception as e:
        enrollment_logger.error(f"Error getting enrollments list: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enrollment_bp.route('/<int:enrollment_id>', methods=['PUT'])
@jwt_required()
def admin_update_enrollment(enrollment_id):
    """Update student enrollment"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        enrollment = StudentClassEnrollment.query.get(enrollment_id)
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'status' in data:
            enrollment.status = data['status']
        
        if 'final_grade' in data:
            enrollment.final_grade = data['final_grade']
        
        if 'is_active' in data:
            enrollment.is_active = data['is_active']
        
        enrollment.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Get related data for response
        student = Student.query.get(enrollment.student_id)
        class_obj = Classes.query.get(enrollment.class_id)
        
        return jsonify({
            'success': True,
            'message': 'Enrollment updated successfully',
            'enrollment': {
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'student_name': f"{student.first_name} {student.last_name}" if student else None,
                'student_code': student.student_code if student else None,
                'class_id': enrollment.class_id,
                'class_name': class_obj.class_name if class_obj else None,
                'class_code': class_obj.class_code if class_obj else None,
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None,
                'updated_at': enrollment.updated_at.isoformat() if enrollment.updated_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        enrollment_logger.error(f"Error updating enrollment {enrollment_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enrollment_bp.route('/<int:enrollment_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_enrollment(enrollment_id):
    """Delete student enrollment"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        enrollment = StudentClassEnrollment.query.get(enrollment_id)
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        db.session.delete(enrollment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Enrollment deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        enrollment_logger.error(f"Error deleting enrollment {enrollment_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enrollment_bp.route('/students/<int:student_id>/enrollments', methods=['GET'])
@jwt_required()
def admin_get_student_enrollments(student_id):
    """Get all enrollments for a specific student"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Check if student exists
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get enrollments with related data
        enrollments_data = db.session.query(StudentClassEnrollment, Classes, Faculty).join(
            Classes, StudentClassEnrollment.class_id == Classes.class_id
        ).join(
            Faculty, Classes.faculty_id == Faculty.faculty_id
        ).filter(StudentClassEnrollment.student_id == student_id).all()
        
        enrollments_list = []
        for enrollment, class_obj, faculty in enrollments_data:
            enrollments_list.append({
                'enrollment_id': enrollment.enrollment_id,
                'class_id': enrollment.class_id,
                'class_name': class_obj.class_name,
                'class_code': class_obj.class_code,
                'faculty_name': f"{faculty.first_name} {faculty.last_name}",
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None
            })
        
        return jsonify({
            'success': True,
            'student': {
                'student_id': student.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code
            },
            'enrollments': enrollments_list
        })
        
    except Exception as e:
        enrollment_logger.error(f"Error getting student {student_id} enrollments: {str(e)}")
        return jsonify({'error': str(e)}), 500

@enrollment_bp.route('/classes/<int:class_id>/enrollments', methods=['GET'])
@jwt_required()
def admin_get_class_enrollments(class_id):
    """Get all enrollments for a specific class"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Check if class exists
        class_obj = Classes.query.get(class_id)
        if not class_obj:
            return jsonify({'error': 'Class not found'}), 404
        
        # Get enrollments with related data
        enrollments_data = db.session.query(StudentClassEnrollment, Student).join(
            Student, StudentClassEnrollment.student_id == Student.student_id
        ).filter(StudentClassEnrollment.class_id == class_id).all()
        
        enrollments_list = []
        for enrollment, student in enrollments_data:
            enrollments_list.append({
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code,
                'student_email': student.email,
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None
            })
        
        return jsonify({
            'success': True,
            'class': {
                'class_id': class_obj.class_id,
                'class_name': class_obj.class_name,
                'class_code': class_obj.class_code
            },
            'enrollments': enrollments_list
        })
        
    except Exception as e:
        enrollment_logger.error(f"Error getting class {class_id} enrollments: {str(e)}")
        return jsonify({'error': str(e)}), 500