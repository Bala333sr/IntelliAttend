#!/usr/bin/env python3
"""
IntelliAttend - Single Device Enforcement (PhonePe-style)
Only ONE device can be active at a time with 48-hour device switch cooldown
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\

from app import db
from app import (
    Student, StudentDevices, WiFiNetwork, 
    DeviceSwitchRequest, DeviceActivityLog
)

# Create Blueprint
mobile_device_bp = Blueprint('mobile_device', __name__, url_prefix='/api/mobile/device')

# Constants
DEVICE_SWITCH_COOLDOWN_HOURS = 48  # 48-hour waiting period
DEVICE_SWITCH_EXPIRY_DAYS = 7      # Request expires after 7 days


def validate_campus_wifi(wifi_info):
    """Validate that student is connected to registered campus Wi-Fi"""
    if not wifi_info:
        return False, None, "Wi-Fi information is required"
    
    ssid = wifi_info.get('ssid')
    bssid = wifi_info.get('bssid')
    
    if not ssid or not bssid:
        return False, None, "Both SSID and BSSID are required"
    
    bssid = bssid.upper().replace('-', ':')
    
    registered_wifi = WiFiNetwork.query.filter_by(
        bssid=bssid,
        is_active=True
    ).first()
    
    if not registered_wifi:
        return False, None, f"Not a registered campus network"
    
    return True, registered_wifi.classroom_id, None


def log_device_activity(student_id, device_uuid, activity_type, additional_info=None):
    """Log device activity for security monitoring"""
    try:
        activity_log = DeviceActivityLog(
            student_id=student_id,
            device_uuid=device_uuid,
            activity_type=activity_type,
            ip_address=request.remote_addr if request else None,
            wifi_ssid=additional_info.get('wifi_ssid') if additional_info else None,
            additional_info=additional_info
        )
        db.session.add(activity_log)
        db.session.flush()
    except Exception as e:
        print(f"⚠️  Failed to log device activity: {e}")


def deactivate_all_other_devices(student_id, current_device_uuid):
    """Deactivate all devices except the current one"""
    other_devices = StudentDevices.query.filter(
        StudentDevices.student_id == student_id,
        StudentDevices.device_uuid != current_device_uuid,
        StudentDevices.is_active == True
    ).all()
    
    for device in other_devices:
        device.is_active = False
        device.deactivated_at = datetime.utcnow()
        
        # Log deactivation
        log_device_activity(
            student_id=student_id,
            device_uuid=device.device_uuid,
            activity_type='device_deactivated',
            additional_info={'reason': 'new_device_activated', 'new_device': current_device_uuid}
        )


@mobile_device_bp.route('/login-secure', methods=['POST'])
def secure_login_with_device_enforcement():
    """
    Enhanced login with SINGLE ACTIVE DEVICE enforcement (PhonePe-style)
    
    Rules:
    1. Only ONE device can be active at a time
    2. New device login → Deactivate old device immediately
    3. Device switch requires 48-hour cooldown before full activation
    4. Prevents credential sharing and multi-device abuse
    
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
            "app_version": "1.0.5"
        },
        "wifi_info": {
            "ssid": "University-WiFi",
            "bssid": "00:1A:2B:3C:4D:5E"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        device_info = data.get('device_info', {})
        wifi_info = data.get('wifi_info', {})
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400
        
        # Find student
        student = Student.query.filter_by(email=email.lower()).first()
        
        if not student or not student.is_active:
            log_device_activity(
                student_id=student.student_id if student else 0,
                device_uuid=device_info.get('device_uuid', 'unknown'),
                activity_type='failed_login',
                additional_info={'reason': 'invalid_credentials'}
            )
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Check password
        if not check_password_hash(student.password_hash, password):
            log_device_activity(
                student_id=student.student_id,
                device_uuid=device_info.get('device_uuid', 'unknown'),
                activity_type='failed_login',
                additional_info={'reason': 'wrong_password'}
            )
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        device_uuid = device_info.get('device_uuid')
        
        if not device_uuid:
            return jsonify({
                'success': False,
                'error': 'Device information is required'
            }), 400
        
        # ============================================================================
        # SINGLE DEVICE ENFORCEMENT LOGIC
        # ============================================================================
        
        # Check if this device is already registered
        current_device = StudentDevices.query.filter_by(
            device_uuid=device_uuid
        ).first()
        
        # Get currently active device (if any)
        active_device = StudentDevices.query.filter_by(
            student_id=student.student_id,
            is_active=True
        ).first()
        
        # SCENARIO 1: Same device login (device already active)
        if current_device and active_device and current_device.device_id == active_device.device_id:
            # Update last seen
            current_device.last_seen = datetime.utcnow()
            current_device.device_name = device_info.get('device_name', current_device.device_name)
            current_device.os_version = device_info.get('os_version', current_device.os_version)
            current_device.app_version = device_info.get('app_version', current_device.app_version)
            
            log_device_activity(
                student_id=student.student_id,
                device_uuid=device_uuid,
                activity_type='login',
                additional_info={'login_type': 'same_device'}
            )
            
            db.session.commit()
            
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
                    'email': student.email
                },
                'device_status': 'active',
                'device_id': current_device.device_id
            }), 200
        
        # SCENARIO 2: New device OR different device login
        # This triggers DEVICE SWITCH ENFORCEMENT
        
        # Validate campus Wi-Fi (REQUIRED for new device)
        wifi_valid, classroom_id, wifi_error = validate_campus_wifi(wifi_info)
        
        if not wifi_valid:
            return jsonify({
                'success': False,
                'error': 'Campus Wi-Fi connection required',
                'details': wifi_error,
                'requires_wifi': True
            }), 403
        
        # Check if there's a pending device switch request
        existing_request = DeviceSwitchRequest.query.filter_by(
            student_id=student.student_id,
            new_device_uuid=device_uuid,
            status='pending'
        ).first()
        
        # Check if 48-hour cooldown has passed
        if existing_request:
            hours_elapsed = (datetime.utcnow() - existing_request.requested_at).total_seconds() / 3600
            
            if hours_elapsed >= DEVICE_SWITCH_COOLDOWN_HOURS:
                # COOLDOWN COMPLETE - But still need ADMIN APPROVAL
                
                # Check if admin has approved
                if existing_request.status != 'approved':
                    # 48 hours passed but admin hasn't approved yet
                    access_token = create_access_token(identity=student.student_id)
                    
                    return jsonify({
                        'success': True,
                        'message': 'Login successful (Awaiting Admin Approval)',
                        'access_token': access_token,
                        'student': {
                            'student_id': student.student_id,
                            'student_code': student.student_code,
                            'first_name': student.first_name,
                            'last_name': student.last_name,
                            'email': student.email
                        },
                        'device_status': 'awaiting_admin_approval',
                        'limited_access': True,
                        'can_mark_attendance': False,
                        'approval_info': {
                            'cooldown_completed': True,
                            'cooldown_hours': round(hours_elapsed, 1),
                            'admin_approval_pending': True,
                            'status': 'pending_admin_approval',
                            'message': 'The 48-hour cooldown is complete. Your device activation request is now pending admin approval. You can view your data but cannot mark attendance until an administrator approves your device.',
                            'next_steps': 'Please contact your administrator to approve your device switch request.',
                            'restrictions': {
                                'can_view_history': True,
                                'can_view_classes': True,
                                'can_view_profile': True,
                                'can_mark_attendance': False,
                                'reason': 'Dual approval required: 48-hour cooldown complete ✓ | Admin approval pending ⏳'
                            }
                        }
                    }), 200
                
                # BOTH CONDITIONS MET: 48 hours passed AND admin approved
                # Deactivate all other devices
                deactivate_all_other_devices(student.student_id, device_uuid)
                
                # Register or activate the new device
                if current_device:
                    current_device.is_active = True
                    current_device.activated_at = datetime.utcnow()
                    current_device.last_seen = datetime.utcnow()
                else:
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
                    db.session.flush()
                
                # Mark request as completed
                existing_request.completed_at = datetime.utcnow()
                
                log_device_activity(
                    student_id=student.student_id,
                    device_uuid=device_uuid,
                    activity_type='device_activated',
                    additional_info={
                        'activation_type': 'dual_approval_complete',
                        'cooldown_completed': True,
                        'admin_approved': True,
                        'hours_elapsed': round(hours_elapsed, 1)
                    }
                )
                
                db.session.commit()
                
                access_token = create_access_token(identity=student.student_id)
                
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
                    'device_switch_completed': True,
                    'dual_approval_complete': {
                        'cooldown_completed': True,
                        'admin_approved': True,
                        'cooldown_hours': round(hours_elapsed, 1)
                    }
                }), 200
                
            else:
                # STILL IN COOLDOWN PERIOD
                # BUT ALLOW LOGIN - User can view data but NOT mark attendance (PhonePe-style)
                remaining_hours = DEVICE_SWITCH_COOLDOWN_HOURS - hours_elapsed
                will_activate_at = existing_request.requested_at + timedelta(hours=DEVICE_SWITCH_COOLDOWN_HOURS)
                
                # Create access token - Allow login!
                access_token = create_access_token(identity=student.student_id)
                
                log_device_activity(
                    student_id=student.student_id,
                    device_uuid=device_uuid,
                    activity_type='login',
                    additional_info={
                        'login_type': 'cooldown_period',
                        'limited_access': True,
                        'can_mark_attendance': False
                    }
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful (Limited Access)',
                    'access_token': access_token,
                    'student': {
                        'student_id': student.student_id,
                        'student_code': student.student_code,
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                        'email': student.email
                    },
                    'device_status': 'pending_activation',
                    'limited_access': True,
                    'can_mark_attendance': False,
                    'device_switch_info': {
                        'status': 'pending',
                        'requested_at': existing_request.requested_at.isoformat(),
                        'hours_elapsed': round(hours_elapsed, 1),
                        'hours_remaining': round(remaining_hours, 1),
                        'will_activate_at': will_activate_at.isoformat(),
                        'activation_date_readable': will_activate_at.strftime('%B %d, %Y at %I:%M %p'),
                        'restrictions': {
                            'can_view_history': True,
                            'can_view_classes': True,
                            'can_view_profile': True,
                            'can_mark_attendance': False,
                            'reason': 'Device is pending activation. You can view your data but cannot mark attendance for 48 hours.'
                        }
                    }
                }), 200
        
        # NO EXISTING REQUEST - Create new device switch request
        else:
            # First device registration (no active device exists)
            if not active_device:
                # Register first device immediately (no cooldown needed)
                new_device = StudentDevices(
                    student_id=student.student_id,
                    device_uuid=device_uuid,
                    device_name=device_info.get('device_name', 'Unknown Device'),
                    device_type=device_info.get('device_type', 'android'),
                    device_model=device_info.get('device_model'),
                    os_version=device_info.get('os_version'),
                    app_version=device_info.get('app_version'),
                    is_active=True
                )
                new_device.activated_at = datetime.utcnow()
                
                db.session.add(new_device)
                db.session.flush()
                
                log_device_activity(
                    student_id=student.student_id,
                    device_uuid=device_uuid,
                    activity_type='device_activated',
                    additional_info={'activation_type': 'first_device'}
                )
                
                db.session.commit()
                
                access_token = create_access_token(identity=student.student_id)
                
                return jsonify({
                    'success': True,
                    'message': 'First device registered successfully!',
                    'access_token': access_token,
                    'student': {
                        'student_id': student.student_id,
                        'student_code': student.student_code,
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                        'email': student.email
                    },
                    'device_status': 'active',
                    'device_id': new_device.device_id,
                    'is_first_device': True
                }), 201
            
            # Device switch requested (different device, active device exists)
            else:
                # Immediately deactivate old device
                deactivate_all_other_devices(student.student_id, device_uuid)
                
                # Create device switch request with 48-hour cooldown
                switch_request = DeviceSwitchRequest(
                    student_id=student.student_id,
                    old_device_uuid=active_device.device_uuid if active_device else None,
                    new_device_uuid=device_uuid,
                    new_device_info=device_info,
                    request_reason='manual_switch'
                )
                switch_request.ip_address = request.remote_addr
                switch_request.wifi_ssid = wifi_info.get('ssid')
                
                db.session.add(switch_request)
                
                log_device_activity(
                    student_id=student.student_id,
                    device_uuid=device_uuid,
                    activity_type='login',
                    additional_info={
                        'login_type': 'new_device_switch',
                        'limited_access': True,
                        'cooldown_hours': DEVICE_SWITCH_COOLDOWN_HOURS
                    }
                )
                
                db.session.commit()
                
                will_activate_at = switch_request.requested_at + timedelta(hours=DEVICE_SWITCH_COOLDOWN_HOURS)
                
                # ALLOW LOGIN with LIMITED ACCESS (PhonePe-style)
                access_token = create_access_token(identity=student.student_id)
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful (Limited Access - Device Pending Activation)',
                    'access_token': access_token,
                    'student': {
                        'student_id': student.student_id,
                        'student_code': student.student_code,
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                        'email': student.email
                    },
                    'device_status': 'pending_activation',
                    'limited_access': True,
                    'can_mark_attendance': False,
                    'device_switch_info': {
                        'status': 'pending',
                        'requested_at': switch_request.requested_at.isoformat(),
                        'cooldown_hours': DEVICE_SWITCH_COOLDOWN_HOURS,
                        'will_activate_at': will_activate_at.isoformat(),
                        'activation_date_readable': will_activate_at.strftime('%B %d, %Y at %I:%M %p'),
                        'hours_remaining': DEVICE_SWITCH_COOLDOWN_HOURS,
                        'old_device_deactivated': True,
                        'restrictions': {
                            'can_view_history': True,
                            'can_view_classes': True,
                            'can_view_profile': True,
                            'can_view_timetable': True,
                            'can_mark_attendance': False,
                            'reason': 'New device is pending activation. You can login and view all your data, but cannot mark attendance for 48 hours. This security measure prevents credential sharing.'
                        },
                        'user_message': f'Your previous device has been deactivated. You can view your attendance history and classes, but cannot mark attendance until {will_activate_at.strftime("%B %d at %I:%M %p")}.'
                    }
                }), 200
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Server error occurred',
            'details': str(e)
        }), 500


@mobile_device_bp.route('/switch-status', methods=['GET'])
@jwt_required()
def get_device_switch_status():
    """
    Get current device switch status and cooldown information
    """
    try:
        student_id = get_jwt_identity()
        
        # Get active device
        active_device = StudentDevices.query.filter_by(
            student_id=student_id,
            is_active=True
        ).first()
        
        # Get pending switch requests
        pending_requests = DeviceSwitchRequest.query.filter_by(
            student_id=student_id,
            status='pending'
        ).order_by(DeviceSwitchRequest.requested_at.desc()).all()
        
        requests_data = []
        for req in pending_requests:
            hours_elapsed = (datetime.utcnow() - req.requested_at).total_seconds() / 3600
            remaining_hours = max(0, DEVICE_SWITCH_COOLDOWN_HOURS - hours_elapsed)
            
            requests_data.append({
                'request_id': req.request_id,
                'new_device_model': req.new_device_info.get('device_model') if req.new_device_info else 'Unknown',
                'requested_at': req.requested_at.isoformat(),
                'hours_elapsed': round(hours_elapsed, 1),
                'hours_remaining': round(remaining_hours, 1),
                'can_activate': hours_elapsed >= DEVICE_SWITCH_COOLDOWN_HOURS,
                'will_activate_at': (req.requested_at + timedelta(hours=DEVICE_SWITCH_COOLDOWN_HOURS)).isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': {
                'active_device': {
                    'device_uuid': active_device.device_uuid,
                    'device_name': active_device.device_name,
                    'device_model': active_device.device_model,
                    'activated_at': active_device.activated_at.isoformat() if active_device.activated_at else None
                } if active_device else None,
                'pending_switch_requests': requests_data,
                'has_pending_requests': len(requests_data) > 0
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@mobile_device_bp.route('/activity-log', methods=['GET'])
@jwt_required()
def get_device_activity_log():
    """
    Get device activity log for the current student
    Useful for security - student can see all their device activities
    """
    try:
        student_id = get_jwt_identity()
        limit = request.args.get('limit', 50, type=int)
        
        activities = DeviceActivityLog.query.filter_by(
            student_id=student_id
        ).order_by(DeviceActivityLog.timestamp.desc()).limit(limit).all()
        
        activity_list = [
            {
                'activity_type': activity.activity_type,
                'device_uuid': activity.device_uuid,
                'timestamp': activity.timestamp.isoformat(),
                'ip_address': activity.ip_address,
                'wifi_ssid': activity.wifi_ssid,
                'additional_info': activity.additional_info
            }
            for activity in activities
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'activities': activity_list,
                'total_count': len(activity_list)
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
