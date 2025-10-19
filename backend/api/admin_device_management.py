"""
Admin APIs for Device Management
Handles device switch requests, device approvals, and device monitoring
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from models import (
    Users, Students, StudentDevices, DeviceSwitchRequests, 
    DeviceActivityLogs
)
from api.mobile_device_enforcement import (
    deactivate_all_other_devices, log_device_activity,
    DEVICE_SWITCH_COOLDOWN_HOURS
)

admin_device_bp = Blueprint('admin_device', __name__, url_prefix='/api/admin/devices')


def require_admin_role():
    """Verify that the current user is an admin"""
    user_id = get_jwt_identity()
    user = Users.query.get(user_id)
    
    if not user or user.role != 'admin':
        return jsonify({
            'success': False,
            'error': 'Admin access required'
        }), 403
    
    return None


# ==================== DEVICE SWITCH REQUESTS ====================

@admin_device_bp.route('/switch-requests', methods=['GET'])
@jwt_required()
def get_device_switch_requests():
    """
    Get all device switch requests with filtering options
    Query params:
        - status: pending/approved/rejected/all (default: pending)
        - student_code: filter by student code
        - cooldown_complete: true/false - filter by cooldown status
        - page: page number (default: 1)
        - per_page: items per page (default: 20)
    """
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    # Query parameters
    status = request.args.get('status', 'pending')
    student_code = request.args.get('student_code')
    cooldown_complete = request.args.get('cooldown_complete')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # Build query
    query = db.session.query(
        DeviceSwitchRequests,
        Students,
        StudentDevices
    ).join(
        Students, DeviceSwitchRequests.student_id == Students.student_id
    ).outerjoin(
        StudentDevices,
        (DeviceSwitchRequests.new_device_uuid == StudentDevices.device_uuid) &
        (DeviceSwitchRequests.student_id == StudentDevices.student_id)
    )
    
    # Apply filters
    if status != 'all':
        query = query.filter(DeviceSwitchRequests.status == status)
    
    if student_code:
        query = query.filter(Students.student_code.ilike(f'%{student_code}%'))
    
    # Apply cooldown filter if specified
    if cooldown_complete is not None:
        if cooldown_complete.lower() == 'true':
            # Calculate minimum requested_at time for cooldown to be complete
            from datetime import timedelta
            cooldown_threshold = datetime.utcnow() - timedelta(hours=DEVICE_SWITCH_COOLDOWN_HOURS)
            query = query.filter(DeviceSwitchRequests.requested_at <= cooldown_threshold)
        else:
            from datetime import timedelta
            cooldown_threshold = datetime.utcnow() - timedelta(hours=DEVICE_SWITCH_COOLDOWN_HOURS)
            query = query.filter(DeviceSwitchRequests.requested_at > cooldown_threshold)
    
    # Order by requested_at descending
    query = query.order_by(DeviceSwitchRequests.requested_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Format results
    results = []
    for switch_request, student, device in pagination.items:
        # Calculate cooldown status
        hours_elapsed = (datetime.utcnow() - switch_request.requested_at).total_seconds() / 3600
        cooldown_completed = hours_elapsed >= DEVICE_SWITCH_COOLDOWN_HOURS
        hours_remaining = max(0, DEVICE_SWITCH_COOLDOWN_HOURS - hours_elapsed)
        
        results.append({
            'request_id': switch_request.request_id,
            'student': {
                'student_id': student.student_id,
                'student_code': student.student_code,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email
            },
            'device_info': {
                'device_uuid': switch_request.new_device_uuid,
                'device_name': switch_request.new_device_name,
                'device_type': switch_request.new_device_type,
                'device_model': switch_request.new_device_model,
                'old_device_uuid': switch_request.old_device_uuid,
                'old_device_name': switch_request.old_device_name,
                'is_registered': device is not None,
                'is_active': device.is_active if device else False
            },
            'status': switch_request.status,
            'cooldown_status': {
                'completed': cooldown_completed,
                'hours_elapsed': round(hours_elapsed, 1),
                'hours_remaining': round(hours_remaining, 1),
                'total_required_hours': DEVICE_SWITCH_COOLDOWN_HOURS
            },
            'approval_ready': cooldown_completed and switch_request.status == 'pending',
            'reason': switch_request.reason,
            'requested_at': switch_request.requested_at.isoformat(),
            'approved_at': switch_request.approved_at.isoformat() if switch_request.approved_at else None,
            'rejected_at': switch_request.rejected_at.isoformat() if switch_request.rejected_at else None,
            'rejected_reason': switch_request.rejected_reason,
            'approved_by_admin_id': switch_request.approved_by_admin_id,
            'completed_at': switch_request.completed_at.isoformat() if switch_request.completed_at else None
        })
    
    return jsonify({
        'success': True,
        'requests': results,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@admin_device_bp.route('/switch-requests/<int:request_id>', methods=['GET'])
@jwt_required()
def get_device_switch_request_detail(request_id):
    """Get detailed information about a specific device switch request"""
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    switch_request = DeviceSwitchRequests.query.get(request_id)
    if not switch_request:
        return jsonify({
            'success': False,
            'error': 'Device switch request not found'
        }), 404
    
    student = Students.query.get(switch_request.student_id)
    device = StudentDevices.query.filter_by(
        student_id=switch_request.student_id,
        device_uuid=switch_request.new_device_uuid
    ).first()
    
    # Get old device info
    old_device = None
    if switch_request.old_device_uuid:
        old_device = StudentDevices.query.filter_by(
            student_id=switch_request.student_id,
            device_uuid=switch_request.old_device_uuid
        ).first()
    
    # Get device activity logs
    activity_logs = DeviceActivityLogs.query.filter_by(
        student_id=switch_request.student_id,
        device_uuid=switch_request.new_device_uuid
    ).order_by(DeviceActivityLogs.activity_timestamp.desc()).limit(10).all()
    
    # Calculate cooldown status
    hours_elapsed = (datetime.utcnow() - switch_request.requested_at).total_seconds() / 3600
    cooldown_completed = hours_elapsed >= DEVICE_SWITCH_COOLDOWN_HOURS
    hours_remaining = max(0, DEVICE_SWITCH_COOLDOWN_HOURS - hours_elapsed)
    
    return jsonify({
        'success': True,
        'request': {
            'request_id': switch_request.request_id,
            'student': {
                'student_id': student.student_id,
                'student_code': student.student_code,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone': student.phone
            },
            'new_device': {
                'device_uuid': switch_request.new_device_uuid,
                'device_name': switch_request.new_device_name,
                'device_type': switch_request.new_device_type,
                'device_model': switch_request.new_device_model,
                'is_registered': device is not None,
                'is_active': device.is_active if device else False,
                'activated_at': device.activated_at.isoformat() if device and device.activated_at else None
            },
            'old_device': {
                'device_uuid': switch_request.old_device_uuid,
                'device_name': switch_request.old_device_name,
                'is_active': old_device.is_active if old_device else False,
                'last_seen': old_device.last_seen.isoformat() if old_device and old_device.last_seen else None
            } if switch_request.old_device_uuid else None,
            'status': switch_request.status,
            'cooldown_status': {
                'completed': cooldown_completed,
                'hours_elapsed': round(hours_elapsed, 1),
                'hours_remaining': round(hours_remaining, 1),
                'total_required_hours': DEVICE_SWITCH_COOLDOWN_HOURS,
                'percentage_complete': min(100, round((hours_elapsed / DEVICE_SWITCH_COOLDOWN_HOURS) * 100, 1))
            },
            'approval_ready': cooldown_completed and switch_request.status == 'pending',
            'reason': switch_request.reason,
            'requested_at': switch_request.requested_at.isoformat(),
            'approved_at': switch_request.approved_at.isoformat() if switch_request.approved_at else None,
            'rejected_at': switch_request.rejected_at.isoformat() if switch_request.rejected_at else None,
            'rejected_reason': switch_request.rejected_reason,
            'approved_by_admin_id': switch_request.approved_by_admin_id,
            'completed_at': switch_request.completed_at.isoformat() if switch_request.completed_at else None,
            'activity_logs': [{
                'log_id': log.log_id,
                'activity_type': log.activity_type,
                'activity_timestamp': log.activity_timestamp.isoformat(),
                'additional_info': log.additional_info
            } for log in activity_logs]
        }
    }), 200


@admin_device_bp.route('/switch-requests/<int:request_id>/approve', methods=['POST'])
@jwt_required()
def approve_device_switch_request(request_id):
    """
    Approve a device switch request
    This will activate the new device (if cooldown is also complete)
    
    Request body:
        - notes (optional): admin notes about the approval
    """
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    admin_id = get_jwt_identity()
    
    switch_request = DeviceSwitchRequests.query.get(request_id)
    if not switch_request:
        return jsonify({
            'success': False,
            'error': 'Device switch request not found'
        }), 404
    
    if switch_request.status != 'pending':
        return jsonify({
            'success': False,
            'error': f'Cannot approve request with status: {switch_request.status}'
        }), 400
    
    data = request.get_json() or {}
    admin_notes = data.get('notes', '')
    
    # Calculate cooldown status
    hours_elapsed = (datetime.utcnow() - switch_request.requested_at).total_seconds() / 3600
    cooldown_completed = hours_elapsed >= DEVICE_SWITCH_COOLDOWN_HOURS
    
    # Update request status to approved
    switch_request.status = 'approved'
    switch_request.approved_at = datetime.utcnow()
    switch_request.approved_by_admin_id = admin_id
    
    if admin_notes:
        if not switch_request.additional_info:
            switch_request.additional_info = {}
        switch_request.additional_info['admin_notes'] = admin_notes
    
    # If cooldown is also complete, activate the device immediately
    device_activated = False
    if cooldown_completed:
        # Deactivate all other devices
        deactivate_all_other_devices(
            switch_request.student_id,
            switch_request.new_device_uuid
        )
        
        # Activate the new device
        device = StudentDevices.query.filter_by(
            student_id=switch_request.student_id,
            device_uuid=switch_request.new_device_uuid
        ).first()
        
        if device:
            device.is_active = True
            device.activated_at = datetime.utcnow()
            device.last_seen = datetime.utcnow()
        else:
            # Create device if it doesn't exist
            device = StudentDevices(
                student_id=switch_request.student_id,
                device_uuid=switch_request.new_device_uuid,
                device_name=switch_request.new_device_name,
                device_type=switch_request.new_device_type,
                device_model=switch_request.new_device_model,
                is_active=True
            )
            device.activated_at = datetime.utcnow()
            db.session.add(device)
        
        # Mark request as completed
        switch_request.completed_at = datetime.utcnow()
        device_activated = True
        
        # Log device activation
        log_device_activity(
            student_id=switch_request.student_id,
            device_uuid=switch_request.new_device_uuid,
            activity_type='device_activated',
            additional_info={
                'activation_type': 'admin_approved_with_cooldown',
                'admin_id': admin_id,
                'hours_elapsed': round(hours_elapsed, 1),
                'admin_notes': admin_notes
            }
        )
    else:
        # Cooldown not complete yet, device will be activated when student logs in next
        log_device_activity(
            student_id=switch_request.student_id,
            device_uuid=switch_request.new_device_uuid,
            activity_type='switch_request_approved',
            additional_info={
                'admin_id': admin_id,
                'hours_elapsed': round(hours_elapsed, 1),
                'hours_remaining': round(DEVICE_SWITCH_COOLDOWN_HOURS - hours_elapsed, 1),
                'admin_notes': admin_notes,
                'activation_pending': 'cooldown_incomplete'
            }
        )
    
    db.session.commit()
    
    message = (
        'Device switch approved and activated!' if device_activated else
        f'Device switch approved! Device will be activated after cooldown completes ({round(DEVICE_SWITCH_COOLDOWN_HOURS - hours_elapsed, 1)} hours remaining).'
    )
    
    return jsonify({
        'success': True,
        'message': message,
        'request_id': request_id,
        'status': 'approved',
        'device_activated': device_activated,
        'cooldown_completed': cooldown_completed,
        'hours_elapsed': round(hours_elapsed, 1)
    }), 200


@admin_device_bp.route('/switch-requests/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def reject_device_switch_request(request_id):
    """
    Reject a device switch request
    
    Request body:
        - reason (required): reason for rejection
    """
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    admin_id = get_jwt_identity()
    
    switch_request = DeviceSwitchRequests.query.get(request_id)
    if not switch_request:
        return jsonify({
            'success': False,
            'error': 'Device switch request not found'
        }), 404
    
    if switch_request.status != 'pending':
        return jsonify({
            'success': False,
            'error': f'Cannot reject request with status: {switch_request.status}'
        }), 400
    
    data = request.get_json()
    if not data or not data.get('reason'):
        return jsonify({
            'success': False,
            'error': 'Rejection reason is required'
        }), 400
    
    rejection_reason = data['reason']
    
    # Update request status
    switch_request.status = 'rejected'
    switch_request.rejected_at = datetime.utcnow()
    switch_request.rejected_reason = rejection_reason
    switch_request.approved_by_admin_id = admin_id  # Track who rejected it
    
    # Log rejection
    log_device_activity(
        student_id=switch_request.student_id,
        device_uuid=switch_request.new_device_uuid,
        activity_type='switch_request_rejected',
        additional_info={
            'admin_id': admin_id,
            'rejection_reason': rejection_reason
        }
    )
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Device switch request rejected',
        'request_id': request_id,
        'status': 'rejected',
        'rejection_reason': rejection_reason
    }), 200


# ==================== DEVICE MANAGEMENT ====================

@admin_device_bp.route('/students/<string:student_code>/devices', methods=['GET'])
@jwt_required()
def get_student_devices(student_code):
    """Get all devices for a specific student"""
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    student = Students.query.filter_by(student_code=student_code).first()
    if not student:
        return jsonify({
            'success': False,
            'error': 'Student not found'
        }), 404
    
    devices = StudentDevices.query.filter_by(student_id=student.student_id).all()
    
    # Get pending switch requests
    pending_requests = DeviceSwitchRequests.query.filter_by(
        student_id=student.student_id,
        status='pending'
    ).all()
    
    return jsonify({
        'success': True,
        'student': {
            'student_id': student.student_id,
            'student_code': student.student_code,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email
        },
        'devices': [{
            'device_id': device.device_id,
            'device_uuid': device.device_uuid,
            'device_name': device.device_name,
            'device_type': device.device_type,
            'device_model': device.device_model,
            'os_version': device.os_version,
            'app_version': device.app_version,
            'is_active': device.is_active,
            'registered_at': device.registered_at.isoformat(),
            'activated_at': device.activated_at.isoformat() if device.activated_at else None,
            'last_seen': device.last_seen.isoformat() if device.last_seen else None
        } for device in devices],
        'pending_switch_requests': [{
            'request_id': req.request_id,
            'new_device_uuid': req.new_device_uuid,
            'new_device_name': req.new_device_name,
            'requested_at': req.requested_at.isoformat(),
            'reason': req.reason
        } for req in pending_requests]
    }), 200


@admin_device_bp.route('/students/<string:student_code>/devices/<string:device_uuid>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_device(student_code, device_uuid):
    """Manually deactivate a device (admin override)"""
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    admin_id = get_jwt_identity()
    
    student = Students.query.filter_by(student_code=student_code).first()
    if not student:
        return jsonify({
            'success': False,
            'error': 'Student not found'
        }), 404
    
    device = StudentDevices.query.filter_by(
        student_id=student.student_id,
        device_uuid=device_uuid
    ).first()
    
    if not device:
        return jsonify({
            'success': False,
            'error': 'Device not found'
        }), 404
    
    data = request.get_json() or {}
    reason = data.get('reason', 'Admin deactivation')
    
    # Deactivate device
    device.is_active = False
    
    # Log activity
    log_device_activity(
        student_id=student.student_id,
        device_uuid=device_uuid,
        activity_type='device_deactivated',
        additional_info={
            'deactivated_by': 'admin',
            'admin_id': admin_id,
            'reason': reason
        }
    )
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Device deactivated successfully',
        'device_uuid': device_uuid
    }), 200


@admin_device_bp.route('/students/<string:student_code>/devices/<string:device_uuid>/emergency-activate', methods=['POST'])
@jwt_required()
def emergency_activate_device(student_code, device_uuid):
    """
    Emergency device activation (bypasses 48-hour cooldown)
    Use for emergencies like lost phone, broken device, etc.
    
    Request body:
        - reason (required): reason for emergency activation
        - admin_notes (optional): additional admin notes
    """
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    admin_id = get_jwt_identity()
    
    student = Students.query.filter_by(student_code=student_code).first()
    if not student:
        return jsonify({
            'success': False,
            'error': 'Student not found'
        }), 404
    
    data = request.get_json()
    if not data or not data.get('reason'):
        return jsonify({
            'success': False,
            'error': 'Emergency activation reason is required'
        }), 400
    
    reason = data['reason']
    admin_notes = data.get('admin_notes', '')
    
    try:
        # Check if there's a pending device switch request
        pending_request = DeviceSwitchRequests.query.filter_by(
            student_id=student.student_id,
            new_device_uuid=device_uuid,
            status='pending'
        ).first()
        
        if pending_request:
            # Approve the pending request immediately
            pending_request.status = 'approved'
            pending_request.approved_at = datetime.utcnow()
            pending_request.approved_by_admin_id = admin_id
            pending_request.completed_at = datetime.utcnow()
            
            if not pending_request.additional_info:
                pending_request.additional_info = {}
            pending_request.additional_info['emergency_activation'] = True
            pending_request.additional_info['emergency_reason'] = reason
            pending_request.additional_info['admin_notes'] = admin_notes
        
        # Deactivate all other devices
        deactivate_all_other_devices(student.student_id, device_uuid)
        
        # Get or create the device
        device = StudentDevices.query.filter_by(
            student_id=student.student_id,
            device_uuid=device_uuid
        ).first()
        
        if device:
            device.is_active = True
            device.activated_at = datetime.utcnow()
            device.last_seen = datetime.utcnow()
        else:
            # If device doesn't exist, create it (shouldn't normally happen but handle it)
            device = StudentDevices(
                student_id=student.student_id,
                device_uuid=device_uuid,
                device_name='Emergency Device',
                device_type='unknown',
                is_active=True
            )
            device.activated_at = datetime.utcnow()
            db.session.add(device)
        
        # Log emergency activation
        log_device_activity(
            student_id=student.student_id,
            device_uuid=device_uuid,
            activity_type='emergency_activation',
            additional_info={
                'admin_id': admin_id,
                'reason': reason,
                'admin_notes': admin_notes,
                'bypassed_cooldown': True,
                'activation_type': 'emergency_override'
            }
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Device activated immediately (emergency override)',
            'device_uuid': device_uuid,
            'student_code': student_code,
            'emergency_activation': True,
            'bypassed_cooldown': True,
            'admin_id': admin_id,
            'activation_timestamp': device.activated_at.isoformat()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Emergency activation failed: {str(e)}'
        }), 500


@admin_device_bp.route('/activity-logs', methods=['GET'])
@jwt_required()
def get_device_activity_logs():
    """
    Get device activity logs with filtering
    Query params:
        - student_code: filter by student
        - device_uuid: filter by device
        - activity_type: filter by activity type
        - start_date: filter logs after this date (ISO format)
        - end_date: filter logs before this date (ISO format)
        - page: page number (default: 1)
        - per_page: items per page (default: 50)
    """
    admin_check = require_admin_role()
    if admin_check:
        return admin_check
    
    # Query parameters
    student_code = request.args.get('student_code')
    device_uuid = request.args.get('device_uuid')
    activity_type = request.args.get('activity_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    # Build query
    query = db.session.query(DeviceActivityLogs, Students).join(
        Students, DeviceActivityLogs.student_id == Students.student_id
    )
    
    # Apply filters
    if student_code:
        query = query.filter(Students.student_code == student_code)
    
    if device_uuid:
        query = query.filter(DeviceActivityLogs.device_uuid == device_uuid)
    
    if activity_type:
        query = query.filter(DeviceActivityLogs.activity_type == activity_type)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(DeviceActivityLogs.activity_timestamp >= start_dt)
        except:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(DeviceActivityLogs.activity_timestamp <= end_dt)
        except:
            pass
    
    # Order by timestamp descending
    query = query.order_by(DeviceActivityLogs.activity_timestamp.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Format results
    results = []
    for log, student in pagination.items:
        results.append({
            'log_id': log.log_id,
            'student': {
                'student_id': student.student_id,
                'student_code': student.student_code,
                'first_name': student.first_name,
                'last_name': student.last_name
            },
            'device_uuid': log.device_uuid,
            'activity_type': log.activity_type,
            'activity_timestamp': log.activity_timestamp.isoformat(),
            'additional_info': log.additional_info
        })
    
    return jsonify({
        'success': True,
        'logs': results,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200
