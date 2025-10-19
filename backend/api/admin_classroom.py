#!/usr/bin/env python3
"""
IntelliAttend - Admin Classroom Registration API
Endpoints for classroom registration and management with Wi-Fi and Bluetooth beacon support
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db
from app import (
    Classroom, WiFiNetwork, BluetoothBeacon, 
    RegistrationAuditLog, Admin
)
from validators import (
    validate_classroom_registration,
    validate_gps_coordinates,
    validate_mac_address,
    validate_beacon_uuid,
    normalize_mac_address,
    normalize_beacon_uuid,
    sanitize_string
)
from utils.audit_helpers import (
    log_registration_action,
    create_audit_details,
    sanitize_audit_data
)

# Import geofencing service
try:
    from geofencing_service import GeofencingService
    geofencing = GeofencingService()
except Exception as e:
    print(f"⚠️  Geofencing service not available: {e}")
    geofencing = None

# Create Blueprint
admin_classroom_bp = Blueprint('admin_classroom', __name__, url_prefix='/api/admin/classrooms')


@admin_classroom_bp.route('', methods=['POST'])
@jwt_required()
def register_classroom():
    """
    Register a new classroom with GPS, Wi-Fi, and Bluetooth beacon information
    
    Request Body:
    {
        "room_number": "Room-501",
        "building_name": "Engineering Building",
        "floor_number": 5,
        "capacity": 60,
        "latitude": 37.7219,
        "longitude": -122.4782,
        "geofence_radius": 50.0,
        "wifi": {
            "ssid": "University-WiFi",
            "bssid": "00:1A:2B:3C:4D:5E",
            "security_type": "WPA2"
        },
        "bluetooth_beacon": {
            "beacon_uuid": "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0",
            "major": 1,
            "minor": 501,
            "mac_address": "00:1A:2B:3C:4D:5F"
        }
    }
    
    Returns:
        JSON response with classroom details or error message
    """
    try:
        # Get admin ID from JWT
        admin_id = get_jwt_identity()
        
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate input data
        is_valid, errors = validate_classroom_registration(data)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'validation_errors': errors
            }), 400
        
        # Check for duplicate room number
        existing_classroom = Classroom.query.filter_by(
            room_number=sanitize_string(data['room_number'])
        ).first()
        
        if existing_classroom:
            return jsonify({
                'success': False,
                'error': f"Classroom with room number '{data['room_number']}' already exists"
            }), 409
        
        # Check for duplicate BSSID if Wi-Fi provided
        if 'wifi' in data and 'bssid' in data['wifi']:
            normalized_bssid = normalize_mac_address(data['wifi']['bssid'])
            existing_wifi = WiFiNetwork.query.filter_by(bssid=normalized_bssid).first()
            
            if existing_wifi:
                return jsonify({
                    'success': False,
                    'error': f"Wi-Fi BSSID '{data['wifi']['bssid']}' is already registered"
                }), 409
        
        # Check for duplicate Bluetooth beacon if provided
        if 'bluetooth_beacon' in data:
            beacon_data = data['bluetooth_beacon']
            if 'beacon_uuid' in beacon_data and 'major' in beacon_data and 'minor' in beacon_data:
                normalized_uuid = normalize_beacon_uuid(beacon_data['beacon_uuid'])
                existing_beacon = BluetoothBeacon.query.filter_by(
                    beacon_uuid=normalized_uuid,
                    major=beacon_data['major'],
                    minor=beacon_data['minor']
                ).first()
                
                if existing_beacon:
                    return jsonify({
                        'success': False,
                        'error': f"Bluetooth beacon (UUID: {beacon_data['beacon_uuid']}, Major: {beacon_data['major']}, Minor: {beacon_data['minor']}) is already registered"
                    }), 409
        
        # Begin transaction
        try:
            # Create classroom
            classroom = Classroom(
                room_number=sanitize_string(data['room_number']),
                building_name=sanitize_string(data['building_name']),
                floor_number=data.get('floor_number'),
                capacity=data.get('capacity', 50),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                geofence_radius=data.get('geofence_radius', 50.0),
                is_active=True
            )
            
            db.session.add(classroom)
            db.session.flush()  # Get classroom_id
            
            classroom_id = classroom.classroom_id
            
            # Create Wi-Fi network if provided
            wifi_id = None
            if 'wifi' in data:
                wifi_data = data['wifi']
                wifi_network = WiFiNetwork(
                    classroom_id=classroom_id,
                    ssid=wifi_data.get('ssid'),
                    bssid=normalize_mac_address(wifi_data.get('bssid')),
                    security_type=wifi_data.get('security_type', 'WPA2'),
                    registered_by=admin_id,
                    is_active=True
                )
                db.session.add(wifi_network)
                db.session.flush()
                wifi_id = wifi_network.wifi_id
            
            # Create Bluetooth beacon if provided
            beacon_id = None
            if 'bluetooth_beacon' in data:
                beacon_data = data['bluetooth_beacon']
                beacon = BluetoothBeacon(
                    classroom_id=classroom_id,
                    beacon_uuid=normalize_beacon_uuid(beacon_data.get('beacon_uuid')),
                    major=beacon_data.get('major'),
                    minor=beacon_data.get('minor'),
                    mac_address=normalize_mac_address(beacon_data['mac_address']) if beacon_data.get('mac_address') else None,
                    expected_rssi=beacon_data.get('expected_rssi', -75),
                    registered_by=admin_id,
                    is_active=True
                )
                db.session.add(beacon)
                db.session.flush()
                beacon_id = beacon.beacon_id
            
            # Sync to Tile38 geofencing service if available
            tile38_synced = False
            if geofencing and data.get('latitude') and data.get('longitude'):
                try:
                    metadata = {
                        'room_number': data['room_number'],
                        'building': data['building_name'],
                        'floor': data.get('floor_number', 0)
                    }
                    
                    tile38_synced = geofencing.set_classroom_geofence(
                        classroom_id=classroom_id,
                        latitude=float(data['latitude']),
                        longitude=float(data['longitude']),
                        radius=float(data.get('geofence_radius', 50.0)),
                        metadata=metadata
                    )
                except Exception as e:
                    print(f"⚠️  Tile38 sync failed (non-critical): {e}")
            
            # Log to audit trail
            audit_details = create_audit_details(
                operation='classroom_registration',
                new_values=sanitize_audit_data({
                    'classroom_id': classroom_id,
                    'room_number': data['room_number'],
                    'building_name': data['building_name'],
                    'has_wifi': 'wifi' in data,
                    'has_beacon': 'bluetooth_beacon' in data,
                    'has_gps': 'latitude' in data and 'longitude' in data
                }),
                metadata={
                    'wifi_id': wifi_id,
                    'beacon_id': beacon_id,
                    'tile38_synced': tile38_synced
                }
            )
            
            log_registration_action(
                db=db,
                RegistrationAuditLog=RegistrationAuditLog,
                Admin=Admin,
                action='create',
                resource_type='classroom',
                resource_id=classroom_id,
                admin_id=admin_id,
                details=audit_details
            )
            
            # Commit transaction
            db.session.commit()
            
            # Prepare response
            response_data = {
                'classroom_id': classroom_id,
                'room_number': classroom.room_number,
                'building_name': classroom.building_name,
                'floor_number': classroom.floor_number,
                'capacity': classroom.capacity,
                'latitude': float(classroom.latitude) if classroom.latitude else None,
                'longitude': float(classroom.longitude) if classroom.longitude else None,
                'geofence_radius': float(classroom.geofence_radius) if classroom.geofence_radius else None,
                'tile38_synced': tile38_synced
            }
            
            if wifi_id:
                response_data['wifi'] = {
                    'wifi_id': wifi_id,
                    'ssid': data['wifi']['ssid'],
                    'security_type': data['wifi'].get('security_type', 'WPA2')
                }
            
            if beacon_id:
                response_data['bluetooth_beacon'] = {
                    'beacon_id': beacon_id,
                    'major': data['bluetooth_beacon']['major'],
                    'minor': data['bluetooth_beacon']['minor']
                }
            
            return jsonify({
                'success': True,
                'message': 'Classroom registered successfully',
                'data': response_data
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Database error: {e}")
            return jsonify({
                'success': False,
                'error': 'Database error occurred during registration',
                'details': str(e)
            }), 500
            
    except Exception as e:
        print(f"❌ Server error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error occurred',
            'details': str(e)
        }), 500


@admin_classroom_bp.route('', methods=['GET'])
@jwt_required()
def get_classrooms():
    """
    Get all classrooms with optional filters
    
    Query Parameters:
        - building: Filter by building name
        - floor: Filter by floor number
        - is_active: Filter by active status (true/false)
        - has_wifi: Filter classrooms with Wi-Fi (true/false)
        - has_beacon: Filter classrooms with Bluetooth beacons (true/false)
    
    Returns:
        JSON response with list of classrooms
    """
    try:
        # Get query parameters
        building = request.args.get('building')
        floor = request.args.get('floor', type=int)
        is_active = request.args.get('is_active', type=lambda v: v.lower() == 'true')
        has_wifi = request.args.get('has_wifi', type=lambda v: v.lower() == 'true')
        has_beacon = request.args.get('has_beacon', type=lambda v: v.lower() == 'true')
        
        # Build query
        query = Classroom.query
        
        if building:
            query = query.filter(Classroom.building_name.ilike(f'%{building}%'))
        
        if floor is not None:
            query = query.filter_by(floor_number=floor)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        # Execute query
        classrooms = query.all()
        
        # Format response
        result = []
        for classroom in classrooms:
            # Get Wi-Fi networks
            wifi_networks = WiFiNetwork.query.filter_by(
                classroom_id=classroom.classroom_id,
                is_active=True
            ).all()
            
            # Get Bluetooth beacons
            beacons = BluetoothBeacon.query.filter_by(
                classroom_id=classroom.classroom_id,
                is_active=True
            ).all()
            
            # Apply filters
            if has_wifi is not None and (len(wifi_networks) > 0) != has_wifi:
                continue
            
            if has_beacon is not None and (len(beacons) > 0) != has_beacon:
                continue
            
            classroom_data = {
                'classroom_id': classroom.classroom_id,
                'room_number': classroom.room_number,
                'building_name': classroom.building_name,
                'floor_number': classroom.floor_number,
                'capacity': classroom.capacity,
                'latitude': float(classroom.latitude) if classroom.latitude else None,
                'longitude': float(classroom.longitude) if classroom.longitude else None,
                'geofence_radius': float(classroom.geofence_radius) if classroom.geofence_radius else None,
                'is_active': classroom.is_active,
                'wifi_networks_count': len(wifi_networks),
                'bluetooth_beacons_count': len(beacons),
                'created_at': classroom.created_at.isoformat() if classroom.created_at else None
            }
            
            result.append(classroom_data)
        
        return jsonify({
            'success': True,
            'data': {
                'classrooms': result,
                'total_count': len(result)
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching classrooms: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch classrooms',
            'details': str(e)
        }), 500


@admin_classroom_bp.route('/<int:classroom_id>', methods=['GET'])
@jwt_required()
def get_classroom_details(classroom_id):
    """
    Get detailed information about a specific classroom
    
    Returns:
        JSON response with classroom details including Wi-Fi networks and Bluetooth beacons
    """
    try:
        # Get classroom
        classroom = Classroom.query.get(classroom_id)
        
        if not classroom:
            return jsonify({
                'success': False,
                'error': f'Classroom with ID {classroom_id} not found'
            }), 404
        
        # Get Wi-Fi networks
        wifi_networks = WiFiNetwork.query.filter_by(classroom_id=classroom_id).all()
        
        # Get Bluetooth beacons
        beacons = BluetoothBeacon.query.filter_by(classroom_id=classroom_id).all()
        
        # Format response
        response_data = {
            'classroom_id': classroom.classroom_id,
            'room_number': classroom.room_number,
            'building_name': classroom.building_name,
            'floor_number': classroom.floor_number,
            'capacity': classroom.capacity,
            'latitude': float(classroom.latitude) if classroom.latitude else None,
            'longitude': float(classroom.longitude) if classroom.longitude else None,
            'geofence_radius': float(classroom.geofence_radius) if classroom.geofence_radius else None,
            'is_active': classroom.is_active,
            'created_at': classroom.created_at.isoformat() if classroom.created_at else None,
            'updated_at': classroom.updated_at.isoformat() if classroom.updated_at else None,
            'wifi_networks': [
                {
                    'wifi_id': wifi.wifi_id,
                    'ssid': wifi.ssid,
                    'bssid': wifi.bssid,
                    'security_type': wifi.security_type,
                    'is_active': wifi.is_active
                }
                for wifi in wifi_networks
            ],
            'bluetooth_beacons': [
                {
                    'beacon_id': beacon.beacon_id,
                    'beacon_uuid': beacon.beacon_uuid,
                    'major': beacon.major,
                    'minor': beacon.minor,
                    'mac_address': beacon.mac_address,
                    'expected_rssi': beacon.expected_rssi,
                    'is_active': beacon.is_active
                }
                for beacon in beacons
            ]
        }
        
        return jsonify({
            'success': True,
            'data': response_data
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching classroom details: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch classroom details',
            'details': str(e)
        }), 500
