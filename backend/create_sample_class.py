#!/usr/bin/env python3
"""
Script to create a sample class CSE-AIML-A in the database
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_sample_class():
    """Create a sample class CSE-AIML-A in the database"""
    
    with app.app_context():
        try:
            # First, let's create a sample faculty member since classes need a faculty_id
            faculty_insert_sql = """
            INSERT INTO faculty (faculty_code, first_name, last_name, email, phone_number, department, password_hash, is_active)
            VALUES (:faculty_code, :first_name, :last_name, :email, :phone_number, :department, :password_hash, :is_active)
            """
            
            faculty_data = {
                'faculty_code': 'FAC001',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@university.edu',
                'phone_number': '1234567890',
                'department': 'Computer Science',
                'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PZvO.S',  # bcrypt hash for "faculty123"
                'is_active': True
            }
            
            db.session.execute(text(faculty_insert_sql), faculty_data)
            db.session.commit()
            
            # Get the faculty_id of the inserted faculty
            result = db.session.execute(text("SELECT faculty_id FROM faculty WHERE faculty_code = :faculty_code"), 
                                      {'faculty_code': 'FAC001'})
            faculty_row = result.fetchone()
            if faculty_row is None:
                raise Exception('Failed to retrieve faculty record')
            faculty_id = faculty_row[0]
            
            # Now create the class CSE-AIML-A
            class_insert_sql = """
            INSERT INTO classes (class_code, class_name, faculty_id, semester, academic_year, credits, max_students, is_active)
            VALUES (:class_code, :class_name, :faculty_id, :semester, :academic_year, :credits, :max_students, :is_active)
            """
            
            class_data = {
                'class_code': 'CSE-AIML-A',
                'class_name': 'Computer Science and Engineering - Artificial Intelligence and Machine Learning - Section A',
                'faculty_id': faculty_id,
                'semester': 'Fall',
                'academic_year': '2025-2026',
                'credits': 3,
                'max_students': 60,
                'is_active': True
            }
            
            db.session.execute(text(class_insert_sql), class_data)
            db.session.commit()
            
            print("✅ Sample class 'CSE-AIML-A' created successfully!")
            print("✅ Sample faculty 'John Doe' created successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT class_id, class_code, class_name FROM classes WHERE class_code = :class_code"), 
                                      {'class_code': 'CSE-AIML-A'})
            class_row = result.fetchone()
            if class_row:
                print(f"✅ Class details: ID={class_row[0]}, Code={class_row[1]}, Name={class_row[2]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample class: {e}")

if __name__ == '__main__':
    create_sample_class()