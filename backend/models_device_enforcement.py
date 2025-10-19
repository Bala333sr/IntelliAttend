"""
Additional database models for device enforcement system
Import these in your main models.py or app.py
"""

from app import db
from datetime import datetime


class CampusWifiNetworks(db.Model):
    """
    Stores registered campus WiFi networks for validation
    """
    __tablename__ = 'campus_wifi_networks'
    
    wifi_network_id = db.Column(db.Integer, primary_key=True)
    network_name = db.Column(db.String(100), nullable=False)
    ssid = db.Column(db.String(100), nullable=False)
    bssid = db.Column(db.String(17), nullable=False)  # MAC address format: AA:BB:CC:DD:EE:FF
    building = db.Column(db.String(100))
    floor = db.Column(db.String(20))
    coverage_area = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, network_name, ssid, bssid, building=None, floor=None, coverage_area=None, is_active=True):
        self.network_name = network_name
        self.ssid = ssid
        self.bssid = bssid
        self.building = building
        self.floor = floor
        self.coverage_area = coverage_area
        self.is_active = is_active


class DeviceSwitchRequests(db.Model):
    """
    Tracks device switch requests from students
    Implements 48-hour cooldown + admin approval mechanism
    """
    __tablename__ = 'device_switch_requests'
    
    request_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    
    # Old device info
    old_device_uuid = db.Column(db.String(255))
    old_device_name = db.Column(db.String(255))
    
    # New device info
    new_device_uuid = db.Column(db.String(255), nullable=False)
    new_device_name = db.Column(db.String(255))
    new_device_type = db.Column(db.String(50))
    new_device_model = db.Column(db.String(255))
    
    # Request status and approval
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    reason = db.Column(db.Text)
    
    # Timestamps
    requested_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    approved_at = db.Column(db.DateTime)
    rejected_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Admin approval
    rejected_reason = db.Column(db.Text)
    approved_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    
    # Additional metadata
    additional_info = db.Column(db.JSON)
    
    def __init__(self, student_id, new_device_uuid, old_device_uuid=None, old_device_name=None,
                 new_device_name=None, new_device_type=None, new_device_model=None,
                 status='pending', reason=None, additional_info=None):
        self.student_id = student_id
        self.old_device_uuid = old_device_uuid
        self.old_device_name = old_device_name
        self.new_device_uuid = new_device_uuid
        self.new_device_name = new_device_name
        self.new_device_type = new_device_type
        self.new_device_model = new_device_model
        self.status = status
        self.reason = reason
        self.additional_info = additional_info or {}


class DeviceActivityLogs(db.Model):
    """
    Comprehensive audit log for all device-related activities
    """
    __tablename__ = 'device_activity_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    device_uuid = db.Column(db.String(255))
    activity_type = db.Column(db.String(100), nullable=False)
    activity_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    additional_info = db.Column(db.JSON)
    
    def __init__(self, student_id, device_uuid, activity_type, additional_info=None):
        self.student_id = student_id
        self.device_uuid = device_uuid
        self.activity_type = activity_type
        self.additional_info = additional_info or {}


# Indexes for performance (add these manually via migration or create_all with index=True)
"""
CREATE INDEX idx_device_switch_student_status ON device_switch_requests(student_id, status);
CREATE INDEX idx_device_switch_requested_at ON device_switch_requests(requested_at);
CREATE INDEX idx_activity_logs_student ON device_activity_logs(student_id);
CREATE INDEX idx_activity_logs_timestamp ON device_activity_logs(activity_timestamp);
CREATE INDEX idx_campus_wifi_active ON campus_wifi_networks(is_active, ssid, bssid);
"""
