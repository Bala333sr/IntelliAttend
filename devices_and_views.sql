-- Insert sample devices (students already exist with IDs 1, 2, 3)
INSERT INTO student_devices (student_id, device_uuid, device_name, device_type, device_model, os_version, biometric_enabled, location_permission, bluetooth_permission) VALUES
(1, 'DEVICE_001_ALICE', 'Alice iPhone', 'ios', 'iPhone 14', '17.0', TRUE, TRUE, TRUE),
(2, 'DEVICE_002_BOB', 'Bob Android', 'android', 'Samsung Galaxy S23', '14.0', TRUE, TRUE, TRUE),
(3, 'DEVICE_003_CHARLIE', 'Charlie Phone', 'android', 'Google Pixel 7', '13.0', FALSE, TRUE, TRUE);

-- ============================================================================
-- DATABASE VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active classes with enrollment count
DROP VIEW IF EXISTS view_active_classes;
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
GROUP BY c.class_id, c.class_code, c.class_name, f.first_name, f.last_name, f.email, cr.room_number, cr.building_name, c.max_students, c.schedule_day, c.start_time, c.end_time;

-- Recent attendance sessions with statistics
DROP VIEW IF EXISTS view_recent_sessions;
CREATE VIEW view_recent_sessions AS
SELECT 
    s.session_id,
    s.session_date,
    c.class_code,
    c.class_name,
    CONCAT(f.first_name, ' ', f.last_name) as faculty_name,
    COUNT(DISTINCT ar.record_id) as students_present,
    s.total_students_enrolled,
    s.attendance_percentage,
    s.status,
    s.start_time,
    s.end_time
FROM attendance_sessions s
LEFT JOIN classes c ON s.class_id = c.class_id
LEFT JOIN faculty f ON s.faculty_id = f.faculty_id
LEFT JOIN attendance_records ar ON s.session_id = ar.session_id AND ar.status = 'present'
GROUP BY s.session_id, s.session_date, c.class_code, c.class_name, f.first_name, f.last_name, s.total_students_enrolled, s.attendance_percentage, s.status, s.start_time, s.end_time
ORDER BY s.session_date DESC, s.start_time DESC;

-- Student attendance summary
DROP VIEW IF EXISTS view_student_attendance_summary;
CREATE VIEW view_student_attendance_summary AS
SELECT 
    s.student_id,
    CONCAT(s.first_name, ' ', s.last_name) as student_name,
    s.student_code,
    s.program,
    COUNT(DISTINCT e.class_id) as enrolled_classes,
    COUNT(DISTINCT ar.record_id) as total_sessions_attended,
    AVG(ar.verification_score) as avg_verification_score,
    CASE 
        WHEN COUNT(DISTINCT ar.record_id) = 0 THEN 0
        ELSE (COUNT(DISTINCT ar.record_id) * 100.0 / COUNT(DISTINCT ats.session_id))
    END as overall_attendance_percentage,
    CASE
        WHEN AVG(ar.verification_score) >= 0.8 THEN 'High Trust'
        WHEN AVG(ar.verification_score) >= 0.6 THEN 'Medium Trust'
        ELSE 'Low Trust'
    END as trust_level
FROM students s
LEFT JOIN student_class_enrollments e ON s.student_id = e.student_id AND e.is_active = TRUE
LEFT JOIN attendance_sessions ats ON e.class_id = ats.class_id
LEFT JOIN attendance_records ar ON ats.session_id = ar.session_id AND ar.student_id = s.student_id
WHERE s.is_active = TRUE
GROUP BY s.student_id, s.first_name, s.last_name, s.student_code, s.program;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================
SELECT 'IntelliAttend database setup completed successfully!' as message;