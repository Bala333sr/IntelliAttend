#!/usr/bin/env python3
"""
Script to create attendance statistics tables according to PRD specifications
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_attendance_statistics_tables():
    """Create attendance statistics tables"""
    
    with app.app_context():
        try:
            print("Creating attendance statistics tables...")
            
            # Create attendance_history table
            create_history_table_sql = """
            CREATE TABLE IF NOT EXISTS attendance_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                subject_id INT NOT NULL,
                session_id INT NOT NULL,
                attendance_status ENUM('present', 'absent', 'late') NOT NULL,
                marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                attendance_type ENUM('qr_scan', 'manual', 'warm_scan', 'auto') NOT NULL,
                location_verified BOOLEAN DEFAULT FALSE,
                classroom_id INT,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id),
                FOREIGN KEY (session_id) REFERENCES timetable(id),
                INDEX idx_student_subject (student_id, subject_id),
                INDEX idx_marked_at (marked_at)
            )
            """
            
            db.session.execute(text(create_history_table_sql))
            print("✅ attendance_history table created successfully!")
            
            # Create attendance_statistics table
            create_statistics_table_sql = """
            CREATE TABLE IF NOT EXISTS attendance_statistics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                subject_id INT,  -- NULL for overall stats
                total_sessions INT DEFAULT 0,
                attended_sessions INT DEFAULT 0,
                absent_sessions INT DEFAULT 0,
                late_sessions INT DEFAULT 0,
                attendance_percentage DECIMAL(5,2) DEFAULT 0.00,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                academic_year VARCHAR(10),
                semester INT,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id),
                UNIQUE KEY unique_student_subject (student_id, subject_id, academic_year, semester)
            )
            """
            
            db.session.execute(text(create_statistics_table_sql))
            print("✅ attendance_statistics table created successfully!")
            
            # Create attendance_trends table
            create_trends_table_sql = """
            CREATE TABLE IF NOT EXISTS attendance_trends (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                subject_id INT,
                trend_date DATE NOT NULL,
                sessions_count INT DEFAULT 0,
                attended_count INT DEFAULT 0,
                attendance_rate DECIMAL(5,2),
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id),
                UNIQUE KEY unique_student_subject_date (student_id, subject_id, trend_date)
            )
            """
            
            db.session.execute(text(create_trends_table_sql))
            print("✅ attendance_trends table created successfully!")
            
            db.session.commit()
            print("✅ All attendance statistics tables created successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating attendance statistics tables: {e}")
            raise e

if __name__ == '__main__':
    create_attendance_statistics_tables()