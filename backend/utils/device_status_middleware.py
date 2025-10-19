#!/usr/bin/env python3
"""
IntelliAttend - Device Status Middleware
Checks if device is fully activated before allowing attendance marking
"""

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from functools import wraps
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def require_activated_device(f):
    """
    Decorator to check if device is fully activated before allowing attendance operations
    
    Usage:
        @app.route('/api/attendance/mark', methods=['POST'])
        @jwt_required()
        @require_activated_device
        def mark_attendance():
            # This function only runs if device is fully activated
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Import here to avoid circular imports
        from app import StudentDevices, DeviceSwitchRequest
        
        # Verify JWT token
        verify_jwt_in_request()
        student_id = get_jwt_identity()
        
        # Get device UUID from request
        data = request.get_json() if request.is_json else {}
        device_uuid = data.get('device_uuid') or request.headers.get('X-Device-UUID')
        
        if not device_uuid:
            return jsonify({
                'success': False,
                'error': 'Device identification required',
                'details': 'device_uuid must be provided in request body or X-Device-UUID header'
            }), 400
        
        # Check if device is registered
        device = StudentDevices.query.filter_by(
            student_id=student_id,
            device_uuid=device_uuid
        ).first()
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not registered',
                'details': 'This device is not registered to your account. Please login first.'
            }), 403
        
        # Check if device is active
        if not device.is_active:
            return jsonify({
                'success': False,
                'error': 'Device is deactivated',
                'details': 'This device has been deactivated. Please login from your primary device or contact support.'
            }), 403
        
        # Check if device is in cooldown period
        pending_request = DeviceSwitchRequest.query.filter_by(
            student_id=student_id,
            new_device_uuid=device_uuid,
            status='pending'
        ).first()
        
        if pending_request:
            # Calculate remaining cooldown time
            hours_elapsed = (datetime.utcnow() - pending_request.requested_at).total_seconds() / 3600
            COOLDOWN_HOURS = 48
            
            if hours_elapsed < COOLDOWN_HOURS:
                remaining_hours = COOLDOWN_HOURS - hours_elapsed
                will_activate_at = pending_request.requested_at + timedelta(hours=COOLDOWN_HOURS)
                
                return jsonify({
                    'success': False,
                    'error': 'Device pending activation',
                    'can_mark_attendance': False,
                    'details': {
                        'message': f'Your device will be activated in {round(remaining_hours, 1)} hours',
                        'activation_date': will_activate_at.isoformat(),
                        'activation_date_readable': will_activate_at.strftime('%B %d, %Y at %I:%M %p'),
                        'hours_remaining': round(remaining_hours, 1),
                        'restrictions': {
                            'can_view_history': True,
                            'can_view_classes': True,
                            'can_view_profile': True,
                            'can_mark_attendance': False
                        },
                        'reason': 'You can view your data, but cannot mark attendance until the 48-hour device activation period is complete.',
                        'user_message': f'For security purposes, new devices require 48 hours before attendance marking is enabled. You can view all your data in the meantime.'
                    }
                }), 403
        
        # Device is fully activated - allow attendance marking
        return f(*args, **kwargs)
    
    return decorated_function


def get_device_status(student_id, device_uuid):
    """
    Get comprehensive device status information
    
    Args:
        student_id: Student ID
        device_uuid: Device UUID
        
    Returns:
        Dictionary with device status details
    """
    from app import StudentDevices, DeviceSwitchRequest
    
    device = StudentDevices.query.filter_by(
        student_id=student_id,
        device_uuid=device_uuid
    ).first()
    
    if not device:
        return {
            'registered': False,
            'active': False,
            'can_mark_attendance': False,
            'status': 'not_registered'
        }
    
    # Check for pending activation
    pending_request = DeviceSwitchRequest.query.filter_by(
        student_id=student_id,
        new_device_uuid=device_uuid,
        status='pending'
    ).first()
    
    if pending_request:
        hours_elapsed = (datetime.utcnow() - pending_request.requested_at).total_seconds() / 3600
        COOLDOWN_HOURS = 48
        
        if hours_elapsed < COOLDOWN_HOURS:
            remaining_hours = COOLDOWN_HOURS - hours_elapsed
            will_activate_at = pending_request.requested_at + timedelta(hours=COOLDOWN_HOURS)
            
            return {
                'registered': True,
                'active': device.is_active,
                'can_mark_attendance': False,
                'status': 'pending_activation',
                'cooldown_info': {
                    'hours_remaining': round(remaining_hours, 1),
                    'will_activate_at': will_activate_at.isoformat(),
                    'activation_date_readable': will_activate_at.strftime('%B %d, %Y at %I:%M %p')
                },
                'permissions': {
                    'can_view_history': True,
                    'can_view_classes': True,
                    'can_view_profile': True,
                    'can_view_timetable': True,
                    'can_mark_attendance': False
                }
            }
    
    # Device is fully activated
    return {
        'registered': True,
        'active': device.is_active,
        'can_mark_attendance': device.is_active,
        'status': 'active' if device.is_active else 'deactivated',
        'permissions': {
            'can_view_history': True,
            'can_view_classes': True,
            'can_view_profile': True,
            'can_view_timetable': True,
            'can_mark_attendance': device.is_active
        }
    }


def check_can_mark_attendance(student_id, device_uuid):
    """
    Quick check if student can mark attendance from this device
    
    Args:
        student_id: Student ID
        device_uuid: Device UUID
        
    Returns:
        Tuple of (can_mark: bool, reason: str or None)
    """
    status = get_device_status(student_id, device_uuid)
    
    if not status['registered']:
        return False, "Device not registered"
    
    if not status['active']:
        return False, "Device is deactivated"
    
    if not status['can_mark_attendance']:
        if status['status'] == 'pending_activation':
            hours_remaining = status['cooldown_info']['hours_remaining']
            return False, f"Device pending activation ({round(hours_remaining, 1)} hours remaining)"
        return False, "Device cannot mark attendance"
    
    return True, None
