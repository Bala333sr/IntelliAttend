#!/usr/bin/env python3
"""
Script to update student data for BALA (23N31A6645) to add section_id
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def update_student_data():
    """Update student data for BALA (23N31A6645) to add section_id"""
    
    with app.app_context():
        try:
            print("Updating student data for BALA (23N31A6645) to add section_id...")
            
            # Get section ID for Section A of III CSE (AIML)
            result = db.session.execute(text("SELECT id FROM sections WHERE section_name = 'A' AND course = 'III CSE (AIML)'"))
            row = result.fetchone()
            if not row:
                print("❌ Section A not found")
                return
            section_id = row[0]
            print(f"Section ID: {section_id}")
            
            # Update student data to add section_id
            update_student_sql = """
            UPDATE students 
            SET section_id = :section_id, 
                first_name = :first_name, 
                program = :program, 
                year_of_study = :year_of_study
            WHERE student_code = :student_code
            """
            
            student_data = {
                "student_code": "23N31A6645",
                "first_name": "BALA",
                "program": "CSE (AIML)",
                "year_of_study": 3,
                "section_id": section_id
            }
            
            result = db.session.execute(text(update_student_sql), student_data)
            db.session.commit()
            
            print("✅ Student data updated successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating student data: {e}")
            raise e

if __name__ == '__main__':
    update_student_data()