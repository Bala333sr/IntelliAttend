#!/usr/bin/env python3
"""
INTELLIATTEND - Main Flask Application
Smart Attendance System with QR Code, Biometric, and Location Verification
"""

import os
import json
import secrets
import hashlib
import subprocess
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash, generate_password_hash
import bcrypt


def check_password(password, password_hash):
    """Check password against hash, supporting both bcrypt and werkzeug formats"""
    try:
        # Try bcrypt first (newer format)
        if password_hash.startswith('$2b$') or password_hash.startswith('$2a$'):
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        else:
            # Fall back to werkzeug (older format)
            return check_password_hash(password_hash, password)
    except Exception:
        # If all else fails, try werkzeug as fallback
        try:
            return check_password_hash(password_hash, password)
        except:
            return False
from werkzeug.utils import secure_filename
import pymysql
import qrcode
from PIL import Image
import cv2
import numpy as np
# Optional QR decoding import - graceful fallback if not available
try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    print("⚠️  pyzbar not available - QR decoding features disabled")
import random
import string
import time
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from geopy.distance import geodesic
import logging
import logging.handlers

# Import configuration
from config import config

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/intelliattend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/public')

# Load configuration
config_name = os.environ.get('FLASK_CONFIG', 'development')
app.config.from_object(config[config_name])

# JWT Token Blacklist for secure logout
jwt_blacklist = set()
jwt_blacklist_lock = threading.Lock()

# Initialize extensions
db = SQLAlchemy(app)
cors = CORS(app, origins=app.config['CORS_ORIGINS'])
jwt = JWTManager(app)

# JWT Blacklist handler for token revocation
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if token has been revoked (blacklisted)"""
    jti = jwt_payload['jti']
    with jwt_blacklist_lock:
        return jti in jwt_blacklist

# Initialize Flask-Limiter with storage configuration
if os.environ.get('FLASK_CONFIG') == 'production' and os.environ.get('REDIS_URL'):
    # Use Redis storage for production
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.environ.get('REDIS_URL')
    )
else:
    # Use in-memory storage for development
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
limiter.init_app(app)

# Global variables for QR management
active_qr_sessions = {}
active_qr_sessions_lock = threading.Lock()
scheduler = BackgroundScheduler()

# ============================================================================
# DATABASE MODELS
# ============================================================================

class Faculty(db.Model):
    __tablename__ = 'faculty'
    
    faculty_id = db.Column(db.Integer, primary_key=True)
    faculty_code = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, faculty_code, first_name, last_name, email, phone_number, department, password_hash, is_active=True):
        self.faculty_code = faculty_code
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.department = department
        self.password_hash = password_hash
        self.is_active = is_active

class Student(db.Model):
    __tablename__ = 'students'
    
    student_id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15))
    year_of_study = db.Column(db.Integer)
    program = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, student_code, first_name, last_name, email, program, password_hash, phone_number=None, year_of_study=None, is_active=True):
        self.student_code = student_code
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.year_of_study = year_of_study
        self.program = program
        self.password_hash = password_hash
        self.is_active = is_active

class Classroom(db.Model):
    __tablename__ = 'classrooms'
    
    classroom_id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False)
    building_name = db.Column(db.String(100), nullable=False)
    floor_number = db.Column(db.Integer)
    capacity = db.Column(db.Integer, default=50)
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    geofence_radius = db.Column(db.Numeric(8, 2), default=50.00)
    bluetooth_beacon_id = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, room_number, building_name, capacity=50, floor_number=None, latitude=None, longitude=None, 
                 geofence_radius=50.00, bluetooth_beacon_id=None, is_active=True):
        self.room_number = room_number
        self.building_name = building_name
        self.floor_number = floor_number
        self.capacity = capacity
        self.latitude = latitude
        self.longitude = longitude
        self.geofence_radius = geofence_radius
        self.bluetooth_beacon_id = bluetooth_beacon_id
        self.is_active = is_active

class Classes(db.Model):
    __tablename__ = 'classes'
    
    class_id = db.Column(db.Integer, primary_key=True)
    class_code = db.Column(db.String(20), unique=True, nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.classroom_id'))
    semester = db.Column(db.String(20), nullable=False)
    academic_year = db.Column(db.String(9), nullable=False)
    credits = db.Column(db.Integer, default=3)
    max_students = db.Column(db.Integer, default=60)
    schedule_day = db.Column(db.Enum('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, class_code, class_name, faculty_id, semester, academic_year, credits=3, max_students=60, 
                 classroom_id=None, schedule_day=None, start_time=None, end_time=None, is_active=True):
        self.class_code = class_code
        self.class_name = class_name
        self.faculty_id = faculty_id
        self.classroom_id = classroom_id
        self.semester = semester
        self.academic_year = academic_year
        self.credits = credits
        self.max_students = max_students
        self.schedule_day = schedule_day
        self.start_time = start_time
        self.end_time = end_time
        self.is_active = is_active

class StudentDevices(db.Model):
    __tablename__ = 'student_devices'
    
    device_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    device_uuid = db.Column(db.String(255), unique=True, nullable=False)
    device_name = db.Column(db.String(100))
    device_type = db.Column(db.Enum('android', 'ios', 'web'), nullable=False)
    device_model = db.Column(db.String(100))
    os_version = db.Column(db.String(50))
    app_version = db.Column(db.String(20))
    fcm_token = db.Column(db.String(255))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    biometric_enabled = db.Column(db.Boolean, default=False)
    location_permission = db.Column(db.Boolean, default=False)
    bluetooth_permission = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, student_id, device_uuid, device_type, device_name=None, device_model=None, 
                 os_version=None, app_version=None, fcm_token=None, is_active=True, 
                 biometric_enabled=False, location_permission=False, bluetooth_permission=False):
        self.student_id = student_id
        self.device_uuid = device_uuid
        self.device_type = device_type
        self.device_name = device_name
        self.device_model = device_model
        self.os_version = os_version
        self.app_version = app_version
        self.fcm_token = fcm_token
        self.is_active = is_active
        self.biometric_enabled = biometric_enabled
        self.location_permission = location_permission
        self.bluetooth_permission = bluetooth_permission

class AttendanceSession(db.Model):
    __tablename__ = 'attendance_sessions'
    
    session_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    session_date = db.Column(db.Date, default=datetime.utcnow().date)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    qr_token = db.Column(db.String(255), unique=True)
    qr_secret_key = db.Column(db.String(255))
    qr_expires_at = db.Column(db.DateTime)
    otp_used = db.Column(db.String(10))
    status = db.Column(db.Enum('active', 'completed', 'cancelled'), default='active')
    total_students_enrolled = db.Column(db.Integer, default=0)
    total_students_present = db.Column(db.Integer, default=0)
    attendance_percentage = db.Column(db.Numeric(5, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, class_id, faculty_id, qr_token, qr_secret_key, qr_expires_at, otp_used=None, status='active'):
        self.class_id = class_id
        self.faculty_id = faculty_id
        self.qr_token = qr_token
        self.qr_secret_key = qr_secret_key
        self.qr_expires_at = qr_expires_at
        self.otp_used = otp_used
        self.status = status

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    record_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.session_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    scan_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    biometric_verified = db.Column(db.Boolean, default=False)
    location_verified = db.Column(db.Boolean, default=False)
    bluetooth_verified = db.Column(db.Boolean, default=False)
    gps_latitude = db.Column(db.Numeric(10, 8))
    gps_longitude = db.Column(db.Numeric(11, 8))
    gps_accuracy = db.Column(db.Numeric(8, 2))
    bluetooth_rssi = db.Column(db.Integer)
    device_info = db.Column(db.JSON)
    verification_score = db.Column(db.Numeric(3, 2), default=0.00)
    status = db.Column(db.Enum('present', 'late', 'absent', 'invalid'), default='present')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, session_id, student_id, biometric_verified=False, location_verified=False, 
                 bluetooth_verified=False, gps_latitude=None, gps_longitude=None, gps_accuracy=None,
                 bluetooth_rssi=None, device_info=None, verification_score=0.00, status='present', notes=None):
        self.session_id = session_id
        self.student_id = student_id
        self.biometric_verified = biometric_verified
        self.location_verified = location_verified
        self.bluetooth_verified = bluetooth_verified
        self.gps_latitude = gps_latitude
        self.gps_longitude = gps_longitude
        self.gps_accuracy = gps_accuracy
        self.bluetooth_rssi = bluetooth_rssi
        self.device_info = device_info
        self.verification_score = verification_score
        self.status = status
        self.notes = notes

class OTPLog(db.Model):
    __tablename__ = 'otp_logs'
    
    otp_id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    otp_code = db.Column(db.String(10), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.session_id'))
    is_used = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, faculty_id, otp_code, expires_at, ip_address=None, user_agent=None):
        self.faculty_id = faculty_id
        self.otp_code = otp_code
        self.expires_at = expires_at
        self.ip_address = ip_address
        self.user_agent = user_agent

# ============================================================================
# QR TOKENS LOG MODEL
# ============================================================================

class QRTokensLog(db.Model):
    __tablename__ = 'qr_tokens_log'
    
    log_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.session_id'), nullable=False)
    token_value = db.Column(db.String(255), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    scan_count = db.Column(db.Integer, default=0)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship definitions
    session = db.relationship('AttendanceSession', backref=db.backref('qr_tokens', lazy=True))
    
    def __init__(self, session_id, token_value, expires_at, ip_address=None):
        self.session_id = session_id
        self.token_value = token_value
        self.expires_at = expires_at
        self.ip_address = ip_address

# ============================================================================
# ENROLLMENT MODEL
# ============================================================================

class StudentClassEnrollment(db.Model):
    __tablename__ = 'student_class_enrollments'
    
    enrollment_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    enrollment_date = db.Column(db.Date, default=datetime.utcnow().date)
    status = db.Column(db.Enum('enrolled', 'dropped', 'completed'), default='enrolled')
    final_grade = db.Column(db.String(5))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship definitions
    student = db.relationship('Student', backref=db.backref('enrollments', lazy=True))
    class_ = db.relationship('Classes', backref=db.backref('enrollments', lazy=True))
    
    def __init__(self, student_id, class_id, status='enrolled', final_grade=None, is_active=True):
        self.student_id = student_id
        self.class_id = class_id
        self.status = status
        self.final_grade = final_grade
        self.is_active = is_active

# ============================================================================
# ADMIN MODEL
# ============================================================================

class Admin(db.Model):
    __tablename__ = 'admins'
    
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum('super_admin', 'admin', 'operator'), default='admin')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def standardize_response(success, data=None, message=None, error=None, status_code=200):
    """
    Standardize API response format
    
    Args:
        success (bool): Whether the request was successful
        data (dict, optional): Data to return
        message (str, optional): Success message
        error (str, optional): Error message
        status_code (int): HTTP status code
    
    Returns:
        tuple: (response_dict, status_code)
    """
    response = {
        'success': success,
        'status_code': status_code
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if error:
        response['error'] = error
    
    return jsonify(response), status_code

def get_first_active_class():
    """Get the first active class from the database"""
    try:
        class_obj = Classes.query.filter_by(is_active=True).first()
        return class_obj.class_id if class_obj else 1  # fallback to 1 if no active class found
    except Exception as e:
        logger.warning(f"Error getting first active class: {e}")
        return 1  # fallback to default

def get_first_active_faculty():
    """Get the first active faculty from the database"""
    try:
        faculty_obj = Faculty.query.filter_by(is_active=True).first()
        return faculty_obj.faculty_id if faculty_obj else 1  # fallback to 1 if no active faculty found
    except Exception as e:
        logger.warning(f"Error getting first active faculty: {e}")
        return 1  # fallback to default

def generate_otp(length=6):
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))

def generate_token(length=32):
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)

def create_qr_code(data, session_id):
    """Create QR code image"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=app.config['QR_CODE_SIZE'],
            border=app.config['QR_CODE_BORDER'],
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Generate filename
        filename = f"qr_session_{session_id}_{int(time.time())}.png"
        
        # Use absolute path to QR_DATA folder in parent directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        qr_tokens_folder = os.path.join(project_root, 'QR_DATA', 'tokens')
        os.makedirs(qr_tokens_folder, exist_ok=True)
        
        # Save to centralized QR_DATA location
        file_path = os.path.join(qr_tokens_folder, filename)
        with open(file_path, 'wb') as f:
            img.save(f, 'PNG')
        
        logger.info(f"QR saved to: {file_path}")
        return filename
    except Exception as e:
        logger.error(f"Error creating QR code: {e}")
        return None

def verify_geofence(student_lat, student_lng, classroom_lat, classroom_lng, radius=50, accuracy=None):
    """Verify if student is within classroom geofence with enhanced security checks"""
    try:
        student_coords = (float(student_lat), float(student_lng))
        classroom_coords = (float(classroom_lat), float(classroom_lng))
        
        # Calculate distance
        distance = geodesic(student_coords, classroom_coords).meters
        
        # Enhanced geofencing with accuracy validation
        is_within_radius = distance <= radius
        
        # Additional security checks
        is_accurate = accuracy is None or accuracy <= app.config.get('GPS_ACCURACY_THRESHOLD', 10)
        
        # Combined verification
        verification_result = is_within_radius and is_accurate
        
        return verification_result, distance
    except Exception as e:
        logger.error(f"Geofence verification error: {e}")
        return False, float('inf')

def calculate_verification_score(biometric, location, bluetooth):
    """Calculate overall verification score"""
    score = 0.0
    if biometric:
        score += 0.4  # 40% weight for biometric
    if location:
        score += 0.4  # 40% weight for location
    if bluetooth:
        score += 0.2  # 20% weight for bluetooth
    
    return round(score, 2)

@contextmanager
def db_transaction():
    """Context manager for database transactions"""
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/api/faculty/login', methods=['POST'])
@limiter.limit("5 per minute")
def faculty_login():
    """Faculty login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return standardize_response(
                success=False,
                error='Email and password required',
                status_code=400
            )
        
        faculty = Faculty.query.filter_by(email=email, is_active=True).first()
        
        if faculty and check_password(password, faculty.password_hash):
            access_token = create_access_token(
                identity=str(faculty.faculty_id),
                additional_claims={'type': 'faculty', 'faculty_id': faculty.faculty_id}
            )
            
            faculty_data = {
                'faculty_id': faculty.faculty_id,
                'name': f'{faculty.first_name} {faculty.last_name}',
                'email': faculty.email,
                'department': faculty.department,
                'is_active': faculty.is_active,
            }
            
            return standardize_response(
                success=True,
                data={
                    'access_token': access_token,
                    'faculty': faculty_data
                },
                message='Login successful',
                status_code=200
            )
        else:
            return standardize_response(
                success=False,
                error='Invalid email or password',
                status_code=401
            )
    except Exception as e:
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

# ============================================================================
# ADMIN DASHBOARD ROUTES
# ============================================================================

@app.route('/admin')
def admin_login_page():
    """Admin login page"""
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard page"""
    return render_template('admin/enhanced_dashboard.html')


@app.route('/api/student/login', methods=['POST'])
@limiter.limit("5 per minute")
def student_login():
    """Student login endpoint"""
    try:
        # Debug logging
        logger.info(f"Student login attempt from {request.remote_addr}")
        logger.debug(f"Headers: {dict(request.headers)}")
        logger.debug(f"Content-Type: {request.content_type}")
        
        data = request.get_json()
        logger.debug(f"Request data: {data}")
        
        email = data.get('email') if data else None
        password = data.get('password') if data else None
        
        logger.info(f"Login attempt - Email: {email}, Password: {'***' if password else 'None'}")
        
        if not email or not password:
            logger.warning("Missing email or password")
            return standardize_response(
                success=False,
                error='Email and password required',
                status_code=400
            )
        
        student = Student.query.filter_by(email=email, is_active=True).first()
        logger.debug(f"Student found: {student is not None}")
        
        if student:
            logger.debug(f"Student details - ID: {student.student_id}, Email: {student.email}")
            password_check = check_password(password, student.password_hash)
            logger.debug(f"Password check result: {password_check}")
            
            if password_check:
                access_token = create_access_token(
                    identity=str(student.student_id),
                    additional_claims={'type': 'student', 'student_id': student.student_id}
                )
                
                student_data = {
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'program': student.program,
                    'year_of_study': student.year_of_study or 1
                }
                
                logger.debug(f"Sending response: {student_data}")
                logger.info(f"Login successful for {email}")
                
                return standardize_response(
                    success=True,
                    data={
                        'access_token': access_token,
                        'student': student_data
                    },
                    message='Login successful',
                    status_code=200
                )
            else:
                logger.warning(f"Invalid password for {email}")
        else:
            logger.warning(f"No student found with email: {email}")
        
        logger.info(f"Login failed for {email}")
        return standardize_response(
            success=False,
            error='Invalid credentials',
            status_code=401
        )
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

# ============================================================================
# OTP MANAGEMENT ROUTES
# ============================================================================

@app.route('/api/faculty/generate-otp', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def generate_faculty_otp():
    """Generate OTP for faculty"""
    try:
        from flask_jwt_extended import get_jwt
        
        # Get claims from JWT
        claims = get_jwt()
        if claims.get('type') != 'faculty':
            return standardize_response(
                success=False,
                error='Faculty access required',
                status_code=403
            )
        
        faculty_id = claims.get('faculty_id')
        
        # Generate new OTP
        otp_code = generate_otp(app.config['OTP_LENGTH'])
        expires_at = datetime.utcnow() + timedelta(minutes=app.config['OTP_EXPIRY_MINUTES'])
        
        # Save OTP to database
        otp_log = OTPLog(
            faculty_id=faculty_id,
            otp_code=otp_code,
            expires_at=expires_at,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        db.session.add(otp_log)
        db.session.commit()
        
        return standardize_response(
            success=True,
            data={
                'otp': otp_code,
                'expires_at': expires_at.isoformat()
            },
            message='OTP generated successfully',
            status_code=200
        )
        
    except Exception as e:
        db.session.rollback()
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and start attendance session"""
    try:
        data = request.get_json()
        otp_code = data.get('otp')
        class_id = data.get('class_id')
        
        if not otp_code:
            return standardize_response(
                success=False,
                error='OTP required',
                status_code=400
            )
        
        # Find valid OTP for faculty login (removed default OTP "000000" bypass)
        current_time = datetime.utcnow()
        otp_log = db.session.query(OTPLog).filter(
            db.and_(
                getattr(OTPLog, 'otp_code') == otp_code,
                getattr(OTPLog, 'is_used').is_(False),
                getattr(OTPLog, 'expires_at') > current_time
            )
        ).first()
        
        if not otp_log:
            return standardize_response(
                success=False,
                error='Invalid or expired OTP',
                status_code=400
            )
        
        # Mark OTP as used
        otp_log.is_used = True
        otp_log.used_at = datetime.utcnow()
        
        # Validate that faculty has assigned classes
        faculty_classes = Classes.query.filter_by(faculty_id=otp_log.faculty_id, is_active=True).count()
        if faculty_classes == 0:
            return standardize_response(
                success=False,
                error='No classes assigned to this faculty. Please contact admin to assign classes.',
                status_code=400
            )
        
        # If class_id is provided, verify it belongs to this faculty
        if class_id:
            assigned_class = Classes.query.filter_by(
                class_id=class_id,
                faculty_id=otp_log.faculty_id,
                is_active=True
            ).first()
            
            if not assigned_class:
                return standardize_response(
                    success=False,
                    error='Selected class is not assigned to you. Please select an assigned class.',
                    status_code=400
                )
            
            # Use the provided class
            actual_class_id = class_id
        else:
            # Get the first assigned class as default
            first_class = Classes.query.filter_by(
                faculty_id=otp_log.faculty_id,
                is_active=True
            ).first()
            
            if not first_class:
                return standardize_response(
                    success=False,
                    error='No classes assigned to this faculty. Please contact admin to assign classes.',
                    status_code=400
                )
            
            actual_class_id = first_class.class_id
        
        # Business logic validation: Check if class is scheduled for today
        current_class = Classes.query.get(actual_class_id)
        if not current_class:
            return standardize_response(
                success=False,
                error='Class not found.',
                status_code=400
            )
        
        # Check if class has schedule information
        if current_class.schedule_day and current_class.start_time and current_class.end_time:
            # Get current day and time
            current_day = datetime.utcnow().strftime('%A')
            current_time = datetime.utcnow().time()
            
            # Check if class is scheduled for today
            if current_class.schedule_day != current_day:
                return standardize_response(
                    success=False,
                    error=f'Class {current_class.class_name} is not scheduled for {current_day}.',
                    data={
                        'scheduled_day': current_class.schedule_day,
                        'current_day': current_day
                    },
                    status_code=400
                )
            
            # Check if class is within scheduled time window (with 15-minute grace period)
            grace_period = timedelta(minutes=15)
            early_start = (datetime.combine(datetime.today(), current_class.start_time) - grace_period).time()
            late_end = (datetime.combine(datetime.today(), current_class.end_time) + grace_period).time()
            
            if not (early_start <= current_time <= late_end):
                return standardize_response(
                    success=False,
                    error=f'Class {current_class.class_name} is not scheduled at this time.',
                    data={
                        'scheduled_time': f'{current_class.start_time} - {current_class.end_time}',
                        'current_time': current_time.isoformat()
                    },
                    status_code=400
                )
        
        # Business logic validation: Check if class has students enrolled
        # Note: This would require a student enrollment table which is not currently implemented
        # For now, we'll just log a warning if no students are found
        # In a full implementation, this would prevent session creation
        
        # Create attendance session
        session_token = generate_token()
        secret_key = generate_token()
        expires_at = datetime.utcnow() + timedelta(seconds=app.config['QR_SESSION_DURATION'])
        
        attendance_session = AttendanceSession(
            class_id=actual_class_id,
            faculty_id=otp_log.faculty_id,
            qr_token=session_token,
            qr_secret_key=secret_key,
            qr_expires_at=expires_at,
            otp_used=otp_code,
            status='active'
        )
        
        db.session.add(attendance_session)
        db.session.commit()
        
        # Store session in memory for QR management
        with active_qr_sessions_lock:
            active_qr_sessions[attendance_session.session_id] = {
                'session_id': attendance_session.session_id,
                'token': session_token,
                'secret': secret_key,
                'expires_at': expires_at,
                'current_qr': None,
                'qr_count': 0
            }
        
        # Start QR generation
        start_qr_generation(attendance_session.session_id)
        
        # Get class information for response
        class_obj = Classes.query.get(actual_class_id)
        class_info = {
            'class_id': class_obj.class_id if class_obj else None,
            'class_code': class_obj.class_code if class_obj else None,
            'class_name': class_obj.class_name if class_obj else None
        }
        
        return standardize_response(
            success=True,
            data={
                'session_id': attendance_session.session_id,
                'class_info': class_info,
                'expires_at': expires_at.isoformat()
            },
            message='Attendance session started',
            status_code=200
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in verify_otp: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/qr/start', methods=['POST'])
def start_attendance_session():
    """Start an attendance session"""
    try:
        data = request.get_json()
        actual_class_id = data.get('class_id')
        duration = data.get('duration', 10)  # Default duration is 10 minutes

        if not actual_class_id:
            return standardize_response(
                success=False,
                error='Class ID is required',
                status_code=400
            )

        # Get the first active faculty (this is a temporary solution)
        faculty = Faculty.query.filter_by(is_active=True).first()
        if not faculty:
            return standardize_response(
                success=False,
                error='No active faculty found',
                status_code=400
            )
            
        faculty_id = faculty.faculty_id

        # Generate session token and secret key
        session_token = generate_token()
        secret_key = generate_token()
        expires_at = datetime.utcnow() + timedelta(minutes=duration)

        # Create a new attendance session
        attendance_session = AttendanceSession(
            class_id=actual_class_id,
            faculty_id=faculty_id,
            qr_token=session_token,
            qr_secret_key=secret_key,
            qr_expires_at=expires_at,
            status='active'
        )
        db.session.add(attendance_session)
        db.session.commit()
        
        # Store session in memory for QR management
        with active_qr_sessions_lock:
            active_qr_sessions[attendance_session.session_id] = {
                'session_id': attendance_session.session_id,
                'token': session_token,
                'secret': secret_key,
                'expires_at': expires_at,
                'current_qr': None,
                'qr_count': 0
            }
        
        # Start QR generation
        start_qr_generation(attendance_session.session_id)
        
        # Get class information for response
        class_obj = Classes.query.get(actual_class_id)
        class_info = {
            'class_id': class_obj.class_id if class_obj else None,
            'class_code': class_obj.class_code if class_obj else None,
            'class_name': class_obj.class_name if class_obj else None
        }
        
        return standardize_response(
            success=True,
            data={
                'session_id': attendance_session.session_id,
                'class_info': class_info,
                'expires_at': expires_at.isoformat()
            },
            message='Attendance session started',
            status_code=200
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in start_attendance_session: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

# ============================================================================
# QR CODE MANAGEMENT
# ============================================================================

def start_qr_generation(session_id):
    """Start QR code generation for a session"""
    def generate_qr_sequence():
        try:
            with app.app_context():
                session_data = active_qr_sessions.get(session_id)
                if not session_data:
                    logger.warning(f"Session {session_id} not found in active sessions")
                    return
                
                start_time = datetime.utcnow()
                end_time = session_data['expires_at']
                logger.info(f"Starting QR generation for session {session_id}")
                
                while datetime.utcnow() < end_time:
                    # Check if session is still active with lock
                    with active_qr_sessions_lock:
                        if session_id not in active_qr_sessions:
                            break
                    # Check if session is still active in database with proper synchronization
                    try:
                        db_session = AttendanceSession.query.get(session_id)
                        if not db_session:
                            logger.warning(f"Session {session_id} not found in database")
                            # Remove from active sessions if not in database
                            with active_qr_sessions_lock:
                                if session_id in active_qr_sessions:
                                    del active_qr_sessions[session_id]
                            break
                        
                        # Check if session status has changed
                        if db_session.status != 'active':
                            logger.warning(f"Session {session_id} no longer active in database (status: {db_session.status})")
                            # Remove from active sessions if not active
                            with active_qr_sessions_lock:
                                if session_id in active_qr_sessions:
                                    del active_qr_sessions[session_id]
                            break
                            
                        # Check if session has expired in database
                        if db_session.qr_expires_at and datetime.utcnow() > db_session.qr_expires_at:
                            logger.info(f"Session {session_id} expired in database")
                            # Update status and remove from active sessions
                            db_session.status = 'completed'
                            db_session.end_time = datetime.utcnow()
                            db.session.commit()
                            with active_qr_sessions_lock:
                                if session_id in active_qr_sessions:
                                    del active_qr_sessions[session_id]
                            break
                    except Exception as e:
                        logger.error(f"Database error checking session status: {e}")
                        # Continue generation but log the error
                        pass
                        
                    # Generate new QR token
                    current_time = int(time.time())
                    qr_data = {
                        'session_id': session_id,
                        'token': session_data['token'],
                        'timestamp': current_time,
                        'sequence': session_data['qr_count']
                    }
                    
                    # Create QR code
                    try:
                        qr_filename = create_qr_code(json.dumps(qr_data), session_id)
                        
                        if qr_filename:
                            session_data['current_qr'] = qr_filename
                            session_data['qr_count'] += 1
                            
                            logger.info(f"Generated QR {session_data['qr_count']} for session {session_id}: {qr_filename}")
                        else:
                            logger.warning(f"Failed to create QR code for session {session_id}")
                    except Exception as e:
                        logger.error(f"Error creating QR code for session {session_id}: {e}")
                        # Continue with next iteration
                        pass
                    
                    # Wait for refresh interval
                    try:
                        time.sleep(app.config['QR_REFRESH_INTERVAL'])
                    except Exception as e:
                        logger.error(f"Error during sleep in QR generation: {e}")
                        break
                
                # Clean up session with proper synchronization
                try:
                    # Remove from active sessions first
                    with active_qr_sessions_lock:
                        if session_id in active_qr_sessions:
                            del active_qr_sessions[session_id]
                            logger.info(f"Cleaned up session {session_id} from active sessions")
                    
                    # Update session status in database
                    try:
                        session = AttendanceSession.query.get(session_id)
                        if session and session.status == 'active':
                            session.status = 'completed'
                            session.end_time = datetime.utcnow()
                            db.session.commit()
                            logger.info(f"Database session {session_id} marked as completed")
                    except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error updating database session {session_id}: {e}")
                except Exception as e:
                    logger.error(f"Error during session cleanup for {session_id}: {e}")
                    
                logger.info(f"QR generation completed for session {session_id}")
        
        except Exception as e:
            logger.error(f"Critical error in QR generation thread for session {session_id}: {e}")
            # Attempt to clean up
            try:
                with active_qr_sessions_lock:
                    if session_id in active_qr_sessions:
                        del active_qr_sessions[session_id]
            except:
                pass
    
    # Start generation in background thread
    try:
        thread = threading.Thread(target=generate_qr_sequence, daemon=True)
        thread.start()
        logger.info(f"QR generation thread started for session {session_id}")
    except Exception as e:
        logger.error(f"Failed to start QR generation thread for session {session_id}: {e}")

@app.route('/api/qr/current/<int:session_id>')
def get_current_qr(session_id):
    """Get current QR code for display"""
    try:
        with active_qr_sessions_lock:
            session_data = active_qr_sessions.get(session_id)
        
        if not session_data:
            return jsonify({'error': 'Session not found or expired'}), 404
        
        if datetime.utcnow() > session_data['expires_at']:
            return jsonify({'error': 'Session expired'}), 410
        
        current_qr = session_data.get('current_qr')
        if not current_qr:
            return jsonify({'error': 'QR not ready'}), 404
        
        return jsonify({
            'success': True,
            'qr_filename': current_qr,
            'qr_url': f"/static/qr_tokens/{current_qr}",
            'sequence': session_data['qr_count'],
            'expires_at': session_data['expires_at'].isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/stop/<int:session_id>', methods=['POST'])
def stop_session(session_id):
    """Stop QR generation session"""
    try:
        # Update database session status
        session = AttendanceSession.query.get(session_id)
        if session:
            session.status = 'completed'
            session.end_time = datetime.utcnow()
            db.session.commit()
            logger.info(f"Database session {session_id} marked as completed")
        
        # Remove from active sessions to stop QR generation
        with active_qr_sessions_lock:
            if session_id in active_qr_sessions:
                del active_qr_sessions[session_id]
                logger.info(f"Removed session {session_id} from active sessions")
        
        return standardize_response(
            success=True,
            message='Session stopped successfully',
            status_code=200
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error stopping session {session_id}: {e}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout and cleanup all active sessions"""
    try:
        # Get JWT claims for token blacklisting
        claims = get_jwt()
        
        # Add token to blacklist for secure logout
        jti = claims['jti']
        with jwt_blacklist_lock:
            jwt_blacklist.add(jti)
        
        # Stop all active QR sessions
        with active_qr_sessions_lock:
            active_session_ids = list(active_qr_sessions.keys())
        
        for session_id in active_session_ids:
            # Update database session status
            session = AttendanceSession.query.get(session_id)
            if session and session.status == 'active':
                session.status = 'completed'
                session.end_time = datetime.utcnow()
                logger.info(f"Logout: Database session {session_id} marked as completed")
            
            # Remove from active sessions
            with active_qr_sessions_lock:
                if session_id in active_qr_sessions:
                    del active_qr_sessions[session_id]
                    logger.info(f"Logout: Removed session {session_id} from active sessions")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Logged out and stopped {len(active_session_ids)} active sessions'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during logout: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ATTENDANCE SCANNING ROUTES
# ============================================================================

@app.route('/api/attendance/scan', methods=['POST'])
@jwt_required()
def scan_attendance():
    """Process attendance scan from student"""
    try:
        current_user = get_jwt_identity()
        if current_user['type'] != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        student_id = current_user['student_id']
        data = request.get_json()
        
        # Extract scan data
        qr_data_str = data.get('qr_data')
        biometric_verified = data.get('biometric_verified', False)
        location_data = data.get('location', {})
        bluetooth_data = data.get('bluetooth', {})
        device_info = data.get('device_info', {})
        
        if not qr_data_str:
            return jsonify({'error': 'QR data required'}), 400
        
        # Parse QR data
        try:
            qr_data = json.loads(qr_data_str)
            session_id = qr_data.get('session_id')
            token = qr_data.get('token')
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid QR data format'}), 400
        
        # Validate session
        session = AttendanceSession.query.filter_by(
            session_id=session_id,
            qr_token=token,
            status='active'
        ).first()
        
        if not session:
            return jsonify({'error': 'Invalid or expired session'}), 400
        
        if datetime.utcnow() > session.qr_expires_at:
            return jsonify({'error': 'Session expired'}), 400
        
        # Check if already marked
        existing_record = AttendanceRecord.query.filter_by(
            session_id=session_id,
            student_id=student_id
        ).first()
        
        if existing_record:
            return jsonify({'error': 'Attendance already marked'}), 400
        
        # Verify location if provided
        location_verified = False
        gps_distance = None
        
        if location_data.get('latitude') and location_data.get('longitude'):
            # Get actual classroom coordinates from database
            try:
                # Get the class associated with this session
                class_obj = Classes.query.get(session.class_id)
                if class_obj and class_obj.classroom_id:
                    # Get the classroom details
                    classroom = Classroom.query.get(class_obj.classroom_id)
                    if classroom and classroom.latitude and classroom.longitude:
                        classroom_lat = float(classroom.latitude)
                        classroom_lng = float(classroom.longitude)
                        radius = int(float(classroom.geofence_radius)) if classroom.geofence_radius else 50
                        
                        # Enhanced geofencing with accuracy validation
                        gps_accuracy = location_data.get('accuracy')
                        location_verified, gps_distance = verify_geofence(
                            location_data['latitude'],
                            location_data['longitude'],
                            classroom_lat,
                            classroom_lng,
                            radius,
                            gps_accuracy
                        )
                    else:
                        logger.warning(f"Classroom {class_obj.classroom_id} has no coordinates")
                else:
                    logger.warning(f"Class {session.class_id} has no classroom assigned")
            except Exception as e:
                logger.error(f"Error getting classroom coordinates: {e}")
                # Fallback to default coordinates if database lookup fails
                classroom_lat = 40.7128  # Default coordinates
                classroom_lng = -74.0060
                # Enhanced geofencing with fallback coordinates and accuracy validation
                gps_accuracy = location_data.get('accuracy')
                location_verified, gps_distance = verify_geofence(
                    location_data['latitude'],
                    location_data['longitude'],
                    classroom_lat,
                    classroom_lng,
                    50,  # Default radius
                    gps_accuracy
                )

        # Verify Bluetooth proximity
        bluetooth_verified = False
        bluetooth_rssi = bluetooth_data.get('rssi')
        
        if bluetooth_rssi:
            bluetooth_verified = int(bluetooth_rssi) >= app.config['BLUETOOTH_PROXIMITY_RSSI']
        
        # Calculate verification score
        verification_score = calculate_verification_score(
            biometric_verified,
            location_verified,
            bluetooth_verified
        )
        
        # Determine attendance status
        status = 'present' if verification_score >= 0.6 else 'invalid'
        
        # Create attendance record
        attendance_record = AttendanceRecord(
            session_id=session_id,
            student_id=student_id,
            biometric_verified=biometric_verified,
            location_verified=location_verified,
            bluetooth_verified=bluetooth_verified,
            gps_latitude=location_data.get('latitude'),
            gps_longitude=location_data.get('longitude'),
            gps_accuracy=location_data.get('accuracy'),
            bluetooth_rssi=bluetooth_rssi,
            device_info=device_info,
            verification_score=verification_score,
            status=status
        )
        
        db.session.add(attendance_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'status': status,
            'verification_score': verification_score,
            'verifications': {
                'biometric': biometric_verified,
                'location': location_verified,
                'bluetooth': bluetooth_verified
            },
            'message': 'Attendance recorded successfully' if status == 'present' else 'Verification failed'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# STATIC FILE ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main faculty portal"""
    return render_template('index.html')

@app.route('/smartboard')
def smartboard_portal():
    """SmartBoard QR display portal"""
    return render_template('smartboard/index.html')

@app.route('/student')
def student_portal():
    """Student portal"""
    return render_template('student/index.html')

@app.route('/static/qr_tokens/<filename>')
def serve_qr_image(filename):
    """Serve QR code images from centralized QR_DATA folder"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    qr_tokens_path = os.path.join(project_root, 'QR_DATA', 'tokens')
    return send_from_directory(qr_tokens_path, filename)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# SYSTEM MONITORING & CONTROL ROUTES
# ============================================================================

# Global variables for system monitoring
system_metrics = {
    'start_time': datetime.utcnow(),
    'active_sessions': 0,
    'qr_generated': 0,
    'total_logins': 0
}

@app.route('/monitor')
def system_monitor():
    """System monitoring dashboard"""
    return render_template('system_monitor.html')

@app.route('/api/system/metrics')
def get_system_metrics():
    """Get system metrics for monitoring dashboard"""
    try:
        # Count active sessions
        with active_qr_sessions_lock:
            active_sessions_count = len(active_qr_sessions)
        
        # Count QR codes generated today
        today = datetime.utcnow().date()
        qr_count = 0
        with active_qr_sessions_lock:
            for session_data in active_qr_sessions.values():
                if session_data.get('start_time', datetime.utcnow()).date() == today:
                    qr_count += session_data.get('qr_count', 0)
        
        # Count logins today (from database)
        login_count = 0
        try:
            # This would need to be implemented based on login tracking
            login_count = system_metrics.get('total_logins', 0)
        except:
            pass
        
        return jsonify({
            'success': True,
            'data': {
                'active_sessions': active_sessions_count,
                'qr_generated': qr_count,
                'total_logins': login_count,
                'uptime': (datetime.utcnow() - system_metrics['start_time']).total_seconds()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check database connectivity
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        with active_qr_sessions_lock:
            qr_status = 'healthy' if active_qr_sessions else 'idle'
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': 'healthy',
                'qr_generator': qr_status,
                'auth_service': 'healthy'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/qr/status')
def qr_service_status():
    """QR generation service status"""
    try:
        with active_qr_sessions_lock:
            active_count = len(active_qr_sessions)
            
            return jsonify({
                'success': True,
                'status': 'running' if active_count > 0 else 'idle',
                'active_sessions': active_count,
                'sessions': list(active_qr_sessions.keys())
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/db/status')
def database_status():
    """Database service status"""
    try:
        # Test database connection
        from sqlalchemy import text
        result = db.session.execute(text('SELECT COUNT(*) as count FROM students'))
        row = result.fetchone()
        student_count = row[0] if row else 0
        
        result = db.session.execute(text('SELECT COUNT(*) as count FROM faculty'))
        row = result.fetchone()
        faculty_count = row[0] if row else 0
        
        return jsonify({
            'success': True,
            'status': 'connected',
            'students': student_count,
            'faculty': faculty_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'disconnected',
            'error': str(e)
        }), 500

@app.route('/api/auth/status')
def auth_service_status():
    """Authentication service status"""
    try:
        return jsonify({
            'success': True,
            'status': 'running',
            'jwt_enabled': True,
            'endpoints': {
                'faculty_login': '/api/faculty/login',
                'student_login': '/api/student/login'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/session/status')
def session_service_status():
    """Session management service status"""
    try:
        active_count = len(active_qr_sessions)
        with active_qr_sessions_lock:
            sessions_info = []
            
            for session_id, session_data in active_qr_sessions.items():
                sessions_info.append({
                    'session_id': session_id,
                    'status': 'active',
                    'start_time': session_data.get('start_time', datetime.utcnow()).isoformat(),
                    'expires_at': session_data.get('expires_at', datetime.utcnow()).isoformat(),
                    'qr_count': session_data.get('qr_count', 0)
                })
        
        return jsonify({
            'success': True,
            'status': 'running',
            'active_sessions': active_count,
            'sessions': sessions_info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/process/<action>', methods=['POST'])
def control_process(action):
    """Control system processes (start/stop/restart)"""
    try:
        data = request.get_json()
        process_id = data.get('process_id')
        
        if not process_id:
            return jsonify({'success': False, 'error': 'Process ID required'}), 400
        
        if action == 'stop':
            if process_id == 'qr-generator':
                # Stop all QR generation sessions
                with active_qr_sessions_lock:
                    active_session_ids = list(active_qr_sessions.keys())
                    for session_id in active_session_ids:
                        # Stop QR generation for this session
                        if session_id in active_qr_sessions:
                            del active_qr_sessions[session_id]
                
                return jsonify({
                    'success': True,
                    'message': f'Stopped {len(active_session_ids)} QR generation sessions'
                })
            
            elif process_id == 'session-manager':
                # Stop all active sessions
                with active_qr_sessions_lock:
                    stopped_sessions = []
                    for session_id in list(active_qr_sessions.keys()):
                        session = AttendanceSession.query.get(session_id)
                        if session and session.status == 'active':
                            session.status = 'completed'
                            session.end_time = datetime.utcnow()
                            stopped_sessions.append(session_id)
                    
                    db.session.commit()
                    active_qr_sessions.clear()
                
                return jsonify({
                    'success': True,
                    'message': f'Stopped {len(stopped_sessions)} sessions'
                })
        
        elif action == 'start':
            return jsonify({
                'success': True,
                'message': f'Process {process_id} start command acknowledged'
            })
        
        elif action == 'restart':
            return jsonify({
                'success': True,
                'message': f'Process {process_id} restart command acknowledged'
            })
        
        return jsonify({'success': False, 'error': 'Invalid action'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ADMIN AUTHENTICATION ROUTES
# ============================================================================

@app.route('/api/admin/login', methods=['POST'])
@limiter.limit("5 per minute")
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        admin = Admin.query.filter_by(username=username, is_active=True).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            # Update last login
            admin.last_login = datetime.utcnow()
            db.session.commit()
            
            access_token = create_access_token(
                identity=str(admin.admin_id),
                additional_claims={'type': 'admin', 'admin_id': admin.admin_id, 'role': admin.role}
            )
            
            return jsonify({
                'success': True,
                'access_token': access_token,
                'admin': {
                    'admin_id': admin.admin_id,
                    'username': admin.username,
                    'email': admin.email,
                    'name': f"{admin.first_name} {admin.last_name}",
                    'role': admin.role
                }
            })
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/logout', methods=['POST'])
@jwt_required()
def admin_logout():
    """Admin logout endpoint"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        # Add token to blacklist for secure logout
        jti = claims['jti']
        with jwt_blacklist_lock:
            jwt_blacklist.add(jti)
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ADMIN API ROUTES
# ============================================================================

# Faculty Management Routes
@app.route('/api/admin/faculty', methods=['GET'])
@jwt_required()
def admin_get_faculty_list():
    """Get list of all faculty members"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get search parameter
        search = request.args.get('search', '')
        
        # Build query
        query = db.session.query(Faculty)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    getattr(Faculty, 'first_name').like('%' + search_filter + '%'),
                    getattr(Faculty, 'last_name').like('%' + search_filter + '%'),
                    getattr(Faculty, 'email').like('%' + search_filter + '%'),
                    getattr(Faculty, 'faculty_code').like('%' + search_filter + '%')
                )
            )
        
        # Execute query and manually paginate
        total_count = query.count()
        offset = (page - 1) * per_page
        faculty_items = query.offset(offset).limit(per_page).all()
        
        faculty_list = []
        for faculty in faculty_items:
            faculty_list.append({
                'faculty_id': faculty.faculty_id,
                'faculty_code': faculty.faculty_code,
                'first_name': faculty.first_name,
                'last_name': faculty.last_name,
                'email': faculty.email,
                'phone_number': faculty.phone_number,
                'department': faculty.department,
                'is_active': faculty.is_active,
                'created_at': faculty.created_at.isoformat() if faculty.created_at else None,
                'updated_at': faculty.updated_at.isoformat() if faculty.updated_at else None
            })
        
        # Calculate pagination details
        total_pages = (total_count + per_page - 1) // per_page
        
        return jsonify({
            'success': True,
            'faculty': faculty_list,
            'pagination': {
                'page': page,
                'pages': total_pages,
                'per_page': per_page,
                'total': total_count
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/faculty/<int:faculty_id>', methods=['GET'])
@jwt_required()
def admin_get_faculty(faculty_id):
    """Get specific faculty member details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        return jsonify({
            'success': True,
            'faculty': {
                'faculty_id': faculty.faculty_id,
                'faculty_code': faculty.faculty_code,
                'first_name': faculty.first_name,
                'last_name': faculty.last_name,
                'email': faculty.email,
                'phone_number': faculty.phone_number,
                'department': faculty.department,
                'is_active': faculty.is_active,
                'created_at': faculty.created_at.isoformat() if faculty.created_at else None,
                'updated_at': faculty.updated_at.isoformat() if faculty.updated_at else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/faculty', methods=['POST'])
@jwt_required()
def admin_create_faculty():
    """Create new faculty member"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['faculty_code', 'first_name', 'last_name', 'email', 'phone_number', 'department', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if faculty code or email already exists
        existing = db.session.query(Faculty).filter(
            db.or_(
                Faculty.faculty_code == data['faculty_code'],
                Faculty.email == data['email']
            )
        ).first()
        
        if existing:
            return jsonify({'error': 'Faculty code or email already exists'}), 400
        
        # Create new faculty
        faculty = Faculty(
            faculty_code=data['faculty_code'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone_number=data['phone_number'],
            department=data['department'],
            password_hash=bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(faculty)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Faculty created successfully',
            'faculty': {
                'faculty_id': faculty.faculty_id,
                'faculty_code': faculty.faculty_code,
                'first_name': faculty.first_name,
                'last_name': faculty.last_name,
                'email': faculty.email,
                'phone_number': faculty.phone_number,
                'department': faculty.department,
                'is_active': faculty.is_active
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/faculty/<int:faculty_id>', methods=['PUT'])
@jwt_required()
def admin_update_faculty(faculty_id):
    """Update faculty member"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'faculty_code' in data and data['faculty_code'] != faculty.faculty_code:
            # Check if faculty code or email already exists
            existing = db.session.query(Faculty).filter(
                db.or_(
                    getattr(Faculty, 'faculty_code') == data['faculty_code'],
                    getattr(Faculty, 'email') == data['email']
                )
            ).first()
            if existing:
                return jsonify({'error': 'Faculty code already exists'}), 400
            faculty.faculty_code = data['faculty_code']
        
        if 'first_name' in data:
            faculty.first_name = data['first_name']
        
        if 'last_name' in data:
            faculty.last_name = data['last_name']
        
        if 'email' in data and data['email'] != faculty.email:
            # Check if new email already exists
            existing = db.session.query(Faculty).filter(
                Faculty.email == data['email'],
                Faculty.faculty_id != faculty_id
            ).first()
            if existing:
                return jsonify({'error': 'Email already exists'}), 400
            faculty.email = data['email']
        
        if 'phone_number' in data:
            faculty.phone_number = data['phone_number']
        
        if 'department' in data:
            faculty.department = data['department']
        
        if 'is_active' in data:
            faculty.is_active = data['is_active']
        
        if 'password' in data:
            faculty.password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        faculty.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Faculty updated successfully',
            'faculty': {
                'faculty_id': faculty.faculty_id,
                'faculty_code': faculty.faculty_code,
                'first_name': faculty.first_name,
                'last_name': faculty.last_name,
                'email': faculty.email,
                'phone_number': faculty.phone_number,
                'department': faculty.department,
                'is_active': faculty.is_active
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/faculty/<int:faculty_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_faculty(faculty_id):
    """Delete faculty member"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Check if faculty has any classes
        classes = Classes.query.filter_by(faculty_id=faculty_id).count()
        if classes > 0:
            return jsonify({'error': 'Cannot delete faculty with associated classes'}), 400
        
        db.session.delete(faculty)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Faculty deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Student Management Routes
@app.route('/api/admin/students', methods=['GET'])
@jwt_required()
def admin_get_students_list():
    """Get list of all students"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get search parameter
        search = request.args.get('search', '')
        
        # Build query
        query = Student.query
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Student.first_name.like(search_filter),
                    Student.last_name.like(search_filter),
                    Student.email.like(search_filter),
                    Student.student_code.like(search_filter),
                    Student.program.like(search_filter)
                )
            )
        
        # Paginate results
        students_pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        students_list = []
        for student in students_pagination.items:
            students_list.append({
                'student_id': student.student_id,
                'student_code': student.student_code,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone_number': student.phone_number,
                'program': student.program,
                'year_of_study': student.year_of_study,
                'is_active': student.is_active,
                'created_at': student.created_at.isoformat() if student.created_at else None,
                'updated_at': student.updated_at.isoformat() if student.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'students': students_list,
            'pagination': {
                'page': students_pagination.page,
                'pages': students_pagination.pages,
                'per_page': students_pagination.per_page,
                'total': students_pagination.total
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/students/<int:student_id>', methods=['GET'])
@jwt_required()
def admin_get_student(student_id):
    """Get specific student details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        return jsonify({
            'success': True,
            'student': {
                'student_id': student.student_id,
                'student_code': student.student_code,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone_number': student.phone_number,
                'program': student.program,
                'year_of_study': student.year_of_study,
                'is_active': student.is_active,
                'created_at': student.created_at.isoformat() if student.created_at else None,
                'updated_at': student.updated_at.isoformat() if student.updated_at else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/students', methods=['POST'])
@jwt_required()
def admin_create_student():
    """Create new student"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_code', 'first_name', 'last_name', 'email', 'program', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if student code or email already exists
        existing = Student.query.filter(
            db.or_(
                Student.student_code == data['student_code'],
                Student.email == data['email']
            )
        ).first()
        
        if existing:
            return jsonify({'error': 'Student code or email already exists'}), 400
        
        # Create new student
        student = Student(
            student_code=data['student_code'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            program=data['program'],
            password_hash=bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            phone_number=data.get('phone_number'),
            year_of_study=data.get('year_of_study'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Student created successfully',
            'student': {
                'student_id': student.student_id,
                'student_code': student.student_code,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'program': student.program,
                'phone_number': student.phone_number,
                'year_of_study': student.year_of_study,
                'is_active': student.is_active
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/students/<int:student_id>', methods=['PUT'])
@jwt_required()
def admin_update_student(student_id):
    """Update student"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'student_code' in data and data['student_code'] != student.student_code:
            # Check if new student code already exists
            existing = Student.query.filter(
                Student.student_code == data['student_code'],
                Student.student_id != student_id
            ).first()
            if existing:
                return jsonify({'error': 'Student code already exists'}), 400
            student.student_code = data['student_code']
        
        if 'first_name' in data:
            student.first_name = data['first_name']
        
        if 'last_name' in data:
            student.last_name = data['last_name']
        
        if 'email' in data and data['email'] != student.email:
            # Check if new email already exists
            existing = Student.query.filter(
                Student.email == data['email'],
                Student.student_id != student_id
            ).first()
            if existing:
                return jsonify({'error': 'Email already exists'}), 400
            student.email = data['email']
        
        if 'phone_number' in data:
            student.phone_number = data['phone_number']
        
        if 'program' in data:
            student.program = data['program']
        
        if 'year_of_study' in data:
            student.year_of_study = data['year_of_study']
        
        if 'is_active' in data:
            student.is_active = data['is_active']
        
        if 'password' in data:
            student.password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        student.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Student updated successfully',
            'student': {
                'student_id': student.student_id,
                'student_code': student.student_code,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'program': student.program,
                'phone_number': student.phone_number,
                'year_of_study': student.year_of_study,
                'is_active': student.is_active
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_student_permanent(student_id):
    """Delete student"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Check if student is enrolled in any classes
        classes = Classes.query.filter_by(student_id=student_id).count()
        if classes > 0:
            return jsonify({'error': 'Cannot delete student enrolled in classes'}), 400
        
        db.session.delete(student)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Student deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Classroom Management Routes
@app.route('/api/admin/classrooms', methods=['GET'])
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
        
        # Build query
        query = Classroom.query
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Classroom.room_number.like(search_filter),
                    Classroom.building_name.like(search_filter)
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classrooms/<int:classroom_id>', methods=['GET'])
@jwt_required()
def admin_get_classroom(classroom_id):
    """Get specific classroom details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classrooms', methods=['POST'])
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
        
        # Check if room number already exists
        existing = Classroom.query.filter_by(room_number=data['room_number']).first()
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
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classrooms/<int:classroom_id>', methods=['PUT'])
@jwt_required()
def admin_update_classroom_detailed(classroom_id):
    """Update classroom"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        classroom = Classroom.query.get(classroom_id)
        if not classroom:
            return jsonify({'error': 'Classroom not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'room_number' in data and data['room_number'] != classroom.room_number:
            # Check if new room number already exists
            existing = Classroom.query.filter(
                Classroom.room_number == data['room_number'],
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
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classrooms/<int:classroom_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_classroom_permanent(classroom_id):
    """Delete classroom"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
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
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/students/<int:student_id>/update', methods=['PUT'])
@jwt_required()
def admin_get_classes_list():
    """Get list of all classes"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get search parameter
        search = request.args.get('search', '')
        
        # Build query
        query = db.session.query(Faculty)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Faculty.first_name.like(search_filter),
                    Faculty.last_name.like(search_filter),
                    Faculty.email.like(search_filter),
                    Faculty.faculty_code.like(search_filter)
                )
            )
        # Build query with joins to get related data
        query = db.session.query(Classes, Faculty, Classroom).outerjoin(
            Faculty, Classes.faculty_id == Faculty.faculty_id
        ).outerjoin(
            Classroom, Classes.classroom_id == Classroom.classroom_id
        )
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Classes.class_code.like(search_filter),
                    Classes.class_name.like(search_filter),
                    Faculty.first_name.like(search_filter),
                    Faculty.last_name.like(search_filter),
                    Classroom.room_number.like(search_filter)
                )
            )
        
        # Paginate results
        classes_pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        classes_list = []
        for class_obj, faculty, classroom in classes_pagination.items:
            classes_list.append({
                'class_id': class_obj.class_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'faculty_id': class_obj.faculty_id,
                'faculty_name': f"{faculty.first_name} {faculty.last_name}" if faculty else None,
                'classroom_id': class_obj.classroom_id,
                'room_number': classroom.room_number if classroom else None,
                'semester': class_obj.semester,
                'academic_year': class_obj.academic_year,
                'credits': class_obj.credits,
                'max_students': class_obj.max_students,
                'created_at': class_obj.created_at.isoformat() if class_obj.created_at else None,
                'updated_at': class_obj.updated_at.isoformat() if class_obj.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'classes': classes_list,
            'pagination': {
                'page': classes_pagination.page,
                'pages': classes_pagination.pages,
                'per_page': classes_pagination.per_page,
                'total': classes_pagination.total
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classes/<int:class_id>', methods=['GET'])
@jwt_required()
def admin_get_class_summary(class_id):
    """Get specific class details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get class with related data
        class_data = db.session.query(Classes, Faculty, Classroom).outerjoin(
            Faculty, Classes.faculty_id == Faculty.faculty_id
        ).outerjoin(
            Classroom, Classes.classroom_id == Classroom.classroom_id
        ).filter(Classes.class_id == class_id).first()
        
        if not class_data:
            return jsonify({'error': 'Class not found'}), 404
        
        class_obj, faculty, classroom = class_data
        
        return jsonify({
            'success': True,
            'class': {
                'class_id': class_obj.class_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'faculty_id': class_obj.faculty_id,
                'faculty_name': f"{faculty.first_name} {faculty.last_name}" if faculty else None,
                'classroom_id': class_obj.classroom_id,
                'room_number': classroom.room_number if classroom else None,
                'semester': class_obj.semester,
                'academic_year': class_obj.academic_year,
                'credits': class_obj.credits,
                'max_students': class_obj.max_students,
                'created_at': class_obj.created_at.isoformat() if class_obj.created_at else None,
                'updated_at': class_obj.updated_at.isoformat() if class_obj.updated_at else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classes', methods=['POST'])
@jwt_required()
def admin_create_class():
    """Create new class"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['class_code', 'class_name', 'faculty_id', 'classroom_id', 'semester', 'academic_year']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new class
        class_obj = Classes(
            class_code=data['class_code'],
            class_name=data['class_name'],
            faculty_id=data['faculty_id'],
            classroom_id=data['classroom_id'],
            semester=data['semester'],
            academic_year=data['academic_year'],
            credits=data.get('credits', 3),
            max_students=data.get('max_students', 30)
        )
        
        db.session.add(class_obj)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Class created successfully',
            'class': {
                'class_id': class_obj.class_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'faculty_id': class_obj.faculty_id,
                'classroom_id': class_obj.classroom_id,
                'semester': class_obj.semester,
                'academic_year': class_obj.academic_year,
                'credits': class_obj.credits,
                'max_students': class_obj.max_students,
                'created_at': class_obj.created_at.isoformat() if class_obj.created_at else None,
                'updated_at': class_obj.updated_at.isoformat() if class_obj.updated_at else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classes/<int:class_id>', methods=['PUT'])
@jwt_required()
def admin_update_class(class_id):
    """Update class"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        class_obj = Classes.query.get(class_id)
        if not class_obj:
            return jsonify({'error': 'Class not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'class_code' in data:
            class_obj.class_code = data['class_code']
        
        if 'class_name' in data:
            class_obj.class_name = data['class_name']
        
        if 'faculty_id' in data:
            class_obj.faculty_id = data['faculty_id']
        
        if 'classroom_id' in data:
            class_obj.classroom_id = data['classroom_id']
        
        if 'semester' in data:
            class_obj.semester = data['semester']
        
        if 'academic_year' in data:
            class_obj.academic_year = data['academic_year']
        
        if 'credits' in data:
            class_obj.credits = data['credits']
        
        if 'max_students' in data:
            class_obj.max_students = data['max_students']
        
        class_obj.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Class updated successfully',
            'class': {
                'class_id': class_obj.class_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'faculty_id': class_obj.faculty_id,
                'classroom_id': class_obj.classroom_id,
                'semester': class_obj.semester,
                'academic_year': class_obj.academic_year,
                'credits': class_obj.credits,
                'max_students': class_obj.max_students,
                'created_at': class_obj.created_at.isoformat() if class_obj.created_at else None,
                'updated_at': class_obj.updated_at.isoformat() if class_obj.updated_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classes/<int:class_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_class(class_id):
    """Delete class"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        class_obj = Classes.query.get(class_id)
        if not class_obj:
            return jsonify({'error': 'Class not found'}), 404
        
        # Check if class has any students enrolled
        students = Classes.query.filter_by(class_id=class_id).count()
        if students > 0:
            return jsonify({'error': 'Cannot delete class with students enrolled'}), 400
        
        db.session.delete(class_obj)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Class deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Device Management Routes
@app.route('/api/admin/devices', methods=['GET'])
@jwt_required()
def admin_get_devices_list():
    """Get list of all student devices"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get search parameter
        search = request.args.get('search', '')
        
        # Build query with joins to get related data
        query = db.session.query(StudentDevices, Student).join(
            Student, StudentDevices.student_id == Student.student_id
        )
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Student.first_name.like(search_filter),
                    Student.last_name.like(search_filter),
                    Student.student_code.like(search_filter),
                    StudentDevices.device_uuid.like(search_filter),
                    StudentDevices.device_name.like(search_filter)
                )
            )
        
        # Order by last seen descending
        query = query.order_by(StudentDevices.last_seen.desc())
        
        # Paginate results
        devices_pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        devices_list = []
        for device, student in devices_pagination.items:
            devices_list.append({
                'device_id': device.device_id,
                'student_id': device.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code,
                'device_uuid': device.device_uuid,
                'device_name': device.device_name,
                'device_type': device.device_type,
                'device_model': device.device_model,
                'os_version': device.os_version,
                'app_version': device.app_version,
                'fcm_token': device.fcm_token,
                'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                'is_active': device.is_active,
                'biometric_enabled': device.biometric_enabled,
                'location_permission': device.location_permission,
                'bluetooth_permission': device.bluetooth_permission,
                'created_at': device.created_at.isoformat() if device.created_at else None,
                'updated_at': device.updated_at.isoformat() if device.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'devices': devices_list,
            'pagination': {
                'page': devices_pagination.page,
                'pages': devices_pagination.pages,
                'per_page': devices_pagination.per_page,
                'total': devices_pagination.total
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/devices/<int:device_id>', methods=['GET'])
@jwt_required()
def admin_get_device(device_id):
    """Get specific device details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get device with related data
        device_data = db.session.query(StudentDevices, Student).join(
            Student, StudentDevices.student_id == Student.student_id
        ).filter(StudentDevices.device_id == device_id).first()
        
        if not device_data:
            return jsonify({'error': 'Device not found'}), 404
        
        device, student = device_data
        
        return jsonify({
            'success': True,
            'device': {
                'device_id': device.device_id,
                'student_id': device.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code,
                'student_email': student.email,
                'device_uuid': device.device_uuid,
                'device_name': device.device_name,
                'device_type': device.device_type,
                'device_model': device.device_model,
                'os_version': device.os_version,
                'app_version': device.app_version,
                'fcm_token': device.fcm_token,
                'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                'is_active': device.is_active,
                'biometric_enabled': device.biometric_enabled,
                'location_permission': device.location_permission,
                'bluetooth_permission': device.bluetooth_permission,
                'created_at': device.created_at.isoformat() if device.created_at else None,
                'updated_at': device.updated_at.isoformat() if device.updated_at else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/devices/<int:device_id>', methods=['PUT'])
@jwt_required()
def admin_update_device(device_id):
    """Update device"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        device = StudentDevices.query.get(device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'device_name' in data:
            device.device_name = data['device_name']
        
        if 'is_active' in data:
            device.is_active = data['is_active']
        
        if 'biometric_enabled' in data:
            device.biometric_enabled = data['biometric_enabled']
        
        if 'location_permission' in data:
            device.location_permission = data['location_permission']
        
        if 'bluetooth_permission' in data:
            device.bluetooth_permission = data['bluetooth_permission']
        
        device.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Get related student data
        student = Student.query.get(device.student_id)
        
        return jsonify({
            'success': True,
            'message': 'Device updated successfully',
            'device': {
                'device_id': device.device_id,
                'student_id': device.student_id,
                'student_name': f"{student.first_name} {student.last_name}" if student else None,
                'student_code': student.student_code if student else None,
                'device_uuid': device.device_uuid,
                'device_name': device.device_name,
                'device_type': device.device_type,
                'device_model': device.device_model,
                'os_version': device.os_version,
                'app_version': device.app_version,
                'fcm_token': device.fcm_token,
                'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                'is_active': device.is_active,
                'biometric_enabled': device.biometric_enabled,
                'location_permission': device.location_permission,
                'bluetooth_permission': device.bluetooth_permission
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/devices/<int:device_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_device(device_id):
    """Delete device"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        device = StudentDevices.query.get(device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        db.session.delete(device)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Device deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Attendance Management Routes
@app.route('/api/admin/attendance/sessions', methods=['GET'])
@jwt_required()
def admin_get_attendance_sessions():
    """Get list of attendance sessions"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get filter parameters
        class_id = request.args.get('class_id', type=int)
        faculty_id = request.args.get('faculty_id', type=int)
        status = request.args.get('status', '')
        
        # Build query with joins to get related data
        query = db.session.query(AttendanceSession, Classes, Faculty).join(
            Classes, AttendanceSession.class_id == Classes.class_id
        ).join(
            Faculty, AttendanceSession.faculty_id == Faculty.faculty_id
        )
        
        # Apply filters
        if class_id:
            query = query.filter(AttendanceSession.class_id == class_id)
        
        if faculty_id:
            query = query.filter(AttendanceSession.faculty_id == faculty_id)
        
        if status:
            query = query.filter(AttendanceSession.status == status)
        
        # Order by start time descending
        query = query.order_by(AttendanceSession.start_time.desc())
        
        # Paginate results
        sessions_pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        sessions_list = []
        for session, class_obj, faculty in sessions_pagination.items:
            sessions_list.append({
                'session_id': session.session_id,
                'class_id': session.class_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'faculty_id': session.faculty_id,
                'faculty_name': f"{faculty.first_name} {faculty.last_name}",
                'session_date': session.session_date.isoformat() if session.session_date else None,
                'start_time': session.start_time.isoformat() if session.start_time else None,
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'status': session.status,
                'total_students_enrolled': session.total_students_enrolled,
                'total_students_present': session.total_students_present,
                'attendance_percentage': float(session.attendance_percentage) if session.attendance_percentage else 0.0
            })
        
        return jsonify({
            'success': True,
            'sessions': sessions_list,
            'pagination': {
                'page': sessions_pagination.page,
                'pages': sessions_pagination.pages,
                'per_page': sessions_pagination.per_page,
                'total': sessions_pagination.total
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/attendance/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def admin_get_attendance_session(session_id):
    """Get specific attendance session details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get session with related data
        session_data = db.session.query(AttendanceSession, Classes, Faculty).join(
            Classes, AttendanceSession.class_id == Classes.class_id
        ).join(
            Faculty, AttendanceSession.faculty_id == Faculty.faculty_id
        ).filter(AttendanceSession.session_id == session_id).first()
        
        if not session_data:
            return jsonify({'error': 'Attendance session not found'}), 404
        
        session, class_obj, faculty = session_data
        
        # Get attendance records for this session
        records = db.session.query(AttendanceRecord, Student).join(
            Student, AttendanceRecord.student_id == Student.student_id
        ).filter(AttendanceRecord.session_id == session_id).all()
        
        attendance_records = []
        for record, student in records:
            attendance_records.append({
                'record_id': record.record_id,
                'student_id': record.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code,
                'scan_timestamp': record.scan_timestamp.isoformat() if record.scan_timestamp else None,
                'biometric_verified': record.biometric_verified,
                'location_verified': record.location_verified,
                'bluetooth_verified': record.bluetooth_verified,
                'verification_score': float(record.verification_score) if record.verification_score else 0.0,
                'status': record.status,
                'notes': record.notes
            })
        
        return jsonify({
            'success': True,
            'session': {
                'session_id': session.session_id,
                'class_id': session.class_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'faculty_id': session.faculty_id,
                'faculty_name': f"{faculty.first_name} {faculty.last_name}",
                'session_date': session.session_date.isoformat() if session.session_date else None,
                'start_time': session.start_time.isoformat() if session.start_time else None,
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'status': session.status,
                'total_students_enrolled': session.total_students_enrolled,
                'total_students_present': session.total_students_present,
                'attendance_percentage': float(session.attendance_percentage) if session.attendance_percentage else 0.0,
                'created_at': session.created_at.isoformat() if session.created_at else None,
                'updated_at': session.updated_at.isoformat() if session.updated_at else None
            },
            'attendance_records': attendance_records
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/attendance/records', methods=['GET'])
@jwt_required()
def admin_get_attendance_records():
    """Get list of attendance records"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get filter parameters
        session_id = request.args.get('session_id', type=int)
        student_id = request.args.get('student_id', type=int)
        status = request.args.get('status', '')
        
        # Build query with joins to get related data
        query = db.session.query(AttendanceRecord, AttendanceSession, Student, Classes).join(
            AttendanceSession, AttendanceRecord.session_id == AttendanceSession.session_id
        ).join(
            Student, AttendanceRecord.student_id == Student.student_id
        ).join(
            Classes, AttendanceSession.class_id == Classes.class_id
        )
        
        # Apply filters
        if session_id:
            query = query.filter(AttendanceRecord.session_id == session_id)
        
        if student_id:
            query = query.filter(AttendanceRecord.student_id == student_id)
        
        if status:
            query = query.filter(AttendanceRecord.status == status)
        
        # Order by scan timestamp descending
        query = query.order_by(AttendanceRecord.scan_timestamp.desc())
        
        # Paginate results
        records_pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        records_list = []
        for record, session, student, class_obj in records_pagination.items:
            records_list.append({
                'record_id': record.record_id,
                'session_id': record.session_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'student_id': record.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code,
                'scan_timestamp': record.scan_timestamp.isoformat() if record.scan_timestamp else None,
                'biometric_verified': record.biometric_verified,
                'location_verified': record.location_verified,
                'bluetooth_verified': record.bluetooth_verified,
                'verification_score': float(record.verification_score) if record.verification_score else 0.0,
                'status': record.status,
                'notes': record.notes
            })
        
        return jsonify({
            'success': True,
            'records': records_list,
            'pagination': {
                'page': records_pagination.page,
                'pages': records_pagination.pages,
                'per_page': records_pagination.per_page,
                'total': records_pagination.total
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/faculty/classes', methods=['GET'])
@jwt_required()
def get_faculty_classes():
    """Get classes assigned to the logged-in faculty"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'faculty':
            return jsonify({'error': 'Faculty access required'}), 403
        
        faculty_id = claims.get('faculty_id')
        
        # Get active classes assigned to this faculty with classroom information
        classes = db.session.query(Classes, Classroom).join(
            Classroom, Classes.classroom_id == Classroom.classroom_id
        ).filter(
            Classes.faculty_id == faculty_id,
            Classes.is_active == True
        ).all()
        
        classes_list = []
        for class_obj, classroom in classes:
            classes_list.append({
                'class_id': class_obj.class_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'classroom_id': class_obj.classroom_id,
                'room_number': classroom.room_number if classroom else None,
                'building_name': classroom.building_name if classroom else None,
                'semester': class_obj.semester,
                'academic_year': class_obj.academic_year,
                'schedule_day': class_obj.schedule_day,
                'start_time': class_obj.start_time.isoformat() if class_obj.start_time else None,
                'end_time': class_obj.end_time.isoformat() if class_obj.end_time else None
            })
        
        return jsonify({
            'success': True,
            'classes': classes_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/classes/<int:class_id>/details', methods=['GET'])
@jwt_required()
def admin_get_class_details(class_id):
    """Get specific class details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get class with related data
        class_data = db.session.query(Classes, Faculty, Classroom).outerjoin(
            Faculty, Classes.faculty_id == Faculty.faculty_id
        ).outerjoin(
            Classroom, Classes.classroom_id == Classroom.classroom_id
        ).filter(Classes.class_id == class_id).first()
        
        if not class_data:
            return jsonify({'error': 'Class not found'}), 404
        
        class_obj, faculty, classroom = class_data
        
        return jsonify({
            'success': True,
            'class': {
                'class_id': class_obj.class_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'faculty_id': class_obj.faculty_id,
                'faculty_name': f"{faculty.first_name} {faculty.last_name}" if faculty else None,
                'faculty_email': faculty.email if faculty else None,
                'classroom_id': class_obj.classroom_id,
                'room_number': classroom.room_number if classroom else None,
                'building_name': classroom.building_name if classroom else None,
                'semester': class_obj.semester,
                'academic_year': class_obj.academic_year,
                'credits': class_obj.credits,
                'max_students': class_obj.max_students,
                'schedule_day': class_obj.schedule_day,
                'start_time': class_obj.start_time.isoformat() if class_obj.start_time else None,
                'end_time': class_obj.end_time.isoformat() if class_obj.end_time else None,
                'is_active': class_obj.is_active,
                'created_at': class_obj.created_at.isoformat() if class_obj.created_at else None,
                'updated_at': class_obj.updated_at.isoformat() if class_obj.updated_at else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/classes/<int:class_id>/records', methods=['GET'])
@jwt_required()
def admin_get_class_records(class_id):
    """Get attendance records for a specific class"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get class with related data
        class_data = db.session.query(Classes, Faculty, Classroom).outerjoin(
            Faculty, Classes.faculty_id == Faculty.faculty_id
        ).outerjoin(
            Classroom, Classes.classroom_id == Classroom.classroom_id
        ).filter(Classes.class_id == class_id).first()
        
        if not class_data:
            return jsonify({'error': 'Class not found'}), 404
        
        class_obj, faculty, classroom = class_data
        
        # Get attendance records for this class
        records_pagination = db.session.query(Attendance, Session, Student).join(
            Session, Attendance.session_id == Session.session_id
        ).join(
            Student, Attendance.student_id == Student.student_id
        ).filter(
            Attendance.class_id == class_id
        ).paginate(page=1, per_page=10)
        
        records_list = []
        for record, session, student, class_obj in records_pagination.items:
            records_list.append({
                'record_id': record.record_id,
                'session_id': record.session_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'student_id': record.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code,
                'scan_timestamp': record.scan_timestamp.isoformat() if record.scan_timestamp else None,
                'biometric_verified': record.biometric_verified,
                'location_verified': record.location_verified,
                'bluetooth_verified': record.bluetooth_verified,
                'verification_score': float(record.verification_score) if record.verification_score else 0.0,
                'status': record.status,
                'notes': record.notes
            })
        
        return jsonify({
            'success': True,
            'records': records_list,
            'pagination': {
                'page': records_pagination.page,
                'pages': records_pagination.pages,
                'per_page': records_pagination.per_page,
                'total': records_pagination.total
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/admin/classes/create', methods=['POST'])
@jwt_required()
def admin_create_new_class():
    """Create new class"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['class_code', 'class_name', 'faculty_id', 'semester', 'academic_year']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if class code already exists
        existing = Classes.query.filter_by(class_code=data['class_code']).first()
        if existing:
            return jsonify({'error': 'Class code already exists'}), 400
        
        # Verify faculty exists
        faculty = Faculty.query.get(data['faculty_id'])
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        # Verify classroom exists if provided
        if 'classroom_id' in data and data['classroom_id']:
            classroom = Classroom.query.get(data['classroom_id'])
            if not classroom:
                return jsonify({'error': 'Classroom not found'}), 404
        
        # Create new class
        class_obj = Classes(
            class_code=data['class_code'],
            class_name=data['class_name'],
            faculty_id=data['faculty_id'],
            classroom_id=data.get('classroom_id'),
            semester=data['semester'],
            academic_year=data['academic_year'],
            credits=data.get('credits', 3),
            max_students=data.get('max_students', 60),
            schedule_day=data.get('schedule_day'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(class_obj)
        db.session.commit()
        
        # Get related data for response
        faculty = Faculty.query.get(class_obj.faculty_id)
        classroom = Classroom.query.get(class_obj.classroom_id) if class_obj.classroom_id else None
        
        return jsonify({
            'success': True,
            'message': 'Class created successfully',
            'class': {
                'class_id': class_obj.class_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'faculty_id': class_obj.faculty_id,
                'faculty_name': f"{faculty.first_name} {faculty.last_name}" if faculty else None,
                'classroom_id': class_obj.classroom_id,
                'room_number': classroom.room_number if classroom else None,
                'semester': class_obj.semester,
                'academic_year': class_obj.academic_year,
                'credits': class_obj.credits,
                'max_students': class_obj.max_students,
                'schedule_day': class_obj.schedule_day,
                'start_time': class_obj.start_time.isoformat() if class_obj.start_time else None,
                'end_time': class_obj.end_time.isoformat() if class_obj.end_time else None,
                'is_active': class_obj.is_active
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classes/<int:class_id>/update', methods=['PUT'])
@jwt_required()
def admin_update_class_detailed(class_id):
    """Update class"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        class_obj = Classes.query.get(class_id)
        if not class_obj:
            return jsonify({'error': 'Class not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'class_code' in data and data['class_code'] != class_obj.class_code:
            # Check if new class code already exists
            existing = Classes.query.filter(
                Classes.class_code == data['class_code'],
                Classes.class_id != class_id
            ).first()
            if existing:
                return jsonify({'error': 'Class code already exists'}), 400
            class_obj.class_code = data['class_code']
        
        if 'class_name' in data:
            class_obj.class_name = data['class_name']
        
        if 'faculty_id' in data:
            # Verify faculty exists
            faculty = Faculty.query.get(data['faculty_id'])
            if not faculty:
                return jsonify({'error': 'Faculty not found'}), 404
            class_obj.faculty_id = data['faculty_id']
        
        if 'classroom_id' in data:
            # Verify classroom exists if provided
            if data['classroom_id']:
                classroom = Classroom.query.get(data['classroom_id'])
                if not classroom:
                    return jsonify({'error': 'Classroom not found'}), 404
            class_obj.classroom_id = data['classroom_id']
        
        if 'semester' in data:
            class_obj.semester = data['semester']
        
        if 'academic_year' in data:
            class_obj.academic_year = data['academic_year']
        
        if 'credits' in data:
            class_obj.credits = data['credits']
        
        if 'max_students' in data:
            class_obj.max_students = data['max_students']
        
        if 'schedule_day' in data:
            class_obj.schedule_day = data['schedule_day']
        
        if 'start_time' in data:
            class_obj.start_time = data['start_time']
        
        if 'end_time' in data:
            class_obj.end_time = data['end_time']
        
        if 'is_active' in data:
            class_obj.is_active = data['is_active']
        
        class_obj.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Get related data for response
        faculty = Faculty.query.get(class_obj.faculty_id)
        classroom = Classroom.query.get(class_obj.classroom_id) if class_obj.classroom_id else None
        
        return jsonify({
            'success': True,
            'message': 'Class updated successfully',
            'class': {
                'class_id': class_obj.class_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'faculty_id': class_obj.faculty_id,
                'faculty_name': f"{faculty.first_name} {faculty.last_name}" if faculty else None,
                'classroom_id': class_obj.classroom_id,
                'room_number': classroom.room_number if classroom else None,
                'semester': class_obj.semester,
                'academic_year': class_obj.academic_year,
                'credits': class_obj.credits,
                'max_students': class_obj.max_students,
                'schedule_day': class_obj.schedule_day,
                'start_time': class_obj.start_time.isoformat() if class_obj.start_time else None,
                'end_time': class_obj.end_time.isoformat() if class_obj.end_time else None,
                'is_active': class_obj.is_active
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classes/<int:class_id>/delete', methods=['DELETE'])
@jwt_required()
def admin_delete_class_permanent(class_id):
    """Delete class"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        class_obj = Classes.query.get(class_id)
        if not class_obj:
            return jsonify({'error': 'Class not found'}), 404
        
        # Check if class has any attendance sessions
        sessions = AttendanceSession.query.filter_by(class_id=class_id).count()
        if sessions > 0:
            return jsonify({'error': 'Cannot delete class with attendance sessions'}), 400
        
        db.session.delete(class_obj)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Class deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/classrooms/<int:classroom_id>/update', methods=['PUT'])
@jwt_required()
def admin_update_classroom(classroom_id):
    """Update classroom"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        classroom = Classroom.query.get(classroom_id)
        if not classroom:
            return jsonify({'error': 'Classroom not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'room_number' in data and data['room_number'] != classroom.room_number:
            # Check if new room number already exists
            existing = Classroom.query.filter(
                Classroom.room_number == data['room_number'],
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
                'is_active': classroom.is_active
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classrooms/<int:classroom_id>/delete', methods=['DELETE'])
@jwt_required()
def admin_delete_classroom(classroom_id):
    """Delete classroom"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        classroom = Classroom.query.get(classroom_id)
        if not classroom:
            return jsonify({'error': 'Classroom not found'}), 404
        
        # Check if classroom is used in any classes
        classes = Classes.query.filter_by(classroom_id=classroom_id).count()
        if classes > 0:
            return jsonify({'error': 'Cannot delete classroom assigned to classes'}), 400
        
        db.session.delete(classroom)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Classroom deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/enrollments', methods=['POST'])
@jwt_required()
def admin_create_enrollment():
    """Create a new student enrollment"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_id', 'class_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if student and class exist
        student = Student.query.get(data['student_id'])
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        class_obj = Classes.query.get(data['class_id'])
        if not class_obj:
            return jsonify({'error': 'Class not found'}), 404
        
        # Check if enrollment already exists
        existing_enrollment = StudentClassEnrollment.query.filter_by(
            student_id=data['student_id'],
            class_id=data['class_id']
        ).first()
        
        if existing_enrollment:
            return jsonify({'error': 'Student already enrolled in this class'}), 400
        
        # Create new enrollment
        enrollment = StudentClassEnrollment(
            student_id=data['student_id'],
            class_id=data['class_id'],
            status=data.get('status', 'enrolled'),
            final_grade=data.get('final_grade'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        # Get related data for response
        student = Student.query.get(enrollment.student_id)
        class_obj = Classes.query.get(enrollment.class_id)
        
        return jsonify({
            'success': True,
            'message': 'Student enrolled successfully',
            'enrollment': {
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'student_name': f"{student.first_name} {student.last_name}" if student else None,
                'student_code': student.student_code if student else None,
                'class_id': enrollment.class_id,
                'class_name': class_obj.class_name if class_obj else None,
                'class_code': class_obj.class_code if class_obj else None,
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None,
                'created_at': enrollment.created_at.isoformat() if enrollment.created_at else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/enrollments/<int:enrollment_id>', methods=['GET'])
@jwt_required()
def admin_get_enrollment(enrollment_id):
    """Get specific enrollment details"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get enrollment with related data
        enrollment_data = db.session.query(StudentClassEnrollment, Student, Classes).join(
            Student, StudentClassEnrollment.student_id == Student.student_id
        ).join(
            Classes, StudentClassEnrollment.class_id == Classes.class_id
        ).filter(StudentClassEnrollment.enrollment_id == enrollment_id).first()
        
        if not enrollment_data:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        enrollment, student, class_obj = enrollment_data
        
        return jsonify({
            'success': True,
            'enrollment': {
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code,
                'student_email': student.email,
                'class_id': enrollment.class_id,
                'class_name': class_obj.class_name,
                'class_code': class_obj.class_code,
                'faculty_id': class_obj.faculty_id,
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None,
                'created_at': enrollment.created_at.isoformat() if enrollment.created_at else None,
                'updated_at': enrollment.updated_at.isoformat() if enrollment.updated_at else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/enrollments', methods=['GET'])
@jwt_required()
def admin_get_enrollments_list():
    """Get list of all student enrollments"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get filter parameters
        student_id = request.args.get('student_id', type=int)
        class_id = request.args.get('class_id', type=int)
        status = request.args.get('status', '')
        
        # Build query with joins to get related data
        query = db.session.query(StudentClassEnrollment, Student, Classes).join(
            Student, StudentClassEnrollment.student_id == Student.student_id
        ).join(
            Classes, StudentClassEnrollment.class_id == Classes.class_id
        )
        
        # Apply filters
        if student_id:
            query = query.filter(StudentClassEnrollment.student_id == student_id)
        
        if class_id:
            query = query.filter(StudentClassEnrollment.class_id == class_id)
        
        if status:
            query = query.filter(StudentClassEnrollment.status == status)
        
        # Order by enrollment date descending
        query = query.order_by(StudentClassEnrollment.enrollment_date.desc())
        
        # Paginate results
        enrollments_pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        enrollments_list = []
        for enrollment, student, class_obj in enrollments_pagination.items:
            enrollments_list.append({
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code,
                'class_id': enrollment.class_id,
                'class_name': class_obj.class_name,
                'class_code': class_obj.class_code,
                'faculty_id': class_obj.faculty_id,
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None
            })
        
        return jsonify({
            'success': True,
            'enrollments': enrollments_list,
            'pagination': {
                'page': enrollments_pagination.page,
                'pages': enrollments_pagination.pages,
                'per_page': enrollments_pagination.per_page,
                'total': enrollments_pagination.total
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/enrollments/<int:enrollment_id>', methods=['PUT'])
@jwt_required()
def admin_update_enrollment(enrollment_id):
    """Update student enrollment"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        enrollment = StudentClassEnrollment.query.get(enrollment_id)
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'status' in data:
            enrollment.status = data['status']
        
        if 'final_grade' in data:
            enrollment.final_grade = data['final_grade']
        
        if 'is_active' in data:
            enrollment.is_active = data['is_active']
        
        enrollment.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Get related data for response
        student = Student.query.get(enrollment.student_id)
        class_obj = Classes.query.get(enrollment.class_id)
        
        return jsonify({
            'success': True,
            'message': 'Enrollment updated successfully',
            'enrollment': {
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'student_name': f"{student.first_name} {student.last_name}" if student else None,
                'student_code': student.student_code if student else None,
                'class_id': enrollment.class_id,
                'class_name': class_obj.class_name if class_obj else None,
                'class_code': class_obj.class_code if class_obj else None,
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None,
                'updated_at': enrollment.updated_at.isoformat() if enrollment.updated_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/enrollments/<int:enrollment_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_enrollment(enrollment_id):
    """Delete student enrollment"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        enrollment = StudentClassEnrollment.query.get(enrollment_id)
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        db.session.delete(enrollment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Enrollment deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/students/<int:student_id>/enrollments', methods=['GET'])
@jwt_required()
def admin_get_student_enrollments(student_id):
    """Get all enrollments for a specific student"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Check if student exists
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get enrollments with related data
        enrollments_data = db.session.query(StudentClassEnrollment, Classes, Faculty).join(
            Classes, StudentClassEnrollment.class_id == Classes.class_id
        ).join(
            Faculty, Classes.faculty_id == Faculty.faculty_id
        ).filter(StudentClassEnrollment.student_id == student_id).all()
        
        enrollments_list = []
        for enrollment, class_obj, faculty in enrollments_data:
            enrollments_list.append({
                'enrollment_id': enrollment.enrollment_id,
                'class_id': enrollment.class_id,
                'class_name': class_obj.class_name,
                'class_code': class_obj.class_code,
                'faculty_name': f"{faculty.first_name} {faculty.last_name}",
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None
            })
        
        return jsonify({
            'success': True,
            'student': {
                'student_id': student.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code
            },
            'enrollments': enrollments_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classes/<int:class_id>/enrollments', methods=['GET'])
@jwt_required()
def admin_get_class_enrollments(class_id):
    """Get all enrollments for a specific class"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Check if class exists
        class_obj = Classes.query.get(class_id)
        if not class_obj:
            return jsonify({'error': 'Class not found'}), 404
        
        # Get enrollments with related data
        enrollments_data = db.session.query(StudentClassEnrollment, Student).join(
            Student, StudentClassEnrollment.student_id == Student.student_id
        ).filter(StudentClassEnrollment.class_id == class_id).all()
        
        enrollments_list = []
        for enrollment, student in enrollments_data:
            enrollments_list.append({
                'enrollment_id': enrollment.enrollment_id,
                'student_id': enrollment.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'student_code': student.student_code,
                'student_email': student.email,
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None
            })
        
        return jsonify({
            'success': True,
            'class': {
                'class_id': class_obj.class_id,
                'class_name': class_obj.class_name,
                'class_code': class_obj.class_code
            },
            'enrollments': enrollments_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

def create_app():
    """Application factory"""
    return app

if __name__ == '__main__':
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Start scheduler
    scheduler.start()
    
    logger.info("🚀 Starting INTELLIATTEND Server...")
    logger.info("=" * 50)
    logger.info("Faculty Portal: http://localhost:5002")
    logger.info("Student Portal: http://localhost:5002/student")
    logger.info("API Base URL: http://localhost:5002/api")
    logger.info("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5002, threaded=True)
