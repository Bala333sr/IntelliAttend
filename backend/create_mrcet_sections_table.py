#!/usr/bin/env python3
"""
Script to create MRCET sections table and insert section data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_mrcet_sections_table():
    """Create MRCET sections table and insert data"""
    
    with app.app_context():
        try:
            print("Creating MRCET sections table...")
            
            # Create sections table
            create_sections_table_sql = """
            CREATE TABLE IF NOT EXISTS mrcet_sections (
                section_id INT AUTO_INCREMENT PRIMARY KEY,
                department_code VARCHAR(20) NOT NULL,
                section_name VARCHAR(10) NOT NULL,
                student_count INT DEFAULT 0,
                class_incharge VARCHAR(100),
                room_number VARCHAR(20),
                building_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                UNIQUE KEY unique_dept_section (department_code, section_name),
                INDEX idx_department (department_code),
                INDEX idx_section (section_name)
            );
            """
            
            db.session.execute(text(create_sections_table_sql))
            db.session.commit()
            print("✅ MRCET sections table created successfully!")
            
            # Insert MRCET sections data
            sections_data = [
                # CSE Department (240 students, 4 sections)
                {"department_code": "CSE", "section_name": "A", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Main Academic Block"},
                {"department_code": "CSE", "section_name": "B", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Main Academic Block"},
                {"department_code": "CSE", "section_name": "C", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Main Academic Block"},
                {"department_code": "CSE", "section_name": "D", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Main Academic Block"},
                
                # CSE-AI&ML Department (600 students, 10 sections)
                {"department_code": "CSE-AI", "section_name": "A", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "CSE-AIML Block"},
                {"department_code": "CSE-AI", "section_name": "B", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "CSE-AIML Block"},
                {"department_code": "CSE-AI", "section_name": "C", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "CSE-AIML Block"},
                {"department_code": "CSE-AI", "section_name": "D", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "CSE-AIML Block"},
                {"department_code": "CSE-AI", "section_name": "E", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "CSE-AIML Block"},
                {"department_code": "CSE-AI", "section_name": "F", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "CSE-AIML Block"},
                {"department_code": "CSE-AI", "section_name": "G", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "CSE-AIML Block"},
                {"department_code": "CSE-AI", "section_name": "H", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "CSE-AIML Block"},
                {"department_code": "CSE-AI", "section_name": "I", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "CSE-AIML Block"},
                {"department_code": "CSE-AI", "section_name": "J", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "CSE-AIML Block"},
                
                # CSE-Data Science Department (180 students, 3 sections)
                {"department_code": "CSE-DS", "section_name": "A", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Main Academic Block"},
                {"department_code": "CSE-DS", "section_name": "B", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Main Academic Block"},
                {"department_code": "CSE-DS", "section_name": "C", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Main Academic Block"},
                
                # CSE-Cyber Security Department (60 students, 1 section)
                {"department_code": "CSE-CS", "section_name": "A", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Main Academic Block"},
                
                # CSE-IoT Department (60 students, 1 section)
                {"department_code": "CSE-IoT", "section_name": "A", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Main Academic Block"},
                
                # IT Department (180 students, 3 sections)
                {"department_code": "IT", "section_name": "A", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Main Academic Block"},
                {"department_code": "IT", "section_name": "B", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Main Academic Block"},
                {"department_code": "IT", "section_name": "C", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Main Academic Block"},
                
                # ECE Department (240 students, 4 sections)
                {"department_code": "ECE", "section_name": "A", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Electronics & Electrical Block"},
                {"department_code": "ECE", "section_name": "B", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Electronics & Electrical Block"},
                {"department_code": "ECE", "section_name": "C", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Electronics & Electrical Block"},
                {"department_code": "ECE", "section_name": "D", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Electronics & Electrical Block"},
                
                # EEE Department (60 students, 1 section)
                {"department_code": "EEE", "section_name": "A", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Electronics & Electrical Block"},
                
                # MECH Department (180 students, 3 sections)
                {"department_code": "MECH", "section_name": "A", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Mechanical & Aeronautical Block"},
                {"department_code": "MECH", "section_name": "B", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Mechanical & Aeronautical Block"},
                {"department_code": "MECH", "section_name": "C", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Mechanical & Aeronautical Block"},
                
                # AERO Department (120 students, 2 sections)
                {"department_code": "AERO", "section_name": "A", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Mechanical & Aeronautical Block"},
                {"department_code": "AERO", "section_name": "B", "student_count": 60, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Mechanical & Aeronautical Block"},
                
                # CE Department (30 students, 1 section)
                {"department_code": "CE", "section_name": "A", "student_count": 30, "class_incharge": "TBD", "room_number": "TBD", "building_name": "Humanities & Sciences Block"}
            ]
            
            # Clear existing data
            db.session.execute(text("DELETE FROM mrcet_sections"))
            
            # Insert sections data
            insert_sql = """
            INSERT INTO mrcet_sections (
                department_code, section_name, student_count, class_incharge, room_number, building_name
            ) VALUES (
                :department_code, :section_name, :student_count, :class_incharge, :room_number, :building_name
            )
            """
            
            for section in sections_data:
                db.session.execute(text(insert_sql), section)
            
            db.session.commit()
            print("✅ MRCET sections data inserted successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT COUNT(*) as count FROM mrcet_sections"))
            row = result.fetchone()
            if row:
                print(f"✅ Total sections in database: {row[0]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating MRCET sections table: {e}")
            raise e

if __name__ == '__main__':
    create_mrcet_sections_table()