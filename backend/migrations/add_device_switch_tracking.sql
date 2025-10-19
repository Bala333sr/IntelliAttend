-- ============================================================================
-- IntelliAttend - Device Switch Tracking
-- Implements PhonePe-style single active device enforcement
-- ============================================================================

-- Device Switch Requests Table
CREATE TABLE IF NOT EXISTS device_switch_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    old_device_uuid VARCHAR(255) COMMENT 'Previous active device',
    new_device_uuid VARCHAR(255) NOT NULL COMMENT 'Device requesting to become active',
    new_device_info JSON COMMENT 'New device details',
    request_reason ENUM('device_upgrade', 'device_lost', 'device_stolen', 'manual_switch') DEFAULT 'manual_switch',
    status ENUM('pending', 'approved', 'rejected', 'expired') DEFAULT 'pending',
    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME COMMENT 'When 48-hour cooldown completes',
    expires_at DATETIME COMMENT 'Auto-expire after 7 days if not completed',
    completed_at DATETIME,
    ip_address VARCHAR(45),
    wifi_ssid VARCHAR(100) COMMENT 'Wi-Fi network used for request',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    
    INDEX idx_student_id (student_id),
    INDEX idx_status (status),
    INDEX idx_requested_at (requested_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tracks device switch requests with 48-hour cooldown period';

-- Device Activity Log Table (for security monitoring)
CREATE TABLE IF NOT EXISTS device_activity_log (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    device_uuid VARCHAR(255) NOT NULL,
    activity_type ENUM('login', 'logout', 'attendance_scan', 'device_activated', 'device_deactivated', 'failed_login') NOT NULL,
    ip_address VARCHAR(45),
    location_lat DECIMAL(10, 8),
    location_lon DECIMAL(11, 8),
    wifi_ssid VARCHAR(100),
    additional_info JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    
    INDEX idx_student_device (student_id, device_uuid),
    INDEX idx_timestamp (timestamp),
    INDEX idx_activity_type (activity_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Logs all device activities for security monitoring';

-- Add new columns to student_devices table for single device enforcement
ALTER TABLE student_devices 
ADD COLUMN IF NOT EXISTS is_primary_device BOOLEAN DEFAULT FALSE COMMENT 'Only one device can be primary',
ADD COLUMN IF NOT EXISTS activated_at DATETIME COMMENT 'When device became active',
ADD COLUMN IF NOT EXISTS deactivated_at DATETIME COMMENT 'When device was deactivated',
ADD COLUMN IF NOT EXISTS device_binding_expires_at DATETIME COMMENT 'Device binding expiry (48 hours from activation)',
ADD COLUMN IF NOT EXISTS switch_cooldown_until DATETIME COMMENT 'Cannot switch device until this time';

-- Create unique constraint to ensure only one active device per student
-- This will be enforced at application level with is_active flag

-- Verification Queries
-- SELECT * FROM device_switch_requests WHERE status = 'pending';
-- SELECT * FROM device_activity_log WHERE student_id = 1 ORDER BY timestamp DESC LIMIT 20;
-- SELECT * FROM student_devices WHERE student_id = 1 AND is_active = TRUE;
