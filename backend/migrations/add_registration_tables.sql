-- ============================================================================
-- IntelliAttend Registration System - Database Migration
-- Creates new tables for Wi-Fi networks, Bluetooth beacons, audit logging,
-- and approval queues
-- ============================================================================

-- Wi-Fi Networks Table
CREATE TABLE IF NOT EXISTS wifi_networks (
    wifi_id INT AUTO_INCREMENT PRIMARY KEY,
    classroom_id INT NOT NULL,
    ssid VARCHAR(32) NOT NULL,
    bssid VARCHAR(17) NOT NULL UNIQUE COMMENT 'MAC address format XX:XX:XX:XX:XX:XX',
    security_type ENUM('Open', 'WEP', 'WPA', 'WPA2', 'WPA3') DEFAULT 'WPA2',
    is_active BOOLEAN DEFAULT TRUE,
    registered_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id) ON DELETE CASCADE,
    FOREIGN KEY (registered_by) REFERENCES admins(admin_id) ON DELETE SET NULL,
    
    INDEX idx_classroom_id (classroom_id),
    INDEX idx_bssid (bssid),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Wi-Fi network information for classroom location verification';

-- Bluetooth Beacons Table
CREATE TABLE IF NOT EXISTS bluetooth_beacons (
    beacon_id INT AUTO_INCREMENT PRIMARY KEY,
    classroom_id INT NOT NULL,
    beacon_uuid VARCHAR(36) NOT NULL COMMENT 'UUID format: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
    major INT NOT NULL COMMENT 'Beacon major value (0-65535)',
    minor INT NOT NULL COMMENT 'Beacon minor value (0-65535)',
    mac_address VARCHAR(17) COMMENT 'Beacon MAC address',
    expected_rssi INT DEFAULT -75 COMMENT 'Expected signal strength at classroom entrance',
    is_active BOOLEAN DEFAULT TRUE,
    registered_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id) ON DELETE CASCADE,
    FOREIGN KEY (registered_by) REFERENCES admins(admin_id) ON DELETE SET NULL,
    
    UNIQUE KEY uix_beacon_unique (beacon_uuid, major, minor),
    INDEX idx_classroom_id (classroom_id),
    INDEX idx_beacon_uuid (beacon_uuid),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bluetooth beacon information for classroom proximity verification';

-- Registration Audit Log Table
CREATE TABLE IF NOT EXISTS registration_audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    action ENUM('create', 'update', 'delete', 'approve', 'reject') NOT NULL,
    resource_type ENUM('classroom', 'student', 'faculty', 'device', 'wifi', 'beacon') NOT NULL,
    resource_id INT NOT NULL COMMENT 'ID of the affected resource',
    admin_id INT NOT NULL,
    admin_username VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45) COMMENT 'Supports both IPv4 and IPv6',
    user_agent TEXT,
    details JSON COMMENT 'Additional context about the action',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    FOREIGN KEY (admin_id) REFERENCES admins(admin_id) ON DELETE CASCADE,
    
    INDEX idx_admin_id (admin_id),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_action (action),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Audit log for all registration and administrative actions';

-- Device Approval Queue Table
CREATE TABLE IF NOT EXISTS device_approval_queue (
    queue_id INT AUTO_INCREMENT PRIMARY KEY,
    device_uuid VARCHAR(255) NOT NULL UNIQUE,
    student_id INT NOT NULL,
    device_info JSON COMMENT 'Device details (model, OS, etc.)',
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    reviewed_by INT,
    review_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES admins(admin_id) ON DELETE SET NULL,
    
    INDEX idx_student_id (student_id),
    INDEX idx_status (status),
    INDEX idx_submitted_at (submitted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Queue for pending device registrations requiring approval';

-- Student Registration Queue Table
CREATE TABLE IF NOT EXISTS student_registration_queue (
    queue_id INT AUTO_INCREMENT PRIMARY KEY,
    student_code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(15),
    program VARCHAR(100) NOT NULL,
    year_of_study INT,
    password_hash VARCHAR(255) NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    reviewed_by INT,
    approval_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (reviewed_by) REFERENCES admins(admin_id) ON DELETE SET NULL,
    
    INDEX idx_email (email),
    INDEX idx_student_code (student_code),
    INDEX idx_status (status),
    INDEX idx_submitted_at (submitted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Queue for pending student self-registrations requiring approval';

-- ============================================================================
-- Verification Queries
-- Run these after migration to verify table creation
-- ============================================================================

-- Verify all tables exist
-- SELECT TABLE_NAME, TABLE_COMMENT 
-- FROM INFORMATION_SCHEMA.TABLES 
-- WHERE TABLE_SCHEMA = DATABASE() 
-- AND TABLE_NAME IN (
--     'wifi_networks', 
--     'bluetooth_beacons', 
--     'registration_audit_log', 
--     'device_approval_queue', 
--     'student_registration_queue'
-- );

-- Verify table structures
-- DESCRIBE wifi_networks;
-- DESCRIBE bluetooth_beacons;
-- DESCRIBE registration_audit_log;
-- DESCRIBE device_approval_queue;
-- DESCRIBE student_registration_queue;

-- ============================================================================
-- Rollback Script (if needed)
-- ============================================================================

-- DROP TABLE IF EXISTS student_registration_queue;
-- DROP TABLE IF EXISTS device_approval_queue;
-- DROP TABLE IF EXISTS registration_audit_log;
-- DROP TABLE IF EXISTS bluetooth_beacons;
-- DROP TABLE IF EXISTS wifi_networks;
