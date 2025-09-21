-- ============================================================================
-- IntelliAttend Database Creation Script
-- Complete MySQL database structure for smart attendance management
-- ============================================================================

-- Drop existing database if exists
DROP DATABASE IF EXISTS IntelliAttend_DataBase;

-- Create database with UTF8MB4 support
CREATE DATABASE IntelliAttend_DataBase 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE IntelliAttend_DataBase;

-- ============================================================================
-- 1. FACULTY TABLE
-- ============================================================================
CREATE TABLE faculty (
    faculty_id INT PRIMARY KEY AUTO_INCREMENT,
    faculty_code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(15) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_faculty_code (faculty_code),
    INDEX idx_faculty_email (email),
    INDEX idx_faculty_department (department),
    INDEX idx_faculty_active (is_active)
);

-- ============================================================================
-- 2. STUDENTS TABLE
-- ============================================================================
CREATE TABLE students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    student_code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(15) NULL,
    year_of_study INT NULL,
    program VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_student_code (student_code),
    INDEX idx_student_email (email),
    INDEX idx_student_program (program),
    INDEX idx_student_year (year_of_study),
    INDEX idx_student_active (is_active)
);

-- ============================================================================
-- 3. CLASSROOMS TABLE
-- ============================================================================
CREATE TABLE classrooms (
    classroom_id INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(20) NOT NULL UNIQUE,
    building_name VARCHAR(100) NOT NULL,
    floor_number INT NULL,
    capacity INT DEFAULT 50,
    latitude DECIMAL(10,8) NULL COMMENT 'GPS latitude for geofencing',
    longitude DECIMAL(11,8) NULL COMMENT 'GPS longitude for geofencing',
    geofence_radius DECIMAL(8,2) DEFAULT 50.00 COMMENT 'Radius in meters',
    bluetooth_beacon_id VARCHAR(100) NULL COMMENT 'Bluetooth beacon identifier',
    wifi_ssid VARCHAR(100) NULL COMMENT 'Classroom WiFi network',
    wifi_bssid VARCHAR(17) NULL COMMENT 'WiFi MAC address',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_room_number (room_number),
    INDEX idx_building (building_name),
    INDEX idx_capacity (capacity),
    INDEX idx_location (latitude, longitude),
    INDEX idx_beacon (bluetooth_beacon_id),
    INDEX idx_active (is_active)
);

-- ============================================================================
-- 4. CLASSES TABLE
-- ============================================================================
CREATE TABLE classes (
    class_id INT PRIMARY KEY AUTO_INCREMENT,
    class_code VARCHAR(20) NOT NULL UNIQUE,
    class_name VARCHAR(100) NOT NULL,
    faculty_id INT NOT NULL,
    classroom_id INT NULL,
    semester VARCHAR(20) NOT NULL,
    academic_year VARCHAR(9) NOT NULL COMMENT 'Format: 2024-2025',
    credits INT DEFAULT 3,
    max_students INT DEFAULT 60,
    schedule_day ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NULL,
    start_time TIME NULL,
    end_time TIME NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id) ON DELETE SET NULL,
    
    INDEX idx_class_code (class_code),
    INDEX idx_faculty (faculty_id),
    INDEX idx_classroom (classroom_id),
    INDEX idx_semester (semester, academic_year),
    INDEX idx_schedule (schedule_day, start_time),
    INDEX idx_active (is_active)
);

-- ============================================================================
-- 5. STUDENT CLASS ENROLLMENTS TABLE
-- ============================================================================
CREATE TABLE student_class_enrollments (
    enrollment_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    enrollment_date DATE DEFAULT (CURRENT_DATE),
    status ENUM('enrolled','dropped','completed','withdrawn') DEFAULT 'enrolled',
    final_grade VARCHAR(5) NULL COMMENT 'A+, A, B+, B, etc.',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_enrollment (student_id, class_id),
    INDEX idx_student (student_id),
    INDEX idx_class (class_id),
    INDEX idx_status (status),
    INDEX idx_active (is_active)
);

-- ============================================================================
-- 6. STUDENT DEVICES TABLE
-- ============================================================================
CREATE TABLE student_devices (
    device_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    device_uuid VARCHAR(255) NOT NULL UNIQUE COMMENT 'Unique device identifier',
    device_name VARCHAR(100) NULL COMMENT 'User-friendly device name',
    device_type ENUM('android','ios','web') NOT NULL,
    device_model VARCHAR(100) NULL,
    os_version VARCHAR(50) NULL,
    app_version VARCHAR(20) NULL,
    fcm_token VARCHAR(255) NULL COMMENT 'Firebase push notification token',
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    biometric_enabled BOOLEAN DEFAULT FALSE,
    location_permission BOOLEAN DEFAULT FALSE,
    bluetooth_permission BOOLEAN DEFAULT FALSE,
    push_notification_enabled BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    
    INDEX idx_student (student_id),
    INDEX idx_uuid (device_uuid),
    INDEX idx_type (device_type),
    INDEX idx_last_seen (last_seen),
    INDEX idx_active (is_active),
    INDEX idx_permissions (biometric_enabled, location_permission, bluetooth_permission)
);

-- ============================================================================
-- 7. ATTENDANCE SESSIONS TABLE
-- ============================================================================
CREATE TABLE attendance_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    class_id INT NOT NULL,
    faculty_id INT NOT NULL,
    session_date DATE DEFAULT (CURRENT_DATE),
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NULL,
    qr_token VARCHAR(255) UNIQUE NULL COMMENT 'Base session token for QR generation',
    qr_secret_key VARCHAR(255) NULL COMMENT 'Secret key for QR validation',
    qr_expires_at DATETIME NULL COMMENT 'Session expiration time',
    otp_used VARCHAR(10) NULL COMMENT 'OTP code used to start session',
    status ENUM('active','completed','cancelled','expired') DEFAULT 'active',
    total_students_enrolled INT DEFAULT 0,
    total_students_present INT DEFAULT 0,
    attendance_percentage DECIMAL(5,2) DEFAULT 0.00,
    session_notes TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    
    INDEX idx_class (class_id),
    INDEX idx_faculty (faculty_id),
    INDEX idx_date (session_date),
    INDEX idx_status (status),
    INDEX idx_qr_token (qr_token),
    INDEX idx_expires (qr_expires_at)
);

-- ============================================================================
-- 8. ATTENDANCE RECORDS TABLE
-- ============================================================================
CREATE TABLE attendance_records (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    student_id INT NOT NULL,
    device_id INT NULL,
    scan_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    biometric_verified BOOLEAN DEFAULT FALSE,
    location_verified BOOLEAN DEFAULT FALSE,
    bluetooth_verified BOOLEAN DEFAULT FALSE,
    wifi_verified BOOLEAN DEFAULT FALSE,
    gps_latitude DECIMAL(10,8) NULL,
    gps_longitude DECIMAL(11,8) NULL,
    gps_accuracy DECIMAL(8,2) NULL COMMENT 'GPS accuracy in meters',
    gps_distance_from_classroom DECIMAL(8,2) NULL COMMENT 'Distance in meters',
    bluetooth_rssi INT NULL COMMENT 'Bluetooth signal strength',
    bluetooth_devices_detected JSON NULL COMMENT 'List of detected BLE devices',
    wifi_ssid VARCHAR(100) NULL,
    wifi_bssid VARCHAR(17) NULL,
    wifi_rssi INT NULL COMMENT 'WiFi signal strength',
    device_info JSON NULL COMMENT 'Device metadata',
    verification_score DECIMAL(3,2) DEFAULT 0.00 COMMENT 'Overall verification score 0-1',
    status ENUM('present','late','absent','invalid','suspicious') DEFAULT 'present',
    notes TEXT NULL,
    flagged_for_review BOOLEAN DEFAULT FALSE,
    reviewed_by INT NULL COMMENT 'Faculty ID who reviewed',
    reviewed_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES student_devices(device_id) ON DELETE SET NULL,
    FOREIGN KEY (reviewed_by) REFERENCES faculty(faculty_id) ON DELETE SET NULL,
    
    UNIQUE KEY unique_attendance (session_id, student_id),
    INDEX idx_session (session_id),
    INDEX idx_student (student_id),
    INDEX idx_timestamp (scan_timestamp),
    INDEX idx_status (status),
    INDEX idx_verification (verification_score),
    INDEX idx_location (gps_latitude, gps_longitude),
    INDEX idx_flagged (flagged_for_review),
    INDEX idx_reviewed (reviewed_by, reviewed_at)
);

-- ============================================================================
-- 9. OTP LOGS TABLE
-- ============================================================================
CREATE TABLE otp_logs (
    otp_id INT PRIMARY KEY AUTO_INCREMENT,
    faculty_id INT NOT NULL,
    otp_code VARCHAR(10) NOT NULL,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL,
    session_id INT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    attempts INT DEFAULT 0,
    ip_address VARCHAR(45) NULL COMMENT 'IPv4 or IPv6 address',
    user_agent TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id) ON DELETE SET NULL,
    
    INDEX idx_faculty (faculty_id),
    INDEX idx_otp_code (otp_code),
    INDEX idx_expires (expires_at),
    INDEX idx_used (is_used),
    INDEX idx_session (session_id)
);

-- ============================================================================
-- 10. QR TOKENS LOG TABLE
-- ============================================================================
CREATE TABLE qr_tokens_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    sequence_number INT NOT NULL COMMENT 'QR sequence in session',
    token_value VARCHAR(255) NOT NULL,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    scan_count INT DEFAULT 0,
    student_scans JSON NULL COMMENT 'Array of student scan attempts',
    ip_address VARCHAR(45) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id) ON DELETE CASCADE,
    
    INDEX idx_session (session_id),
    INDEX idx_token (token_value),
    INDEX idx_expires (expires_at),
    INDEX idx_sequence (session_id, sequence_number),
    INDEX idx_generated (generated_at)
);

-- ============================================================================
-- 11. ADMINS TABLE
-- ============================================================================
CREATE TABLE admins (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role ENUM('super_admin','admin','operator') DEFAULT 'admin',
    permissions JSON NULL COMMENT 'Custom permission settings',
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME NULL,
    login_attempts INT DEFAULT 0,
    locked_until DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_active (is_active)
);

-- ============================================================================
-- 12. SYSTEM LOGS TABLE
-- ============================================================================
CREATE TABLE system_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    log_level ENUM('DEBUG','INFO','WARNING','ERROR','CRITICAL') NOT NULL,
    category VARCHAR(50) NOT NULL COMMENT 'AUTH, QR, ATTENDANCE, SYSTEM, etc.',
    message TEXT NOT NULL,
    user_type ENUM('faculty','student','admin','system') NULL,
    user_id INT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    request_id VARCHAR(36) NULL COMMENT 'UUID for request tracking',
    session_id INT NULL,
    additional_data JSON NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_level (log_level),
    INDEX idx_category (category),
    INDEX idx_user (user_type, user_id),
    INDEX idx_created (created_at),
    INDEX idx_session (session_id),
    INDEX idx_request (request_id)
);

-- ============================================================================
-- 13. NOTIFICATIONS TABLE
-- ============================================================================
CREATE TABLE notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    recipient_type ENUM('faculty','student','admin','all') NOT NULL,
    recipient_id INT NULL COMMENT 'NULL for broadcast messages',
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('attendance','system','security','update','reminder') NOT NULL,
    priority ENUM('low','medium','high','urgent') DEFAULT 'medium',
    data JSON NULL COMMENT 'Additional notification data',
    scheduled_at DATETIME NULL,
    sent_at DATETIME NULL,
    read_at DATETIME NULL,
    status ENUM('pending','sent','delivered','failed','cancelled') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_recipient (recipient_type, recipient_id),
    INDEX idx_type (type),
    INDEX idx_priority (priority),
    INDEX idx_status (status),
    INDEX idx_scheduled (scheduled_at),
    INDEX idx_created (created_at)
);

-- ============================================================================
-- SAMPLE DATA INSERTION
-- ============================================================================

-- Insert sample faculty
INSERT INTO faculty (faculty_code, first_name, last_name, email, phone_number, department, password_hash) VALUES
('PROF001', 'John', 'Smith', 'john.smith@university.edu', '+1234567890', 'Computer Science', '$2b$12$KIXWvYc7QjR8Kf9ZA4gSj.VqI.XG0Vu.ZjJXOOJ5PVQ7Rx5Y6MeWi'),
('PROF002', 'Jane', 'Doe', 'jane.doe@university.edu', '+1234567891', 'Mathematics', '$2b$12$KIXWvYc7QjR8Kf9ZA4gSj.VqI.XG0Vu.ZjJXOOJ5PVQ7Rx5Y6MeWi');

-- Insert sample students
INSERT INTO students (student_code, first_name, last_name, email, phone_number, year_of_study, program, password_hash) VALUES
('STU2024001', 'Alice', 'Williams', 'alice.williams@student.edu', '+1987654321', 2, 'Computer Science', '$2b$12$KIXWvYc7QjR8Kf9ZA4gSj.VqI.XG0Vu.ZjJXOOJ5PVQ7Rx5Y6MeWi'),
('STU2024002', 'Bob', 'Johnson', 'bob.johnson@student.edu', '+1987654322', 2, 'Computer Science', '$2b$12$KIXWvYc7QjR8Kf9ZA4gSj.VqI.XG0Vu.ZjJXOOJ5PVQ7Rx5Y6MeWi'),
('STU2024003', 'Charlie', 'Brown', 'charlie.brown@student.edu', '+1987654323', 1, 'Engineering', '$2b$12$KIXWvYc7QjR8Kf9ZA4gSj.VqI.XG0Vu.ZjJXOOJ5PVQ7Rx5Y6MeWi');

-- Insert sample classrooms
INSERT INTO classrooms (room_number, building_name, floor_number, capacity, latitude, longitude, geofence_radius, bluetooth_beacon_id) VALUES
('CS101', 'Engineering Building', 1, 60, 40.712800, -74.006000, 30.00, 'BEACON_CS101'),
('MATH201', 'Science Building', 2, 40, 40.712900, -74.005900, 25.00, 'BEACON_MATH201'),
('LAB301', 'Technology Center', 3, 30, 40.712700, -74.006100, 20.00, 'BEACON_LAB301');

-- Insert sample classes
INSERT INTO classes (class_code, class_name, faculty_id, classroom_id, semester, academic_year, credits, schedule_day, start_time, end_time) VALUES
('CS101', 'Introduction to Computer Science', 1, 1, 'Fall', '2024-2025', 3, 'Monday', '09:00:00', '10:30:00'),
('MATH101', 'Calculus I', 2, 2, 'Fall', '2024-2025', 4, 'Wednesday', '14:00:00', '15:30:00'),
('CS102', 'Data Structures', 1, 3, 'Fall', '2024-2025', 3, 'Friday', '11:00:00', '12:30:00');

-- Insert sample enrollments
INSERT INTO student_class_enrollments (student_id, class_id, status) VALUES
(1, 1, 'enrolled'),
(1, 3, 'enrolled'),
(2, 1, 'enrolled'),
(2, 2, 'enrolled'),
(3, 1, 'enrolled'),
(3, 2, 'enrolled');

-- Insert admin user
INSERT INTO admins (username, email, password_hash, first_name, last_name, role) VALUES
('admin', 'admin@university.edu', '$2b$12$KIXWvYc7QjR8Kf9ZA4gSj.VqI.XG0Vu.ZjJXOOJ5PVQ7Rx5Y6MeWi', 'System', 'Administrator', 'super_admin');

-- Insert sample devices
INSERT INTO student_devices (student_id, device_uuid, device_name, device_type, device_model, os_version, biometric_enabled, location_permission, bluetooth_permission) VALUES
(1, 'DEVICE_001_ALICE', 'Alice iPhone', 'ios', 'iPhone 14', '17.0', TRUE, TRUE, TRUE),
(2, 'DEVICE_002_BOB', 'Bob Android', 'android', 'Samsung Galaxy S23', '14.0', TRUE, TRUE, TRUE),
(3, 'DEVICE_003_CHARLIE', 'Charlie Phone', 'android', 'Google Pixel 7', '13.0', FALSE, TRUE, TRUE);

-- ============================================================================
-- DATABASE VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active classes with enrollment count
CREATE VIEW view_active_classes AS
SELECT 
    c.class_id,
    c.class_code,
    c.class_name,
    CONCAT(f.first_name, ' ', f.last_name) as faculty_name,
    f.email as faculty_email,
    cr.room_number,
    cr.building_name,
    COUNT(e.student_id) as enrolled_students,
    c.max_students,
    c.schedule_day,
    c.start_time,
    c.end_time
FROM classes c
LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
LEFT JOIN classrooms cr ON c.classroom_id = cr.classroom_id
LEFT JOIN student_class_enrollments e ON c.class_id = e.class_id AND e.is_active = TRUE
WHERE c.is_active = TRUE
GROUP BY c.class_id;

-- Attendance summary view
CREATE VIEW view_attendance_summary AS
SELECT 
    s.session_id,
    s.session_date,
    c.class_code,
    c.class_name,
    CONCAT(f.first_name, ' ', f.last_name) as faculty_name,
    COUNT(ar.record_id) as total_attended,
    s.total_students_enrolled,
    s.attendance_percentage,
    s.status as session_status,
    s.start_time,
    s.end_time
FROM attendance_sessions s
LEFT JOIN classes c ON s.class_id = c.class_id
LEFT JOIN faculty f ON s.faculty_id = f.faculty_id
LEFT JOIN attendance_records ar ON s.session_id = ar.session_id AND ar.status = 'present'
GROUP BY s.session_id
ORDER BY s.session_date DESC;

-- Student performance view
CREATE VIEW view_student_performance AS
SELECT 
    s.student_id,
    CONCAT(s.first_name, ' ', s.last_name) as student_name,
    s.student_code,
    s.program,
    COUNT(DISTINCT e.class_id) as enrolled_classes,
    COUNT(ar.record_id) as total_attendance,
    AVG(ar.verification_score) as avg_verification_score,
    COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_count,
    COUNT(CASE WHEN ar.flagged_for_review = TRUE THEN 1 END) as flagged_count
FROM students s
LEFT JOIN student_class_enrollments e ON s.student_id = e.student_id AND e.is_active = TRUE
LEFT JOIN attendance_records ar ON s.student_id = ar.student_id
WHERE s.is_active = TRUE
GROUP BY s.student_id;

COMMIT;

-- ============================================================================
-- SETUP COMPLETE MESSAGE
-- ============================================================================
SELECT 'IntelliAttend database setup completed successfully!' as message;