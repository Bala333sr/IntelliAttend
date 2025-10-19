#!/usr/bin/env python3
"""
Script to create MRCET mid-term examination structure table and insert structure data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_mrcet_midterm_structure_table():
    """Create MRCET mid-term examination structure table and insert data"""
    
    with app.app_context():
        try:
            print("Creating MRCET mid-term examination structure table...")
            
            # Create mid-term examination structure table
            create_structure_table_sql = """
            CREATE TABLE IF NOT EXISTS mrcet_midterm_structure (
                structure_id INT AUTO_INCREMENT PRIMARY KEY,
                midterm_number INT NOT NULL, -- 1 for First Mid, 2 for Second Mid
                units_covered VARCHAR(50) NOT NULL,
                weeks_conducted VARCHAR(50) NOT NULL,
                duration_hours DECIMAL(3, 1) NOT NULL,
                marks_descriptive INT NOT NULL,
                marks_assignments INT NOT NULL,
                total_marks INT NOT NULL,
                academic_year VARCHAR(9) NOT NULL, -- Format: 2024-2025
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_midterm_number (midterm_number),
                INDEX idx_academic_year (academic_year)
            );
            """
            
            db.session.execute(text(create_structure_table_sql))
            db.session.commit()
            print("✅ MRCET mid-term examination structure table created successfully!")
            
            # Insert MRCET mid-term examination structure data
            structure_data = [
                {
                    "midterm_number": 1,
                    "units_covered": "Units 1-2",
                    "weeks_conducted": "Weeks 8-9",
                    "duration_hours": 2.0,
                    "marks_descriptive": 24,
                    "marks_assignments": 6,
                    "total_marks": 30,
                    "academic_year": "2024-2025"
                },
                {
                    "midterm_number": 2,
                    "units_covered": "Units 3-5",
                    "weeks_conducted": "Weeks 16-17",
                    "duration_hours": 2.0,
                    "marks_descriptive": 24,
                    "marks_assignments": 6,
                    "total_marks": 30,
                    "academic_year": "2024-2025"
                }
            ]
            
            # Clear existing data
            db.session.execute(text("DELETE FROM mrcet_midterm_structure"))
            
            # Insert structure data
            insert_sql = """
            INSERT INTO mrcet_midterm_structure (
                midterm_number, units_covered, weeks_conducted, duration_hours, 
                marks_descriptive, marks_assignments, total_marks, academic_year
            ) VALUES (
                :midterm_number, :units_covered, :weeks_conducted, :duration_hours,
                :marks_descriptive, :marks_assignments, :total_marks, :academic_year
            )
            """
            
            for structure in structure_data:
                db.session.execute(text(insert_sql), structure)
            
            db.session.commit()
            print("✅ MRCET mid-term examination structure data inserted successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT COUNT(*) as count FROM mrcet_midterm_structure"))
            row = result.fetchone()
            if row:
                print(f"✅ Total midterm structures in database: {row[0]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating MRCET mid-term examination structure table: {e}")
            raise e

if __name__ == '__main__':
    create_mrcet_midterm_structure_table()