"""
Enhanced Mobile Device Enforcement with GPS + WiFi Validation
Ensures registration is genuine and within campus boundaries
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from datetime import datetime, timedelta
from app import db, tile38_client
from models import Students, Users, StudentDevices, DeviceSwitchRequests, DeviceActivityLogs, CampusWifiNetworks
from werkzeug.security import check_password_hash
import uuid

mobile_enhanced_bp = Blueprint('mobile_enhanced', __name__, url_prefix='/api/mobile/v2')

# Constants
DEVICE_SWITCH_COOLDOWN_HOURS = 48
CAMPUS_BOUNDARY_VALIDATION_RADIUS_METERS = 500  # Allow 500m from nearest classroom


def validate_campus_wifi(ssid, bssid):
    """
    Validate that the WiFi network is a registered campus network
    
    Args:
        ssid: WiFi network SSID
        bssid: WiFi network BSSID (MAC address)
        
    Returns:
        tuple: (is_valid, campus_wifi_record)
    """
    if not ssid or not bssid:
        return False, None
    
    # Check against registered campus WiFi networks
    campus_wifi = CampusWifiNetworks.query.filter(
        (CampusWifiNetworks.ssid == ssid) | (CampusWifiNetworks.bssid == bssid)
    ).filter_by(is_active=True).first()
    
    return campus_wifi is not None, campus_wifi


def validate_campus_gps_location(latitude, longitude):
    """
    Validate that GPS location is within campus boundaries using Tile38
    
    Args:
        latitude: GPS latitude
        longitude: GPS longitude
        
    Returns:
        dict: {
            'is_valid': bool,
            'nearest_classroom': dict or None,
            'distance_meters': float or None,
            'within_bounds': bool
        }
    """
    try:
        if not latitude or not longitude:
            return {
                'is_valid': False,
                'nearest_classroom': None,
                'distance_meters': None,
                'within_bounds': False,
                'error': 'GPS coordinates not provided'
            }
        
        # Search for nearby classrooms within validation radius
        response = tile38_client.nearby(
            'classrooms',
            'POINT',
            latitude,
            longitude,
            CAMPUS_BOUNDARY_VALIDATION_RADIUS_METERS,
            count=1
        )
        
        if response and len(response) > 0:
            nearest = response[0]
            classroom_id = nearest.get('id')
            distance = nearest.get('distance', 0)
            
            return {
                'is_valid': True,
                'nearest_classroom': {
                    'classroom_code': classroom_id,
                    'distance_meters': round(distance, 2)
                },
                'distance_meters': round(distance, 2),
                'within_bounds': True
            }
        
        # No classrooms found nearby - student is outside campus
        return {
            'is_valid': False,
            'nearest_classroom': None,
            'distance_meters': None,
            'within_bounds': False,
            'error': 'Location outside campus boundaries'
        }
        
    except Exception as e:
        return {
            'is_valid': False,
            'nearest_classroom': None,
            'distance_meters': None,
            'within_bounds': False,
            'error': f'GPS validation error: {str(e)}'
        }


def log_device_activity(student_id, device_uuid, activity_type, additional_info=None):
    """Log device-related activity"""
    log = DeviceActivityLogs(
        student_id=student_id,
        device_uuid=device_uuid,
        activity_type=activity_type,
        additional_info=additional_info or {}
    )
    db.session.add(log)
    db.session.flush()


def deactivate_all_other_devices(student_id, current_device_uuid):
    """Deactivate all devices except the specified one"""
    StudentDevices.query.filter(
        StudentDevices.student_id == student_id,
        StudentDevices.device_uuid != current_device_uuid
    ).update({
        'is_active': False,
        'deactivated_at': datetime.utcnow()
    })
    db.session.flush()


@mobile_enhanced_bp.route('/permissions-check', methods=['POST'])
def check_permissions():
    """
    Mobile app calls this to report which permissions are granted
    Returns list of required permissions and their status
    
    Request body:
        - permissions: {
            'wifi': bool,
            'gps': bool,
            'bluetooth': bool
        }
    """
    data = request.get_json() or {}
    granted_permissions = data.get('permissions', {})
    
    required_permissions = {
        'wifi': {
            'required': True,
            'granted': granted_permissions.get('wifi', False),
            'reason': 'Required to validate campus WiFi network during device registration',
            'permission_name': 'ACCESS_WIFI_STATE, ACCESS_NETWORK_STATE'
        },
        'gps': {
            'required': True,
            'granted': granted_permissions.get('gps', False),
            'reason': 'Required to verify you are on campus during registration and attendance marking',
            'permission_name': 'ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION'
        },
        'bluetooth': {
            'required': False,
            'granted': granted_permissions.get('bluetooth', False),
            'reason': 'Optional - May be used for future proximity features',
            'permission_name': 'BLUETOOTH, BLUETOOTH_ADMIN'
        }
    }
    
    all_required_granted = all(
        perm['granted'] for perm in required_permissions.values() if perm['required']
    )
    
    return jsonify({
        'success': True,
        'permissions': required_permissions,
        'all_required_granted': all_required_granted,
        'can_proceed': all_required_granted,
        'message': 'All required permissions granted' if all_required_granted else 'Please grant WiFi and GPS permissions to continue'
    }), 200


@mobile_enhanced_bp.route('/login-with-validation', methods=['POST'])
def login_with_enhanced_validation():
    """
    Enhanced mobile login with both WiFi AND GPS validation
    
    Request body:
        - email (required)
        - password (required)
        - device_info (required): {
            device_uuid, device_name, device_type, device_model,
            os_version, app_version
        }
        - wifi_info (required): {
            ssid, bssid, signal_strength (optional)
        }
        - gps_info (required): {
            latitude, longitude, accuracy (optional), timestamp (optional)
        }
        - permissions (required): {
            wifi: bool, gps: bool, bluetooth: bool
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Extract data
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        device_info = data.get('device_info', {})
        wifi_info = data.get('wifi_info', {})
        gps_info = data.get('gps_info', {})
        permissions = data.get('permissions', {})
        
        # Validate required fields
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        if not device_info.get('device_uuid'):
            return jsonify({
                'success': False,
                'error': 'Device information is required'
            }), 400
        
        # Check permissions
        if not permissions.get('wifi') or not permissions.get('gps'):
            return jsonify({
                'success': False,
                'error': 'WiFi and GPS permissions are required for device registration',
                'error_code': 'PERMISSIONS_DENIED',
                'required_permissions': {
                    'wifi': not permissions.get('wifi'),
                    'gps': not permissions.get('gps')
                }
            }), 403
        
        # Validate WiFi info
        if not wifi_info.get('ssid') or not wifi_info.get('bssid'):
            return jsonify({
                'success': False,
                'error': 'Campus WiFi connection is required for device registration',
                'error_code': 'WIFI_INFO_MISSING',
                'hint': 'Please connect to campus WiFi and try again'
            }), 403
        
        # Validate GPS info
        if not gps_info.get('latitude') or not gps_info.get('longitude'):
            return jsonify({
                'success': False,
                'error': 'GPS location is required for device registration',
                'error_code': 'GPS_INFO_MISSING',
                'hint': 'Please enable location services and try again'
            }), 403
        
        # Authenticate student
        student = Students.query.filter_by(email=email).first()
        if not student:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials',
                'error_code': 'INVALID_CREDENTIALS'
            }), 401
        
        user = Users.query.get(student.user_id)
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({
                'success': False,
                'error': 'Invalid credentials',
                'error_code': 'INVALID_CREDENTIALS'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'Account is deactivated. Please contact administration.',
                'error_code': 'ACCOUNT_INACTIVE'
            }), 403
        
        # STEP 1: Validate Campus WiFi
        wifi_valid, campus_wifi = validate_campus_wifi(
            wifi_info.get('ssid'),
            wifi_info.get('bssid')
        )
        
        if not wifi_valid:
            log_device_activity(
                student_id=student.student_id,
                device_uuid=device_info.get('device_uuid'),
                activity_type='login_attempt_failed',
                additional_info={
                    'reason': 'invalid_wifi',
                    'ssid': wifi_info.get('ssid'),
                    'bssid': wifi_info.get('bssid')
                }
            )
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': 'Device registration requires connection to campus WiFi',
                'error_code': 'INVALID_CAMPUS_WIFI',
                'wifi_info': {
                    'provided_ssid': wifi_info.get('ssid'),
                    'provided_bssid': wifi_info.get('bssid'),
                    'is_valid': False
                },
                'hint': 'Please connect to campus WiFi network and try again'
            }), 403
        
        # STEP 2: Validate GPS Location
        gps_validation = validate_campus_gps_location(
            gps_info.get('latitude'),
            gps_info.get('longitude')
        )
        
        if not gps_validation['is_valid']:
            log_device_activity(
                student_id=student.student_id,
                device_uuid=device_info.get('device_uuid'),
                activity_type='login_attempt_failed',
                additional_info={
                    'reason': 'invalid_gps_location',
                    'latitude': gps_info.get('latitude'),
                    'longitude': gps_info.get('longitude'),
                    'validation_result': gps_validation
                }
            )
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': 'Device registration requires you to be on campus',
                'error_code': 'OUTSIDE_CAMPUS_BOUNDARIES',
                'gps_info': {
                    'latitude': gps_info.get('latitude'),
                    'longitude': gps_info.get('longitude'),
                    'within_campus': False,
                    'validation_details': gps_validation
                },
                'hint': 'Please ensure you are physically present on campus and try again'
            }), 403
        
        # BOTH WiFi AND GPS validated successfully - Proceed with device registration
        device_uuid = device_info.get('device_uuid')
        
        # Check if device already exists
        current_device = StudentDevices.query.filter_by(
            student_id=student.student_id,
            device_uuid=device_uuid
        ).first()
        
        # Check if student has any active device
        active_device = StudentDevices.query.filter_by(
            student_id=student.student_id,
            is_active=True
        ).first()
        
        # SCENARIO 1: First device registration (no active device)
        if not active_device:
            if current_device:
                # Device exists but was deactivated - reactivate it
                current_device.is_active = True
                current_device.activated_at = datetime.utcnow()
                current_device.last_seen = datetime.utcnow()
            else:
                # Brand new device - register and activate immediately
                current_device = StudentDevices(
                    student_id=student.student_id,
                    device_uuid=device_uuid,
                    device_name=device_info.get('device_name', 'Unknown Device'),
                    device_type=device_info.get('device_type', 'android'),
                    device_model=device_info.get('device_model'),
                    os_version=device_info.get('os_version'),
                    app_version=device_info.get('app_version'),
                    is_active=True
                )
                current_device.activated_at = datetime.utcnow()
                db.session.add(current_device)
            
            log_device_activity(
                student_id=student.student_id,
                device_uuid=device_uuid,
                activity_type='device_registered_and_activated',
                additional_info={
                    'first_device': True,
                    'wifi_validated': True,
                    'gps_validated': True,
                    'wifi_info': {
                        'ssid': wifi_info.get('ssid'),
                        'bssid': wifi_info.get('bssid'),
                        'campus_network_id': campus_wifi.wifi_network_id if campus_wifi else None
                    },
                    'gps_info': {
                        'latitude': gps_info.get('latitude'),
                        'longitude': gps_info.get('longitude'),
                        'nearest_classroom': gps_validation.get('nearest_classroom'),
                        'distance_meters': gps_validation.get('distance_meters')
                    },
                    'device_info': device_info
                }
            )
            
            db.session.commit()
            
            access_token = create_access_token(identity=student.student_id)
            
            return jsonify({
                'success': True,
                'message': 'Welcome! Your device has been registered and activated.',
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
                'device_status': 'active',
                'can_mark_attendance': True,
                'first_device': True,
                'validation_details': {
                    'wifi_validated': True,
                    'gps_validated': True,
                    'campus_wifi': {
                        'ssid': wifi_info.get('ssid'),
                        'network_name': campus_wifi.network_name if campus_wifi else None
                    },
                    'location': {
                        'within_campus': True,
                        'nearest_classroom': gps_validation.get('nearest_classroom'),
                        'distance_meters': gps_validation.get('distance_meters')
                    }
                }
            }), 200
        
        # SCENARIO 2: Same device login (device already active)
        if active_device and active_device.device_uuid == device_uuid:
            active_device.last_seen = datetime.utcnow()
            
            log_device_activity(
                student_id=student.student_id,
                device_uuid=device_uuid,
                activity_type='login_success',
                additional_info={
                    'same_device': True,
                    'wifi_validated': True,
                    'gps_validated': True
                }
            )
            
            db.session.commit()
            
            access_token = create_access_token(identity=student.student_id)
            
            return jsonify({
                'success': True,
                'message': 'Welcome back!',
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
                'device_status': 'active',
                'can_mark_attendance': True,
                'same_device': True
            }), 200
        
        # SCENARIO 3: Device switch detected (different device)
        # Check if there's already a pending request for this device
        existing_request = DeviceSwitchRequests.query.filter_by(
            student_id=student.student_id,
            new_device_uuid=device_uuid,
            status='pending'
        ).first()
        
        if not existing_request:
            # Create new device switch request
            switch_request = DeviceSwitchRequests(
                student_id=student.student_id,
                old_device_uuid=active_device.device_uuid,
                old_device_name=active_device.device_name,
                new_device_uuid=device_uuid,
                new_device_name=device_info.get('device_name', 'Unknown Device'),
                new_device_type=device_info.get('device_type', 'android'),
                new_device_model=device_info.get('device_model'),
                status='pending',
                reason=data.get('switch_reason', 'Device change'),
                additional_info={
                    'wifi_validation': {
                        'ssid': wifi_info.get('ssid'),
                        'bssid': wifi_info.get('bssid'),
                        'validated': True
                    },
                    'gps_validation': gps_validation
                }
            )
            db.session.add(switch_request)
            db.session.flush()
            
            existing_request = switch_request
        
        # Register new device (but keep it inactive)
        if not current_device:
            current_device = StudentDevices(
                student_id=student.student_id,
                device_uuid=device_uuid,
                device_name=device_info.get('device_name', 'Unknown Device'),
                device_type=device_info.get('device_type', 'android'),
                device_model=device_info.get('device_model'),
                os_version=device_info.get('os_version'),
                app_version=device_info.get('app_version'),
                is_active=False
            )
            db.session.add(current_device)
        else:
            current_device.last_seen = datetime.utcnow()
        
        log_device_activity(
            student_id=student.student_id,
            device_uuid=device_uuid,
            activity_type='device_switch_detected',
            additional_info={
                'old_device_uuid': active_device.device_uuid,
                'new_device_uuid': device_uuid,
                'switch_request_id': existing_request.request_id,
                'wifi_validated': True,
                'gps_validated': True,
                'validation_details': {
                    'wifi': {
                        'ssid': wifi_info.get('ssid'),
                        'validated': True
                    },
                    'gps': gps_validation
                }
            }
        )
        
        db.session.commit()
        
        # Calculate cooldown information
        hours_elapsed = (datetime.utcnow() - existing_request.requested_at).total_seconds() / 3600
        hours_remaining = max(0, DEVICE_SWITCH_COOLDOWN_HOURS - hours_elapsed)
        cooldown_completed = hours_elapsed >= DEVICE_SWITCH_COOLDOWN_HOURS
        activation_date = existing_request.requested_at + timedelta(hours=DEVICE_SWITCH_COOLDOWN_HOURS)
        
        access_token = create_access_token(identity=student.student_id)
        
        # Check admin approval status
        if cooldown_completed and existing_request.status == 'approved':
            # Both conditions met - activate device
            deactivate_all_other_devices(student.student_id, device_uuid)
            current_device.is_active = True
            current_device.activated_at = datetime.utcnow()
            existing_request.completed_at = datetime.utcnow()
            
            log_device_activity(
                student_id=student.student_id,
                device_uuid=device_uuid,
                activity_type='device_activated',
                additional_info={
                    'activation_type': 'dual_approval_complete',
                    'cooldown_completed': True,
                    'admin_approved': True
                }
            )
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Device fully activated! You can now mark attendance.',
                'access_token': access_token,
                'student': {
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email
                },
                'device_status': 'active',
                'can_mark_attendance': True,
                'device_switch_completed': True
            }), 200
        
        # Device switch in progress
        if cooldown_completed:
            status_message = 'pending_admin_approval'
            user_message = f'The 48-hour cooldown is complete. Your device activation is pending admin approval. You can view data but cannot mark attendance.'
        else:
            status_message = 'pending_cooldown'
            user_message = f'New device detected. Your device will be eligible for activation after {DEVICE_SWITCH_COOLDOWN_HOURS} hours. You can view data but cannot mark attendance until activation.'
        
        return jsonify({
            'success': True,
            'message': user_message,
            'access_token': access_token,
            'student': {
                'student_id': student.student_id,
                'student_code': student.student_code,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email
            },
            'device_status': status_message,
            'limited_access': True,
            'can_mark_attendance': False,
            'device_switch_info': {
                'request_id': existing_request.request_id,
                'status': existing_request.status,
                'requested_at': existing_request.requested_at.isoformat(),
                'cooldown_info': {
                    'total_hours': DEVICE_SWITCH_COOLDOWN_HOURS,
                    'hours_elapsed': round(hours_elapsed, 1),
                    'hours_remaining': round(hours_remaining, 1),
                    'cooldown_completed': cooldown_completed,
                    'activation_date': activation_date.isoformat(),
                    'activation_date_formatted': activation_date.strftime('%B %d, %Y at %I:%M %p')
                },
                'approval_info': {
                    'admin_approval_required': True,
                    'admin_approved': existing_request.status == 'approved',
                    'approval_pending': existing_request.status == 'pending'
                },
                'restrictions': {
                    'can_view_history': True,
                    'can_view_classes': True,
                    'can_view_profile': True,
                    'can_mark_attendance': False,
                    'reason': 'Dual approval required: 48-hour cooldown ' + ('✓' if cooldown_completed else '⏳') + ' | Admin approval ' + ('✓' if existing_request.status == 'approved' else '⏳')
                }
            },
            'validation_details': {
                'wifi_validated': True,
                'gps_validated': True,
                'location_verified': True
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Login failed: {str(e)}',
            'error_code': 'INTERNAL_ERROR'
        }), 500


@mobile_enhanced_bp.route('/device-status-detailed', methods=['GET'])
@jwt_required()
def get_device_status_detailed():
    """
    Get comprehensive device status for mobile app UI
    Includes cooldown timer, admin approval status, restrictions, etc.
    """
    try:
        student_id = get_jwt_identity()
        student = Students.query.get(student_id)
        
        if not student:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
        
        # Get active device
        active_device = StudentDevices.query.filter_by(
            student_id=student_id,
            is_active=True
        ).first()
        
        # Get all devices
        all_devices = StudentDevices.query.filter_by(student_id=student_id).all()
        
        # Get pending switch request
        pending_request = DeviceSwitchRequests.query.filter_by(
            student_id=student_id,
            status='pending'
        ).order_by(DeviceSwitchRequests.requested_at.desc()).first()
        
        if not pending_request:
            # No pending switch - device is active
            return jsonify({
                'success': True,
                'device_status': 'active',
                'can_mark_attendance': True,
                'active_device': {
                    'device_uuid': active_device.device_uuid if active_device else None,
                    'device_name': active_device.device_name if active_device else None,
                    'device_type': active_device.device_type if active_device else None,
                    'activated_at': active_device.activated_at.isoformat() if active_device and active_device.activated_at else None
                },
                'all_devices': [{
                    'device_uuid': d.device_uuid,
                    'device_name': d.device_name,
                    'device_type': d.device_type,
                    'is_active': d.is_active,
                    'registered_at': d.registered_at.isoformat()
                } for d in all_devices],
                'restrictions': None,
                'message': 'Your device is active. You can mark attendance.'
            }), 200
        
        # Pending switch request exists
        hours_elapsed = (datetime.utcnow() - pending_request.requested_at).total_seconds() / 3600
        hours_remaining = max(0, DEVICE_SWITCH_COOLDOWN_HOURS - hours_elapsed)
        cooldown_completed = hours_elapsed >= DEVICE_SWITCH_COOLDOWN_HOURS
        activation_date = pending_request.requested_at + timedelta(hours=DEVICE_SWITCH_COOLDOWN_HOURS)
        
        # Calculate percentage for progress bar
        progress_percentage = min(100, (hours_elapsed / DEVICE_SWITCH_COOLDOWN_HOURS) * 100)
        
        # Determine status
        if cooldown_completed:
            status = 'awaiting_admin_approval'
            status_message = 'Cooldown complete! Awaiting admin approval.'
            status_color = 'blue'  # Info color
        else:
            status = 'pending_cooldown'
            status_message = f'Device activation in progress. {round(hours_remaining, 1)} hours remaining.'
            status_color = 'orange'  # Warning color
        
        return jsonify({
            'success': True,
            'device_status': status,
            'can_mark_attendance': False,
            'active_device': {
                'device_uuid': active_device.device_uuid if active_device else None,
                'device_name': active_device.device_name if active_device else None,
                'device_type': active_device.device_type if active_device else None
            },
            'pending_device': {
                'device_uuid': pending_request.new_device_uuid,
                'device_name': pending_request.new_device_name,
                'device_type': pending_request.new_device_type,
                'requested_at': pending_request.requested_at.isoformat()
            },
            'cooldown_timer': {
                'total_hours': DEVICE_SWITCH_COOLDOWN_HOURS,
                'hours_elapsed': round(hours_elapsed, 1),
                'hours_remaining': round(hours_remaining, 1),
                'minutes_remaining': round(hours_remaining * 60, 0),
                'cooldown_completed': cooldown_completed,
                'progress_percentage': round(progress_percentage, 1),
                'activation_date': activation_date.isoformat(),
                'activation_date_formatted': activation_date.strftime('%B %d, %Y'),
                'activation_time_formatted': activation_date.strftime('%I:%M %p')
            },
            'approval_status': {
                'admin_approval_required': True,
                'admin_approved': pending_request.status == 'approved',
                'approval_pending': pending_request.status == 'pending',
                'cooldown_check': cooldown_completed,
                'admin_check': pending_request.status == 'approved',
                'both_complete': cooldown_completed and pending_request.status == 'approved'
            },
            'restrictions': {
                'can_view_history': True,
                'can_view_classes': True,
                'can_view_profile': True,
                'can_view_schedule': True,
                'can_mark_attendance': False,
                'reason': 'Device activation pending'
            },
            'ui_display': {
                'show_banner': True,
                'banner_type': status_color,
                'banner_title': status_message,
                'banner_message': f'You can view your data but cannot mark attendance until {activation_date.strftime("%B %d at %I:%M %p")}' + (' and admin approves your request.' if not cooldown_completed else '. Admin approval is pending.'),
                'show_countdown': not cooldown_completed,
                'show_progress_bar': not cooldown_completed,
                'disable_attendance_button': True,
                'attendance_button_tooltip': 'Your device is pending activation. You cannot mark attendance yet.'
            },
            'message': status_message
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get device status: {str(e)}'
        }), 500
