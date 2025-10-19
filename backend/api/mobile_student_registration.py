#!/usr/bin/env python3
"""
IntelliAttend - Mobile Student Registration & Device Binding
Two-phase registration: Admin creates account → Student binds device on first login
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db
from app import Student, StudentDevices, WiFiNetwork, DeviceApprovalQueue, RegistrationAuditLog

# Create Blueprint
mobile_student_bp = Blueprint('mobile_student', __name__, url_prefix='/api/mobile/student')


def validate_campus_wifi(wifi_info):
    """
    Validate that student is connected to registered campus Wi-Fi
    This ensures students can only register devices when on campus
    
    Args:
        wifi_info: Dictionary with 'ssid' and 'bssid' (MAC address of router)
    
    Returns:
        Tuple of (is_valid: bool, classroom_id: int or None, error_message: str or None)
    """
    if not wifi_info:
        return False, None, "Wi-Fi information is required for device registration"
    
    ssid = wifi_info.get('ssid')
    bssid = wifi_info.get('bssid')  # MAC address of the Wi-Fi router
    
    if not ssid or not bssid:
        return False, None, "Both SSID and BSSID are required"
    
    # Normalize BSSID (MAC address)
    bssid = bssid.upper().replace('-', ':')
    
    # Check if this BSSID is registered in our system
    registered_wifi = WiFiNetwork.query.filter_by(
        bssid=bssid,
        is_active=True
    ).first()
    
    if not registered_wifi:
        return False, None, f"This Wi-Fi network (BSSID: {bssid}) is not a registered campus network. Please connect to campus Wi-Fi to register your device."
    
    # Optionally verify SSID matches (some routers may have multiple SSIDs)
    if registered_wifi.ssid.lower() not in ssid.lower():
        return False, None, f"Wi-Fi SSID mismatch. Expected network: {registered_wifi.ssid}"
    
    return True, registered_wifi.classroom_id, None


@mobile_student_bp.route('/login', methods=['POST'])
def student_login_with_device_registration():
    """
    Enhanced student login with automatic device registration
    
    SECURITY REQUIREMENT: Students can only register devices when connected to campus Wi-Fi
    
    Request Body:
    {
        "email": "john.doe@university.edu",
        "password": "SecurePassword123",
        "device_info": {
            "device_uuid": "a1b2c3d4-e5f6-7890",
            "device_name": "John's Samsung",
            "device_type": "android",
            "device_model": "Samsung Galaxy S21",
            "os_version": "Android 13",
            "app_version": "1.0.5",
            "biometric_enabled": true,
            "location_permission": true,
            "bluetooth_permission": true
        },
        "wifi_info": {
            "ssid": "University-WiFi",
            "bssid": "00:1A:2B:3C:4D:5E"
        }
    }
    
    Returns:
        JSON response with JWT token and registration status
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        email = data.get('email')
        password = data.get('password')
        device_info = data.get('device_info', {})
        wifi_info = data.get('wifi_info', {})
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        # Find student by email
        student = Student.query.filter_by(email=email.lower()).first()
        
        if not student:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials. Please check your email and password.'
            }), 401
        
        if not student.is_active:
            return jsonify({
                'success': False,
                'error': 'Your account is inactive. Please contact the administrator.'
            }), 403
        
        # Check password
        if not check_password_hash(student.password_hash, password):
            return jsonify({
                'success': False,
                'error': 'Invalid credentials. Please check your email and password.'
            }), 401
        
        # Check if this is first login (no devices registered)
        existing_devices = StudentDevices.query.filter_by(
            student_id=student.student_id,
            is_active=True
        ).count()
        
        is_first_login = existing_devices == 0
        
        # Extract device UUID
        device_uuid = device_info.get('device_uuid')
        
        if not device_uuid:
            # No device info provided - allow login but flag as incomplete
            access_token = create_access_token(identity=student.student_id)
            
            return jsonify({
                'success': True,
                'message': 'Login successful but device registration is incomplete',
                'access_token': access_token,
                'student': {
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'program': student.program
                },
                'device_registered': False,
                'requires_wifi': True,
                'message_detail': 'Please provide device information to complete registration'
            }), 200
        
        # Check if device is already registered
        existing_device = StudentDevices.query.filter_by(
            device_uuid=device_uuid
        ).first()
        
        if existing_device:
            # Device exists - update last seen and login
            existing_device.last_seen = datetime.utcnow()
            existing_device.device_name = device_info.get('device_name', existing_device.device_name)
            existing_device.os_version = device_info.get('os_version', existing_device.os_version)
            existing_device.app_version = device_info.get('app_version', existing_device.app_version)
            existing_device.biometric_enabled = device_info.get('biometric_enabled', existing_device.biometric_enabled)
            existing_device.location_permission = device_info.get('location_permission', existing_device.location_permission)
            existing_device.bluetooth_permission = device_info.get('bluetooth_permission', existing_device.bluetooth_permission)
            
            db.session.commit()
            
            # Create access token
            access_token = create_access_token(identity=student.student_id)
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'access_token': access_token,
                'student': {
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'program': student.program,
                    'year_of_study': student.year_of_study
                },
                'device_registered': True,
                'device_id': existing_device.device_id,
                'is_first_login': False
            }), 200
        
        # NEW DEVICE REGISTRATION - REQUIRE CAMPUS WI-FI
        # ==============================================
        
        # Validate campus Wi-Fi connection
        wifi_valid, classroom_id, wifi_error = validate_campus_wifi(wifi_info)
        
        if not wifi_valid:
            return jsonify({
                'success': False,
                'error': 'Device registration requires campus Wi-Fi connection',
                'details': wifi_error,
                'requires_wifi': True,
                'wifi_requirement': 'You must be connected to a registered campus Wi-Fi network to register your device. Please connect to campus Wi-Fi and try again.'
            }), 403
        
        # Wi-Fi validated - proceed with device registration
        try:
            # Create new device record
            new_device = StudentDevices(
                student_id=student.student_id,
                device_uuid=device_uuid,
                device_name=device_info.get('device_name', 'Unknown Device'),
                device_type=device_info.get('device_type', 'android'),
                device_model=device_info.get('device_model'),
                os_version=device_info.get('os_version'),
                app_version=device_info.get('app_version'),
                biometric_enabled=device_info.get('biometric_enabled', False),
                location_permission=device_info.get('location_permission', False),
                bluetooth_permission=device_info.get('bluetooth_permission', False),
                is_active=True
            )
            
            db.session.add(new_device)
            db.session.flush()
            
            device_id = new_device.device_id
            
            # Optional: Add to approval queue for admin review (if required)
            # approval_queue = DeviceApprovalQueue(
            #     device_uuid=device_uuid,
            #     student_id=student.student_id,
            #     device_info={
            #         'model': device_info.get('device_model'),
            #         'os': device_info.get('os_version'),
            #         'registered_via_wifi': wifi_info.get('ssid'),
            #         'registered_at_classroom': classroom_id
            #     },
            #     status='approved'  # Auto-approve if Wi-Fi validated
            # )
            # db.session.add(approval_queue)
            
            db.session.commit()
            
            # Create access token
            access_token = create_access_token(identity=student.student_id)
            
            return jsonify({
                'success': True,
                'message': 'Device registered successfully! You can now use this device for attendance.',
                'access_token': access_token,
                'student': {
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'program': student.program,
                    'year_of_study': student.year_of_study
                },
                'device_registered': True,
                'device_id': device_id,
                'is_first_login': is_first_login,
                'registration_details': {
                    'registered_via_wifi': wifi_info.get('ssid'),
                    'classroom_id': classroom_id,
                    'device_model': device_info.get('device_model'),
                    'permissions': {
                        'biometric': device_info.get('biometric_enabled', False),
                        'location': device_info.get('location_permission', False),
                        'bluetooth': device_info.get('bluetooth_permission', False)
                    }
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Device registration error: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to register device',
                'details': str(e)
            }), 500
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error occurred',
            'details': str(e)
        }), 500


@mobile_student_bp.route('/device/update', methods=['PUT'])
@jwt_required()
def update_device_info():
    """
    Update device information (permissions, OS version, app version)
    Called when app settings change or app is updated
    
    Request Body:
    {
        "device_uuid": "a1b2c3d4-e5f6-7890",
        "os_version": "Android 14",
        "app_version": "1.0.6",
        "biometric_enabled": true,
        "location_permission": true,
        "bluetooth_permission": true
    }
    """
    try:
        student_id = get_jwt_identity()
        data = request.get_json()
        
        device_uuid = data.get('device_uuid')
        
        if not device_uuid:
            return jsonify({
                'success': False,
                'error': 'Device UUID is required'
            }), 400
        
        # Get device
        device = StudentDevices.query.filter_by(
            device_uuid=device_uuid,
            student_id=student_id
        ).first()
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found or not owned by this student'
            }), 404
        
        # Update fields
        if 'os_version' in data:
            device.os_version = data['os_version']
        if 'app_version' in data:
            device.app_version = data['app_version']
        if 'biometric_enabled' in data:
            device.biometric_enabled = data['biometric_enabled']
        if 'location_permission' in data:
            device.location_permission = data['location_permission']
        if 'bluetooth_permission' in data:
            device.bluetooth_permission = data['bluetooth_permission']
        
        device.last_seen = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Device information updated successfully',
            'device': {
                'device_id': device.device_id,
                'device_uuid': device.device_uuid,
                'os_version': device.os_version,
                'app_version': device.app_version,
                'permissions': {
                    'biometric': device.biometric_enabled,
                    'location': device.location_permission,
                    'bluetooth': device.bluetooth_permission
                }
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Device update error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update device information',
            'details': str(e)
        }), 500


@mobile_student_bp.route('/devices', methods=['GET'])
@jwt_required()
def get_student_devices():
    """
    Get all devices registered to the current student
    Useful for security - student can see all their registered devices
    """
    try:
        student_id = get_jwt_identity()
        
        devices = StudentDevices.query.filter_by(student_id=student_id).all()
        
        device_list = [
            {
                'device_id': device.device_id,
                'device_name': device.device_name,
                'device_model': device.device_model,
                'device_type': device.device_type,
                'os_version': device.os_version,
                'app_version': device.app_version,
                'is_active': device.is_active,
                'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                'registered_at': device.created_at.isoformat() if device.created_at else None,
                'permissions': {
                    'biometric': device.biometric_enabled,
                    'location': device.location_permission,
                    'bluetooth': device.bluetooth_permission
                }
            }
            for device in devices
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'devices': device_list,
                'total_count': len(device_list)
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching devices: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch devices',
            'details': str(e)
        }), 500


@mobile_student_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_student_profile():
    """
    Get current student's profile information
    """
    try:
        student_id = get_jwt_identity()
        
        student = Student.query.get(student_id)
        
        if not student:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
        
        # Get device count
        device_count = StudentDevices.query.filter_by(
            student_id=student_id,
            is_active=True
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'student_id': student.student_id,
                'student_code': student.student_code,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone_number': student.phone_number,
                'program': student.program,
                'year_of_study': student.year_of_study,
                'is_active': student.is_active,
                'registered_devices_count': device_count,
                'created_at': student.created_at.isoformat() if student.created_at else None
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching profile: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch profile',
            'details': str(e)
        }), 500
