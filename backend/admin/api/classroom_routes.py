"""
Classroom management routes for IntelliAttend admin panel
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

# Import models and components from app.py
# We'll import these within functions to avoid circular imports

# Configure logging
classroom_logger = logging.getLogger(__name__)

# Classroom routes blueprint
classroom_bp = Blueprint('classroom', __name__, url_prefix='/api/admin/classrooms')

@classroom_bp.route('', methods=['GET'])
@jwt_required()
def admin_get_classrooms_list():
    """Get list of all classrooms"""
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
        from app import app, db, Classroom
        
        with app.app_context():
            # Build query
            query = Classroom.query
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        getattr(Classroom, 'room_number').like(search_filter),
                        getattr(Classroom, 'building_name').like(search_filter)
                    )
                )
            
            # Paginate results
            classrooms_pagination = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            classrooms_list = []
            for classroom in classrooms_pagination.items:
                classrooms_list.append({
                    'classroom_id': classroom.classroom_id,
                    'room_number': classroom.room_number,
                    'building_name': classroom.building_name,
                    'floor_number': classroom.floor_number,
                    'capacity': classroom.capacity,
                    'latitude': float(classroom.latitude) if classroom.latitude else None,
                    'longitude': float(classroom.longitude) if classroom.longitude else None,
                    'geofence_radius': float(classroom.geofence_radius) if classroom.geofence_radius else None,
                    'bluetooth_beacon_id': classroom.bluetooth_beacon_id,
                    'is_active': classroom.is_active,
                    'created_at': classroom.created_at.isoformat() if classroom.created_at else None,
                    'updated_at': classroom.updated_at.isoformat() if classroom.updated_at else None
                })
            
            return jsonify({
                'success': True,
                'classrooms': classrooms_list,
                'pagination': {
                    'page': classrooms_pagination.page,
                    'pages': classrooms_pagination.pages,
                    'per_page': classrooms_pagination.per_page,
                    'total': classrooms_pagination.total
                }
            })
        
    except Exception as e:
        classroom_logger.error(f"Error getting classrooms list: {str(e)}")
        return jsonify({'error': str(e)}), 500

@classroom_bp.route('/<int:classroom_id>', methods=['GET'])
@jwt_required()
def admin_get_classroom(classroom_id):
    """Get specific classroom details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app, Classroom
        
        with app.app_context():
            classroom = Classroom.query.get(classroom_id)
            if not classroom:
                return jsonify({'error': 'Classroom not found'}), 404
            
            return jsonify({
                'success': True,
                'classroom': {
                    'classroom_id': classroom.classroom_id,
                    'room_number': classroom.room_number,
                    'building_name': classroom.building_name,
                    'floor_number': classroom.floor_number,
                    'capacity': classroom.capacity,
                    'latitude': float(classroom.latitude) if classroom.latitude else None,
                    'longitude': float(classroom.longitude) if classroom.longitude else None,
                    'geofence_radius': float(classroom.geofence_radius) if classroom.geofence_radius else None,
                    'bluetooth_beacon_id': classroom.bluetooth_beacon_id,
                    'is_active': classroom.is_active,
                    'created_at': classroom.created_at.isoformat() if classroom.created_at else None,
                    'updated_at': classroom.updated_at.isoformat() if classroom.updated_at else None
                }
            })
        
    except Exception as e:
        classroom_logger.error(f"Error getting classroom {classroom_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@classroom_bp.route('', methods=['POST'])
@jwt_required()
def admin_create_classroom():
    """Create new classroom"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['room_number', 'building_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Import app components
        from app import app, db, Classroom
        
        with app.app_context():
            # Check if room number already exists
            existing = Classroom.query.filter(
                getattr(Classroom, 'room_number') == data['room_number']
            ).first()
            if existing:
                return jsonify({'error': 'Room number already exists'}), 400
            
            # Create new classroom
            classroom = Classroom(
                room_number=data['room_number'],
                building_name=data['building_name'],
                floor_number=data.get('floor_number'),
                capacity=data.get('capacity', 50),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                geofence_radius=data.get('geofence_radius', 50.00),
                bluetooth_beacon_id=data.get('bluetooth_beacon_id'),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(classroom)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Classroom created successfully',
                'classroom': {
                    'classroom_id': classroom.classroom_id,
                    'room_number': classroom.room_number,
                    'building_name': classroom.building_name,
                    'floor_number': classroom.floor_number,
                    'capacity': classroom.capacity,
                    'latitude': float(classroom.latitude) if classroom.latitude else None,
                    'longitude': float(classroom.longitude) if classroom.longitude else None,
                    'geofence_radius': float(classroom.geofence_radius) if classroom.geofence_radius else None,
                    'bluetooth_beacon_id': classroom.bluetooth_beacon_id,
                    'is_active': classroom.is_active,
                    'created_at': classroom.created_at.isoformat() if classroom.created_at else None,
                    'updated_at': classroom.updated_at.isoformat() if classroom.updated_at else None
                }
            }), 201
        
    except Exception as e:
        # Import app components
        from app import app, db
        with app.app_context():
            db.session.rollback()
        classroom_logger.error(f"Error creating classroom: {str(e)}")
        return jsonify({'error': str(e)}), 500

@classroom_bp.route('/<int:classroom_id>', methods=['PUT'])
@jwt_required()
def admin_update_classroom_detailed(classroom_id):
    """Update classroom"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app, Classroom, db
        
        with app.app_context():
            classroom = Classroom.query.get(classroom_id)
            if not classroom:
                return jsonify({'error': 'Classroom not found'}), 404
            
            data = request.get_json()
            
            # Update fields if provided
            if 'room_number' in data and data['room_number'] != classroom.room_number:
                # Check if new room number already exists
                existing = Classroom.query.filter(
                    getattr(Classroom, 'room_number') == data['room_number'],
                    Classroom.classroom_id != classroom_id
                ).first()
                if existing:
                    return jsonify({'error': 'Room number already exists'}), 400
                classroom.room_number = data['room_number']
            
            if 'building_name' in data:
                classroom.building_name = data['building_name']
            
            if 'floor_number' in data:
                classroom.floor_number = data['floor_number']
            
            if 'capacity' in data:
                classroom.capacity = data['capacity']
            
            if 'latitude' in data:
                classroom.latitude = data['latitude']
            
            if 'longitude' in data:
                classroom.longitude = data['longitude']
            
            if 'geofence_radius' in data:
                classroom.geofence_radius = data['geofence_radius']
            
            if 'bluetooth_beacon_id' in data:
                classroom.bluetooth_beacon_id = data['bluetooth_beacon_id']
            
            if 'is_active' in data:
                classroom.is_active = data['is_active']
            
            classroom.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Classroom updated successfully',
                'classroom': {
                    'classroom_id': classroom.classroom_id,
                    'room_number': classroom.room_number,
                    'building_name': classroom.building_name,
                    'floor_number': classroom.floor_number,
                    'capacity': classroom.capacity,
                    'latitude': float(classroom.latitude) if classroom.latitude else None,
                    'longitude': float(classroom.longitude) if classroom.longitude else None,
                    'geofence_radius': float(classroom.geofence_radius) if classroom.geofence_radius else None,
                    'bluetooth_beacon_id': classroom.bluetooth_beacon_id,
                    'is_active': classroom.is_active,
                    'created_at': classroom.created_at.isoformat() if classroom.created_at else None,
                    'updated_at': classroom.updated_at.isoformat() if classroom.updated_at else None
                }
            })
        
    except Exception as e:
        # Import app components
        from app import app, db
        with app.app_context():
            db.session.rollback()
        classroom_logger.error(f"Error updating classroom {classroom_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@classroom_bp.route('/<int:classroom_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_classroom_permanent(classroom_id):
    """Delete classroom"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Import app components
        from app import app, Classroom, Classes, db
        
        with app.app_context():
            classroom = Classroom.query.get(classroom_id)
            if not classroom:
                return jsonify({'error': 'Classroom not found'}), 404
            
            # Check if classroom is used in any classes
            classes = Classes.query.filter_by(classroom_id=classroom_id).count()
            if classes > 0:
                return jsonify({'error': 'Cannot delete classroom used in classes'}), 400
            
            db.session.delete(classroom)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Classroom deleted successfully'
            })
        
    except Exception as e:
        # Import app components
        from app import app, db
        with app.app_context():
            db.session.rollback()
        classroom_logger.error(f"Error deleting classroom {classroom_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500