-- INTELLIATTEND Database Schema
-- MySQL Database Setup Script

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS IntelliAttend_Database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE IntelliAttend_Database;

-- Enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- 1. FACULTY TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_code VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_faculty_code (faculty_code),
    INDEX idx_faculty_email (email),
    INDEX idx_faculty_phone (phone_number)
);

-- ============================================================================
-- 2. STUDENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    student_code VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(15),
    year_of_study INT CHECK (year_of_study BETWEEN 1 AND 4),
    program VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_student_code (student_code),
    INDEX idx_student_email (email),
    INDEX idx_student_program (program)
);

-- ============================================================================
-- 3. CLASSROOMS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS classrooms (
    classroom_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(20) UNIQUE NOT NULL,
    building_name VARCHAR(100) NOT NULL,
    floor_number INT,
    capacity INT DEFAULT 50,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    geofence_radius DECIMAL(8, 2) DEFAULT 50.00,
    bluetooth_beacon_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_room_number (room_number),
    INDEX idx_building (building_name),
    INDEX idx_coordinates (latitude, longitude)
);

-- ============================================================================
-- 4. CLASSES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    class_code VARCHAR(20) UNIQUE NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    faculty_id INT NOT NULL,
    classroom_id INT,
    semester VARCHAR(20) NOT NULL,
    academic_year VARCHAR(9) NOT NULL, -- Format: 2024-2025
    credits INT DEFAULT 3,
    max_students INT DEFAULT 60,
    schedule_day ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
    start_time TIME,
    end_time TIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id) ON DELETE SET NULL,
    
    INDEX idx_class_code (class_code),
    INDEX idx_faculty_id (faculty_id),
    INDEX idx_classroom_id (classroom_id),
    INDEX idx_schedule (schedule_day, start_time),
    INDEX idx_semester_year (semester, academic_year)
);

-- ============================================================================
-- 5. STUDENT_CLASS_ENROLLMENTS TABLE (Many-to-Many)
-- ============================================================================
CREATE TABLE IF NOT EXISTS student_class_enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    enrollment_date DATE DEFAULT (CURRENT_DATE),
    status ENUM('enrolled', 'dropped', 'completed') DEFAULT 'enrolled',
    final_grade VARCHAR(5),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_student_class (student_id, class_id),
    INDEX idx_student_id (student_id),
    INDEX idx_class_id (class_id),
    INDEX idx_enrollment_status (status)
);

-- ============================================================================
-- 6. ATTENDANCE_SESSIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS attendance_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    faculty_id INT NOT NULL,
    session_date DATE DEFAULT (CURRENT_DATE),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    qr_token VARCHAR(255) UNIQUE,
    qr_secret_key VARCHAR(255),
    qr_expires_at TIMESTAMP,
    otp_used VARCHAR(10),
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    total_students_enrolled INT DEFAULT 0,
    total_students_present INT DEFAULT 0,
    attendance_percentage DECIMAL(5, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    
    INDEX idx_class_id (class_id),
    INDEX idx_faculty_id (faculty_id),
    INDEX idx_session_date (session_date),
    INDEX idx_qr_token (qr_token),
    INDEX idx_status (status)
);

-- ============================================================================
-- 7. ATTENDANCE_RECORDS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS attendance_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    student_id INT NOT NULL,
    scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    biometric_verified BOOLEAN DEFAULT FALSE,
    location_verified BOOLEAN DEFAULT FALSE,
    bluetooth_verified BOOLEAN DEFAULT FALSE,
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(11, 8),
    gps_accuracy DECIMAL(8, 2),
    bluetooth_rssi INT,
    device_info JSON,
    verification_score DECIMAL(3, 2) DEFAULT 0.00, -- 0.00 to 1.00
    status ENUM('present', 'late', 'absent', 'invalid') DEFAULT 'present',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_session_student (session_id, student_id),
    INDEX idx_session_id (session_id),
    INDEX idx_student_id (student_id),
    INDEX idx_scan_timestamp (scan_timestamp),
    INDEX idx_status (status),
    INDEX idx_verification_score (verification_score)
);

-- ============================================================================
-- 8. OTP_LOGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS otp_logs (
    otp_id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    otp_code VARCHAR(10) NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP NULL,
    session_id INT,
    is_used BOOLEAN DEFAULT FALSE,
    attempts INT DEFAULT 0,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id) ON DELETE SET NULL,
    
    INDEX idx_faculty_id (faculty_id),
    INDEX idx_otp_code (otp_code),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_used (is_used)
);

-- ============================================================================
-- 9. STUDENT_DEVICES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS student_devices (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    device_uuid VARCHAR(255) UNIQUE NOT NULL,
    device_name VARCHAR(100),
    device_type ENUM('android', 'ios', 'web') NOT NULL,
    device_model VARCHAR(100),
    os_version VARCHAR(50),
    app_version VARCHAR(20),
    fcm_token VARCHAR(255), -- For push notifications
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    biometric_enabled BOOLEAN DEFAULT FALSE,
    location_permission BOOLEAN DEFAULT FALSE,
    bluetooth_permission BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    
    INDEX idx_student_id (student_id),
    INDEX idx_device_uuid (device_uuid),
    INDEX idx_device_type (device_type),
    INDEX idx_last_seen (last_seen)
);

-- ============================================================================
-- 10. ATTENDANCE_SUMMARY TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS attendance_summary (
    summary_id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    student_id INT NOT NULL,
    total_sessions INT DEFAULT 0,
    attended_sessions INT DEFAULT 0,
    late_sessions INT DEFAULT 0,
    absent_sessions INT DEFAULT 0,
    attendance_percentage DECIMAL(5, 2) DEFAULT 0.00,
    first_attendance_date DATE,
    last_attendance_date DATE,
    semester VARCHAR(20),
    academic_year VARCHAR(9),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_class_student_semester (class_id, student_id, semester, academic_year),
    INDEX idx_class_id (class_id),
    INDEX idx_student_id (student_id),
    INDEX idx_attendance_percentage (attendance_percentage),
    INDEX idx_semester_year (semester, academic_year)
);

-- ============================================================================
-- 11. QR_TOKENS_LOG TABLE (for tracking QR code generation)
-- ============================================================================
CREATE TABLE IF NOT EXISTS qr_tokens_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    token_value VARCHAR(255) NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    scan_count INT DEFAULT 0,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id) ON DELETE CASCADE,
    
    INDEX idx_session_id (session_id),
    INDEX idx_token_value (token_value),
    INDEX idx_expires_at (expires_at),
    INDEX idx_generated_at (generated_at)
);

-- ============================================================================
-- 12. ADMINS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role ENUM('super_admin', 'admin', 'operator') DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Trigger to update attendance summary when new attendance record is added
DELIMITER //
CREATE TRIGGER update_attendance_summary_after_insert
AFTER INSERT ON attendance_records
FOR EACH ROW
BEGIN
    DECLARE class_id_val INT;
    DECLARE semester_val VARCHAR(20);
    DECLARE academic_year_val VARCHAR(9);
    
    -- Get class info
    SELECT c.class_id, c.semester, c.academic_year 
    INTO class_id_val, semester_val, academic_year_val
    FROM classes c
    INNER JOIN attendance_sessions s ON c.class_id = s.class_id
    WHERE s.session_id = NEW.session_id;
    
    -- Insert or update attendance summary
    INSERT INTO attendance_summary (
        class_id, student_id, total_sessions, attended_sessions, late_sessions, 
        absent_sessions, attendance_percentage, first_attendance_date, 
        last_attendance_date, semester, academic_year
    )
    VALUES (
        class_id_val, NEW.student_id, 1, 
        CASE WHEN NEW.status = 'present' THEN 1 ELSE 0 END,
        CASE WHEN NEW.status = 'late' THEN 1 ELSE 0 END,
        CASE WHEN NEW.status = 'absent' THEN 1 ELSE 0 END,
        CASE WHEN NEW.status = 'present' THEN 100.00 ELSE 0.00 END,
        DATE(NEW.scan_timestamp), DATE(NEW.scan_timestamp),
        semester_val, academic_year_val
    )
    ON DUPLICATE KEY UPDATE
        total_sessions = total_sessions + 1,
        attended_sessions = attended_sessions + CASE WHEN NEW.status = 'present' THEN 1 ELSE 0 END,
        late_sessions = late_sessions + CASE WHEN NEW.status = 'late' THEN 1 ELSE 0 END,
        absent_sessions = absent_sessions + CASE WHEN NEW.status = 'absent' THEN 1 ELSE 0 END,
        attendance_percentage = (attended_sessions / total_sessions) * 100,
        last_attendance_date = DATE(NEW.scan_timestamp),
        updated_at = CURRENT_TIMESTAMP;
END//
DELIMITER ;

-- ============================================================================
-- SAMPLE DATA INSERTION
-- ============================================================================

-- Insert sample faculty
INSERT INTO faculty (faculty_code, first_name, last_name, email, phone_number, department, password_hash) VALUES
('FAC001', 'John', 'Smith', 'john.smith@university.edu', '+1234567890', 'Computer Science', '$2b$12$LQv3c1yqBwUVHdkuLM3uXeH6GS'), -- password: faculty123
('FAC002', 'Sarah', 'Johnson', 'sarah.johnson@university.edu', '+1234567891', 'Information Technology', '$2b$12$LQv3c1yqBwUVHdkuLM3uXeH6GS'),
('FAC003', 'Michael', 'Brown', 'michael.brown@university.edu', '+1234567892', 'Computer Science', '$2b$12$LQv3c1yqBwUVHdkuLM3uXeH6GS');

-- Insert sample students
INSERT INTO students (student_code, first_name, last_name, email, phone_number, year_of_study, program, password_hash) VALUES
('STU001', 'Alice', 'Williams', 'alice.williams@student.edu', '+1234567893', 2, 'Computer Science', '$2b$12$LQv3c1yqBwUVHdkuLM3uXeH6GS'), -- password: student123
('STU002', 'Bob', 'Davis', 'bob.davis@student.edu', '+1234567894', 2, 'Computer Science', '$2b$12$LQv3c1yqBwUVHdkuLM3uXeH6GS'),
('STU003', 'Charlie', 'Miller', 'charlie.miller@student.edu', '+1234567895', 3, 'Information Technology', '$2b$12$LQv3c1yqBwUVHdkuLM3uXeH6GS'),
('STU004', 'Diana', 'Wilson', 'diana.wilson@student.edu', '+1234567896', 1, 'Computer Science', '$2b$12$LQv3c1yqBwUVHdkuLM3uXeH6GS'),
('STU005', 'Eve', 'Moore', 'eve.moore@student.edu', '+1234567897', 2, 'Information Technology', '$2b$12$LQv3c1yqBwUVHdkuLM3uXeH6GS');

-- Insert sample classrooms
INSERT INTO classrooms (room_number, building_name, floor_number, capacity, latitude, longitude, geofence_radius, bluetooth_beacon_id) VALUES
('CS101', 'Computer Science Building', 1, 50, 40.7128, -74.0060, 50.00, 'BEACON_CS101'),
('CS102', 'Computer Science Building', 1, 40, 40.7129, -74.0061, 50.00, 'BEACON_CS102'),
('IT201', 'IT Building', 2, 60, 40.7130, -74.0062, 50.00, 'BEACON_IT201'),
('LAB301', 'Lab Building', 3, 30, 40.7131, -74.0063, 50.00, 'BEACON_LAB301');

-- Insert sample classes
INSERT INTO classes (class_code, class_name, faculty_id, classroom_id, semester, academic_year, credits, max_students, schedule_day, start_time, end_time) VALUES
('CS101', 'Introduction to Programming', 1, 1, 'Fall', '2024-2025', 3, 50, 'Monday', '09:00:00', '10:30:00'),
('CS201', 'Data Structures', 1, 2, 'Fall', '2024-2025', 4, 40, 'Wednesday', '11:00:00', '12:30:00'),
('IT301', 'Database Systems', 2, 3, 'Fall', '2024-2025', 3, 60, 'Friday', '14:00:00', '15:30:00'),
('CS301', 'Software Engineering', 3, 1, 'Fall', '2024-2025', 4, 45, 'Tuesday', '10:00:00', '11:30:00');

-- Insert sample enrollments
INSERT INTO student_class_enrollments (student_id, class_id, enrollment_date, status) VALUES
(1, 1, '2024-08-15', 'enrolled'),
(1, 2, '2024-08-15', 'enrolled'),
(2, 1, '2024-08-15', 'enrolled'),
(2, 3, '2024-08-15', 'enrolled'),
(3, 2, '2024-08-15', 'enrolled'),
(3, 3, '2024-08-15', 'enrolled'),
(4, 1, '2024-08-15', 'enrolled'),
(5, 3, '2024-08-15', 'enrolled');

-- Insert sample admin user (password: admin123)
INSERT INTO admins (username, email, password_hash, first_name, last_name, role, is_active) VALUES
('admin', 'admin@intelliattend.com', '$2b$12$LQv3c1yqBwUVHdkuLM3uXeH6GS', 'System', 'Administrator', 'super_admin', TRUE);

-- Show table status
SELECT 'Database setup completed successfully!' AS status;