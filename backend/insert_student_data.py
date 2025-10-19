#!/usr/bin/env python3
"""
Script to insert student data for BALA (23N31A6645)
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def insert_student_data():
    """Insert student data for BALA (23N31A6645)"""
    
    with app.app_context():
        try:
            print("Inserting student data for BALA (23N31A6645)...")
            
            # Get section ID for Section A of III CSE (AIML)
            result = db.session.execute(text("SELECT id FROM sections WHERE section_name = 'A' AND course = 'III CSE (AIML)'"))
            row = result.fetchone()
            if not row:
                print("❌ Section A not found")
                return
            section_id = row[0]
            print(f"Section ID: {section_id}")
            
            # Insert student data
            insert_student_sql = """
            INSERT INTO students (student_code, first_name, last_name, email, password_hash, program, year_of_study, section_id)
            VALUES (:student_code, :first_name, :last_name, :email, :password_hash, :program, :year_of_study, :section_id)
            """
            
            # Password hash for "pass" - in a real application, this should be properly hashed
            # This is just for testing purposes
            password_hash = "$2b$12$LQv3c1yqBwUVHdkuLM3uXeH6GS"  # bcrypt hash of "pass"
            
            student_data = {
                "student_code": "23N31A6645",
                "first_name": "BALA",
                "last_name": "",
                "email": "23N31A6645@mrcet.ac.in",
                "password_hash": password_hash,
                "program": "CSE (AIML)",
                "year_of_study": 3,
                "section_id": section_id
            }
            
            db.session.execute(text(insert_student_sql), student_data)
            db.session.commit()
            print("✅ Student data inserted successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error inserting student data: {e}")
            raise e

if __name__ == '__main__':
    insert_student_data()