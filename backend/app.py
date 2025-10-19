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
from datetime import datetime, timedelta, time
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
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

# Register admin blueprint
# We'll register it after the app is created to avoid circular imports
admin_bp = None

# Load configuration
config_name = os.environ.get('FLASK_CONFIG', 'development')
app.config.from_object(config[config_name])

# OTP Configuration
app.config['OTP_LENGTH'] = int(os.environ.get('OTP_LENGTH', 6))
app.config['OTP_EXPIRY_MINUTES'] = int(os.environ.get('OTP_EXPIRY_MINUTES', 5))

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

# Initialize Flask-Limiter with intelligent configuration
def get_client_key():
    """Intelligent key function for rate limiting"""
    # Check if this is a test environment
    if os.environ.get('TESTING') or request.headers.get('X-Testing-Mode'):
        return f"test-{get_remote_address()}-{int(time.time() / 300)}"  # 5-minute windows for testing
    return get_remote_address()

# Enhanced rate limiting configuration
if os.environ.get('FLASK_CONFIG') == 'production' and os.environ.get('REDIS_URL'):
    # Production: Strict limits with Redis
    limiter = Limiter(
        key_func=get_client_key,
        default_limits=["1000 per day", "100 per hour", "20 per minute"],
        storage_uri=os.environ.get('REDIS_URL')
    )
else:
    # Development: More lenient limits for testing
    limiter = Limiter(
        key_func=get_client_key,
        default_limits=["10000 per day", "2000 per hour", "200 per minute"]
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
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=True)
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
    notifications_enabled = db.Column(db.Boolean, default=True)
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
# SECURITY VIOLATIONS MODEL
# ============================================================================

class SecurityViolation(db.Model):
    __tablename__ = 'security_violations'
    
    violation_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    violation_type = db.Column(db.Enum('screenshot', 'screen_recording', 'root_detected', 'vpn_detected', 'gps_spoofing'), nullable=False)
    details = db.Column(db.JSON)
    device_info = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer)  # admin_id if resolved by admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, student_id, violation_type, details=None, device_info=None, is_resolved=False):
        self.student_id = student_id
        self.violation_type = violation_type
        self.details = details
        self.device_info = device_info
        self.is_resolved = is_resolved

# ============================================================================
# ADMIN MODEL
# ============================================================================

class Admin(db.Model):
    __tablename__ = 'admins'
    
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum('superadmin', 'admin'), default='admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, username, password_hash, role='admin'):
        self.username = username
        self.password_hash = password_hash
        self.role = role

# ============================================================================
# REGISTRATION SYSTEM MODELS
# ============================================================================

class WiFiNetwork(db.Model):
    """Wi-Fi network information for classrooms"""
    __tablename__ = 'wifi_networks'
    
    wifi_id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.classroom_id'), nullable=False)
    ssid = db.Column(db.String(32), nullable=False)
    bssid = db.Column(db.String(17), unique=True, nullable=False)  # MAC address format XX:XX:XX:XX:XX:XX
    security_type = db.Column(db.Enum('Open', 'WEP', 'WPA', 'WPA2', 'WPA3'), default='WPA2')
    is_active = db.Column(db.Boolean, default=True)
    registered_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classroom = db.relationship('Classroom', backref=db.backref('wifi_networks', lazy=True))
    
    def __init__(self, classroom_id, ssid, bssid, security_type='WPA2', registered_by=None, is_active=True):
        self.classroom_id = classroom_id
        self.ssid = ssid
        self.bssid = bssid
        self.security_type = security_type
        self.registered_by = registered_by
        self.is_active = is_active

class BluetoothBeacon(db.Model):
    """Bluetooth beacon information for classrooms"""
    __tablename__ = 'bluetooth_beacons'
    
    beacon_id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.classroom_id'), nullable=False)
    beacon_uuid = db.Column(db.String(36), nullable=False)  # UUID format: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
    major = db.Column(db.Integer, nullable=False)  # 0-65535
    minor = db.Column(db.Integer, nullable=False)  # 0-65535
    mac_address = db.Column(db.String(17))  # Beacon MAC address
    expected_rssi = db.Column(db.Integer, default=-75)  # Expected signal strength at classroom entrance
    is_active = db.Column(db.Boolean, default=True)
    registered_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classroom = db.relationship('Classroom', backref=db.backref('bluetooth_beacons', lazy=True))
    
    # Unique constraint on UUID + Major + Minor combination
    __table_args__ = (
        db.UniqueConstraint('beacon_uuid', 'major', 'minor', name='uix_beacon_unique'),
    )
    
    def __init__(self, classroom_id, beacon_uuid, major, minor, mac_address=None, expected_rssi=-75, registered_by=None, is_active=True):
        self.classroom_id = classroom_id
        self.beacon_uuid = beacon_uuid
        self.major = major
        self.minor = minor
        self.mac_address = mac_address
        self.expected_rssi = expected_rssi
        self.registered_by = registered_by
        self.is_active = is_active

class RegistrationAuditLog(db.Model):
    """Audit log for all registration actions"""
    __tablename__ = 'registration_audit_log'
    
    log_id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.Enum('create', 'update', 'delete', 'approve', 'reject'), nullable=False)
    resource_type = db.Column(db.Enum('classroom', 'student', 'faculty', 'device', 'wifi', 'beacon'), nullable=False)
    resource_id = db.Column(db.Integer, nullable=False)  # ID of the affected resource
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=False)
    admin_username = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(45))  # Supports both IPv4 and IPv6
    user_agent = db.Column(db.Text)
    details = db.Column(db.JSON)  # Additional context about the action
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    admin = db.relationship('Admin', backref=db.backref('audit_logs', lazy=True))
    
    def __init__(self, action, resource_type, resource_id, admin_id, admin_username, ip_address=None, user_agent=None, details=None):
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.admin_id = admin_id
        self.admin_username = admin_username
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.details = details

class DeviceApprovalQueue(db.Model):
    """Queue for pending device registrations"""
    __tablename__ = 'device_approval_queue'
    
    queue_id = db.Column(db.Integer, primary_key=True)
    device_uuid = db.Column(db.String(255), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    device_info = db.Column(db.JSON)  # Device details (model, OS, etc.)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'))
    review_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref=db.backref('device_approvals', lazy=True))
    reviewer = db.relationship('Admin', backref=db.backref('device_reviews', lazy=True))
    
    def __init__(self, device_uuid, student_id, device_info=None, status='pending'):
        self.device_uuid = device_uuid
        self.student_id = student_id
        self.device_info = device_info
        self.status = status

class StudentRegistrationQueue(db.Model):
    """Queue for pending student self-registrations requiring approval"""
    __tablename__ = 'student_registration_queue'
    
    queue_id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15))
    program = db.Column(db.String(100), nullable=False)
    year_of_study = db.Column(db.Integer)
    password_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'))
    approval_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviewer = db.relationship('Admin', backref=db.backref('student_reviews', lazy=True))
    
    def __init__(self, student_code, first_name, last_name, email, program, password_hash, phone_number=None, year_of_study=None):
        self.student_code = student_code
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.program = program
        self.year_of_study = year_of_study
        self.password_hash = password_hash

# ============================================================================
# SINGLE DEVICE ENFORCEMENT MODELS (PhonePe-style)
# ============================================================================

class DeviceSwitchRequest(db.Model):
    """Track device switch requests with 48-hour cooldown"""
    __tablename__ = 'device_switch_requests'
    
    request_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    old_device_uuid = db.Column(db.String(255))  # Previous active device
    new_device_uuid = db.Column(db.String(255), nullable=False)  # Device requesting to become active
    new_device_info = db.Column(db.JSON)  # New device details
    request_reason = db.Column(db.Enum('device_upgrade', 'device_lost', 'device_stolen', 'manual_switch'), default='manual_switch')
    status = db.Column(db.Enum('pending', 'approved', 'rejected', 'expired'), default='pending')
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)  # When 48-hour cooldown completes
    expires_at = db.Column(db.DateTime)  # Auto-expire after 7 days
    completed_at = db.Column(db.DateTime)
    ip_address = db.Column(db.String(45))
    wifi_ssid = db.Column(db.String(100))  # Wi-Fi network used for request
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref=db.backref('device_switch_requests', lazy=True))
    
    def __init__(self, student_id, new_device_uuid, old_device_uuid=None, new_device_info=None, request_reason='manual_switch'):
        self.student_id = student_id
        self.old_device_uuid = old_device_uuid
        self.new_device_uuid = new_device_uuid
        self.new_device_info = new_device_info
        self.request_reason = request_reason
        # Set expiry to 7 days from now
        self.expires_at = datetime.utcnow() + timedelta(days=7)

class DeviceActivityLog(db.Model):
    """Log all device activities for security monitoring"""
    __tablename__ = 'device_activity_log'
    
    log_id = db.Column(db.BigInteger, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    device_uuid = db.Column(db.String(255), nullable=False)
    activity_type = db.Column(db.Enum('login', 'logout', 'attendance_scan', 'device_activated', 'device_deactivated', 'failed_login'), nullable=False)
    ip_address = db.Column(db.String(45))
    location_lat = db.Column(db.Numeric(10, 8))
    location_lon = db.Column(db.Numeric(11, 8))
    wifi_ssid = db.Column(db.String(100))
    additional_info = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    student = db.relationship('Student', backref=db.backref('device_activities', lazy=True))
    
    def __init__(self, student_id, device_uuid, activity_type, ip_address=None, location_lat=None, location_lon=None, wifi_ssid=None, additional_info=None):
        self.student_id = student_id
        self.device_uuid = device_uuid
        self.activity_type = activity_type
        self.ip_address = ip_address
        self.location_lat = location_lat
        self.location_lon = location_lon
        self.wifi_ssid = wifi_ssid
        self.additional_info = additional_info

# ============================================================================
# OTP LOG MODEL
# ============================================================================

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
# UTILITY FUNCTIONS
# ============================================================================

def standardize_response(success, data=None, message=None, error=None, status_code=200):
    """
    Standardize API response format with enhanced security
    
    Args:
        success (bool): Whether the request was successful
        data (dict, optional): Data to return
        message (str, optional): Success message
        error (str, optional): Error message
        status_code (int): HTTP status code
    
    Returns:
        tuple: (response_dict, status_code)
    """
    # Import security functions locally to avoid circular imports
    try:
        from security_enhancements import InputValidator
        sanitize_text = InputValidator.sanitize_text
    except ImportError:
        # Fallback if security_enhancements is not available
        def sanitize_text(text):
            if not text:
                return ""
            return str(text)[:1000]  # Limit length and convert to string
    
    response = {
        'success': success,
        'status_code': status_code,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = sanitize_text(message)
    
    if error:
        # Sanitize error messages to prevent information leakage
        response['error'] = sanitize_text(error)
    
    return jsonify(response), status_code

def get_first_active_class():
    """Get the first active class from the database with proper error handling"""
    try:
        class_obj = Classes.query.filter_by(is_active=True).first()
        if class_obj and hasattr(class_obj, 'class_id'):
            return class_obj.class_id
        else:
            logger.warning("No active classes found in database")
            return None  # Return None instead of hardcoded fallback
    except Exception as e:
        logger.error(f"Database error getting first active class: {e}")
        return None  # Return None instead of hardcoded fallback

def get_first_active_faculty():
    """Get the first active faculty from the database with proper error handling"""
    try:
        faculty_obj = Faculty.query.filter_by(is_active=True).first()
        if faculty_obj and hasattr(faculty_obj, 'faculty_id'):
            return faculty_obj.faculty_id
        else:
            logger.warning("No active faculty found in database")
            return None  # Return None instead of hardcoded fallback
    except Exception as e:
        logger.error(f"Database error getting first active faculty: {e}")
        return None  # Return None instead of hardcoded fallback

def generate_otp(length=6):
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))

def generate_token(length=32):
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)

def create_qr_code(data, session_id):
    """Create QR code image with enhanced error handling and security"""
    try:
        # Validate inputs
        if not data or not session_id:
            logger.error("Invalid parameters for QR code creation")
            return None
        
        # Create QR code with enhanced error correction
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_M,  # Medium error correction
            box_size=app.config.get('QR_CODE_SIZE', 10),
            border=app.config.get('QR_CODE_BORDER', 4),
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Generate secure filename
        timestamp = int(time.time())
        # Use secrets for additional randomness
        random_suffix = secrets.token_hex(4)
        filename = f"qr_session_{session_id}_{timestamp}_{random_suffix}.png"
        
        # Use absolute path to QR_DATA folder in parent directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        qr_tokens_folder = os.path.join(project_root, 'QR_DATA', 'tokens')
        
        # Ensure directory exists with proper permissions
        os.makedirs(qr_tokens_folder, mode=0o755, exist_ok=True)
        
        # Save to centralized QR_DATA location
        file_path = os.path.join(qr_tokens_folder, filename)
        
        # Validate file path to prevent directory traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(qr_tokens_folder)):
            logger.error("Invalid file path for QR code creation")
            return None
        
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

# ============================================================================
# BUSINESS LOGIC VALIDATION FUNCTIONS
# ============================================================================

def validate_faculty_availability(faculty_id, start_time, end_time):
    """
    Prevent faculty from teaching concurrent classes
    
    Args:
        faculty_id (int): Faculty ID to check
        start_time (datetime): Start time of new session
        end_time (datetime): End time of new session
    
    Raises:
        ValidationError: If faculty is already teaching another class at this time
    """
    # Query for overlapping active sessions for the same faculty
    overlapping_sessions = db.session.query(AttendanceSession).filter(
        db.and_(
            getattr(AttendanceSession, 'faculty_id') == faculty_id,
            getattr(AttendanceSession, 'status') == 'active',
            getattr(AttendanceSession, 'start_time') < end_time,
            getattr(AttendanceSession, 'end_time') > start_time
        )
    ).first()
    
    if overlapping_sessions:
        raise ValidationError("Faculty already teaching another class at this time")

def validate_student_enrollment(student_id, class_id):
    """
    Validate that student is enrolled in the class before marking attendance
    
    Args:
        student_id (int): Student ID to check
        class_id (int): Class ID to check enrollment for
    
    Raises:
        ValidationError: If student is not enrolled in the class
    """
    # Query for student enrollment in the class
    enrollment = db.session.query(StudentClassEnrollment).filter(
        db.and_(
            getattr(StudentClassEnrollment, 'student_id') == student_id,
            getattr(StudentClassEnrollment, 'class_id') == class_id,
            getattr(StudentClassEnrollment, 'status') == 'enrolled',
            getattr(StudentClassEnrollment, 'is_active') == True
        )
    ).first()
    
    if not enrollment:
        raise ValidationError("Student is not enrolled in this class")

def validate_student_session_conflict(student_id, session_start_time, session_end_time):
    """
    Prevent students from attending concurrent sessions
    
    Args:
        student_id (int): Student ID to check
        session_start_time (datetime): Start time of new session
        session_end_time (datetime): End time of new session
    
    Raises:
        ValidationError: If student is already attending another session at this time
    """
    # Query for overlapping active sessions where student has attendance records
    overlapping_sessions = db.session.query(AttendanceSession).join(
        AttendanceRecord, 
        getattr(AttendanceSession, 'session_id') == getattr(AttendanceRecord, 'session_id')
    ).filter(
        db.and_(
            getattr(AttendanceRecord, 'student_id') == student_id,
            getattr(AttendanceSession, 'status') == 'active',
            getattr(AttendanceSession, 'start_time') < session_end_time,
            getattr(AttendanceSession, 'end_time') > session_start_time
        )
    ).first()
    
    if overlapping_sessions:
        raise ValidationError("Student already attending another session at this time")

def validate_classroom_capacity(class_id):
    """
    Validate that class enrollment does not exceed classroom capacity
    
    Args:
        class_id (int): Class ID to check
        
    Raises:
        ValidationError: If class enrollment exceeds classroom capacity
    """
    # Get the class with its classroom
    class_obj = db.session.query(Classes).filter(
        getattr(Classes, 'class_id') == class_id
    ).first()
    
    if not class_obj or not class_obj.classroom_id:
        # No classroom assigned, skip capacity validation
        return
    
    # Get the classroom
    classroom = db.session.query(Classroom).filter(
        getattr(Classroom, 'classroom_id') == class_obj.classroom_id
    ).first()
    
    if not classroom or not classroom.capacity:
        # No capacity defined, skip validation
        return
    
    # Count enrolled students in this class
    enrolled_count = db.session.query(StudentClassEnrollment).filter(
        db.and_(
            getattr(StudentClassEnrollment, 'class_id') == class_id,
            getattr(StudentClassEnrollment, 'status') == 'enrolled',
            getattr(StudentClassEnrollment, 'is_active') == True
        )
    ).count()
    
    # Check if enrolled students exceed classroom capacity
    if enrolled_count > classroom.capacity:
        raise ValidationError(f"Class enrollment ({enrolled_count}) exceeds classroom capacity ({classroom.capacity})")

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

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
@limiter.limit("30 per minute")
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
            claims = {'type': 'faculty', 'faculty_id': faculty.faculty_id}
            access_token = create_access_token(
                identity=str(faculty.faculty_id),
                additional_claims=claims
            )
            refresh_token = create_refresh_token(
                identity=str(faculty.faculty_id),
                additional_claims=claims
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
                    'refresh_token': refresh_token,
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
    return render_template('admin/unified_dashboard.html')


@app.route('/api/student/login', methods=['POST'])
@limiter.limit("30 per minute")
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
                claims = {'type': 'student', 'student_id': student.student_id}
                access_token = create_access_token(
                    identity=str(student.student_id),
                    additional_claims=claims
                )
                refresh_token = create_refresh_token(
                    identity=str(student.student_id),
                    additional_claims=claims
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
                        'refresh_token': refresh_token,
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

# ----------------------------------------------------------------------------
# JWT Refresh Token Endpoint
# ----------------------------------------------------------------------------
@app.route('/api/token/refresh', methods=['POST'])
@limiter.limit("50 per minute")
@jwt_required(refresh=True)
def refresh_access_token():
    """Issue a new access token using a valid refresh token"""
    try:
        identity = get_jwt_identity()
        claims = get_jwt()
        user_type = claims.get('type')

        additional_claims = {'type': user_type} if user_type else {}
        try:
            id_int = int(identity) if identity is not None else None
        except Exception:
            id_int = identity

        if user_type == 'student' and id_int is not None:
            additional_claims['student_id'] = id_int
        elif user_type == 'faculty' and id_int is not None:
            additional_claims['faculty_id'] = id_int
        elif user_type == 'admin' and id_int is not None:
            additional_claims['admin_id'] = id_int

        new_access_token = create_access_token(identity=str(identity), additional_claims=additional_claims)
        return standardize_response(
            success=True,
            data={'access_token': new_access_token},
            message='Token refreshed',
            status_code=200
        )
    except Exception as e:
        return standardize_response(success=False, error=str(e), status_code=500)

@app.route('/api/student/register', methods=['POST'])
@limiter.limit("20 per minute")
def student_register():
    """Student registration endpoint for mobile app"""
    try:
        logger.info(f"Student registration attempt from {request.remote_addr}")
        
        data = request.get_json()
        if not data:
            return standardize_response(
                success=False,
                error='JSON data required',
                status_code=400
            )
        
        # Validate required fields
        required_fields = ['student_code', 'first_name', 'last_name', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return standardize_response(
                    success=False,
                    error=f'{field} is required',
                    status_code=400
                )
        
        # Check if student already exists
        existing = Student.query.filter(
            db.or_(
                getattr(Student, 'student_code') == data['student_code'],
                getattr(Student, 'email') == data['email']
            )
        ).first()
        
        if existing:
            return standardize_response(
                success=False,
                error='Student with this code or email already exists',
                status_code=400
            )
        
        # Create new student
        student = Student(
            student_code=data['student_code'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone_number=data.get('phone_number'),
            program=data.get('program', 'Not Specified'),
            year_of_study=data.get('year_of_study', 1),
            password_hash=bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            is_active=True
        )
        
        db.session.add(student)
        db.session.commit()
        
        logger.info(f"Student registered successfully: {student.email}")
        
        # Create tokens for auto-login
        claims = {'type': 'student', 'student_id': student.student_id}
        access_token = create_access_token(
            identity=str(student.student_id),
            additional_claims=claims
        )
        refresh_token = create_refresh_token(
            identity=str(student.student_id),
            additional_claims=claims
        )
        
        student_data = {
            'student_id': student.student_id,
            'student_code': student.student_code,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email,
            'program': student.program,
            'year_of_study': student.year_of_study
        }
        
        return standardize_response(
            success=True,
            data={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'student': student_data
            },
            message='Registration successful',
            status_code=201
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/student/profile', methods=['GET'])
@app.route('/api/student/me', methods=['GET'])
@jwt_required()
def student_profile():
    """Get current student profile - used for auto-login verification"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'student':
            return standardize_response(
                success=False,
                error='Student access required',
                status_code=403
            )
        
        student_id = claims.get('student_id')
        
        # Get student with section information
        student_query = text("""
            SELECT s.student_id, s.student_code, s.first_name, s.last_name, s.email, 
                   s.phone_number, s.program, s.year_of_study, s.is_active,
                   sec.id as section_id, sec.section_name
            FROM students s
            LEFT JOIN sections sec ON s.section_id = sec.id
            WHERE s.student_id = :student_id AND s.is_active = TRUE
        """)
        
        student_result = db.session.execute(student_query, {'student_id': student_id})
        student_row = student_result.fetchone()
        
        if not student_row:
            return standardize_response(
                success=False,
                error='Student not found or inactive',
                status_code=404
            )
        
        student_data = {
            'student_id': student_row.student_id,
            'student_code': student_row.student_code,
            'first_name': student_row.first_name,
            'last_name': student_row.last_name,
            'email': student_row.email,
            'phone_number': student_row.phone_number,
            'program': student_row.program,
            'year_of_study': student_row.year_of_study or 1,
            'is_active': student_row.is_active,
            'section_id': student_row.section_id,
            'section_name': student_row.section_name
        }
        
        return standardize_response(
            success=True,
            data={
                'student': student_data
            },
            message='Profile retrieved successfully',
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/device/register', methods=['POST'])
@jwt_required()
def register_student_device():
    """Register a student device for attendance tracking"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'student':
            return standardize_response(
                success=False,
                error='Student access required',
                status_code=403
            )
        
        student_id = claims.get('student_id')
        data = request.get_json()
        
        if not data:
            return standardize_response(
                success=False,
                error='JSON data required',
                status_code=400
            )
        
        device_id = data.get('device_id')
        device_name = data.get('device_name')
        device_type = data.get('device_type')
        device_os = data.get('device_os')
        device_os_version = data.get('device_os_version')
        device_model = data.get('device_model')
        device_manufacturer = data.get('device_manufacturer')
        device_ip = request.remote_addr
        
        if not device_id or not device_name or not device_type or not device_os:
            return standardize_response(
                success=False,
                error='device_id, device_name, device_type, and device_os are required',
                status_code=400
            )
        
        # Check if device already exists
        existing_device = StudentDevices.query.filter_by(device_id=device_id).first()
        if existing_device:
            return standardize_response(
                success=False,
                error='Device with this ID already exists',
                status_code=400
            )
        
        # Create new device
        device = StudentDevices(
            student_id=student_id,
            device_uuid=device_id,
            device_type='web',  # Default to web for this endpoint
            device_name=device_name,
            device_model=device_model,
            os_version=device_os_version,
            app_version=None,  # Not available in this endpoint
            fcm_token=None,  # Not available in this endpoint
            is_active=True
        )
        
        db.session.add(device)
        db.session.commit()
        
        logger.info(f"Device registered successfully: {device_id}")
        
        return standardize_response(
            success=True,
            data={
                'device_id': device_id,
                'device_name': device_name,
                'device_type': device_type,
                'device_os': device_os,
                'device_os_version': device_os_version,
                'device_model': device_model,
                'device_manufacturer': device_manufacturer,
                'device_ip': device_ip,
                'student_id': student_id
            },
            message='Device registration successful',
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Device registration error: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

# ============================================================================
# STUDENT TIMETABLE API ENDPOINTS (Updated for new structure)
# ============================================================================

@app.route('/api/student/timetable/today', methods=['GET'])
@jwt_required()
def get_todays_timetable():
    """Get today's timetable for the current student"""
    try:
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return standardize_response(
                success=False,
                error='Student access required',
                status_code=403
            )
        
        student_id = claims.get('student_id')
        
        # Get current day of week in uppercase format (as stored in DB)
        from datetime import datetime
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
            return standardize_response(
                success=False,
                error='Student not found',
                status_code=404
            )
        
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
                'subject_name': row.subject_name if row.subject_name else 'TBA',
                'subject_code': row.subject_code if row.subject_code else 'TBA',
                'short_name': row.short_name if row.short_name else row.subject_code if row.subject_code else 'TBA',
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
            'program': 'CSE(AIML)'  # Placeholder - could be retrieved from student data
        }
        
        return standardize_response(
            success=True,
            data={
                'date': datetime.now().strftime('%Y-%m-%d'),
                'day_of_week': day_of_week,
                'sessions': sessions,
                'student_info': student_info
            },
            message='Today\'s schedule retrieved successfully' if sessions else 'No classes scheduled for today'
        )
        
    except Exception as e:
        logger.error(f"Error fetching today's timetable: {e}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/student/timetable/<day>', methods=['GET'])
@jwt_required()
def get_timetable_for_day(day):
    """Get timetable for a specific day"""
    try:
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return standardize_response(
                success=False,
                error='Student access required',
                status_code=403
            )
        
        student_id = claims.get('student_id')
        
        # Validate day parameter
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if day not in valid_days:
            return standardize_response(
                success=False,
                error='Invalid day. Must be one of: ' + ', '.join(valid_days),
                status_code=400
            )
        
        # Get the student's section
        student_query = text("""
            SELECT sec.id as section_id, sec.section_name
            FROM students s
            JOIN sections sec ON s.section_id = sec.id
            WHERE s.student_id = :student_id
        """)
        
        student_result = db.session.execute(student_query, {'student_id': student_id})
        student_row = student_result.fetchone()
        
        if not student_row:
            return standardize_response(
                success=False,
                error='Student not found',
                status_code=404
            )
        
        section_id = student_row.section_id
        section_name = student_row.section_name
        
        # Get timetable for the student's section, excluding breaks/lunch/free slots
        timetable_query = text("""
            SELECT t.id, s.section, t.day_of_week, t.slot_number, t.slot_type, 
                   t.start_time, t.end_time, t.subject_code, t.subject_name, t.faculty_name, t.room_number
            FROM timetable t
            JOIN sections s ON t.section_id = s.id
            WHERE t.section_id = :section_id AND t.day_of_week = :day_of_week
            AND t.slot_type NOT IN ('break', 'lunch', 'free')
            AND t.subject_code IS NOT NULL
            AND t.subject_code != ''
            ORDER BY t.slot_number, t.start_time
        """)
        
        result = db.session.execute(timetable_query, {'section_id': section_id, 'day_of_week': day})
        timetable_data = []
        
        for row in result:
            timetable_data.append({
                'id': row[0],
                'section': section_name,
                'day_of_week': row[2],
                'slot_number': row[3],
                'slot_type': row[4],
                'start_time': str(row[5]) if row[5] else None,
                'end_time': str(row[6]) if row[6] else None,
                'subject_code': row[7],
                'subject_name': row[8],
                'faculty_name': row[9],
                'room_number': row[10]
            })
        
        return standardize_response(
            success=True,
            data={
                'day': day,
                'timetable': timetable_data
            },
            message=f'{day}\'s timetable retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error fetching timetable for {day}: {e}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )


@app.route('/api/student/timetable', methods=['GET'])
@jwt_required()
def get_student_timetable():
    """Get complete timetable for the current student"""
    try:
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return standardize_response(
                success=False,
                error='Student access required',
                status_code=403
            )
        
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
            return standardize_response(
                success=False,
                error='Student not found',
                status_code=404
            )
        
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
        
        return standardize_response(
            success=True,
            data={
                'student': student_info,
                'timetable': timetable_schedule
            },
            message='Student timetable retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error fetching student timetable: {e}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )


@app.route('/api/student/current-session', methods=['GET'])
@jwt_required()
def get_current_session():
    """Get current and next session for the student"""
    try:
        from datetime import datetime, time
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return standardize_response(
                success=False,
                error='Student access required',
                status_code=403
            )
        
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
            return standardize_response(
                success=False,
                error='Student not found',
                status_code=404
            )
        
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
            
            # Parse time strings to datetime.time objects
            start_time_parsed = None
            end_time_parsed = None
            
            if start_time_obj:
                try:
                    time_parts = str(start_time_obj).split(':')
                    start_time_parsed = time(int(time_parts[0]), int(time_parts[1]), int(time_parts[2]) if len(time_parts) > 2 else 0)
                except (ValueError, IndexError):
                    pass
            
            if end_time_obj:
                try:
                    time_parts = str(end_time_obj).split(':')
                    end_time_parsed = time(int(time_parts[0]), int(time_parts[1]), int(time_parts[2]) if len(time_parts) > 2 else 0)
                except (ValueError, IndexError):
                    pass
            
            # Calculate elapsed and remaining time
            elapsed_minutes = 0
            remaining_minutes = 0
            
            if start_time_parsed:
                try:
                    elapsed_minutes = int((now - datetime.combine(now.date(), start_time_parsed)).total_seconds() / 60)
                except:
                    pass
            
            if end_time_parsed:
                try:
                    remaining_minutes = int((datetime.combine(now.date(), end_time_parsed) - now).total_seconds() / 60)
                except:
                    pass
            
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
            
            # Parse time strings to datetime.time objects
            start_time_parsed = None
            
            if start_time_obj:
                try:
                    time_parts = str(start_time_obj).split(':')
                    start_time_parsed = time(int(time_parts[0]), int(time_parts[1]), int(time_parts[2]) if len(time_parts) > 2 else 0)
                except (ValueError, IndexError):
                    pass
            
            # Calculate minutes until start
            minutes_until_start = 0
            if start_time_parsed:
                try:
                    minutes_until_start = int((datetime.combine(now.date(), start_time_parsed) - now).total_seconds() / 60)
                except:
                    pass
            
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
        
        return standardize_response(
            success=True,
            data={
                'currentSession': current_session,
                'nextSession': next_session,
                'warmWindowActive': warm_window_active,
                'warmWindowStartsIn': warm_window_starts_in
            },
            message='Current session information retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error fetching current session: {e}")
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
@limiter.limit("5 per minute")
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
        expires_at = datetime.now() + timedelta(minutes=app.config['OTP_EXPIRY_MINUTES'])
        
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
        
        # Bypass OTP validation for smart board portal - accept "000000" as default OTP
        if otp_code == "000000":
            # For smart board portal, we'll use a default faculty (first faculty in DB)
            default_faculty = Faculty.query.first()
            if not default_faculty:
                return standardize_response(
                    success=False,
                    error='No faculty found in system',
                    status_code=400
                )
            
            faculty_id = default_faculty.faculty_id
        else:
            # Find valid OTP for faculty login
            current_time = datetime.now()
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
            otp_log.used_at = datetime.now()
            faculty_id = otp_log.faculty_id
        
        # Validate that faculty has assigned classes
        faculty_classes = Classes.query.filter_by(faculty_id=faculty_id, is_active=True).count()
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
                faculty_id=faculty_id,
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
                faculty_id=faculty_id,
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
            current_day = datetime.now().strftime('%A')
            current_time = datetime.now().time()
            
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
        
        # Faculty availability validation: Prevent faculty from teaching concurrent classes
        try:
            # Calculate session start and end times
            session_start_time = datetime.now()
            session_end_time = session_start_time + timedelta(seconds=app.config['QR_SESSION_DURATION'])
            
            # Validate faculty availability (skip for default OTP)
            if otp_code != "000000":
                validate_faculty_availability(faculty_id, session_start_time, session_end_time)
            
            # Classroom capacity validation: Prevent exceeding classroom capacity
            validate_classroom_capacity(actual_class_id)
        except ValidationError as e:
            return standardize_response(
                success=False,
                error=str(e),
                status_code=400
            )
        
        # Create attendance session
        session_token = generate_token()
        secret_key = generate_token()
        expires_at = datetime.now() + timedelta(seconds=app.config['QR_SESSION_DURATION'])
        
        attendance_session = AttendanceSession(
            class_id=actual_class_id,
            faculty_id=faculty_id,
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
        
    except ValidationError as e:
        db.session.rollback()
        return standardize_response(
            success=False,
            error=str(e),
            status_code=400
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
        expires_at = datetime.now() + timedelta(minutes=duration)

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

@app.route('/api/smartboard/classes', methods=['GET'])
def get_smartboard_classes():
    """Get classes for smartboard display (no authentication required)"""
    try:
        # Get all active classes
        classes = Classes.query.filter_by(is_active=True).all()
        
        classes_list = []
        for class_obj in classes:
            # Get faculty name
            faculty = Faculty.query.get(class_obj.faculty_id)
            faculty_name = f"{faculty.first_name} {faculty.last_name}" if faculty else None
            
            # Get classroom info
            classroom = Classroom.query.get(class_obj.classroom_id)
            room_number = classroom.room_number if classroom else None
            
            classes_list.append({
                'class_id': class_obj.class_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'faculty_name': faculty_name,
                'room_number': room_number,
                'semester': class_obj.semester,
                'academic_year': class_obj.academic_year
            })
        
        return standardize_response(
            success=True,
            data=classes_list,
            message='Classes retrieved successfully',
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error getting classes for smartboard: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )


@app.route('/api/qr/stop', methods=['POST'])
def stop_attendance_session():
    """Stop an attendance session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return standardize_response(
                success=False,
                error='Session ID is required',
                status_code=400
            )

        # Find the attendance session
        attendance_session = AttendanceSession.query.get(session_id)
        if not attendance_session:
            return standardize_response(
                success=False,
                error='Attendance session not found',
                status_code=404
            )

        # Update the session status to 'inactive'
        attendance_session.status = 'inactive'
        db.session.commit()

        # Remove the session from memory
        with active_qr_sessions_lock:
            if session_id in active_qr_sessions:
                del active_qr_sessions[session_id]

        return standardize_response(
            success=True,
            message='Attendance session stopped',
            status_code=200
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in stop_attendance_session: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/qr/generate', methods=['POST'])
def generate_qr():
    """Generate a new QR code for an active attendance session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return standardize_response(
                success=False,
                error='Session ID is required',
                status_code=400
            )

        # Find the attendance session
        attendance_session = AttendanceSession.query.get(session_id)
        if not attendance_session:
            return standardize_response(
                success=False,
                error='Attendance session not found',
                status_code=404
            )

        # Check if the session is active
        if attendance_session.status != 'active':
            return standardize_response(
                success=False,
                error='Attendance session is not active',
                status_code=400
            )

        # Generate a new QR code
        qr_data = {
            'session_id': attendance_session.session_id,
            'token': attendance_session.qr_token,
            'secret': attendance_session.qr_secret_key
        }
        qr_image = create_qr_code(json.dumps(qr_data), attendance_session.session_id)

        # Store the QR code in memory
        with active_qr_sessions_lock:
            if session_id in active_qr_sessions:
                active_qr_sessions[session_id]['current_qr'] = qr_image
                active_qr_sessions[session_id]['qr_count'] += 1

        return standardize_response(
            success=True,
            data={
                'qr_image': qr_image,
                'qr_count': active_qr_sessions[session_id]['qr_count']
            },
            message='QR code generated successfully',
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error in generate_qr: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/qr/scan', methods=['POST'])
def scan_qr():
    """Scan a QR code and record attendance"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        token = data.get('token')
        secret = data.get('secret')

        if not session_id or not token or not secret:
            return standardize_response(
                success=False,
                error='Session ID, token, and secret are required',
                status_code=400
            )

        # Find the attendance session
        attendance_session = AttendanceSession.query.get(session_id)
        if not attendance_session:
            return standardize_response(
                success=False,
                error='Attendance session not found',
                status_code=404
            )

        # Check if the session is active
        if attendance_session.status != 'active':
            return standardize_response(
                success=False,
                error='Attendance session is not active',
                status_code=400
            )

        # Validate the token and secret
        if attendance_session.qr_token != token or attendance_session.qr_secret_key != secret:
            return standardize_response(
                success=False,
                error='Invalid token or secret',
                status_code=400
            )

        # Record attendance (this is a placeholder for actual attendance recording logic)
        attendance_record = AttendanceRecord(
            session_id=attendance_session.session_id,
            student_id='student_id_here'  # Replace with actual student ID
        )
        db.session.add(attendance_record)
        db.session.commit()

        return standardize_response(
            success=True,
            message='Attendance recorded successfully',
            status_code=200
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in scan_qr: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/qr/status', methods=['GET'])
def get_qr_status():
    """Get the status of an active attendance session"""
    try:
        session_id = request.args.get('session_id')

        if not session_id:
            return standardize_response(
                success=False,
                error='Session ID is required',
                status_code=400
            )

        # Find the attendance session
        attendance_session = AttendanceSession.query.get(session_id)
        if not attendance_session:
            return standardize_response(
                success=False,
                error='Attendance session not found',
                status_code=404
            )

        # Check if the session is active
        if attendance_session.status != 'active':
            return standardize_response(
                success=False,
                error='Attendance session is not active',
                status_code=400
            )

        # Get the current QR code and count
        with active_qr_sessions_lock:
            if session_id in active_qr_sessions:
                current_qr = active_qr_sessions[session_id]['current_qr']
                qr_count = active_qr_sessions[session_id]['qr_count']
            else:
                return standardize_response(
                    success=False,
                    error='QR session not found in memory',
                    status_code=404
                )

        return standardize_response(
            success=True,
            data={
                'current_qr': current_qr,
                'qr_count': qr_count
            },
            message='QR status retrieved successfully',
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error in get_qr_status: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

# ============================================================================
# QR CODE MANAGEMENT
# ============================================================================

def start_qr_generation(session_id):
    """Start QR code generation for a session with enhanced error handling and resource management"""
    def generate_qr_sequence():
        try:
            with app.app_context():
                # Validate session exists
                with active_qr_sessions_lock:
                    session_data = active_qr_sessions.get(session_id)
                    if not session_data:
                        logger.warning(f"Session {session_id} not found in active sessions at startup")
                        return
                
                start_time = datetime.utcnow()
                end_time = session_data['expires_at']
                logger.info(f"Starting QR generation for session {session_id} (expires at {end_time.isoformat()})")
                
                # Validate session duration
                if end_time <= start_time:
                    logger.warning(f"Session {session_id} has already expired")
                    with active_qr_sessions_lock:
                        if session_id in active_qr_sessions:
                            del active_qr_sessions[session_id]
                    return
                
                while datetime.utcnow() < end_time:
                    # Check if session is still active with lock
                    with active_qr_sessions_lock:
                        if session_id not in active_qr_sessions:
                            logger.info(f"Session {session_id} removed from active sessions, stopping generation")
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
                        logger.error(f"Database error checking session status for {session_id}: {e}")
                        # Continue generation but log the error
                        # We don't break here to maintain resilience
                        pass
                        
                    # Generate new QR token
                    current_time = int(time.time())
                    qr_data = {
                        'session_id': session_id,
                        'token': session_data['token'],
                        'timestamp': current_time,
                        'sequence': session_data['qr_count'],
                        'expires_at': current_time + app.config.get('QR_REFRESH_INTERVAL', 5) + 2  # Add buffer
                    }
                    
                    # Create QR code
                    try:
                        qr_json_data = json.dumps(qr_data, separators=(',', ':'))
                        qr_filename = create_qr_code(qr_json_data, session_id)
                        
                        if qr_filename:
                            with active_qr_sessions_lock:
                                # Double-check session still exists
                                if session_id in active_qr_sessions:
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
                        refresh_interval = app.config.get('QR_REFRESH_INTERVAL', 5)
                        time.sleep(refresh_interval)
                    except Exception as e:
                        logger.error(f"Error during sleep in QR generation for session {session_id}: {e}")
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
                    
                logger.info(f"QR generation completed for session {session_id} after {session_data.get('qr_count', 0)} QR codes")
        
        except Exception as e:
            logger.error(f"Critical error in QR generation thread for session {session_id}: {e}", exc_info=True)
            # Attempt to clean up
            try:
                with active_qr_sessions_lock:
                    if session_id in active_qr_sessions:
                        del active_qr_sessions[session_id]
                        logger.info(f"Emergency cleanup for session {session_id}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup session {session_id}: {cleanup_error}")
    
    # Start generation in background thread
    try:
        thread = threading.Thread(target=generate_qr_sequence, daemon=True, name=f"qr-gen-{session_id}")
        thread.start()
        logger.info(f"QR generation thread started for session {session_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to start QR generation thread for session {session_id}: {e}")
        return False

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
# ADMIN LOGIN ROUTE (Direct route for frontend compatibility)
# ============================================================================

@app.route('/api/admin/login', methods=['POST'])
@limiter.limit("10 per minute")
def admin_login():
    """Admin login endpoint - Direct route for frontend compatibility"""
    try:
        data = request.get_json()
        username = data.get('username') if data else None
        password = data.get('password') if data else None
        
        if not username or not password:
            return standardize_response(success=False, error='Username and password required', status_code=400)
        
        # Query admin by username
        admin = Admin.query.filter_by(username=username, is_active=True).first()
        
        if admin and check_password(password, admin.password_hash):
            # Update last login
            admin.last_login = datetime.utcnow()
            db.session.commit()
            
            # Create access and refresh tokens
            claims = {
                'type': 'admin',
                'admin_id': admin.admin_id,
                'username': admin.username,
                'role': admin.role
            }
            access_token = create_access_token(identity=str(admin.admin_id), additional_claims=claims)
            refresh_token = create_refresh_token(identity=str(admin.admin_id), additional_claims=claims)

            admin_data = {
                'admin_id': admin.admin_id,
                'username': admin.username,
                'email': admin.email,
                'name': f"{admin.first_name} {admin.last_name}",
                'first_name': admin.first_name,
                'last_name': admin.last_name,
                'role': admin.role
            }

            # Standardized response with backward-compatible fields inside data
            return standardize_response(
                success=True,
                data={
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'admin': admin_data,
                    'token': access_token,
                    'user': {
                        'id': admin.admin_id,
                        'username': admin.username,
                        'role': admin.role,
                        'type': 'admin'
                    }
                },
                message='Login successful',
                status_code=200
            )
        else:
            return standardize_response(success=False, error='Invalid username or password', status_code=401)
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during admin login: {str(e)}")
        return standardize_response(success=False, error=str(e), message='Login failed', status_code=500)

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

        # Optional warm-scan payload (non-breaking add-on)
        warm_samples = data.get('samples')  # list of historical samples
        final_sample = data.get('final_sample')  # latest sample
        
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
        
        # Student enrollment validation: Check if student is enrolled in the class
        try:
            validate_student_enrollment(student_id, session.class_id)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400
        
        # Student session conflict validation: Prevent concurrent session attendance
        try:
            session_start_time = session.start_time or datetime.utcnow()
            session_end_time = session.end_time or (session_start_time + timedelta(minutes=60))  # Default 1 hour
            validate_student_session_conflict(student_id, session_start_time, session_end_time)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400
        
        # Professional duplicate detection with time window and conflict resolution
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        existing_record = AttendanceRecord.query.filter(
            db.and_(
                getattr(AttendanceRecord, 'student_id') == student_id,
                getattr(AttendanceRecord, 'session_id') == session_id,
                getattr(AttendanceRecord, 'created_at') >= five_minutes_ago
            )
        ).first()
        
        if existing_record:
            logger.warning(f"Duplicate attendance detected for student {student_id} in session {session_id}")
            return standardize_response(
                success=False,
                error="Attendance already marked for this session",
                status_code=409,  # Conflict status code
                data={
                    'existing_record_id': existing_record.record_id,
                    'marked_at': existing_record.scan_timestamp.isoformat(),
                    'conflict_type': 'duplicate_submission',
                    'resolution': 'server_wins',  # Server record takes precedence
                    'retry_after': 300  # Can retry after 5 minutes
                }
            )
        
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
        
        # Optionally compute non-binding confidence additions from warm samples (logged only)
        try:
            extra_meta = {}
            if warm_samples or final_sample:
                # simple counts as preview; do not affect decision
                warm_ble_hits = 0
                if warm_samples:
                    for s in warm_samples:
                        for b in (s.get('ble') or []):
                            if 'rssi' in b:
                                warm_ble_hits += 1
                extra_meta = {
                    'warm_ble_observations': warm_ble_hits,
                    'has_final_sample': bool(final_sample)
                }
            logger.info(f"Warm-scan meta: {extra_meta}")
        except Exception as _e:
            logger.debug("Warm-scan meta parse failed")

        # Enhanced error responses with specific failure reasons
        if status == 'invalid':
            reasons = []
            if not biometric_verified:
                reasons.append("Biometric verification failed")
            if not location_verified:
                reasons.append("Out of range (GPS)")
            if not bluetooth_verified:
                reasons.append("Bluetooth beacon not detected")
            
            if not reasons:
                reasons.append("Unknown verification failure")
            
            reason_text = "; ".join(reasons)
            
            return jsonify({
                'success': False,
                'status': 'invalid',
                'verification_score': verification_score,
                'reason': reason_text,
                'details': {
                    'biometric': biometric_verified,
                    'location': location_verified,
                    'gps_distance': gps_distance,
                    'bluetooth': bluetooth_verified,
                    'bluetooth_rssi': bluetooth_rssi
                }
            }), 200

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
        
    except ValidationError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except BaseException as e:
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

@app.route('/admin/faculty')
def admin_faculty():
    """Admin faculty management page"""
    return render_template('admin/unified_dashboard.html')

@app.route('/admin/students')
def admin_students():
    """Admin student management page"""
    return render_template('admin/unified_dashboard.html')


@app.route('/static/qr_tokens/<filename>')
def serve_qr_token(filename):
    """Serve QR token images"""
    try:
        # Use absolute path to QR_DATA folder in parent directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        qr_tokens_path = os.path.join(project_root, 'QR_DATA', 'tokens')
        return send_from_directory(qr_tokens_path, filename)
    except Exception as e:
        logger.error(f"Error serving QR token: {e}")
        return jsonify({'error': 'File not found'}), 404

@app.route('/static/js/<path:filename>')
def serve_js(filename):
    """Serve static JavaScript files"""
    try:
        static_js_path = os.path.join(app.static_folder or '', 'js')
        return send_from_directory(static_js_path, filename)
    except Exception as e:
        logger.error(f"Error serving JS file: {e}")
        return jsonify({'error': 'File not found'}), 404

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'Endpoint not found. Refer to discovery and status endpoints.',
        'links': {
            'mobile_config': '/api/config/mobile',
            'discover': '/api/discover',
            'health': '/api/health',
            'auth_status': '/api/auth/status',
            'qr_status': '/api/qr/status',
            'session_status': '/api/session/status'
        }
    }), 404

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

@app.route('/mobile-config')
def mobile_config_page():
    """Mobile app configuration page with QR code"""
    return render_template('mobile_config.html')

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

@app.route('/api/config/qr')
def generate_config_qr():
    """Generate QR code for mobile app server configuration"""
    try:
        import io
        import base64
        
        # Get current server URL dynamically
        server_url = f"http://{request.host}/api/"
        
        # Create config JSON for mobile app
        config_data = {
            "server_url": server_url,
            "app_name": "IntelliAttend",
            "version": "1.0.0",
            "config_type": "server_config",
            "timestamp": datetime.utcnow().isoformat(),
            "features": {
                "qr_scanning": True,
                "biometric_auth": True,
                "location_tracking": True,
                "bluetooth_proximity": True
            }
        }
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_M,
            box_size=10,
            border=4
        )
        qr.add_data(json.dumps(config_data))
        qr.make(fit=True)
        
        # Convert to image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for web display
        img_buffer = io.BytesIO()
        img.save(img_buffer, 'PNG')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'qr_image': f"data:image/png;base64,{img_base64}",
            'config': config_data,
            'instructions': {
                'step1': 'Open IntelliAttend mobile app',
                'step2': 'Go to Settings → Server Configuration',
                'step3': 'Tap "Scan Configuration QR"',
                'step4': 'Point camera at this QR code',
                'step5': 'Server will be configured automatically'
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating config QR: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



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
            getattr(Classes, 'faculty_id') == faculty_id,
            getattr(Classes, 'is_active').is_(True)
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








# ============================================================================
# APPLICATION STARTUP
# ============================================================================

def create_app():
    """Application factory"""
    return app

# ============================================================================
# IP DISCOVERY SERVICE INTEGRATION
# ============================================================================
try:
    from simple_ip_discovery import setup_simple_ip_discovery
    
    # Setup simple IP discovery service
    discovery_service = setup_simple_ip_discovery(app, port=5002)
    logger.info("🌐 Simple IP Discovery Service initialized successfully")
    
except ImportError as e:
    logger.warning(f"⚠️  IP Discovery Service not available: {e}")
except Exception as e:
    logger.error(f"❌ Failed to initialize IP Discovery Service: {e}")

@app.route('/api/student/mobile-login', methods=['POST'])
@limiter.limit("30 per minute")
def student_mobile_login():
    """Mobile-app-friendly student login endpoint with common response format"""
    try:
        data = request.get_json()
        email = data.get('email') if data else None
        password = data.get('password') if data else None
        
        if not email or not password:
            return jsonify({
                'status': 'error',
                'success': False,
                'message': 'Email and password required',
                'error': 'Email and password required'
            }), 400
        
        student = Student.query.filter_by(email=email, is_active=True).first()
        
        if student and check_password(password, student.password_hash):
            access_token = create_access_token(
                identity=str(student.student_id),
                additional_claims={'type': 'student', 'student_id': student.student_id}
            )
            
            # Multiple response formats for better mobile app compatibility
            return jsonify({
                # Format 1: Standard
                'status': 'success',
                'success': True,
                'message': 'Login successful',
                
                # Format 2: Token variations
                'token': access_token,
                'access_token': access_token,
                'authToken': access_token,
                'jwt': access_token,
                
                # Format 3: User data variations
                'user': {
                    'id': student.student_id,
                    'user_id': student.student_id,
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'name': f'{student.first_name} {student.last_name}',
                    'email': student.email,
                    'program': student.program,
                    'year_of_study': student.year_of_study or 1,
                    'role': 'student',
                    'user_type': 'student'
                },
                'student': {
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'program': student.program,
                    'year_of_study': student.year_of_study or 1
                },
                
                # Format 4: Additional fields mobile apps often expect
                'authenticated': True,
                'login': True,
                'isLoggedIn': True,
                'status_code': 200,
                'code': 200
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'success': False,
                'message': 'Invalid credentials',
                'error': 'Invalid email or password',
                'authenticated': False,
                'login': False,
                'isLoggedIn': False
            }), 401
            
    except Exception as e:
        logger.error(f"Mobile login error: {str(e)}")
        return jsonify({
            'status': 'error',
            'success': False,
            'message': 'Login failed',
            'error': str(e),
            'authenticated': False
        }), 500

# Register admin blueprints
try:
    # Import blueprints inside a function to avoid circular imports
    def register_admin_blueprints():
        from admin.api.auth_routes import auth_bp
        from admin.api.faculty_routes import faculty_bp
        from admin.api.student_routes import student_bp
        from admin.api.classroom_routes import classroom_bp
        from admin.api.class_routes import class_bp
        from admin.api.device_routes import device_bp
        from admin.api.enrollment_routes import enrollment_bp
        
        # New admin API blueprints
        from api.admin_classroom import admin_classroom_bp
        from api.admin_student import admin_student_bp
        from api.admin_faculty import admin_faculty_bp
        from api.admin_device_management import admin_device_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(faculty_bp)
        app.register_blueprint(student_bp)
        app.register_blueprint(classroom_bp)
        app.register_blueprint(class_bp)
        app.register_blueprint(device_bp)
        app.register_blueprint(enrollment_bp)
        
        # Register new admin APIs
        app.register_blueprint(admin_classroom_bp)
        app.register_blueprint(admin_student_bp)
        app.register_blueprint(admin_faculty_bp)
        app.register_blueprint(admin_device_bp)
    
    register_admin_blueprints()
    logger.info("Admin blueprints registered successfully")
except Exception as e:
    logger.error(f"Failed to register admin blueprints: {e}")

# Register mobile API
try:
    # Import mobile API blueprint
    from mobile_api import mobile_bp
    from api.mobile_device_enforcement import mobile_device_bp
    from api.mobile_enhanced_validation import mobile_enhanced_bp
    from api.attendance_statistics import attendance_stats_bp
    from api.notifications import notifications_bp
    from api.auto_attendance import auto_attendance_bp
    
    app.register_blueprint(mobile_bp)  # Don't override the url_prefix since it's already defined in the blueprint
    app.register_blueprint(mobile_device_bp)  # Mobile device enforcement and login
    app.register_blueprint(mobile_enhanced_bp)  # Enhanced validation with GPS + WiFi
    app.register_blueprint(attendance_stats_bp)  # Attendance statistics API
    app.register_blueprint(notifications_bp)  # Notifications API
    app.register_blueprint(auto_attendance_bp)  # Auto-attendance API
    logger.info("Mobile API registered successfully")
except Exception as e:
    logger.error(f"Failed to register mobile API: {e}")

@app.route('/admin/unified_dashboard.html')
def admin_unified_dashboard():
    """Serve the unified admin dashboard"""
    return render_template('admin/unified_dashboard.html')

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
    logger.info("📱 Mobile App URL: http://localhost:5002/api/")

    logger.info("🌐 Public Access: http://localhost:5002")
    logger.info("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5002, threaded=True)

# ============================================================================
# MOBILE API V2 ENDPOINTS (for mobile app compatibility)
# ============================================================================

@app.route('/api/mobile/v2/login', methods=['POST'])
@limiter.limit("30 per minute")
def mobile_v2_login():
    """Mobile v2 enhanced login endpoint"""
    try:
        logger.info(f"Mobile v2 login attempt from {request.remote_addr}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        data = request.get_json()
        logger.info(f"Request data keys: {list(data.keys()) if data else 'None'}")
        
        if not data:
            logger.warning("No JSON data received")
            return standardize_response(
                success=False,
                error='JSON data required',
                status_code=400
            )
        
        email = data.get('email')
        password = data.get('password')
        device_info = data.get('device_info', {})
        
        logger.info(f"Login attempt - Email: '{email}', Password length: {len(password) if password else 0}")
        
        if not email or not password:
            logger.warning(f"Missing credentials - Email: {bool(email)}, Password: {bool(password)}")
            return standardize_response(
                success=False,
                error='Email and password required',
                status_code=400
            )
        
        student = Student.query.filter_by(email=email, is_active=True).first()
        logger.info(f"Student found: {student is not None}")
        
        if student:
            password_match = check_password(password, student.password_hash)
            logger.info(f"Password check result: {password_match}")
            if password_match:
                claims = {'type': 'student', 'student_id': student.student_id}
                access_token = create_access_token(
                    identity=str(student.student_id),
                    additional_claims=claims
                )
                refresh_token = create_refresh_token(
                    identity=str(student.student_id),
                    additional_claims=claims
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
                
                logger.info(f"Login successful for {email}")
                return standardize_response(
                    success=True,
                    data={
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'student': student_data,
                        'token': access_token,  # Alternative field name
                        'user': student_data,   # Alternative field name
                        'device_status': {
                            'is_active': True,
                            'is_primary': True,
                            'activation_status': 'active',
                            'can_mark_attendance': True,
                            'cooldown_remaining_seconds': 0,
                            'cooldown_end_time': None,
                            'device_switch_pending': False,
                            'requires_admin_approval': False,
                            'message': 'Device authorized'
                        }
                    },
                    message='Login successful',
                    status_code=200
                )
            else:
                logger.warning(f"Invalid password for {email}")
        else:
            logger.warning(f"Student not found or inactive: {email}")
        
        return standardize_response(
            success=False,
            error='Invalid email or password',
            status_code=401
        )
    except Exception as e:
        logger.error(f"Mobile v2 login error: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/mobile/v2/device-status', methods=['GET'])
@jwt_required()
def mobile_v2_device_status():
    """Mobile v2 device status endpoint"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'student':
            return standardize_response(
                success=False,
                error='Student access required',
                status_code=403
            )
        
        student_id = claims.get('student_id')
        student = Student.query.get(student_id)
        
        if not student or not student.is_active:
            return standardize_response(
                success=False,
                error='Student not found or inactive',
                status_code=404
            )
        
        return standardize_response(
            success=True,
            data={
                'device_status': 'active',
                'student_id': student.student_id,
                'email': student.email,
                'is_active': student.is_active,
                'device_registered': True
            },
            message='Device status retrieved successfully',
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Mobile v2 device status error: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/mobile/v2/device-switch-request', methods=['POST'])
@jwt_required()
def mobile_v2_device_switch_request():
    """Mobile v2 device switch request endpoint"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'student':
            return standardize_response(
                success=False,
                error='Student access required',
                status_code=403
            )
        
        data = request.get_json()
        if not data:
            return standardize_response(
                success=False,
                error='JSON data required',
                status_code=400
            )
        
        return standardize_response(
            success=True,
            data={
                'request_id': 'mock_request_id',
                'status': 'approved',
                'message': 'Device switch approved'
            },
            message='Device switch request processed',
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Mobile v2 device switch request error: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/student/timetable/today', methods=['GET'])
@jwt_required()
def student_timetable_today_v2():
    """Return today's timetable for the current student (nested data shape)"""
    try:
        from datetime import datetime
        claims = get_jwt()
        if claims.get('type') != 'student':
            return standardize_response(success=False, error='Student access required', status_code=403)
        student_id = claims.get('student_id')

        # Determine today's day in uppercase (MONDAY..SUNDAY)
        today = datetime.now().strftime('%A').upper()

        # Query student's section
        section_row = db.session.execute(text("SELECT section_id, student_code, first_name, last_name, program FROM students WHERE student_id = :sid"),
                                         {'sid': student_id}).fetchone()
        if not section_row:
            return standardize_response(success=False, error='Student not found', status_code=404)
        section_id, student_code, first_name, last_name, program = section_row

        # Query today's sessions from timetable
        query = text("""
            SELECT t.id, t.start_time, t.end_time, t.subject_code, t.room_number,
                   s.subject_name, s.short_name, s.faculty_name, sec.section_name
            FROM timetable t
            LEFT JOIN subjects s ON s.subject_code = t.subject_code
            LEFT JOIN sections sec ON sec.id = t.section_id
            WHERE t.section_id = :section_id AND t.day_of_week = :day
            ORDER BY t.start_time
        """)
        rows = db.session.execute(query, { 'section_id': section_id, 'day': today }).fetchall()

        sessions = []
        for r in rows:
            start_str = str(r[1])[:5] if r[1] else None  # HH:MM
            end_str = str(r[2])[:5] if r[2] else None
            sessions.append({
                'id': r[0],
                'subject_id': 0,
                'subject_name': r[5] or (r[3] or ''),
                'subject_code': r[3] or '',
                'short_name': r[6] or (r[3] or ''),
                'teacher_name': r[7],
                'room_number': r[4],
                'start_time': (str(r[1]) if r[1] else ''),
                'end_time': (str(r[2]) if r[2] else ''),
                'section': r[8] or ''
            })

        data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'day_of_week': today,
            'sessions': sessions,
            'student_info': {
                'student_id': student_code or str(student_id),
                'name': f"{first_name or ''} {last_name or ''}".strip(),
                'section': db.session.execute(text("SELECT section_name FROM sections WHERE id=:sid"), {'sid': section_id}).scalar() or '',
                'program': program or ''
            }
        }
        return standardize_response(success=True, data=data, message="Today's timetable retrieved successfully", status_code=200)
    except Exception as e:
        logger.error(f"Student today timetable error: {str(e)}")
        return standardize_response(success=False, error=str(e), status_code=500)


@app.route('/api/student/timetable', methods=['GET'])
@jwt_required()
def student_timetable():
    """Return weekly timetable for the current student (top-level shape)"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'student':
            return jsonify({ 'success': False, 'error': 'Student access required' }), 403
        student_id = claims.get('student_id')

        # Get student + section info
        student_row = db.session.execute(text("""
            SELECT s.student_code, s.first_name, s.last_name, s.program, s.section_id, sec.section_name, sec.course, sec.room_number
            FROM students s
            LEFT JOIN sections sec ON sec.id = s.section_id
            WHERE s.student_id = :sid
        """), { 'sid': student_id }).fetchone()
        if not student_row:
            return jsonify({ 'success': False, 'error': 'Student not found' }), 404

        student_code, first_name, last_name, program, section_id, section_name, course, room = student_row

        # Query full timetable for section
        trows = db.session.execute(text("""
            SELECT t.day_of_week, t.slot_number, t.start_time, t.end_time, t.subject_code, t.slot_type, t.room_number,
                   s.subject_name, s.short_name, s.faculty_name
            FROM timetable t
            LEFT JOIN subjects s ON s.subject_code = t.subject_code
            WHERE t.section_id = :section_id
            ORDER BY FIELD(t.day_of_week, 'MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY'), t.slot_number, t.start_time
        """), { 'section_id': section_id }).fetchall()

        # Build timetable map
        timetable_map = {}
        days = ['MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY']
        for d in days:
            timetable_map[d] = []

        for r in trows:
            day = r[0]
            slot = {
                'slotNumber': r[1] or 0,
                'startTime': (str(r[2])[:5] if r[2] else ''),
                'endTime': (str(r[3])[:5] if r[3] else ''),
                'subjectCode': r[4],
                'subjectName': r[7] or (r[4] or 'BREAK'),
                'shortName': r[8] or (r[4] or 'BREAK'),
                'facultyName': r[9],
                'room': r[6] or '',
                'slotType': r[5] or 'regular'
            }
            if day not in timetable_map:
                timetable_map[day] = []
            timetable_map[day].append(slot)

        student_info = {
            'studentCode': student_code or str(student_id),
            'name': f"{first_name or ''} {last_name or ''}".strip(),
            'section': section_name or '',
            'course': course or program or '',
            'room': room or ''
        }

        # Return top-level shape expected by Mobile TimetableResponse
        return jsonify({
            'success': True,
            'student': student_info,
            'timetable': timetable_map,
            'error': None
        }), 200
    except Exception as e:
        logger.error(f"Student timetable error: {str(e)}")
        return jsonify({ 'success': False, 'student': None, 'timetable': None, 'error': str(e) }), 500

@app.route('/api/student/timetable/today', methods=['GET'])
@jwt_required()
def student_timetable_today():
    """Student today's timetable endpoint"""
    try:
        claims = get_jwt()
        if claims.get('type') != 'student':
            return standardize_response(
                success=False,
                error='Student access required',
                status_code=403
            )
        
        return standardize_response(
            success=True,
            data={
                'today_classes': [],
                'date': datetime.utcnow().strftime('%Y-%m-%d'),
                'message': 'No classes scheduled for today'
            },
            message="Today's timetable retrieved successfully",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Student today timetable error: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )



@app.route('/api/sessions/active', methods=['GET'])
def get_active_sessions():
    """Get active attendance sessions"""
    try:
        return standardize_response(
            success=True,
            data={
                'active_sessions': [],
                'count': 0,
                'message': 'No active sessions'
            },
            message='Active sessions retrieved successfully',
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Get active sessions error: {str(e)}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )

@app.route('/api/student/login-debug', methods=['POST'])
@limiter.limit("30 per minute")
def student_login_debug():
    """Debug version of student login to see what mobile app sends"""
    try:
        logger.info(f"DEBUG: Login attempt from {request.remote_addr}")
        logger.info(f"DEBUG: Headers: {dict(request.headers)}")
        logger.info(f"DEBUG: Content-Type: {request.content_type}")
        logger.info(f"DEBUG: Raw data: {request.get_data()}")
        
        data = request.get_json()
        logger.info(f"DEBUG: Parsed JSON: {data}")
        
        if data:
            email = data.get('email')
            password = data.get('password')
            logger.info(f"DEBUG: Email: '{email}' (len: {len(email) if email else 0})")
            logger.info(f"DEBUG: Password: '{password}' (len: {len(password) if password else 0})")
            logger.info(f"DEBUG: Password bytes: {password.encode('utf-8') if password else None}")
        
        return jsonify({
            'debug': True,
            'received_data': data,
            'headers': dict(request.headers),
            'content_type': request.content_type
        })
        
    except Exception as e:
        logger.error(f"DEBUG: Error: {str(e)}")
        return jsonify({'debug_error': str(e)}), 500
