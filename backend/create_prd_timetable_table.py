#!/usr/bin/env python3
"""
Script to create timetable table according to PRD specifications
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_prd_timetable_table():
    """Create timetable table according to PRD specifications"""
    
    with app.app_context():
        try:
            print("Creating timetable table according to PRD specifications...")
            
            # Drop the existing timetable table if it exists
            drop_table_sql = "DROP TABLE IF EXISTS timetable;"
            db.session.execute(text(drop_table_sql))
            
            # Create new timetable table with PRD structure
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS timetable (
                id INT AUTO_INCREMENT PRIMARY KEY,
                section_id INT NOT NULL,
                day_of_week VARCHAR(20) NOT NULL,
                slot_number INT NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                subject_code VARCHAR(20),
                slot_type VARCHAR(20) DEFAULT 'regular',
                room_number VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (section_id) REFERENCES sections(id),
                FOREIGN KEY (subject_code) REFERENCES subjects(subject_code),
                UNIQUE KEY unique_slot (section_id, day_of_week, slot_number)
            );
            """
            
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("✅ Timetable table created successfully according to PRD specifications!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating timetable table: {e}")
            raise e

if __name__ == '__main__':
    create_prd_timetable_table()