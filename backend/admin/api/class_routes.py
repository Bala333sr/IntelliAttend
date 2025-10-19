"""
Class management routes for IntelliAttend admin panel
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
class_logger = logging.getLogger(__name__)

# Class routes blueprint
class_bp = Blueprint('class', __name__, url_prefix='/api/admin/classes')

@class_bp.route('', methods=['GET'])
@jwt_required()
def admin_get_classes_list():
    """Get list of all classes"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app
        
        with app.app_context():
            # Import app components within app context
            from app import db, Classes, Faculty, Classroom
            
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # Get search parameter
            search = request.args.get('search', '')
            
            # Build query with joins to get related data
            query = db.session.query(Classes, Faculty, Classroom).outerjoin(
                Faculty, Classes.faculty_id == Faculty.faculty_id
            ).outerjoin(
                Classroom, Classes.classroom_id == Classroom.classroom_id
            )
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        Classes.class_code.like(search_filter),
                        Classes.class_name.like(search_filter),
                        Faculty.first_name.like(search_filter),
                        Faculty.last_name.like(search_filter),
                        Classroom.room_number.like(search_filter)
                    )
                )
            
            # Paginate results
            # Execute query and manually paginate
            total_count = query.count()
            offset = (page - 1) * per_page
            classes_items = query.offset(offset).limit(per_page).all()
            
            # Calculate pagination details
            total_pages = (total_count + per_page - 1) // per_page
            
            classes_list = []
            for class_obj, faculty, classroom in classes_items:
                classes_list.append({
                    'class_id': class_obj.class_id,
                    'class_code': class_obj.class_code,
                    'class_name': class_obj.class_name,
                    'faculty_id': class_obj.faculty_id,
                    'faculty_name': f"{faculty.first_name} {faculty.last_name}" if faculty else None,
                    'classroom_id': class_obj.classroom_id,
                    'room_number': classroom.room_number if classroom else None,
                    'semester': class_obj.semester,
                    'academic_year': class_obj.academic_year,
                    'credits': class_obj.credits,
                    'max_students': class_obj.max_students,
                    'created_at': class_obj.created_at.isoformat() if class_obj.created_at else None,
                    'updated_at': class_obj.updated_at.isoformat() if class_obj.updated_at else None
                })
            
            return jsonify({
                'success': True,
                'classes': classes_list,
                'pagination': {
                    'page': page,
                    'pages': total_pages,
                    'per_page': per_page,
                    'total': total_count
                }
            })
        
    except Exception as e:
        class_logger.error(f"Error getting classes list: {str(e)}")
        return jsonify({'error': str(e)}), 500

@class_bp.route('/<int:class_id>', methods=['GET'])
@jwt_required()
def admin_get_class_summary(class_id):
    """Get specific class details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app
        
        with app.app_context():
            # Import app components within app context
            from app import db, Classes, Faculty, Classroom
            
            # Get class with related data
            class_data = db.session.query(Classes, Faculty, Classroom).outerjoin(
                Faculty, Classes.faculty_id == Faculty.faculty_id
            ).outerjoin(
                Classroom, Classes.classroom_id == Classroom.classroom_id
            ).filter(Classes.class_id == class_id).first()
            
            if not class_data:
                return jsonify({'error': 'Class not found'}), 404
            
            class_obj, faculty, classroom = class_data
            
            return jsonify({
                'success': True,
                'class': {
                    'class_id': class_obj.class_id,
                    'class_code': class_obj.class_code,
                    'class_name': class_obj.class_name,
                    'faculty_id': class_obj.faculty_id,
                    'faculty_name': f"{faculty.first_name} {faculty.last_name}" if faculty else None,
                    'classroom_id': class_obj.classroom_id,
                    'room_number': classroom.room_number if classroom else None,
                    'semester': class_obj.semester,
                    'academic_year': class_obj.academic_year,
                    'credits': class_obj.credits,
                    'max_students': class_obj.max_students,
                    'created_at': class_obj.created_at.isoformat() if class_obj.created_at else None,
                    'updated_at': class_obj.updated_at.isoformat() if class_obj.updated_at else None
                }
            })
        
    except Exception as e:
        class_logger.error(f"Error getting class {class_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@class_bp.route('', methods=['POST'])
@jwt_required()
def admin_create_class():
    """Create new class"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app
        
        with app.app_context():
            # Import app components within app context
            from app import db, Classes
            
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['class_code', 'class_name', 'faculty_id', 'classroom_id', 'semester', 'academic_year']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'error': f'{field} is required'}), 400
            
            # Create new class
            class_obj = Classes(
                class_code=data['class_code'],
                class_name=data['class_name'],
                faculty_id=data['faculty_id'],
                classroom_id=data['classroom_id'],
                semester=data['semester'],
                academic_year=data['academic_year'],
                credits=data.get('credits', 3),
                max_students=data.get('max_students', 60)
            )
            
            db.session.add(class_obj)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Class created successfully',
                'class': {
                    'class_id': class_obj.class_id,
                    'class_code': class_obj.class_code,
                    'class_name': class_obj.class_name,
                    'faculty_id': class_obj.faculty_id,
                    'classroom_id': class_obj.classroom_id,
                    'semester': class_obj.semester,
                    'academic_year': class_obj.academic_year,
                    'credits': class_obj.credits,
                    'max_students': class_obj.max_students,
                    'created_at': class_obj.created_at.isoformat() if class_obj.created_at else None,
                    'updated_at': class_obj.updated_at.isoformat() if class_obj.updated_at else None
                }
            }), 201
        
    except Exception as e:
        # Import app components
        from app import app
        with app.app_context():
            from app import db
            db.session.rollback()
        class_logger.error(f"Error creating class: {str(e)}")
        return jsonify({'error': str(e)}), 500

@class_bp.route('/<int:class_id>', methods=['PUT'])
@jwt_required()
def admin_update_class(class_id):
    """Update class"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app
        
        with app.app_context():
            # Import app components within app context
            from app import db, Classes
            
            class_obj = Classes.query.get(class_id)
            if not class_obj:
                return jsonify({'error': 'Class not found'}), 404
            
            data = request.get_json()
            
            # Update fields if provided
            if 'class_code' in data:
                class_obj.class_code = data['class_code']
            
            if 'class_name' in data:
                class_obj.class_name = data['class_name']
            
            if 'faculty_id' in data:
                class_obj.faculty_id = data['faculty_id']
            
            if 'classroom_id' in data:
                class_obj.classroom_id = data['classroom_id']
            
            if 'semester' in data:
                class_obj.semester = data['semester']
            
            if 'academic_year' in data:
                class_obj.academic_year = data['academic_year']
            
            if 'credits' in data:
                class_obj.credits = data['credits']
            
            if 'max_students' in data:
                class_obj.max_students = data['max_students']
            
            class_obj.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Class updated successfully',
                'class': {
                    'class_id': class_obj.class_id,
                    'class_code': class_obj.class_code,
                    'class_name': class_obj.class_name,
                    'faculty_id': class_obj.faculty_id,
                    'classroom_id': class_obj.classroom_id,
                    'semester': class_obj.semester,
                    'academic_year': class_obj.academic_year,
                    'credits': class_obj.credits,
                    'max_students': class_obj.max_students,
                    'created_at': class_obj.created_at.isoformat() if class_obj.created_at else None,
                    'updated_at': class_obj.updated_at.isoformat() if class_obj.updated_at else None
                }
            })
        
    except Exception as e:
        # Import app components
        from app import app
        with app.app_context():
            from app import db
            db.session.rollback()
        class_logger.error(f"Error updating class {class_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@class_bp.route('/<int:class_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_class(class_id):
    """Delete class"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app
        
        with app.app_context():
            # Import app components within app context
            from app import db, Classes, StudentClassEnrollment
            
            class_obj = Classes.query.get(class_id)
            if not class_obj:
                return jsonify({'error': 'Class not found'}), 404
            
            # Check if class has any students enrolled
            enrollments = StudentClassEnrollment.query.filter_by(class_id=class_id).count()
            if enrollments > 0:
                return jsonify({'error': 'Cannot delete class with students enrolled'}), 400
            
            db.session.delete(class_obj)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Class deleted successfully'
            })
        
    except Exception as e:
        # Import app components
        from app import app
        with app.app_context():
            from app import db
            db.session.rollback()
        class_logger.error(f"Error deleting class {class_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500