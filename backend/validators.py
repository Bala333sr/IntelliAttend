#!/usr/bin/env python3
"""
IntelliAttend - Input Validation Module
Comprehensive validation functions for registration system
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Tuple, Optional

# ============================================================================
# GPS COORDINATE VALIDATION
# ============================================================================

def validate_gps_coordinates(lat: float, lon: float) -> Tuple[bool, Optional[str]]:
    """
    Validate GPS coordinates
    
    Args:
        lat: Latitude value
        lon: Longitude value
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    try:
        lat = float(lat)
        lon = float(lon)
        
        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90 degrees"
        
        if not (-180 <= lon <= 180):
            return False, "Longitude must be between -180 and 180 degrees"
        
        # Check for obviously invalid coordinates (0, 0) - Gulf of Guinea
        if lat == 0 and lon == 0:
            return False, "Invalid coordinates: (0, 0) is not a valid location"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, "Invalid coordinate format - must be numeric values"


def validate_geofence_radius(radius: float) -> Tuple[bool, Optional[str]]:
    """
    Validate geofence radius
    
    Args:
        radius: Geofence radius in meters
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    try:
        radius = float(radius)
        
        if radius < 10:
            return False, "Geofence radius must be at least 10 meters"
        
        if radius > 500:
            return False, "Geofence radius cannot exceed 500 meters"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, "Invalid radius format - must be a numeric value"


# ============================================================================
# MAC ADDRESS VALIDATION
# ============================================================================

def validate_mac_address(mac: str) -> Tuple[bool, Optional[str]]:
    """
    Validate MAC address format
    Supports formats: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
    
    Args:
        mac: MAC address string
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not mac:
        return False, "MAC address is required"
    
    # Pattern for MAC address (supports : or - separators)
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    
    if re.match(pattern, mac):
        return True, None
    
    return False, "Invalid MAC address format. Expected format: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX"


def normalize_mac_address(mac: str) -> str:
    """
    Normalize MAC address to uppercase with colon separators
    
    Args:
        mac: MAC address string
        
    Returns:
        Normalized MAC address
    """
    # Remove all separators and convert to uppercase
    mac_clean = mac.replace(':', '').replace('-', '').upper()
    
    # Add colon separators
    return ':'.join([mac_clean[i:i+2] for i in range(0, 12, 2)])


# ============================================================================
# BLUETOOTH BEACON VALIDATION
# ============================================================================

def validate_beacon_uuid(uuid: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Bluetooth beacon UUID format (iBeacon standard)
    
    Args:
        uuid: Beacon UUID string
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not uuid:
        return False, "Beacon UUID is required"
    
    # Pattern for UUID (8-4-4-4-12 format)
    pattern = r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$'
    
    if re.match(pattern, uuid):
        return True, None
    
    return False, "Invalid UUID format. Expected format: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"


def validate_beacon_major_minor(major: int, minor: int) -> Tuple[bool, Optional[str]]:
    """
    Validate beacon major and minor values
    
    Args:
        major: Beacon major value (0-65535)
        minor: Beacon minor value (0-65535)
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    try:
        major = int(major)
        minor = int(minor)
        
        if not (0 <= major <= 65535):
            return False, "Beacon major value must be between 0 and 65535"
        
        if not (0 <= minor <= 65535):
            return False, "Beacon minor value must be between 0 and 65535"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, "Invalid major/minor format - must be integer values"


def normalize_beacon_uuid(uuid: str) -> str:
    """
    Normalize beacon UUID to uppercase
    
    Args:
        uuid: Beacon UUID string
        
    Returns:
        Normalized UUID
    """
    return uuid.upper()


# ============================================================================
# WI-FI VALIDATION
# ============================================================================

def validate_ssid(ssid: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Wi-Fi SSID
    
    Args:
        ssid: Wi-Fi SSID string
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not ssid:
        return False, "SSID is required"
    
    ssid_length = len(ssid)
    
    if ssid_length < 1:
        return False, "SSID must be at least 1 character"
    
    if ssid_length > 32:
        return False, "SSID cannot exceed 32 characters (IEEE 802.11 standard)"
    
    return True, None


def validate_bssid(bssid: str) -> Tuple[bool, Optional[str]]:
    """
    Validate BSSID (Basic Service Set Identifier - MAC address of access point)
    
    Args:
        bssid: BSSID string
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    return validate_mac_address(bssid)


# ============================================================================
# CLASSROOM VALIDATION
# ============================================================================

def validate_room_number(room_number: str) -> Tuple[bool, Optional[str]]:
    """
    Validate classroom room number
    
    Args:
        room_number: Room number string
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not room_number:
        return False, "Room number is required"
    
    if len(room_number) > 20:
        return False, "Room number cannot exceed 20 characters"
    
    # Allow alphanumeric, hyphens, and spaces
    if not re.match(r'^[A-Za-z0-9\s\-]+$', room_number):
        return False, "Room number can only contain letters, numbers, spaces, and hyphens"
    
    return True, None


def validate_building_name(building_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate building name
    
    Args:
        building_name: Building name string
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not building_name:
        return False, "Building name is required"
    
    if len(building_name) > 100:
        return False, "Building name cannot exceed 100 characters"
    
    return True, None


def validate_capacity(capacity: int) -> Tuple[bool, Optional[str]]:
    """
    Validate classroom capacity
    
    Args:
        capacity: Classroom capacity
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    try:
        capacity = int(capacity)
        
        if capacity < 1:
            return False, "Classroom capacity must be at least 1"
        
        if capacity > 1000:
            return False, "Classroom capacity cannot exceed 1000"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, "Invalid capacity format - must be an integer"


# ============================================================================
# STUDENT VALIDATION
# ============================================================================

def validate_student_code(student_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate student code format
    
    Args:
        student_code: Student code string
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not student_code:
        return False, "Student code is required"
    
    if len(student_code) > 20:
        return False, "Student code cannot exceed 20 characters"
    
    # Allow alphanumeric and hyphens
    if not re.match(r'^[A-Za-z0-9\-]+$', student_code):
        return False, "Student code can only contain letters, numbers, and hyphens"
    
    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address format
    
    Args:
        email: Email address string
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not email:
        return False, "Email is required"
    
    # Basic email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 100:
        return False, "Email cannot exceed 100 characters"
    
    return True, None


def validate_phone_number(phone_number: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format
    
    Args:
        phone_number: Phone number string
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not phone_number:
        return False, "Phone number is required"
    
    # Remove common separators for validation
    phone_clean = phone_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Allow + for international format
    if phone_clean.startswith('+'):
        phone_clean = phone_clean[1:]
    
    if not phone_clean.isdigit():
        return False, "Phone number can only contain digits and optional + prefix"
    
    if len(phone_clean) < 10:
        return False, "Phone number must be at least 10 digits"
    
    if len(phone_clean) > 15:
        return False, "Phone number cannot exceed 15 digits"
    
    return True, None


def validate_year_of_study(year: int) -> Tuple[bool, Optional[str]]:
    """
    Validate year of study
    
    Args:
        year: Year of study
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    try:
        year = int(year)
        
        if year < 1:
            return False, "Year of study must be at least 1"
        
        if year > 10:
            return False, "Year of study cannot exceed 10"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, "Invalid year format - must be an integer"


# ============================================================================
# FACULTY VALIDATION
# ============================================================================

def validate_faculty_code(faculty_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate faculty code format
    
    Args:
        faculty_code: Faculty code string
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not faculty_code:
        return False, "Faculty code is required"
    
    if len(faculty_code) > 20:
        return False, "Faculty code cannot exceed 20 characters"
    
    # Allow alphanumeric and hyphens
    if not re.match(r'^[A-Za-z0-9\-]+$', faculty_code):
        return False, "Faculty code can only contain letters, numbers, and hyphens"
    
    return True, None


def validate_department(department: str) -> Tuple[bool, Optional[str]]:
    """
    Validate department name
    
    Args:
        department: Department name string
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not department:
        return False, "Department is required"
    
    if len(department) > 100:
        return False, "Department name cannot exceed 100 characters"
    
    return True, None


# ============================================================================
# COMPOSITE VALIDATION
# ============================================================================

def validate_classroom_registration(data: dict) -> Tuple[bool, list]:
    """
    Validate complete classroom registration data
    
    Args:
        data: Dictionary containing classroom registration data
        
    Returns:
        Tuple of (is_valid: bool, errors: list)
    """
    errors = []
    
    # Validate required fields
    if 'room_number' in data:
        valid, error = validate_room_number(data['room_number'])
        if not valid:
            errors.append(error)
    else:
        errors.append("room_number is required")
    
    if 'building_name' in data:
        valid, error = validate_building_name(data['building_name'])
        if not valid:
            errors.append(error)
    else:
        errors.append("building_name is required")
    
    if 'capacity' in data:
        valid, error = validate_capacity(data['capacity'])
        if not valid:
            errors.append(error)
    
    # Validate GPS coordinates if provided
    if 'latitude' in data and 'longitude' in data:
        valid, error = validate_gps_coordinates(data['latitude'], data['longitude'])
        if not valid:
            errors.append(error)
    
    # Validate geofence radius if provided
    if 'geofence_radius' in data:
        valid, error = validate_geofence_radius(data['geofence_radius'])
        if not valid:
            errors.append(error)
    
    # Validate Wi-Fi data if provided
    if 'wifi' in data and isinstance(data['wifi'], dict):
        wifi = data['wifi']
        
        if 'ssid' in wifi:
            valid, error = validate_ssid(wifi['ssid'])
            if not valid:
                errors.append(f"Wi-Fi SSID: {error}")
        
        if 'bssid' in wifi:
            valid, error = validate_bssid(wifi['bssid'])
            if not valid:
                errors.append(f"Wi-Fi BSSID: {error}")
    
    # Validate Bluetooth beacon data if provided
    if 'bluetooth_beacon' in data and isinstance(data['bluetooth_beacon'], dict):
        beacon = data['bluetooth_beacon']
        
        if 'beacon_uuid' in beacon:
            valid, error = validate_beacon_uuid(beacon['beacon_uuid'])
            if not valid:
                errors.append(f"Beacon UUID: {error}")
        
        if 'major' in beacon and 'minor' in beacon:
            valid, error = validate_beacon_major_minor(beacon['major'], beacon['minor'])
            if not valid:
                errors.append(f"Beacon Major/Minor: {error}")
    
    return len(errors) == 0, errors


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def sanitize_string(value: str, max_length: int = None) -> str:
    """
    Sanitize string input by removing dangerous characters
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Apply max length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_json_field(data: dict, field: str, required: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate that a JSON field exists and is properly formatted
    
    Args:
        data: Dictionary to check
        field: Field name
        required: Whether the field is required
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if field not in data:
        if required:
            return False, f"Field '{field}' is required"
        return True, None
    
    value = data[field]
    
    # Check for null values
    if value is None and required:
        return False, f"Field '{field}' cannot be null"
    
    return True, None
