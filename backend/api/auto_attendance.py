#!/usr/bin/env python3
"""
Auto Attendance API Endpoints
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text
from app import db, standardize_response, logger

# Create blueprint for auto-attendance
auto_attendance_bp = Blueprint('auto_attendance', __name__, url_prefix='/api/student/auto-attendance')

@auto_attendance_bp.route('/config', methods=['GET'])
@jwt_required()
def get_auto_attendance_config():
    """
    GET /api/student/auto-attendance/config
    Returns current auto-attendance settings
    """
    try:
        student_id = get_jwt_identity()
        
        # Query auto-attendance configuration
        query = text("""
            SELECT 
                enabled,
                gps_enabled,
                wifi_enabled,
                bluetooth_enabled,
                confidence_threshold,
                require_warm_data,
                auto_submit
            FROM auto_attendance_config 
            WHERE student_id = :student_id
        """)
        
        result = db.session.execute(query, {'student_id': student_id})
        row = result.fetchone()
        
        if not row:
            # Return default configuration if none exists
            config = {
                'enabled': False,
                'gps_enabled': True,
                'wifi_enabled': True,
                'bluetooth_enabled': True,
                'confidence_threshold': 0.85,
                'require_warm_data': True,
                'auto_submit': False
            }
        else:
            config = {
                'enabled': bool(row.enabled),
                'gps_enabled': bool(row.gps_enabled),
                'wifi_enabled': bool(row.wifi_enabled),
                'bluetooth_enabled': bool(row.bluetooth_enabled),
                'confidence_threshold': float(row.confidence_threshold),
                'require_warm_data': bool(row.require_warm_data),
                'auto_submit': bool(row.auto_submit)
            }
        
        return standardize_response({
            'success': True,
            'config': config
        })
        
    except Exception as e:
        logger.error(f"Error getting auto-attendance config: {str(e)}")
        return standardize_response({
            'success': False,
            'error': 'Failed to retrieve auto-attendance configuration'
        }, 500)

@auto_attendance_bp.route('/config', methods=['PUT'])
@jwt_required()
def update_auto_attendance_config():
    """
    PUT /api/student/auto-attendance/config
    Updates auto-attendance configuration
    """
    try:
        student_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return standardize_response({
                'success': False,
                'error': 'No data provided'
            }, 400)
        
        # Upsert auto-attendance configuration
        upsert_query = text("""
            INSERT INTO auto_attendance_config 
            (student_id, enabled, gps_enabled, wifi_enabled, bluetooth_enabled,
             confidence_threshold, require_warm_data, auto_submit)
            VALUES 
            (:student_id, :enabled, :gps_enabled, :wifi_enabled, :bluetooth_enabled,
             :confidence_threshold, :require_warm_data, :auto_submit)
            ON DUPLICATE KEY UPDATE
            enabled = VALUES(enabled),
            gps_enabled = VALUES(gps_enabled),
            wifi_enabled = VALUES(wifi_enabled),
            bluetooth_enabled = VALUES(bluetooth_enabled),
            confidence_threshold = VALUES(confidence_threshold),
            require_warm_data = VALUES(require_warm_data),
            auto_submit = VALUES(auto_submit),
            updated_at = CURRENT_TIMESTAMP
        """)
        
        db.session.execute(upsert_query, {
            'student_id': student_id,
            'enabled': bool(data.get('enabled', False)),
            'gps_enabled': bool(data.get('gps_enabled', True)),
            'wifi_enabled': bool(data.get('wifi_enabled', True)),
            'bluetooth_enabled': bool(data.get('bluetooth_enabled', True)),
            'confidence_threshold': float(data.get('confidence_threshold', 0.85)),
            'require_warm_data': bool(data.get('require_warm_data', True)),
            'auto_submit': bool(data.get('auto_submit', False))
        })
        
        db.session.commit()
        
        return standardize_response({
            'success': True,
            'message': 'Auto-attendance configuration updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating auto-attendance config: {str(e)}")
        db.session.rollback()
        return standardize_response({
            'success': False,
            'error': 'Failed to update auto-attendance configuration'
        }, 500)

@auto_attendance_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_presence():
    """
    POST /api/student/auto-attendance/verify
    Verifies presence based on sensor data, returns confidence score
    """
    try:
        student_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return standardize_response({
                'success': False,
                'error': 'No data provided'
            }, 400)
        
        session_id = data.get('session_id')
        if not session_id:
            return standardize_response({
                'success': False,
                'error': 'Session ID is required'
            }, 400)
        
        # Extract sensor data
        gps_data = data.get('gps_data', {})
        wifi_data = data.get('wifi_data', {})
        bluetooth_data = data.get('bluetooth_data', [])
        
        # Calculate confidence scores for each sensor
        gps_score = _calculate_gps_score(gps_data, session_id)
        wifi_score = _calculate_wifi_score(wifi_data, session_id)
        bluetooth_score = _calculate_bluetooth_score(bluetooth_data, session_id)
        
        # Get student's configuration to determine which sensors to use
        config_query = text("""
            SELECT gps_enabled, wifi_enabled, bluetooth_enabled, confidence_threshold
            FROM auto_attendance_config 
            WHERE student_id = :student_id
        """)
        
        config_result = db.session.execute(config_query, {'student_id': student_id})
        config_row = config_result.fetchone()
        
        if not config_row:
            # Use default configuration if none exists
            gps_enabled = True
            wifi_enabled = True
            bluetooth_enabled = True
            confidence_threshold = 0.85
        else:
            gps_enabled = bool(config_row.gps_enabled)
            wifi_enabled = bool(config_row.wifi_enabled)
            bluetooth_enabled = bool(config_row.bluetooth_enabled)
            confidence_threshold = float(config_row.confidence_threshold)
        
        # Calculate weighted final confidence score
        # Only include sensors that are enabled in the configuration
        total_weight = 0
        weighted_score = 0
        
        if gps_enabled:
            total_weight += 0.4
            weighted_score += gps_score * 0.4
            
        if wifi_enabled:
            total_weight += 0.3
            weighted_score += wifi_score * 0.3
            
        if bluetooth_enabled:
            total_weight += 0.3
            weighted_score += bluetooth_score * 0.3
            
        # Normalize the score based on total weight
        final_confidence = weighted_score / total_weight if total_weight > 0 else 0
        
        # Determine action based on confidence threshold
        if final_confidence >= confidence_threshold:
            action = 'auto_marked'
        elif final_confidence >= 0.65:
            action = 'suggested'
        else:
            action = 'ignored'
        
        # Prepare response
        response_data = {
            'success': True,
            'verification_result': {
                'session_id': session_id,
                'gps_score': round(gps_score, 2),
                'wifi_score': round(wifi_score, 2),
                'bluetooth_score': round(bluetooth_score, 2),
                'final_confidence': round(final_confidence, 2),
                'can_auto_mark': action == 'auto_marked',
                'action': action,
                'contributing_factors': []
            }
        }
        
        # Add contributing factors
        if gps_enabled and gps_score > 0:
            response_data['verification_result']['contributing_factors'].append('GPS')
        if wifi_enabled and wifi_score > 0:
            response_data['verification_result']['contributing_factors'].append('WiFi')
        if bluetooth_enabled and bluetooth_score > 0:
            response_data['verification_result']['contributing_factors'].append('Bluetooth')
        
        return standardize_response(response_data)
        
    except Exception as e:
        logger.error(f"Error verifying presence: {str(e)}")
        return standardize_response({
            'success': False,
            'error': 'Failed to verify presence'
        }, 500)

@auto_attendance_bp.route('/mark', methods=['POST'])
@jwt_required()
def auto_mark_attendance():
    """
    POST /api/student/auto-attendance/mark
    Auto-marks attendance if confidence threshold met
    """
    try:
        student_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return standardize_response({
                'success': False,
                'error': 'No data provided'
            }, 400)
        
        session_id = data.get('session_id')
        if not session_id:
            return standardize_response({
                'success': False,
                'error': 'Session ID is required'
            }, 400)
        
        # Verify presence first
        verification_result = _verify_presence_internal(student_id, session_id, data)
        
        if not verification_result['can_auto_mark']:
            return standardize_response({
                'success': False,
                'error': 'Confidence threshold not met for auto-marking'
            }, 400)
        
        # In a real implementation, this would call the existing attendance marking logic
        # For now, we'll just log the auto-marking attempt
        
        # Log the auto-attendance activity
        insert_log_query = text("""
            INSERT INTO auto_attendance_log 
            (student_id, session_id, gps_score, wifi_score, bluetooth_score, 
             final_confidence, action_taken, latitude, longitude, wifi_ssid, bluetooth_devices)
            VALUES 
            (:student_id, :session_id, :gps_score, :wifi_score, :bluetooth_score,
             :final_confidence, :action_taken, :latitude, :longitude, :wifi_ssid, :bluetooth_devices)
        """)
        
        db.session.execute(insert_log_query, {
            'student_id': student_id,
            'session_id': session_id,
            'gps_score': verification_result['gps_score'],
            'wifi_score': verification_result['wifi_score'],
            'bluetooth_score': verification_result['bluetooth_score'],
            'final_confidence': verification_result['final_confidence'],
            'action_taken': 'auto_marked',
            'latitude': data.get('gps_data', {}).get('latitude'),
            'longitude': data.get('gps_data', {}).get('longitude'),
            'wifi_ssid': data.get('wifi_data', {}).get('ssid'),
            'bluetooth_devices': str(data.get('bluetooth_data', []))  # Simplified for now
        })
        
        db.session.commit()
        
        return standardize_response({
            'success': True,
            'message': 'Attendance auto-marked successfully',
            'verification_result': verification_result
        })
        
    except Exception as e:
        logger.error(f"Error auto-marking attendance: {str(e)}")
        db.session.rollback()
        return standardize_response({
            'success': False,
            'error': 'Failed to auto-mark attendance'
        }, 500)

@auto_attendance_bp.route('/activity', methods=['GET'])
@jwt_required()
def get_activity_log():
    """
    GET /api/student/auto-attendance/activity
    Returns activity log for transparency
    """
    try:
        student_id = get_jwt_identity()
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Query activity log
        query = text("""
            SELECT 
                id,
                session_id,
                detected_at,
                gps_score,
                wifi_score,
                bluetooth_score,
                final_confidence,
                action_taken
            FROM auto_attendance_log 
            WHERE student_id = :student_id
            ORDER BY detected_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = db.session.execute(query, {
            'student_id': student_id,
            'limit': limit,
            'offset': offset
        })
        
        activities = []
        for row in result:
            activity = {
                'id': row.id,
                'session_id': row.session_id,
                'detected_at': row.detected_at.isoformat() if row.detected_at else None,
                'gps_score': float(row.gps_score) if row.gps_score else None,
                'wifi_score': float(row.wifi_score) if row.wifi_score else None,
                'bluetooth_score': float(row.bluetooth_score) if row.bluetooth_score else None,
                'final_confidence': float(row.final_confidence) if row.final_confidence else None,
                'action_taken': row.action_taken
            }
            activities.append(activity)
        
        return standardize_response({
            'success': True,
            'activities': activities
        })
        
    except Exception as e:
        logger.error(f"Error getting activity log: {str(e)}")
        return standardize_response({
            'success': False,
            'error': 'Failed to retrieve activity log'
        }, 500)

@auto_attendance_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_statistics():
    """
    GET /api/student/auto-attendance/stats
    Returns statistics: total auto-marked, success rate, etc.
    """
    try:
        student_id = get_jwt_identity()
        
        # Query statistics
        query = text("""
            SELECT 
                COUNT(*) as total_attempts,
                SUM(CASE WHEN action_taken = 'auto_marked' THEN 1 ELSE 0 END) as total_auto_marked,
                AVG(final_confidence) as average_confidence
            FROM auto_attendance_log 
            WHERE student_id = :student_id
        """)
        
        result = db.session.execute(query, {'student_id': student_id})
        row = result.fetchone()
        
        if not row:
            stats = {
                'total_attempts': 0,
                'total_auto_marked': 0,
                'success_rate': 0,
                'average_confidence': 0
            }
        else:
            total_attempts = row.total_attempts or 0
            total_auto_marked = row.total_auto_marked or 0
            average_confidence = float(row.average_confidence) if row.average_confidence else 0
            
            success_rate = (total_auto_marked / total_attempts * 100) if total_attempts > 0 else 0
            
            stats = {
                'total_attempts': total_attempts,
                'total_auto_marked': total_auto_marked,
                'success_rate': round(success_rate, 2),
                'average_confidence': round(average_confidence, 2)
            }
        
        return standardize_response({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting auto-attendance statistics: {str(e)}")
        return standardize_response({
            'success': False,
            'error': 'Failed to retrieve statistics'
        }, 500)

def _calculate_gps_score(gps_data, session_id):
    """
    Calculate GPS confidence score based on proximity to classroom
    """
    try:
        # In a real implementation, you would get the classroom location from the session_id
        # and calculate the distance to determine the score
        # For now, we'll return a mock score based on the data provided
        
        if not gps_data or not gps_data.get('latitude') or not gps_data.get('longitude'):
            return 0.0
        
        # Mock implementation - in a real system, you would:
        # 1. Get classroom coordinates from database using session_id
        # 2. Calculate distance between student and classroom
        # 3. Return score based on distance (closer = higher score)
        
        accuracy = gps_data.get('accuracy', 100)
        
        # Simple mock scoring based on accuracy
        if accuracy <= 10:
            return 1.0
        elif accuracy <= 30:
            return 0.8
        elif accuracy <= 50:
            return 0.6
        else:
            return 0.3
            
    except Exception as e:
        logger.error(f"Error calculating GPS score: {str(e)}")
        return 0.0

def _calculate_wifi_score(wifi_data, session_id):
    """
    Calculate WiFi confidence score based on connected network
    """
    try:
        # In a real implementation, you would check if the connected WiFi network
        # matches the expected classroom network
        # For now, we'll return a mock score based on the data provided
        
        if not wifi_data or not wifi_data.get('ssid'):
            return 0.0
        
        ssid = wifi_data.get('ssid', '')
        
        # Mock implementation - in a real system, you would:
        # 1. Get expected WiFi SSID from database using session_id
        # 2. Check if connected SSID matches expected SSID
        # 3. Return score based on match (exact match = higher score)
        
        # Simple mock scoring
        if 'classroom' in ssid.lower() or 'campus' in ssid.lower():
            return 1.0
        elif ssid:
            return 0.6
        else:
            return 0.0
            
    except Exception as e:
        logger.error(f"Error calculating WiFi score: {str(e)}")
        return 0.0

def _calculate_bluetooth_score(bluetooth_data, session_id):
    """
    Calculate Bluetooth confidence score based on nearby devices
    """
    try:
        # In a real implementation, you would check if known classroom beacons
        # are detected with good signal strength
        # For now, we'll return a mock score based on the data provided
        
        if not bluetooth_data:
            return 0.0
        
        # Mock implementation - in a real system, you would:
        # 1. Get expected Bluetooth beacons from database using session_id
        # 2. Check if known beacons are detected
        # 3. Return score based on signal strength and proximity
        
        device_count = len(bluetooth_data)
        
        # Simple mock scoring based on number of devices detected
        if device_count >= 3:
            return 1.0
        elif device_count >= 2:
            return 0.8
        elif device_count >= 1:
            return 0.6
        else:
            return 0.0
            
    except Exception as e:
        logger.error(f"Error calculating Bluetooth score: {str(e)}")
        return 0.0

def _verify_presence_internal(student_id, session_id, sensor_data):
    """
    Internal function to verify presence (used by auto_mark_attendance)
    """
    try:
        # Extract sensor data
        gps_data = sensor_data.get('gps_data', {})
        wifi_data = sensor_data.get('wifi_data', {})
        bluetooth_data = sensor_data.get('bluetooth_data', [])
        
        # Calculate confidence scores for each sensor
        gps_score = _calculate_gps_score(gps_data, session_id)
        wifi_score = _calculate_wifi_score(wifi_data, session_id)
        bluetooth_score = _calculate_bluetooth_score(bluetooth_data, session_id)
        
        # Get student's configuration to determine which sensors to use
        config_query = text("""
            SELECT gps_enabled, wifi_enabled, bluetooth_enabled, confidence_threshold
            FROM auto_attendance_config 
            WHERE student_id = :student_id
        """)
        
        config_result = db.session.execute(config_query, {'student_id': student_id})
        config_row = config_result.fetchone()
        
        if not config_row:
            # Use default configuration if none exists
            gps_enabled = True
            wifi_enabled = True
            bluetooth_enabled = True
            confidence_threshold = 0.85
        else:
            gps_enabled = bool(config_row.gps_enabled)
            wifi_enabled = bool(config_row.wifi_enabled)
            bluetooth_enabled = bool(config_row.bluetooth_enabled)
            confidence_threshold = float(config_row.confidence_threshold)
        
        # Calculate weighted final confidence score
        # Only include sensors that are enabled in the configuration
        total_weight = 0
        weighted_score = 0
        
        if gps_enabled:
            total_weight += 0.4
            weighted_score += gps_score * 0.4
            
        if wifi_enabled:
            total_weight += 0.3
            weighted_score += wifi_score * 0.3
            
        if bluetooth_enabled:
            total_weight += 0.3
            weighted_score += bluetooth_score * 0.3
            
        # Normalize the score based on total weight
        final_confidence = weighted_score / total_weight if total_weight > 0 else 0
        
        # Determine action based on confidence threshold
        can_auto_mark = final_confidence >= confidence_threshold
        
        return {
            'session_id': session_id,
            'gps_score': round(gps_score, 2),
            'wifi_score': round(wifi_score, 2),
            'bluetooth_score': round(bluetooth_score, 2),
            'final_confidence': round(final_confidence, 2),
            'can_auto_mark': can_auto_mark,
            'action': 'auto_marked' if can_auto_mark else 'suggested',
            'contributing_factors': []
        }
        
    except Exception as e:
        logger.error(f"Error in internal presence verification: {str(e)}")
        return {
            'session_id': session_id,
            'gps_score': 0,
            'wifi_score': 0,
            'bluetooth_score': 0,
            'final_confidence': 0,
            'can_auto_mark': False,
            'action': 'ignored',
            'contributing_factors': []
        }