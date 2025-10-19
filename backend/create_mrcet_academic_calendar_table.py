#!/usr/bin/env python3
"""
Script to create MRCET academic calendar table and insert calendar data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_mrcet_academic_calendar_table():
    """Create MRCET academic calendar table and insert data"""
    
    with app.app_context():
        try:
            print("Creating MRCET academic calendar table...")
            
            # Create academic calendar table
            create_calendar_table_sql = """
            CREATE TABLE IF NOT EXISTS mrcet_academic_calendar (
                calendar_id INT AUTO_INCREMENT PRIMARY KEY,
                academic_year VARCHAR(9) NOT NULL, -- Format: 2024-2025
                semester VARCHAR(50) NOT NULL,
                event_name VARCHAR(100) NOT NULL,
                event_type ENUM('Instruction', 'Examination', 'Holiday', 'Administrative') NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                duration_days INT,
                notes TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_academic_year (academic_year),
                INDEX idx_semester (semester),
                INDEX idx_event_type (event_type),
                INDEX idx_start_date (start_date)
            );
            """
            
            db.session.execute(text(create_calendar_table_sql))
            db.session.commit()
            print("✅ MRCET academic calendar table created successfully!")
            
            # Insert MRCET academic calendar data for 2024-25 II Semester
            calendar_data = [
                {
                    "academic_year": "2024-2025",
                    "semester": "II B.Tech II Sem",
                    "event_name": "I Spell Instructions",
                    "event_type": "Instruction",
                    "start_date": "2024-12-09",
                    "end_date": "2025-02-01",
                    "duration_days": 54,
                    "notes": "8 weeks of instruction"
                },
                {
                    "academic_year": "2024-2025",
                    "semester": "II B.Tech II Sem",
                    "event_name": "I Mid Examinations",
                    "event_type": "Examination",
                    "start_date": "2025-02-03",
                    "end_date": "2025-02-05",
                    "duration_days": 3,
                    "notes": "3 days of examinations"
                },
                {
                    "academic_year": "2024-2025",
                    "semester": "II B.Tech II Sem",
                    "event_name": "II Spell Instructions",
                    "event_type": "Instruction",
                    "start_date": "2025-02-06",
                    "end_date": "2025-04-01",
                    "duration_days": 55,
                    "notes": "8 weeks of instruction"
                },
                {
                    "academic_year": "2024-2025",
                    "semester": "II B.Tech II Sem",
                    "event_name": "II Mid Examinations",
                    "event_type": "Examination",
                    "start_date": "2025-04-02",
                    "end_date": "2025-04-05",
                    "duration_days": 4,
                    "notes": "4 days of examinations"
                },
                {
                    "academic_year": "2024-2025",
                    "semester": "II B.Tech II Sem",
                    "event_name": "Practical Examinations",
                    "event_type": "Examination",
                    "start_date": "2025-04-07",
                    "end_date": "2025-04-12",
                    "duration_days": 6,
                    "notes": "1 week of practical examinations"
                },
                {
                    "academic_year": "2024-2025",
                    "semester": "II B.Tech II Sem",
                    "event_name": "End Semester Examinations",
                    "event_type": "Examination",
                    "start_date": "2025-04-14",
                    "end_date": "2025-04-26",
                    "duration_days": 13,
                    "notes": "2 weeks of examinations"
                }
            ]
            
            # Clear existing data
            db.session.execute(text("DELETE FROM mrcet_academic_calendar"))
            
            # Insert calendar data
            insert_sql = """
            INSERT INTO mrcet_academic_calendar (
                academic_year, semester, event_name, event_type, start_date, end_date, duration_days, notes
            ) VALUES (
                :academic_year, :semester, :event_name, :event_type, :start_date, :end_date, :duration_days, :notes
            )
            """
            
            for event in calendar_data:
                db.session.execute(text(insert_sql), event)
            
            db.session.commit()
            print("✅ MRCET academic calendar data inserted successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT COUNT(*) as count FROM mrcet_academic_calendar"))
            row = result.fetchone()
            if row:
                print(f"✅ Total calendar events in database: {row[0]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating MRCET academic calendar table: {e}")
            raise e

if __name__ == '__main__':
    create_mrcet_academic_calendar_table()