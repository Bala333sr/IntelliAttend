#!/usr/bin/env python3
"""
Notification API Endpoints
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text
from app import db, standardize_response, logger

# Create blueprint for notifications
notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/student/notifications')

@notifications_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    """
    GET /api/student/notifications/preferences
    Returns current notification settings
    """
    try:
        student_id = get_jwt_identity()
        
        # Query notification preferences
        query = text("""
            SELECT 
                class_reminder_enabled,
                warm_scan_reminder_enabled,
                attendance_warning_enabled,
                weekly_summary_enabled,
                reminder_minutes_before,
                quiet_hours_start,
                quiet_hours_end
            FROM notification_preferences 
            WHERE student_id = :student_id
        """)
        
        result = db.session.execute(query, {'student_id': student_id})
        row = result.fetchone()
        
        if not row:
            # Return default preferences if none exist
            preferences = {
                'class_reminder_enabled': True,
                'warm_scan_reminder_enabled': True,
                'attendance_warning_enabled': True,
                'weekly_summary_enabled': True,
                'reminder_minutes_before': 10,
                'quiet_hours_start': None,
                'quiet_hours_end': None
            }
        else:
            preferences = {
                'class_reminder_enabled': bool(row.class_reminder_enabled),
                'warm_scan_reminder_enabled': bool(row.warm_scan_reminder_enabled),
                'attendance_warning_enabled': bool(row.attendance_warning_enabled),
                'weekly_summary_enabled': bool(row.weekly_summary_enabled),
                'reminder_minutes_before': row.reminder_minutes_before,
                'quiet_hours_start': str(row.quiet_hours_start) if row.quiet_hours_start else None,
                'quiet_hours_end': str(row.quiet_hours_end) if row.quiet_hours_end else None
            }
        
        return standardize_response({
            'success': True,
            'preferences': preferences
        })
        
    except Exception as e:
        logger.error(f"Error getting notification preferences: {str(e)}")
        return standardize_response({
            'success': False,
            'error': 'Failed to retrieve notification preferences'
        }, 500)

@notifications_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_notification_preferences():
    """
    PUT /api/student/notifications/preferences
    Updates notification preferences
    """
    try:
        student_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return standardize_response({
                'success': False,
                'error': 'No data provided'
            }, 400)
        
        # Upsert notification preferences
        upsert_query = text("""
            INSERT INTO notification_preferences 
            (student_id, class_reminder_enabled, warm_scan_reminder_enabled, 
             attendance_warning_enabled, weekly_summary_enabled, reminder_minutes_before,
             quiet_hours_start, quiet_hours_end)
            VALUES 
            (:student_id, :class_reminder_enabled, :warm_scan_reminder_enabled,
             :attendance_warning_enabled, :weekly_summary_enabled, :reminder_minutes_before,
             :quiet_hours_start, :quiet_hours_end)
            ON DUPLICATE KEY UPDATE
            class_reminder_enabled = VALUES(class_reminder_enabled),
            warm_scan_reminder_enabled = VALUES(warm_scan_reminder_enabled),
            attendance_warning_enabled = VALUES(attendance_warning_enabled),
            weekly_summary_enabled = VALUES(weekly_summary_enabled),
            reminder_minutes_before = VALUES(reminder_minutes_before),
            quiet_hours_start = VALUES(quiet_hours_start),
            quiet_hours_end = VALUES(quiet_hours_end),
            updated_at = CURRENT_TIMESTAMP
        """)
        
        db.session.execute(upsert_query, {
            'student_id': student_id,
            'class_reminder_enabled': bool(data.get('class_reminder_enabled', True)),
            'warm_scan_reminder_enabled': bool(data.get('warm_scan_reminder_enabled', True)),
            'attendance_warning_enabled': bool(data.get('attendance_warning_enabled', True)),
            'weekly_summary_enabled': bool(data.get('weekly_summary_enabled', True)),
            'reminder_minutes_before': int(data.get('reminder_minutes_before', 10)),
            'quiet_hours_start': data.get('quiet_hours_start'),
            'quiet_hours_end': data.get('quiet_hours_end')
        })
        
        db.session.commit()
        
        return standardize_response({
            'success': True,
            'message': 'Notification preferences updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating notification preferences: {str(e)}")
        db.session.rollback()
        return standardize_response({
            'success': False,
            'error': 'Failed to update notification preferences'
        }, 500)

@notifications_bp.route('/history', methods=['GET'])
@jwt_required()
def get_notification_history():
    """
    GET /api/student/notifications/history
    Returns notification history
    """
    try:
        student_id = get_jwt_identity()
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Query notification history
        query = text("""
            SELECT 
                id,
                notification_type,
                title,
                message,
                sent_at,
                read_at,
                action_taken
            FROM notification_log 
            WHERE student_id = :student_id
            ORDER BY sent_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = db.session.execute(query, {
            'student_id': student_id,
            'limit': limit,
            'offset': offset
        })
        
        notifications = []
        for row in result:
            notification = {
                'id': row.id,
                'type': row.notification_type,
                'title': row.title,
                'message': row.message,
                'sent_at': row.sent_at.isoformat() if row.sent_at else None,
                'read_at': row.read_at.isoformat() if row.read_at else None,
                'action_taken': bool(row.action_taken)
            }
            notifications.append(notification)
        
        return standardize_response({
            'success': True,
            'notifications': notifications
        })
        
    except Exception as e:
        logger.error(f"Error getting notification history: {str(e)}")
        return standardize_response({
            'success': False,
            'error': 'Failed to retrieve notification history'
        }, 500)

@notifications_bp.route('/test', methods=['POST'])
@jwt_required()
def send_test_notification():
    """
    POST /api/student/notifications/test
    Sends a test notification
    """
    try:
        student_id = get_jwt_identity()
        
        # In a real implementation, this would send an actual notification
        # For now, we'll just log it and return success
        
        # Log the test notification
        insert_query = text("""
            INSERT INTO notification_log 
            (student_id, notification_type, title, message)
            VALUES 
            (:student_id, 'class_reminder', 'Test Notification', 'This is a test notification from IntelliAttend')
        """)
        
        db.session.execute(insert_query, {
            'student_id': student_id
        })
        
        db.session.commit()
        
        return standardize_response({
            'success': True,
            'message': 'Test notification sent successfully'
        })
        
    except Exception as e:
        logger.error(f"Error sending test notification: {str(e)}")
        db.session.rollback()
        return standardize_response({
            'success': False,
            'error': 'Failed to send test notification'
        }, 500)

@notifications_bp.route('/fcm-token', methods=['POST'])
@jwt_required()
def register_fcm_token():
    """
    POST /api/student/notifications/fcm-token
    Registers FCM token for push notifications (Phase 2)
    """
    try:
        student_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'fcm_token' not in data:
            return standardize_response({
                'success': False,
                'error': 'FCM token is required'
            }, 400)
        
        # In a real implementation, this would store the FCM token
        # For now, we'll just return success
        
        logger.info(f"FCM token registered for student {student_id}")
        
        return standardize_response({
            'success': True,
            'message': 'FCM token registered successfully'
        })
        
    except Exception as e:
        logger.error(f"Error registering FCM token: {str(e)}")
        return standardize_response({
            'success': False,
            'error': 'Failed to register FCM token'
        }, 500)