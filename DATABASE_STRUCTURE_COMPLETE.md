# IntelliAttend - Complete MySQL Database Structure

## Overview
This document provides the complete MySQL database structure for the IntelliAttend smart attendance management system. The database is designed to handle multi-factor authentication, QR-based attendance tracking, geolocation verification, and comprehensive reporting.

## Database Configuration
- **Database Name**: `intelliattend_db`
- **Character Set**: `utf8mb4`
- **Collation**: `utf8mb4_unicode_ci`
- **Storage Engine**: InnoDB (for ACID compliance and foreign key support)

---

## Table Structure

### 1. Faculty Table (`faculty`)
**Purpose**: Stores faculty/instructor information

```sql
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
```

**Key Fields**:
- `faculty_id`: Primary key, auto-increment
- `faculty_code`: Unique identifier (e.g., "PROF001")
- `email`: Login credential, must be unique
- `password_hash`: Bcrypt hashed password
- `department`: Faculty department (CS, Math, etc.)
- `is_active`: Soft delete flag

**Sample Data**:
```sql
INSERT INTO faculty VALUES 
(1, 'PROF001', 'John', 'Smith', 'john.smith@university.edu', '+1234567890', 'Computer Science', '$2b$12$...', TRUE, NULL, NOW(), NOW());
```

---

### 2. Students Table (`students`)
**Purpose**: Stores student information

```sql
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
```

**Key Fields**:
- `student_id`: Primary key, auto-increment
- `student_code`: Unique identifier (e.g., "STU2024001")
- `program`: Academic program (Computer Science, Engineering, etc.)
- `year_of_study`: Academic year (1-4)
- `is_active`: Soft delete flag

**Sample Data**:
```sql
INSERT INTO students VALUES 
(1, 'STU2024001', 'Alice', 'Williams', 'alice.williams@student.edu', '+1987654321', 2, 'Computer Science', '$2b$12$...', TRUE, NULL, NOW(), NOW());
```

---

### 3. Classrooms Table (`classrooms`)
**Purpose**: Physical classroom locations with geofencing data

```sql
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
```

**Key Fields**:
- `latitude/longitude`: GPS coordinates for location verification
- `geofence_radius`: Allowed distance from classroom (meters)
- `bluetooth_beacon_id`: For Bluetooth proximity verification
- `wifi_ssid/wifi_bssid`: WiFi network identification

**Sample Data**:
```sql
INSERT INTO classrooms VALUES 
(1, 'CS101', 'Engineering Building', 1, 60, 40.7128, -74.0060, 30.00, 'BEACON_CS101', 'UniversityWiFi', '00:11:22:33:44:55', TRUE, NOW(), NOW());
```

---

### 4. Classes Table (`classes`)
**Purpose**: Academic classes/courses

```sql
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
```

**Key Fields**:
- `class_code`: Unique course identifier (e.g., "CS101")
- `semester`: Fall, Spring, Summer
- `academic_year`: Academic year span
- `schedule_day/start_time/end_time`: Class schedule

---

### 5. Student Class Enrollments (`student_class_enrollments`)
**Purpose**: Links students to classes (many-to-many relationship)

```sql
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
```

---

### 6. Student Devices Table (`student_devices`)
**Purpose**: Track student mobile devices for security and verification

```sql
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
```

**Key Fields**:
- `device_uuid`: Unique device fingerprint
- `biometric_enabled`: Device supports fingerprint/face unlock
- `location_permission`: GPS access granted
- `bluetooth_permission`: Bluetooth scanning allowed
- `fcm_token`: For push notifications

---

### 7. Attendance Sessions Table (`attendance_sessions`)
**Purpose**: Individual attendance taking sessions

```sql
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
```

**Key Fields**:
- `qr_token`: Base token for QR code generation
- `qr_secret_key`: Validates QR authenticity
- `qr_expires_at`: Session timeout
- `attendance_percentage`: Calculated attendance rate

---

### 8. Attendance Records Table (`attendance_records`)
**Purpose**: Individual student attendance records with verification data

```sql
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
```

**Key Features**:
- **Multi-factor Verification**: GPS, Bluetooth, WiFi, Biometric
- **Location Data**: Precise GPS coordinates and accuracy
- **Signal Strength**: RSSI values for proximity verification
- **Verification Score**: Calculated trust score (0.0-1.0)
- **Review System**: Flagging suspicious entries

---

### 9. OTP Logs Table (`otp_logs`)
**Purpose**: Track One-Time-Passwords for session security

```sql
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
```

---

### 10. QR Tokens Log Table (`qr_tokens_log`)
**Purpose**: Track QR token generation and usage

```sql
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
```

---

### 11. Admins Table (`admins`)
**Purpose**: System administrators

```sql
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
```

---

### 12. System Logs Table (`system_logs`)
**Purpose**: Audit trail and system monitoring

```sql
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
```

---

### 13. Notifications Table (`notifications`)
**Purpose**: Push notifications and alerts

```sql
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
```

---

## Database Relationships

### Primary Relationships
1. **Faculty → Classes**: One-to-Many (Faculty teaches multiple classes)
2. **Classes → Classrooms**: Many-to-One (Classes held in classrooms)
3. **Students ↔ Classes**: Many-to-Many (via `student_class_enrollments`)
4. **Students → Devices**: One-to-Many (Student has multiple devices)
5. **Classes → Sessions**: One-to-Many (Class has multiple attendance sessions)
6. **Sessions → Records**: One-to-Many (Session has multiple attendance records)

### Key Constraints
- **Unique Enrollments**: Student can only enroll once per class
- **Unique Attendance**: Student can mark attendance once per session
- **Device Registration**: Device UUID must be unique across system
- **Token Security**: QR tokens must be unique and time-limited

---

## Indexes and Performance Optimization

### Critical Indexes
```sql
-- Performance indexes for common queries
CREATE INDEX idx_attendance_lookup ON attendance_records (session_id, student_id, scan_timestamp);
CREATE INDEX idx_session_active ON attendance_sessions (status, qr_expires_at);
CREATE INDEX idx_student_enrollment ON student_class_enrollments (student_id, status, is_active);
CREATE INDEX idx_device_active ON student_devices (student_id, is_active, last_seen);
CREATE INDEX idx_location_search ON classrooms (latitude, longitude, is_active);
```

### Composite Indexes for Complex Queries
```sql
-- For attendance reporting
CREATE INDEX idx_attendance_report ON attendance_records (session_id, status, scan_timestamp);

-- For QR token validation
CREATE INDEX idx_qr_validation ON qr_tokens_log (token_value, expires_at, is_used);

-- For geolocation queries
CREATE INDEX idx_gps_verification ON attendance_records (gps_latitude, gps_longitude, location_verified);
```

---

## Database Views for Common Queries

### 1. Active Classes View
```sql
CREATE VIEW view_active_classes AS
SELECT 
    c.class_id,
    c.class_code,
    c.class_name,
    CONCAT(f.first_name, ' ', f.last_name) as faculty_name,
    f.email as faculty_email,
    cr.room_number,
    cr.building_name,
    COUNT(e.student_id) as enrolled_students
FROM classes c
LEFT JOIN faculty f ON c.faculty_id = f.faculty_id
LEFT JOIN classrooms cr ON c.classroom_id = cr.classroom_id
LEFT JOIN student_class_enrollments e ON c.class_id = e.class_id AND e.is_active = TRUE
WHERE c.is_active = TRUE
GROUP BY c.class_id;
```

### 2. Attendance Summary View
```sql
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
    s.status as session_status
FROM attendance_sessions s
LEFT JOIN classes c ON s.class_id = c.class_id
LEFT JOIN faculty f ON s.faculty_id = f.faculty_id
LEFT JOIN attendance_records ar ON s.session_id = ar.session_id AND ar.status = 'present'
GROUP BY s.session_id
ORDER BY s.session_date DESC;
```

---

## Database Security and Best Practices

### 1. Security Measures
- **Password Hashing**: All passwords stored with bcrypt
- **SQL Injection Prevention**: Prepared statements only
- **Data Encryption**: Sensitive data encrypted at rest
- **Access Control**: Role-based permissions
- **Audit Logging**: All actions logged with timestamps

### 2. Backup Strategy
```sql
-- Daily backup command
mysqldump --single-transaction --routines --triggers intelliattend_db > backup_$(date +%Y%m%d).sql

-- Point-in-time recovery setup
-- Enable binary logging in my.cnf:
-- log-bin=mysql-bin
-- server-id=1
```

### 3. Maintenance Scripts
```sql
-- Clean old QR tokens (older than 24 hours)
DELETE FROM qr_tokens_log WHERE created_at < DATE_SUB(NOW(), INTERVAL 24 HOUR);

-- Archive old attendance sessions (older than 1 year)
INSERT INTO attendance_sessions_archive SELECT * FROM attendance_sessions 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);

-- Update attendance percentages
UPDATE attendance_sessions s 
SET attendance_percentage = (
    SELECT (COUNT(ar.record_id) * 100.0 / s.total_students_enrolled)
    FROM attendance_records ar 
    WHERE ar.session_id = s.session_id AND ar.status = 'present'
) WHERE s.status = 'completed';
```

---

## Configuration Requirements

### MySQL Settings (`my.cnf`)
```ini
[mysqld]
# Character set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Performance
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
max_connections = 500

# Logging
log-bin = mysql-bin
server-id = 1
expire_logs_days = 7

# JSON support
innodb_strict_mode = ON
```

### Application Connection
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'intelliattend_user',
    'password': 'secure_password_here',
    'database': 'intelliattend_db',
    'charset': 'utf8mb4',
    'autocommit': False,
    'pool_size': 20,
    'pool_recycle': 3600
}
```

---

## Sample Data Population

### Quick Setup Script
```sql
-- Create sample faculty
INSERT INTO faculty (faculty_code, first_name, last_name, email, phone_number, department, password_hash) VALUES
('PROF001', 'John', 'Smith', 'john.smith@university.edu', '+1234567890', 'Computer Science', '$2b$12$hash_here'),
('PROF002', 'Jane', 'Doe', 'jane.doe@university.edu', '+1234567891', 'Mathematics', '$2b$12$hash_here');

-- Create sample students  
INSERT INTO students (student_code, first_name, last_name, email, program, password_hash) VALUES
('STU2024001', 'Alice', 'Williams', 'alice.williams@student.edu', 'Computer Science', '$2b$12$hash_here'),
('STU2024002', 'Bob', 'Johnson', 'bob.johnson@student.edu', 'Computer Science', '$2b$12$hash_here');

-- Create sample classroom
INSERT INTO classrooms (room_number, building_name, capacity, latitude, longitude, geofence_radius) VALUES
('CS101', 'Engineering Building', 60, 40.7128, -74.0060, 30.00);

-- Create sample class
INSERT INTO classes (class_code, class_name, faculty_id, classroom_id, semester, academic_year) VALUES
('CS101', 'Introduction to Computer Science', 1, 1, 'Fall', '2024-2025');

-- Enroll students in class
INSERT INTO student_class_enrollments (student_id, class_id) VALUES (1, 1), (2, 1);
```

This database structure provides:
- **Scalability**: Supports thousands of students and classes
- **Security**: Multi-layer authentication and verification
- **Performance**: Optimized indexes for fast queries
- **Flexibility**: JSON fields for extensible data
- **Reliability**: ACID compliance and data integrity
- **Auditability**: Complete logging and tracking
- **Maintainability**: Well-structured relationships and constraints

The structure is designed to handle the complex requirements of a modern attendance system while maintaining data integrity and performance.