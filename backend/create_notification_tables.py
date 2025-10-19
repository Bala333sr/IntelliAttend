#!/usr/bin/env python3
"""
Script to create database tables for notifications feature
"""

from app import app, db
from sqlalchemy import text

def create_notification_tables():
    """Create tables for notifications feature using SQLAlchemy"""
    with app.app_context():
        try:
            # Create notification_preferences table
            create_prefs_table_sql = text("""
            CREATE TABLE IF NOT EXISTS notification_preferences (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                class_reminder_enabled BOOLEAN DEFAULT TRUE,
                warm_scan_reminder_enabled BOOLEAN DEFAULT TRUE,
                attendance_warning_enabled BOOLEAN DEFAULT TRUE,
                weekly_summary_enabled BOOLEAN DEFAULT TRUE,
                reminder_minutes_before INT DEFAULT 10,
                quiet_hours_start TIME,
                quiet_hours_end TIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE KEY unique_student (student_id)
            )
            """)
            
            db.session.execute(create_prefs_table_sql)
            print("Created notification_preferences table")
            
            # Create notification_log table
            create_log_table_sql = text("""
            CREATE TABLE IF NOT EXISTS notification_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                notification_type ENUM('class_reminder', 'warm_scan', 'attendance_warning', 'weekly_summary') NOT NULL,
                title VARCHAR(255),
                message TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP NULL,
                action_taken BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                INDEX idx_student_sent (student_id, sent_at)
            )
            """)
            
            db.session.execute(create_log_table_sql)
            print("Created notification_log table")
            
            db.session.commit()
            print("All notification tables created successfully!")
            
        except Exception as e:
            print(f"Error creating notification tables: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_notification_tables()