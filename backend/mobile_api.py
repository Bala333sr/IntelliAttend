#!/usr/bin/env python3
"""
Mobile API endpoints for IntelliAttend
Handles communication between mobile application and server
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, get_jwt
from sqlalchemy import text
from datetime import datetime, timedelta
import json
import logging

# Create blueprint for mobile API
mobile_bp = Blueprint('mobile', __name__, url_prefix='/api/mobile')

# Set up logging
logger = logging.getLogger(__name__)

@mobile_bp.route('/device/connect', methods=['POST'])
def device_connect():
    """
    Register/connect a mobile device to the system
    This endpoint is called when a device first connects to the server
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Extract device information
        device_info = data.get('device_info', {})
        device_uuid = device_info.get('device_id')
        device_name = device_info.get('device_name', 'Unknown Device')
        device_type = device_info.get('device_type', 'android')
        device_model = device_info.get('device_model')
        os_version = device_info.get('os_version')
        app_version = device_info.get('app_version')
        
        if not device_uuid:
            return jsonify({'error': 'Device ID is required'}), 400
        
        # Check if device already exists
        device = StudentDevices.query.filter(
            getattr(StudentDevices, 'device_uuid') == device_uuid
        ).first()
        
        if device:
            # Update existing device
            device.last_seen = datetime.utcnow()
            device.device_name = device_name
            device.device_type = device_type
            device.device_model = device_model
            device.os_version = os_version
            device.app_version = app_version
            db.session.commit()
            
            # Check if device is associated with a student
            student = Student.query.get(device.student_id) if device.student_id else None
            
            response_data = {
                'success': True,
                'device_id': device.device_id,
                'device_uuid': device.device_uuid,
                'is_registered': device.student_id is not None,
                'student_email': student.email if student else None,
                'message': 'Device reconnected successfully'
            }
        else:
            # Attempt to create a new device record with nullable student_id
            try:
                new_device = StudentDevices(
                    student_id=None,
                    device_uuid=device_uuid,
                    device_type=device_type,
                    device_name=device_name,
                    device_model=device_model,
                    os_version=os_version,
                    app_version=app_version,
                    fcm_token=None,
                    is_active=True,
                    biometric_enabled=False,
                    location_permission=False,
                    bluetooth_permission=False
                )
                db.session.add(new_device)
                db.session.commit()
                response_data = {
                    'success': True,
                    'device_id': new_device.device_id,
                    'device_uuid': new_device.device_uuid,
                    'is_registered': False,
                    'student_email': None,
                    'message': 'Device registered successfully'
                }
            except Exception as e:
                logger.error(f"Failed to insert device record, likely DB constraint: {str(e)}")
                # Fallback response if underlying DB has NOT NULL constraint on student_id
                response_data = {
                    'success': True,
                    'device_id': None,
                    'device_uuid': device_uuid,
                    'is_registered': False,
                    'student_email': None,
                    'message': 'Device registration acknowledged; database update required'
                }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Error connecting device: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/student/login', methods=['POST'])
def student_login():
    """
    Login endpoint for students using email and password
    Returns JWT token for authenticated access
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db, create_access_token
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        email = data.get('email')
        password = data.get('password')
        device_uuid = data.get('device_uuid')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find student by email
        student = Student.query.filter_by(email=email).first()
        
        if not student or not student.is_active:
            return jsonify({'error': 'Invalid credentials or inactive account'}), 401
        
        # Check password
        if not check_password(password, student.password_hash):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT tokens using the same approach as the main app
        claims = {'type': 'student', 'student_id': student.student_id}
        access_token = create_access_token(
            identity=str(student.student_id),
            additional_claims=claims
        )
        
        # Associate device with student if device_uuid is provided
        if device_uuid:
            device = StudentDevices.query.filter_by(device_uuid=device_uuid).first()
            
            if device:
                device.student_id = student.student_id
                device.last_seen = datetime.utcnow()
                db.session.commit()
        
        # Prepare response
        response_data = {
            'success': True,
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
            'message': 'Login successful'
        }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Error during student login: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/device/status', methods=['GET'])
@jwt_required()
def get_device_status():
    """
    Get device status and permissions for the current student
    Shows if phone is connected and which account is logged in
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        # Get student details
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get all devices for this student
        devices = StudentDevices.query.filter_by(student_id=student_id).all()
        
        device_list = []
        for device in devices:
            device_list.append({
                'device_id': device.device_id,
                'device_uuid': device.device_uuid,
                'device_name': device.device_name,
                'device_type': device.device_type,
                'device_model': device.device_model,
                'os_version': device.os_version,
                'app_version': device.app_version,
                'is_active': device.is_active,
                'location_permission': device.location_permission,
                'bluetooth_permission': device.bluetooth_permission,
                'biometric_enabled': device.biometric_enabled,
                'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                'is_online': (datetime.utcnow() - device.last_seen).total_seconds() < 300 if device.last_seen else False  # Online if seen in last 5 minutes
            })
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'student_email': student.email,
            'devices': device_list,
            'message': 'Device status retrieved successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting device status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/data/collect', methods=['POST'])
@jwt_required()
def collect_mobile_data():
    """
    Collect data from mobile device in JSON format
    This endpoint receives all sensor data from the mobile app
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        # Get student details
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
            
        student_email = student.email
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Log the received data for debugging
        logger.info(f"Data collection from student {student_email} (ID: {student_id}): {json.dumps(data, indent=2)}")
        
        # Extract different types of data
        device_info = data.get('device_info', {})
        location_data = data.get('location', {})
        bluetooth_data = data.get('bluetooth', {})
        wifi_data = data.get('wifi', {})
        sensor_data = data.get('sensors', {})
        attendance_data = data.get('attendance', {})
        
        # Update device information
        device_uuid = device_info.get('device_id')
        if device_uuid:
            device = StudentDevices.query.filter_by(device_uuid=device_uuid, student_id=student_id).first()
            
            if device:
                device.last_seen = datetime.utcnow()
                device.location_permission = device_info.get('location_permission', device.location_permission)
                device.bluetooth_permission = device_info.get('bluetooth_permission', device.bluetooth_permission)
                device.biometric_enabled = device_info.get('biometric_enabled', device.biometric_enabled)
                db.session.commit()
        
        # Prepare response with detailed information about received data
        response_data = {
            'success': True,
            'student_id': student_id,
            'student_email': student_email,
            'timestamp': datetime.utcnow().isoformat(),
            'data_summary': {
                'has_device_info': bool(device_info),
                'has_location_data': bool(location_data),
                'has_bluetooth_data': bool(bluetooth_data),
                'has_wifi_data': bool(wifi_data),
                'has_sensor_data': bool(sensor_data),
                'has_attendance_data': bool(attendance_data)
            },
            'device_info': {
                'device_id': device_uuid,
                'device_name': device_info.get('device_name'),
                'device_type': device_info.get('device_type'),
                'os_version': device_info.get('os_version'),
                'app_version': device_info.get('app_version')
            },
            'message': 'Data collected successfully'
        }
        
        # Add detailed counts if data is present
        if bluetooth_data:
            response_data['data_summary']['bluetooth_device_count'] = len(bluetooth_data.get('devices', []))
        
        if wifi_data:
            response_data['data_summary']['wifi_network_count'] = len(wifi_data.get('networks', []))
        
        if location_data:
            response_data['data_summary']['location_accuracy'] = location_data.get('accuracy')
        
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Error collecting mobile data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# NEW ENDPOINTS FOR MOBILE APP INTEGRATION
# ============================================================================

@mobile_bp.route('/logout', methods=['POST'])
@jwt_required()
def mobile_logout():
    """Logout mobile device"""
    try:
        # Import models and JWT components within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db, jwt_blacklist, jwt_blacklist_lock
        
        # Get JWT claims
        claims = get_jwt()
        jti = claims['jti']
        student_id = claims.get('student_id')
        
        # Add token to blacklist
        with jwt_blacklist_lock:
            jwt_blacklist.add(jti)
        
        # Clear device last_seen if device_uuid provided
        data = request.get_json()
        device_uuid = data.get('device_uuid') if data else None
        
        if device_uuid:
            device = StudentDevices.query.filter_by(
                student_id=student_id,
                device_uuid=device_uuid
            ).first()
            
            if device:
                device.last_seen = None
                db.session.commit()
        
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    except Exception as e:
        logger.error(f"Error during mobile logout: {e}")
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/session/status/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session_status(session_id):
    """Check if session is still active before scanning"""
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        # Get session
        session = AttendanceSession.query.get(session_id)
        
        if not session:
            return jsonify({'active': False, 'reason': 'Session not found'}), 404
        
        # Check if session is active
        is_active = session.status == 'active'
        
        # Check if QR token has expired
        is_expired = False
        if session.qr_expires_at and datetime.utcnow() > session.qr_expires_at:
            is_expired = True
            is_active = False
        
        # Get class information
        class_obj = Classes.query.get(session.class_id) if session.class_id else None
        
        response_data = {
            'active': is_active,
            'session_id': session_id,
            'status': session.status,
            'expires_at': session.qr_expires_at.isoformat() if session.qr_expires_at else None,
            'is_expired': is_expired,
            'class_name': class_obj.class_name if class_obj else None,
            'class_code': class_obj.class_code if class_obj else None
        }
        
        if not is_active:
            if is_expired:
                response_data['reason'] = 'Session expired'
            elif session.status == 'completed':
                response_data['reason'] = 'Session completed'
            elif session.status == 'cancelled':
                response_data['reason'] = 'Session cancelled'
            else:
                response_data['reason'] = 'Session inactive'
        
        return jsonify(response_data), 200
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/student/timetable/today', methods=['GET'])
@jwt_required()
def get_todays_timetable():
    """Get today's timetable for the current student"""
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
            from sqlalchemy import text
            from datetime import datetime
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        # Get current day of week in uppercase format (as stored in DB)
        day_of_week = datetime.now().strftime('%A').upper()
        
        # Get the student's section
        student_query = text("""
            SELECT s.student_code, s.first_name, s.last_name, sec.id as section_id, sec.section_name
            FROM students s
            JOIN sections sec ON s.section_id = sec.id
            WHERE s.student_id = :student_id
        """)
        
        student_result = db.session.execute(student_query, {'student_id': student_id})
        student_row = student_result.fetchone()
        
        if not student_row:
            return jsonify({'error': 'Student not found'}), 404
        
        section_id = student_row.section_id
        
        # Get timetable for the student's section, excluding breaks/lunch/free slots
        timetable_query = text("""
            SELECT t.id, t.day_of_week, t.slot_number, t.slot_type, 
                   t.start_time, t.end_time, t.subject_code, s.subject_name, s.short_name, s.faculty_name, t.room_number
            FROM timetable t
            LEFT JOIN subjects s ON t.subject_code = s.subject_code
            WHERE t.section_id = :section_id 
            AND t.day_of_week = :day_of_week
            AND t.slot_type NOT IN ('break', 'lunch', 'free')
            AND t.subject_code IS NOT NULL 
            AND t.subject_code != ''
            ORDER BY t.slot_number, t.start_time
        """)
        
        result = db.session.execute(timetable_query, {'section_id': section_id, 'day_of_week': day_of_week})
        sessions = []
        
        for row in result:
            sessions.append({
                'id': row.id,
                'subject_id': 0,  # Placeholder - subject_id not in timetable table
                'subject_name': row.subject_name if row.subject_name else row.subject_code,
                'subject_code': row.subject_code,
                'short_name': row.short_name if row.short_name else row.subject_code,
                'teacher_name': row.faculty_name if row.faculty_name else 'TBA',
                'room_number': row.room_number,
                'start_time': str(row.start_time) if row.start_time else None,
                'end_time': str(row.end_time) if row.end_time else None,
                'section': student_row.section_name
            })
        
        # Get student info for response
        student_info = {
            'student_id': student_id,
            'name': f'{student_row.first_name} {student_row.last_name}',
            'section': student_row.section_name,
            'program': student_row.program if hasattr(student_row, 'program') else 'CSE(AIML)'
        }
        
        return jsonify({
            'success': True,
            'data': {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'day_of_week': day_of_week,
                'sessions': sessions,
                'student_info': student_info
            },
            'message': 'Today\'s schedule retrieved successfully' if sessions else 'No classes scheduled for today'
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching today's timetable: {e}")
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/student/timetable', methods=['GET'])
@jwt_required()
def get_student_timetable():
    """Get complete timetable for the current student"""
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
            from sqlalchemy import text
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        # Get student details including section
        student_query = text("""
            SELECT s.student_code, s.first_name, s.last_name, sec.section_name, sec.course, sec.room_number
            FROM students s
            JOIN sections sec ON s.section_id = sec.id
            WHERE s.student_id = :student_id
        """)
        
        student_result = db.session.execute(student_query, {'student_id': student_id})
        student_row = student_result.fetchone()
        
        if not student_row:
            return jsonify({'error': 'Student not found'}), 404
        
        student_info = {
            'studentCode': student_row[0],
            'name': student_row[1] + (' ' + student_row[2] if student_row[2] else ''),
            'section': student_row[3],
            'course': student_row[4],
            'room': student_row[5]
        }
        
        # Get timetable for the student's section, excluding breaks/lunch/free slots
        timetable_query = text("""
            SELECT t.day_of_week, t.slot_number, t.start_time, t.end_time, t.subject_code, 
                   t.slot_type, t.room_number, sub.subject_name, sub.short_name, sub.faculty_name
            FROM timetable t
            JOIN sections sec ON t.section_id = sec.id
            LEFT JOIN subjects sub ON t.subject_code = sub.subject_code
            WHERE t.section_id = (SELECT section_id FROM students WHERE student_id = :student_id)
            AND t.slot_type NOT IN ('break', 'lunch', 'free')
            AND t.subject_code IS NOT NULL
            AND t.subject_code != ''
            ORDER BY FIELD(t.day_of_week, 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'), 
                     t.slot_number, t.start_time
        """)
        
        result = db.session.execute(timetable_query, {'student_id': student_id})
        
        # Organize timetable by day
        timetable_schedule = {}
        days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
        
        for day in days:
            timetable_schedule[day] = []
        
        for row in result:
            slot_data = {
                'slotNumber': row[1],
                'startTime': str(row[2])[:-3] if row[2] else None,  # Remove seconds
                'endTime': str(row[3])[:-3] if row[3] else None,   # Remove seconds
                'subjectCode': row[4],
                'subjectName': row[7] if row[7] else (row[4] if row[4] else ''),
                'shortName': row[8] if row[8] else (row[4] if row[4] else ''),
                'facultyName': row[9],
                'room': row[6],
                'slotType': row[5]
            }
            
            timetable_schedule[row[0]].append(slot_data)
        
        return jsonify({
            'success': True,
            'data': {
                'student': student_info,
                'timetable': timetable_schedule
            },
            'message': 'Student timetable retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching student timetable: {e}")
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/student/current-session', methods=['GET'])
@jwt_required()
def get_current_session():
    """Get current and next session for the student"""
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
            from sqlalchemy import text
            from datetime import datetime, time
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        # Get current day and time
        now = datetime.now()
        current_day = now.strftime('%A').upper()
        current_time = now.time()
        
        # Get student's section
        section_query = text("SELECT section_id FROM students WHERE student_id = :student_id")
        section_result = db.session.execute(section_query, {'student_id': student_id})
        section_row = section_result.fetchone()
        
        if not section_row:
            return jsonify({'error': 'Student not found'}), 404
        
        section_id = section_row[0]
        
        # Get current session, excluding breaks/lunch/free slots
        current_session_query = text("""
            SELECT t.id, t.start_time, t.end_time, t.subject_code, t.slot_type, t.room_number,
                   sub.subject_name, sub.short_name, sub.faculty_name
            FROM timetable t
            LEFT JOIN subjects sub ON t.subject_code = sub.subject_code
            WHERE t.section_id = :section_id 
            AND t.day_of_week = :day_of_week
            AND t.start_time <= :current_time 
            AND t.end_time > :current_time
            AND t.slot_type NOT IN ('break', 'lunch', 'free')
            AND t.subject_code IS NOT NULL
            AND t.subject_code != ''
            ORDER BY t.start_time
            LIMIT 1
        """)
        
        current_result = db.session.execute(current_session_query, {
            'section_id': section_id,
            'day_of_week': current_day,
            'current_time': current_time
        })
        
        current_row = current_result.fetchone()
        
        current_session = None
        if current_row:
            start_time_obj = current_row[1]
            end_time_obj = current_row[2]
            
            # Calculate elapsed and remaining time
            elapsed_minutes = int((now - datetime.combine(now.date(), start_time_obj)).total_seconds() / 60)
            remaining_minutes = int((datetime.combine(now.date(), end_time_obj) - now).total_seconds() / 60)
            
            current_session = {
                'isActive': True,
                'subjectCode': current_row[3],
                'subjectName': current_row[6] if current_row[6] else (current_row[3] if current_row[3] else ''),
                'shortName': current_row[7] if current_row[7] else (current_row[3] if current_row[3] else ''),
                'facultyName': current_row[8],
                'startTime': str(start_time_obj)[:-3] if start_time_obj else None,
                'endTime': str(end_time_obj)[:-3] if end_time_obj else None,
                'room': current_row[5],
                'minutesElapsed': max(0, elapsed_minutes),
                'minutesRemaining': max(0, remaining_minutes)
            }
        
        # Get next session, excluding breaks/lunch/free slots
        next_session_query = text("""
            SELECT t.id, t.start_time, t.end_time, t.subject_code, t.slot_type, t.room_number,
                   sub.subject_name, sub.short_name, sub.faculty_name
            FROM timetable t
            LEFT JOIN subjects sub ON t.subject_code = sub.subject_code
            WHERE t.section_id = :section_id 
            AND t.day_of_week = :day_of_week
            AND t.start_time > :current_time
            AND t.slot_type NOT IN ('break', 'lunch', 'free')
            AND t.subject_code IS NOT NULL
            AND t.subject_code != ''
            ORDER BY t.start_time
            LIMIT 1
        """)
        
        next_result = db.session.execute(next_session_query, {
            'section_id': section_id,
            'day_of_week': current_day,
            'current_time': current_time
        })
        
        next_row = next_result.fetchone()
        
        next_session = None
        if next_row:
            start_time_obj = next_row[1]
            end_time_obj = next_row[2]
            
            # Calculate minutes until start
            minutes_until_start = int((datetime.combine(now.date(), start_time_obj) - now).total_seconds() / 60)
            
            next_session = {
                'subjectCode': next_row[3],
                'subjectName': next_row[6] if next_row[6] else (next_row[3] if next_row[3] else ''),
                'shortName': next_row[7] if next_row[7] else (next_row[3] if next_row[3] else ''),
                'facultyName': next_row[8],
                'startTime': str(start_time_obj)[:-3] if start_time_obj else None,
                'endTime': str(end_time_obj)[:-3] if end_time_obj else None,
                'room': next_row[5],
                'minutesUntilStart': max(0, minutes_until_start)
            }
        
        # Check if warm window is active (3 minutes before next session)
        warm_window_active = False
        warm_window_starts_in = None
        
        if next_session:
            if next_session['minutesUntilStart'] <= 3 and next_session['minutesUntilStart'] >= 0:
                warm_window_active = True
                warm_window_starts_in = 0
            elif next_session['minutesUntilStart'] > 3:
                warm_window_starts_in = next_session['minutesUntilStart'] - 3
        
        return jsonify({
            'success': True,
            'data': {
                'currentSession': current_session,
                'nextSession': next_session,
                'warmWindowActive': warm_window_active,
                'warmWindowStartsIn': warm_window_starts_in
            },
            'message': 'Current session information retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching current session: {e}")
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/student/attendance/summary', methods=['GET'])
@jwt_required()
def get_attendance_summary():
    """Get subject-level attendance summary for the History page"""
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
            from sqlalchemy import text
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        # Get subject-wise statistics
        subject_stats_query = text("""
            SELECT 
                s.subject_code,
                s.subject_name,
                s.short_name,
                f.first_name,
                f.last_name,
                ast.total_sessions,
                ast.attended_sessions,
                ast.attendance_percentage
            FROM attendance_statistics ast
            JOIN subjects s ON ast.subject_id = s.id
            LEFT JOIN faculty f ON s.faculty_id = f.faculty_id
            WHERE ast.student_id = :student_id AND ast.subject_id IS NOT NULL
            ORDER BY ast.total_sessions DESC, s.subject_name
        """)
        
        subject_result = db.session.execute(subject_stats_query, {'student_id': student_id})
        subject_stats = subject_result.fetchall()
        
        # Format subject stats for the History page
        subject_stats_list = []
        for row in subject_stats:
            # Calculate percentage
            percentage = float(row[7]) if row[7] is not None else 0.0
            
            # Get faculty name
            faculty_name = f"{row[3]} {row[4]}".strip() if row[3] or row[4] else "Unknown Faculty"
            
            subject_stats_list.append({
                'subject_code': row[0],
                'subject_name': row[1],
                'short_name': row[2],
                'faculty_name': faculty_name,
                'total_classes': row[5] if row[5] is not None else 0,
                'attended_count': row[6] if row[6] is not None else 0,
                'percentage': percentage
            })
        
        return jsonify({
            'success': True,
            'data': {
                'subjects': subject_stats_list
            },
            'message': 'Subject attendance summary retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching subject attendance summary: {e}")
        return jsonify({'error': str(e)}), 500


@mobile_bp.route('/student/attendance/history', methods=['GET'])
@jwt_required()
def get_attendance_history():
    """Get detailed attendance history with filters"""
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
            from sqlalchemy import text
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        
        # Build query with filters
        query_parts = [
            "SELECT",
            "  ah.record_id,",
            "  ah.session_id,",
            "  s.subject_code,",
            "  s.subject_name,",
            "  f.first_name,",
            "  f.last_name,",
            "  ah.status,",
            "  ah.verification_score,",
            "  ah.scan_timestamp",
            "FROM attendance_records ah",
            "JOIN students st ON ah.student_id = st.student_id",
            "JOIN timetable t ON ah.session_id = t.id",
            "JOIN subjects s ON t.subject_code = s.subject_code",
            "LEFT JOIN faculty f ON s.faculty_id = f.faculty_id",
            "WHERE ah.student_id = :student_id"
        ]
        
        params = {'student_id': student_id}
        
        if from_date:
            query_parts.append("AND DATE(ah.scan_timestamp) >= :from_date")
            params['from_date'] = from_date
        
        if to_date:
            query_parts.append("AND DATE(ah.scan_timestamp) <= :to_date")
            params['to_date'] = to_date
        
        query_parts.append("ORDER BY ah.scan_timestamp DESC")
        query_parts.append("LIMIT :limit")
        params['limit'] = min(limit, 100)  # Cap at 100 records
        
        query = " ".join(query_parts)
        
        result = db.session.execute(text(query), params)
        rows = result.fetchall()
        
        # Format history records
        history_list = []
        for row in rows:
            # Get faculty name
            faculty_name = f"{row[4]} {row[5]}".strip() if row[4] or row[5] else "Unknown Faculty"
            
            history_list.append({
                'record_id': row[0],
                'session_id': row[1],
                'subject_code': row[2],
                'subject_name': row[3],
                'faculty_name': faculty_name,
                'status': row[6].upper() if row[6] else "UNKNOWN",
                'verification_score': float(row[7]) if row[7] is not None else 0.0,
                'scan_timestamp': row[8].isoformat() if row[8] else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'records': history_list
            },
            'message': 'Attendance history retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching attendance history: {e}")
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/attendance/monthly-overview', methods=['GET'])
@jwt_required()
def get_monthly_overview():
    """Get week-by-week attendance for chart"""
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        # Get current month
        today = datetime.now()
        start_of_month = today.replace(day=1)
        
        # Calculate attendance for each week
        weeks = []
        for week_num in range(1, 5):
            week_start = start_of_month + timedelta(days=(week_num - 1) * 7)
            week_end = week_start + timedelta(days=7)
            
            # Count attendance for this week
            records = AttendanceRecord.query.filter(
                getattr(AttendanceRecord, 'student_id') == student_id,
                getattr(AttendanceRecord, 'scan_timestamp') >= week_start,
                getattr(AttendanceRecord, 'scan_timestamp') < week_end
            ).all()
            
            total = len(records)
            present = sum(1 for r in records if r.status == 'present')
            percentage = (present / total * 100) if total > 0 else 0
            
            weeks.append({
                'week': f"W{week_num}",
                'percentage': round(percentage, 2),
                'total_classes': total,
                'present': present
            })
        
        return jsonify({
            'success': True,
            'month': today.strftime('%B %Y'),
            'weeks': weeks
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching monthly overview: {e}")
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/notifications/register', methods=['POST'])
@jwt_required()
def register_fcm_token():
    """Register FCM token for push notifications"""
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        data = request.get_json()
        device_uuid = data.get('device_uuid')
        fcm_token = data.get('fcm_token')
        
        if not fcm_token:
            return jsonify({'error': 'FCM token required'}), 400
        
        # Update device with FCM token
        device = StudentDevices.query.filter_by(
            student_id=student_id,
            device_uuid=device_uuid
        ).first()
        
        if device:
            device.fcm_token = fcm_token
            db.session.commit()
            return jsonify({'success': True}), 200
        
        return jsonify({'error': 'Device not found'}), 404
        
    except Exception as e:
        logger.error(f"Error registering FCM token: {e}")
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/notifications/toggle', methods=['POST'])
@jwt_required()
def toggle_notifications():
    """Enable/disable notifications"""
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        # Update all devices for this student
        devices = StudentDevices.query.filter_by(student_id=student_id).all()
        for device in devices:
            device.notifications_enabled = enabled
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'notifications_enabled': enabled
        }), 200
        
    except Exception as e:
        logger.error(f"Error toggling notifications: {e}")
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/security/violation', methods=['POST'])
@jwt_required()
def log_security_violation():
    """Log security violations (screenshot, screen recording, etc.)"""
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db, SecurityViolation
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        data = request.get_json()
        violation_type = data.get('type')  # screenshot, screen_recording, root_detected
        device_info = data.get('device_info', {})
        details = data.get('details', {})
        
        # Create security violation record
        security_violation = SecurityViolation(
            student_id=student_id,
            violation_type=violation_type,
            device_info=device_info,
            details=details
        )
        
        db.session.add(security_violation)
        db.session.commit()
        
        logger.warning(f"Security violation detected for student {student_id}: {violation_type}")
        
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Error logging security violation: {e}")
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/student/settings', methods=['GET'])
@jwt_required()
def get_student_settings():
    """
    Get current student settings
    This endpoint is used for the settings page in the mobile app
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        # Get student's devices to determine current settings
        devices = StudentDevices.query.filter_by(student_id=student_id).all()
        
        # For now, we'll use the first device's settings as the student's settings
        # In a more advanced implementation, settings could be stored separately
        notifications_enabled = True
        biometric_enabled = False
        dark_mode = False  # This would typically be stored on the device side
        
        if devices:
            # Use the first device's settings
            device = devices[0]
            notifications_enabled = device.notifications_enabled if hasattr(device, 'notifications_enabled') else True
            biometric_enabled = device.biometric_enabled if hasattr(device, 'biometric_enabled') else False
        
        settings_data = {
            'notifications_enabled': notifications_enabled,
            'biometric_enabled': biometric_enabled,
            'dark_mode': dark_mode,  # This would typically be handled client-side
            'devices': len(devices)
        }
        
        return jsonify({
            'success': True,
            'settings': settings_data,
            'message': 'Settings retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting student settings: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/student/settings', methods=['POST'])
@jwt_required()
def update_student_settings():
    """
    Update student settings
    This endpoint is used to save settings changes from the mobile app
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Extract settings from request
        notifications_enabled = data.get('notifications_enabled')
        biometric_enabled = data.get('biometric_enabled')
        dark_mode = data.get('dark_mode')
        
        # Update all devices for this student with the new settings
        devices = StudentDevices.query.filter_by(student_id=student_id).all()
        
        updated_devices = 0
        for device in devices:
            updated = False
            
            # Update notifications setting if provided
            if notifications_enabled is not None and hasattr(device, 'notifications_enabled'):
                device.notifications_enabled = notifications_enabled
                updated = True
            
            # Update biometric setting if provided
            if biometric_enabled is not None and hasattr(device, 'biometric_enabled'):
                device.biometric_enabled = biometric_enabled
                updated = True
            
            if updated:
                updated_devices += 1
        
        if updated_devices > 0:
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Settings updated for {updated_devices} devices',
            'settings': {
                'notifications_enabled': notifications_enabled,
                'biometric_enabled': biometric_enabled,
                'dark_mode': dark_mode
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating student settings: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/student/profile', methods=['GET'])
@mobile_bp.route('/student/me', methods=['GET'])
@jwt_required()
def get_student_profile():
    """
    Get current student profile information
    This endpoint is used for the profile page in the mobile app
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        student = Student.query.get(student_id)
        
        if not student or not student.is_active:
            return jsonify({'error': 'Student not found or inactive'}), 404
        
        # Get student's device information
        devices = StudentDevices.query.filter_by(student_id=student_id).all()
        
        student_data = {
            'student_id': student.student_id,
            'student_code': student.student_code,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email,
            'phone_number': student.phone_number,
            'program': student.program,
            'year_of_study': student.year_of_study or 1,
            'is_active': student.is_active,
            'created_at': student.created_at.isoformat() if student.created_at else None,
            'updated_at': student.updated_at.isoformat() if student.updated_at else None
        }
        
        # Add device information
        device_list = []
        for device in devices:
            device_list.append({
                'device_id': device.device_id,
                'device_uuid': device.device_uuid,
                'device_name': device.device_name,
                'device_type': device.device_type,
                'device_model': device.device_model,
                'os_version': device.os_version,
                'app_version': device.app_version,
                'notifications_enabled': device.notifications_enabled if hasattr(device, 'notifications_enabled') else True,
                'biometric_enabled': device.biometric_enabled,
                'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                'is_online': (datetime.utcnow() - device.last_seen).total_seconds() < 300 if device.last_seen else False
            })
        
        return jsonify({
            'success': True,
            'student': student_data,
            'devices': device_list,
            'message': 'Profile retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting student profile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/time/sync', methods=['GET'])
def time_sync():
    """
    Server time synchronization endpoint
    Prevents time manipulation attacks by providing accurate server time
    """
    try:
        from datetime import datetime
        import time
        
        server_time = datetime.utcnow()
        timestamp = int(time.mktime(server_time.timetuple())) * 1000 + server_time.microsecond // 1000
        
        return jsonify({
            'success': True,
            'server_time': server_time.isoformat(),
            'timestamp': timestamp,
            'timezone': 'UTC'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in time sync endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/auth/biometric-verify', methods=['POST'])
@jwt_required()
def biometric_verify():
    """
    Log biometric verification for audit trail
    Enhances security by tracking biometric success/failure on server
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db, SecurityViolation
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Extract biometric data
        biometric_success = data.get('success', False)
        device_info = data.get('device_info', {})
        verification_method = data.get('method', 'unknown')
        confidence_score = data.get('confidence_score', 0.0)
        
        # Log biometric verification
        logger.info(f"Biometric verification for student {student_id}: {'success' if biometric_success else 'failed'}")
        
        # If biometric failed, log as security violation
        if not biometric_success:
            security_violation = SecurityViolation(
                student_id=student_id,
                violation_type='biometric_failed',
                device_info=device_info,
                details={
                    'method': verification_method,
                    'confidence_score': confidence_score,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            db.session.add(security_violation)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Biometric verification logged',
            'verification_id': str(student_id) + '_' + str(int(datetime.utcnow().timestamp()))
        }), 200
        
    except Exception as e:
        logger.error(f"Error in biometric verification endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/auth/send-otp', methods=['POST'])
def send_otp():
    """
    Send OTP for 2FA verification
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
            import random
            import string
        
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        # Find student by email
        student = Student.query.filter_by(email=email).first()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Generate 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # In a real implementation, you would send this via email/SMS
        # For now, we'll just log it
        logger.info(f"OTP generated for {email}: {otp_code}")
        
        # Store OTP in session (in real implementation, store in database with expiry)
        # For now, we'll return it directly (NOT recommended for production)
        
        return jsonify({
            'success': True,
            'message': 'OTP sent successfully',
            'otp': otp_code  # Remove this in production
        }), 200
        
    except Exception as e:
        logger.error(f"Error in send OTP endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/auth/verify-otp', methods=['POST'])
def verify_otp():
    """
    Verify OTP for 2FA
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        data = request.get_json()
        email = data.get('email')
        otp_code = data.get('otp')
        
        if not email or not otp_code:
            return jsonify({'error': 'Email and OTP required'}), 400
        
        # Find student by email
        student = Student.query.filter_by(email=email).first()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # In a real implementation, you would verify against stored OTP
        # For now, we'll just check if it's 6 digits
        if len(otp_code) == 6 and otp_code.isdigit():
            # Create JWT tokens
            claims = {'type': 'student', 'student_id': student.student_id}
            access_token = create_access_token(
                identity=str(student.student_id),
                additional_claims=claims
            )
            
            return jsonify({
                'success': True,
                'message': 'OTP verified successfully',
                'access_token': access_token,
                'student': {
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'program': student.program,
                    'year_of_study': student.year_of_study
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid OTP'}), 400
        
    except Exception as e:
        logger.error(f"Error in verify OTP endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/faculty/login', methods=['POST'])
def faculty_login():
    """
    Faculty login endpoint for mobile app
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Faculty, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db, create_access_token
        
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        device_uuid = data.get('device_uuid')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find faculty by email
        faculty = Faculty.query.filter_by(email=email, is_active=True).first()
        
        if not faculty:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not check_password(password, faculty.password_hash):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT tokens
        claims = {'type': 'faculty', 'faculty_id': faculty.faculty_id}
        access_token = create_access_token(
            identity=str(faculty.faculty_id),
            additional_claims=claims
        )
        
        # Associate device with faculty if device_uuid is provided
        if device_uuid:
            # Note: Faculty devices would need a different model or extension
            # For now, we'll just log the association
            logger.info(f"Faculty {faculty.faculty_id} logged in from device {device_uuid}")
        
        # Prepare response
        response_data = {
            'success': True,
            'access_token': access_token,
            'faculty': {
                'faculty_id': faculty.faculty_id,
                'faculty_code': faculty.faculty_code,
                'first_name': faculty.first_name,
                'last_name': faculty.last_name,
                'email': faculty.email,
                'department': faculty.department
            },
            'message': 'Login successful'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error during faculty login: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/device/heartbeat', methods=['POST'])
@jwt_required()
def device_heartbeat():
    """
    Device heartbeat endpoint for continuous online/offline tracking
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current user from JWT token
        claims = get_jwt()
        user_type = claims.get('type')
        
        if user_type == 'student':
            user_id = claims.get('student_id')
        elif user_type == 'faculty':
            user_id = claims.get('faculty_id')
        else:
            return jsonify({'error': 'Invalid user type'}), 403
        
        data = request.get_json()
        device_uuid = data.get('device_uuid')
        
        if not device_uuid:
            return jsonify({'error': 'Device UUID required'}), 400
        
        # Update device last_seen timestamp
        if user_type == 'student':
            device = StudentDevices.query.filter_by(
                student_id=user_id,
                device_uuid=device_uuid
            ).first()
        else:
            # For faculty, we would need a FacultyDevices table
            # For now, we'll just log the heartbeat
            device = None
        
        if device:
            device.last_seen = datetime.utcnow()
            db.session.commit()
            
            is_online = True
        else:
            is_online = False
        
        return jsonify({
            'success': True,
            'message': 'Heartbeat received',
            'is_online': is_online,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in device heartbeat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/device/connectivity', methods=['POST'])
@jwt_required()
def log_connectivity_status():
    """
    Log device connectivity status for online/offline tracking
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current user from JWT token
        claims = get_jwt()
        user_type = claims.get('type')
        
        if user_type == 'student':
            user_id = claims.get('student_id')
        elif user_type == 'faculty':
            user_id = claims.get('faculty_id')
        else:
            return jsonify({'error': 'Invalid user type'}), 403
        
        data = request.get_json()
        device_uuid = data.get('device_uuid')
        connectivity_status = data.get('status', 'online')  # online, offline, limited
        network_type = data.get('network_type', 'unknown')  # wifi, cellular, ethernet
        signal_strength = data.get('signal_strength')  # RSSI or signal bars
        
        if not device_uuid:
            return jsonify({'error': 'Device UUID required'}), 400
        
        # Log connectivity status
        logger.info(f"Connectivity status for {user_type} {user_id} on device {device_uuid}: {connectivity_status}")
        
        # Update device information if available
        if user_type == 'student':
            device = StudentDevices.query.filter_by(
                student_id=user_id,
                device_uuid=device_uuid
            ).first()
            
            if device:
                # Update device info
                device_info = data.get('device_info', {})
                if 'app_version' in device_info:
                    device.app_version = device_info['app_version']
                if 'os_version' in device_info:
                    device.os_version = device_info['os_version']
                
                # Update last seen for online status
                if connectivity_status == 'online':
                    device.last_seen = datetime.utcnow()
                
                db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Connectivity status logged',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error logging connectivity status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/student/stats', methods=['GET'])
@jwt_required()
def get_student_stats():
    """
    Get student attendance statistics
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        
        # Get all attendance records for this student
        records = AttendanceRecord.query.filter_by(student_id=student_id).all()
        
        total_classes = len(records)
        present_count = sum(1 for r in records if r.status == 'present')
        late_count = sum(1 for r in records if r.status == 'late')
        absent_count = sum(1 for r in records if r.status == 'absent')
        
        # Calculate attendance percentage
        attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
        
        # Get recent attendance (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_records = AttendanceRecord.query.filter(
            getattr(AttendanceRecord, 'student_id') == student_id,
            getattr(AttendanceRecord, 'scan_timestamp') >= thirty_days_ago
        ).all()
        
        recent_present = sum(1 for r in recent_records if r.status == 'present')
        recent_total = len(recent_records)
        recent_percentage = (recent_present / recent_total * 100) if recent_total > 0 else 0
        
        # Get class-wise statistics
        class_stats = {}
        for record in records:
            session = AttendanceSession.query.get(record.session_id)
            if session:
                class_obj = Classes.query.get(session.class_id)
                if class_obj:
                    class_name = class_obj.class_name
                    if class_name not in class_stats:
                        class_stats[class_name] = {'total': 0, 'present': 0}
                    class_stats[class_name]['total'] += 1
                    if record.status == 'present':
                        class_stats[class_name]['present'] += 1
        
        # Calculate class-wise percentages
        for class_name, stats in class_stats.items():
            stats['percentage'] = (stats['present'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'overall': {
                    'total_classes': total_classes,
                    'present': present_count,
                    'late': late_count,
                    'absent': absent_count,
                    'attendance_percentage': round(attendance_percentage, 2)
                },
                'recent_30_days': {
                    'total_classes': recent_total,
                    'present': recent_present,
                    'attendance_percentage': round(recent_percentage, 2)
                },
                'by_class': class_stats
            },
            'message': 'Statistics retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting student stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/presence/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_presence(student_id):
    """
    Get presence status for a specific student
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current user from JWT token (faculty or admin can access)
        claims = get_jwt()
        user_type = claims.get('type')
        
        # Only faculty or admin can check other students' presence
        if user_type == 'student' and claims.get('student_id') != student_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get student
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get student's devices
        devices = StudentDevices.query.filter_by(student_id=student_id).all()
        
        # Determine presence status based on last seen
        presence_status = 'offline'
        last_seen = None
        device_info = []
        
        for device in devices:
            device_info.append({
                'device_id': device.device_id,
                'device_uuid': device.device_uuid,
                'device_name': device.device_name,
                'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                'is_online': (datetime.utcnow() - device.last_seen).total_seconds() < 300 if device.last_seen else False
            })
            
            if device.last_seen:
                if not last_seen or device.last_seen > last_seen:
                    last_seen = device.last_seen
        
        # If seen in last 5 minutes, consider online
        if last_seen and (datetime.utcnow() - last_seen).total_seconds() < 300:
            presence_status = 'online'
        elif last_seen:
            presence_status = 'away'
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'presence_status': presence_status,
            'last_seen': last_seen.isoformat() if last_seen else None,
            'devices': device_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting student presence: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/presence/all', methods=['GET'])
@jwt_required()
def get_all_presence():
    """
    Get presence status for all students (for faculty/SmartBoard)
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, check_password, db
        
        # Get current user from JWT token
        claims = get_jwt()
        user_type = claims.get('type')
        
        # Only faculty or admin can access all presence
        if user_type not in ['faculty', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get all active students
        students = Student.query.filter_by(is_active=True).all()
        
        presence_data = []
        for student in students:
            # Get student's devices
            devices = StudentDevices.query.filter_by(student_id=student.student_id).all()
            
            # Determine presence status
            presence_status = 'offline'
            last_seen = None
            
            for device in devices:
                if device.last_seen:
                    if not last_seen or device.last_seen > last_seen:
                        last_seen = device.last_seen
            
            # If seen in last 5 minutes, consider online
            if last_seen and (datetime.utcnow() - last_seen).total_seconds() < 300:
                presence_status = 'online'
            elif last_seen:
                presence_status = 'away'
            
            presence_data.append({
                'student_id': student.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code,
                'presence_status': presence_status,
                'last_seen': last_seen.isoformat() if last_seen else None
            })
        
        return jsonify({
            'success': True,
            'presence_data': presence_data,
            'total_students': len(presence_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting all presence: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@mobile_bp.route('/attendance/validate-wifi', methods=['POST'])
@jwt_required()
def validate_wifi_network():
    """
    Validate WiFi network against registered classroom networks
    """
    try:
        # Import models within app context
        with current_app.app_context():
            from app import Student, StudentDevices, AttendanceRecord, AttendanceSession, Classes, Classroom, WiFiNetwork, check_password, db
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = claims.get('student_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Extract WiFi data
        wifi_data = data.get('wifi', {})
        session_id = data.get('session_id')
        
        if not wifi_data or not session_id:
            return jsonify({'error': 'WiFi data and session ID required'}), 400
        
        # Get session
        session = AttendanceSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Invalid session'}), 400
        
        # Get class
        class_obj = Classes.query.get(session.class_id)
        if not class_obj or not class_obj.classroom_id:
            return jsonify({'error': 'Class or classroom not found'}), 400
        
        # Get classroom
        classroom = Classroom.query.get(class_obj.classroom_id)
        if not classroom:
            return jsonify({'error': 'Classroom not found'}), 400
        
        # Get registered WiFi networks for this classroom
        registered_networks = WiFiNetwork.query.filter_by(
            classroom_id=classroom.classroom_id,
            is_active=True
        ).all()
        
        # Extract WiFi information from request
        current_ssid = wifi_data.get('current_ssid')
        current_bssid = wifi_data.get('current_bssid')
        
        # Validate against registered networks
        is_valid_network = False
        matched_network = None
        
        for network in registered_networks:
            if (current_ssid and current_ssid == network.ssid) or \
               (current_bssid and current_bssid == network.bssid):
                is_valid_network = True
                matched_network = {
                    'ssid': network.ssid,
                    'bssid': network.bssid,
                    'security_type': network.security_type
                }
                break
        
        return jsonify({
            'success': True,
            'valid': is_valid_network,
            'matched_network': matched_network,
            'registered_networks_count': len(registered_networks),
            'current_ssid': current_ssid,
            'current_bssid': current_bssid
        }), 200
        
    except Exception as e:
        logger.error(f"Error validating WiFi network: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def register_mobile_api(flask_app):
    """Register the mobile API blueprint with the Flask app"""
    flask_app.register_blueprint(mobile_bp)
    logger.info("Mobile API blueprint registered")