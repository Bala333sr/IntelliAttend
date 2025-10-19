"""
IntelliAttend - Multi-Factor Attendance Validation Module

This module handles validation of:
- GPS Geofencing (location-based verification)
- WiFi Network Detection (SSID/BSSID matching)
- Bluetooth Beacon Detection (MAC address matching)
- QR Token Validation (token validity and expiry)
- Verification Score Calculation (weighted scoring)
"""

from geopy.distance import geodesic
from datetime import datetime
from typing import Tuple, Optional, List, Dict, Any
from sqlalchemy.orm import Session


def validate_gps(
    student_lat: float,
    student_lng: float,
    classroom_lat: float,
    classroom_lng: float,
    radius: int = 50
) -> Tuple[bool, float]:
    """
    Validate student GPS location against classroom geofence
    
    Args:
        student_lat: Student's GPS latitude
        student_lng: Student's GPS longitude
        classroom_lat: Classroom GPS latitude
        classroom_lng: Classroom GPS longitude
        radius: Geofence radius in meters (default: 50m)
    
    Returns:
        Tuple of (is_valid: bool, distance: float in meters)
    """
    try:
        # Calculate distance using geodesic (accounts for Earth's curvature)
        student_location = (student_lat, student_lng)
        classroom_location = (classroom_lat, classroom_lng)
        distance = geodesic(student_location, classroom_location).meters
        
        # Student is valid if within geofence radius
        is_valid = distance <= radius
        
        return is_valid, round(distance, 2)
    
    except Exception as e:
        # If calculation fails, return invalid
        print(f"GPS validation error: {str(e)}")
        return False, -1.0


def validate_wifi(
    detected_ssid: Optional[str],
    detected_bssid: Optional[str],
    registered_networks: List[Any]
) -> Tuple[bool, Optional[str]]:
    """
    Validate WiFi network against registered classroom networks
    
    Args:
        detected_ssid: WiFi SSID detected by student's device
        detected_bssid: WiFi BSSID (MAC address) detected by student's device
        registered_networks: List of ClassroomWiFi objects registered for classroom
    
    Returns:
        Tuple of (is_valid: bool, matched_network: Optional[str])
    """
    if not detected_ssid or not detected_bssid:
        return False, None
    
    # Normalize detected values
    detected_ssid = detected_ssid.strip()
    detected_bssid = detected_bssid.strip().upper()
    
    # Check against all registered networks
    for network in registered_networks:
        if not network.is_active:
            continue
        
        # Normalize registered values
        registered_ssid = network.ssid.strip()
        registered_bssid = network.bssid.strip().upper()
        
        # Match both SSID and BSSID for stronger verification
        if detected_ssid == registered_ssid and detected_bssid == registered_bssid:
            return True, f"{network.ssid} ({network.bssid})"
    
    return False, None


def validate_bluetooth(
    detected_beacons: List[Dict[str, Any]],
    registered_beacons: List[Any]
) -> Tuple[bool, List[str]]:
    """
    Validate Bluetooth beacons against registered classroom beacons
    
    Args:
        detected_beacons: List of detected Bluetooth devices from student's device
                         Format: [{"mac": "AA:BB:CC:DD:EE:FF", "rssi": -65}, ...]
        registered_beacons: List of ClassroomBeacon objects registered for classroom
    
    Returns:
        Tuple of (is_valid: bool, matched_beacons: List[str])
    """
    if not detected_beacons:
        return False, []
    
    # Extract MAC addresses from detected beacons
    detected_macs = set()
    for beacon in detected_beacons:
        if 'mac' in beacon:
            detected_macs.add(beacon['mac'].strip().upper())
    
    # Extract MAC addresses from registered beacons
    registered_macs = {}
    for beacon in registered_beacons:
        if beacon.is_active:
            registered_macs[beacon.mac_address.strip().upper()] = beacon
    
    # Find matches
    matched = []
    for detected_mac in detected_macs:
        if detected_mac in registered_macs:
            beacon = registered_macs[detected_mac]
            matched.append(f"{beacon.mac_address}")
    
    # Valid if at least one beacon matches
    is_valid = len(matched) > 0
    
    return is_valid, matched


def validate_qr_token(
    token: str,
    db: Session
) -> Tuple[bool, Optional[Any], Optional[str]]:
    """
    Validate QR token and check if it's active and not expired
    
    Args:
        token: QR token string scanned by student
        db: Database session
    
    Returns:
        Tuple of (is_valid: bool, session: Optional[AttendanceSession], error: Optional[str])
    """
    # Import here to avoid circular dependency
    from main import AttendanceSession
    
    try:
        # Query for session with matching token
        session = db.query(AttendanceSession).filter(
            AttendanceSession.qr_token == token
        ).first()
        
        if not session:
            return False, None, "Invalid QR token"
        
        # Check if session is active
        if session.status != 'active':
            return False, None, f"Session is {session.status}"
        
        # Check if token has expired
        now = datetime.utcnow()
        if session.qr_expires_at < now:
            return False, None, "QR token has expired"
        
        # Check if attendance window is open
        if now < session.attendance_window_start:
            minutes_until = int((session.attendance_window_start - now).total_seconds() / 60)
            return False, None, f"Attendance window opens in {minutes_until} minutes"
        
        if now > session.attendance_window_end:
            return False, None, "Attendance window has closed"
        
        # Token is valid
        return True, session, None
    
    except Exception as e:
        print(f"QR token validation error: {str(e)}")
        return False, None, f"Validation error: {str(e)}"


def calculate_score(
    qr_valid: bool,
    gps_valid: bool,
    wifi_valid: bool,
    bluetooth_valid: bool,
    gps_distance: Optional[float] = None,
    geofence_radius: int = 50
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate weighted verification score
    
    Scoring weights:
    - QR Token: 40% (mandatory - must be valid)
    - GPS Location: 25%
    - WiFi Network: 20%
    - Bluetooth Beacon: 15%
    
    Additional GPS scoring:
    - Within 50% of radius: Full points (25%)
    - Within 50-75% of radius: Partial points (18%)
    - Within 75-100% of radius: Minimum points (12%)
    - Outside radius: No points (0%)
    
    Args:
        qr_valid: QR token validation result
        gps_valid: GPS validation result
        wifi_valid: WiFi validation result
        bluetooth_valid: Bluetooth validation result
        gps_distance: Actual distance from classroom (for granular scoring)
        geofence_radius: Geofence radius in meters
    
    Returns:
        Tuple of (total_score: float, breakdown: Dict[str, float])
    """
    # Weight configuration
    weights = {
        'qr': 40.0,
        'gps': 25.0,
        'wifi': 20.0,
        'bluetooth': 15.0
    }
    
    # Score breakdown
    breakdown = {}
    
    # QR Score (mandatory)
    breakdown['qr'] = weights['qr'] if qr_valid else 0.0
    
    # GPS Score (with distance-based granularity)
    if gps_valid and gps_distance is not None:
        # Calculate percentage of radius
        distance_percentage = (gps_distance / geofence_radius) * 100
        
        if distance_percentage <= 50:
            # Very close - full points
            breakdown['gps'] = weights['gps']
        elif distance_percentage <= 75:
            # Moderately close - 75% points
            breakdown['gps'] = weights['gps'] * 0.75
        elif distance_percentage <= 100:
            # Edge of geofence - 50% points
            breakdown['gps'] = weights['gps'] * 0.50
        else:
            # Outside geofence - no points
            breakdown['gps'] = 0.0
    else:
        breakdown['gps'] = weights['gps'] if gps_valid else 0.0
    
    # WiFi Score
    breakdown['wifi'] = weights['wifi'] if wifi_valid else 0.0
    
    # Bluetooth Score
    breakdown['bluetooth'] = weights['bluetooth'] if bluetooth_valid else 0.0
    
    # Calculate total
    total_score = sum(breakdown.values())
    
    return round(total_score, 2), breakdown


def check_duplicate_attendance(
    student_id: int,
    session_id: int,
    db: Session
) -> Tuple[bool, Optional[str]]:
    """
    Check if student has already marked attendance for this session
    
    Args:
        student_id: Student ID
        session_id: Attendance Session ID
        db: Database session
    
    Returns:
        Tuple of (already_marked: bool, record_status: Optional[str])
    """
    from main import AttendanceRecord
    
    try:
        existing_record = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.session_id == session_id
        ).first()
        
        if existing_record:
            return True, existing_record.status
        
        return False, None
    
    except Exception as e:
        print(f"Duplicate check error: {str(e)}")
        return False, None


def format_validation_summary(
    qr_valid: bool,
    gps_valid: bool,
    wifi_valid: bool,
    bluetooth_valid: bool,
    gps_distance: Optional[float],
    wifi_network: Optional[str],
    bluetooth_beacons: List[str],
    score: float,
    breakdown: Dict[str, float]
) -> Dict[str, Any]:
    """
    Format validation results into a comprehensive summary
    
    Args:
        All validation results and metadata
    
    Returns:
        Dictionary with formatted validation summary
    """
    return {
        "verification_score": score,
        "score_breakdown": breakdown,
        "verifications": {
            "qr": {
                "valid": qr_valid,
                "weight": breakdown.get('qr', 0.0)
            },
            "gps": {
                "valid": gps_valid,
                "distance": gps_distance,
                "weight": breakdown.get('gps', 0.0)
            },
            "wifi": {
                "valid": wifi_valid,
                "network": wifi_network,
                "weight": breakdown.get('wifi', 0.0)
            },
            "bluetooth": {
                "valid": bluetooth_valid,
                "beacons": bluetooth_beacons,
                "count": len(bluetooth_beacons) if bluetooth_beacons else 0,
                "weight": breakdown.get('bluetooth', 0.0)
            }
        }
    }
