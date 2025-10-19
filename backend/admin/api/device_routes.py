"""
Device management routes for IntelliAttend admin panel
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
device_logger = logging.getLogger(__name__)

# Device routes blueprint
device_bp = Blueprint('device', __name__, url_prefix='/api/admin/devices')

@device_bp.route('', methods=['GET'])
@jwt_required()
def admin_get_devices_list():
    """Get list of all student devices"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app, db, StudentDevices, Student
        
        with app.app_context():
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # Get search parameter
            search = request.args.get('search', '')
            
            # Build query with joins to get related data
            query = db.session.query(StudentDevices, Student).join(
                Student, StudentDevices.student_id == Student.student_id
            )
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        Student.first_name.like(search_filter),
                        Student.last_name.like(search_filter),
                        Student.student_code.like(search_filter),
                        StudentDevices.device_uuid.like(search_filter),
                        StudentDevices.device_name.like(search_filter)
                    )
                )
            
            # Order by last seen descending
            query = query.order_by(StudentDevices.last_seen.desc())
            
            # Execute query and manually paginate
            total_count = query.count()
            offset = (page - 1) * per_page
            devices_items = query.offset(offset).limit(per_page).all()
            
            # Calculate pagination details
            total_pages = (total_count + per_page - 1) // per_page
            
            devices_list = []
            for device, student in devices_items:
                devices_list.append({
                    'device_id': device.device_id,
                    'student_id': device.student_id,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'student_code': student.student_code,
                    'device_uuid': device.device_uuid,
                    'device_name': device.device_name,
                    'device_type': device.device_type,
                    'device_model': device.device_model,
                    'os_version': device.os_version,
                    'app_version': device.app_version,
                    'fcm_token': device.fcm_token,
                    'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                    'is_active': device.is_active,
                    'biometric_enabled': device.biometric_enabled,
                    'location_permission': device.location_permission,
                    'bluetooth_permission': device.bluetooth_permission,
                    'created_at': device.created_at.isoformat() if device.created_at else None,
                    'updated_at': device.updated_at.isoformat() if device.updated_at else None
                })
            
            return jsonify({
                'success': True,
                'devices': devices_list,
                'pagination': {
                    'page': page,
                    'pages': total_pages,
                    'per_page': per_page,
                    'total': total_count
                }
            })
        
    except Exception as e:
        device_logger.error(f"Error getting devices list: {str(e)}")
        return jsonify({'error': str(e)}), 500

@device_bp.route('/<int:device_id>', methods=['GET'])
@jwt_required()
def admin_get_device(device_id):
    """Get specific device details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app, db, StudentDevices, Student
        
        with app.app_context():
            # Get device with related data
            device_data = db.session.query(StudentDevices, Student).join(
                Student, StudentDevices.student_id == Student.student_id
            ).filter(StudentDevices.device_id == device_id).first()
            
            if not device_data:
                return jsonify({'error': 'Device not found'}), 404
            
            device, student = device_data
            
            return jsonify({
                'success': True,
                'device': {
                    'device_id': device.device_id,
                    'student_id': device.student_id,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'student_code': student.student_code,
                    'student_email': student.email,
                    'device_uuid': device.device_uuid,
                    'device_name': device.device_name,
                    'device_type': device.device_type,
                    'device_model': device.device_model,
                    'os_version': device.os_version,
                    'app_version': device.app_version,
                    'fcm_token': device.fcm_token,
                    'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                    'is_active': device.is_active,
                    'biometric_enabled': device.biometric_enabled,
                    'location_permission': device.location_permission,
                    'bluetooth_permission': device.bluetooth_permission,
                    'created_at': device.created_at.isoformat() if device.created_at else None,
                    'updated_at': device.updated_at.isoformat() if device.updated_at else None
                }
            })
        
    except Exception as e:
        device_logger.error(f"Error getting device {device_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@device_bp.route('/<int:device_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_device(device_id):
    """Delete device"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app, db, StudentDevices
        
        with app.app_context():
            device = StudentDevices.query.get(device_id)
            if not device:
                return jsonify({'error': 'Device not found'}), 404
            
            db.session.delete(device)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Device deleted successfully'
            })
        
    except Exception as e:
        # Import app components
        from app import app, db
        with app.app_context():
            db.session.rollback()
        device_logger.error(f"Error deleting device {device_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
