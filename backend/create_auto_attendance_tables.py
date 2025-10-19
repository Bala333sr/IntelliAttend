#!/usr/bin/env python3
"""
Script to create database tables for auto-attendance feature
"""

from app import app, db
from sqlalchemy import text

def create_auto_attendance_tables():
    """Create tables for auto-attendance feature using SQLAlchemy"""
    with app.app_context():
        try:
            # Create auto_attendance_config table
            create_config_table_sql = text("""
            CREATE TABLE IF NOT EXISTS auto_attendance_config (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                enabled BOOLEAN DEFAULT FALSE,
                gps_enabled BOOLEAN DEFAULT TRUE,
                wifi_enabled BOOLEAN DEFAULT TRUE,
                bluetooth_enabled BOOLEAN DEFAULT TRUE,
                confidence_threshold DECIMAL(3,2) DEFAULT 0.85,
                require_warm_data BOOLEAN DEFAULT TRUE,
                auto_submit BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE KEY unique_student (student_id)
            )
            """)
            
            db.session.execute(create_config_table_sql)
            print("Created auto_attendance_config table")
            
            # Create auto_attendance_log table
            create_log_table_sql = text("""
            CREATE TABLE IF NOT EXISTS auto_attendance_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                session_id INT NOT NULL,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                gps_score DECIMAL(3,2),
                wifi_score DECIMAL(3,2),
                bluetooth_score DECIMAL(3,2),
                final_confidence DECIMAL(3,2),
                action_taken ENUM('auto_marked', 'suggested', 'ignored') NOT NULL,
                latitude DECIMAL(10,8),
                longitude DECIMAL(11,8),
                wifi_ssid VARCHAR(100),
                bluetooth_devices JSON,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (session_id) REFERENCES timetable(id),
                INDEX idx_student_session (student_id, session_id)
            )
            """)
            
            db.session.execute(create_log_table_sql)
            print("Created auto_attendance_log table")
            
            db.session.commit()
            print("All auto-attendance tables created successfully!")
            
        except Exception as e:
            print(f"Error creating auto-attendance tables: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_auto_attendance_tables()