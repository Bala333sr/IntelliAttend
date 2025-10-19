#!/usr/bin/env python3
"""
Script to update timetable table structure for detailed timetable data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def update_timetable_structure():
    """Update timetable table structure for detailed timetable data"""
    
    with app.app_context():
        try:
            # Drop the existing timetable table
            drop_table_sql = "DROP TABLE IF EXISTS timetable;"
            db.session.execute(text(drop_table_sql))
            
            # Create new timetable table with detailed structure
            create_table_sql = """
            CREATE TABLE timetable (
                id INT AUTO_INCREMENT PRIMARY KEY,
                section_id INT,
                day_of_week VARCHAR(10),
                slot_number INT,
                slot_type VARCHAR(20),  -- regular, break, lunch
                start_time TIME,
                end_time TIME,
                subject_code VARCHAR(20),
                subject_name VARCHAR(255),
                faculty_name VARCHAR(255),
                room_number VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (section_id) REFERENCES sections(id)
            );
            """
            
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("✅ Timetable table structure updated successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating timetable table structure: {e}")

if __name__ == '__main__':
    update_timetable_structure()