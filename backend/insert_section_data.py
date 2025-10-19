#!/usr/bin/env python3
"""
Script to insert section data for III CSE (AIML) SEC-A
"""

import sys
import os
import datetime
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def insert_section_data():
    """Insert section data for III CSE (AIML) SEC-A"""
    
    with app.app_context():
        try:
            print("Inserting section data for III CSE (AIML) SEC-A...")
            
            # Insert section data
            insert_section_sql = """
            INSERT INTO sections (section_name, course, room_number, department, class_incharge, academic_year, effective_from)
            VALUES (:section_name, :course, :room_number, :department, :class_incharge, :academic_year, :effective_from)
            """
            
            section_data = {
                "section_name": "A",
                "course": "III CSE (AIML)",
                "room_number": "4208",
                "department": "DEPARTMENT OF COMPUTATIONAL INTELLIGENCE",
                "class_incharge": "Dr. KANNAIAH",
                "academic_year": "2025-26",
                "effective_from": "2025-06-02"
            }
            
            db.session.execute(text(insert_section_sql), section_data)
            db.session.commit()
            print("✅ Section data inserted successfully!")
            
            # Get the section ID
            result = db.session.execute(text("SELECT id FROM sections WHERE section_name = 'A' AND course = 'III CSE (AIML)'"))
            row = result.fetchone()
            if row:
                section_id = row[0]
                print(f"Section ID: {section_id}")
                return section_id
            else:
                print("❌ Failed to get section ID")
                return None
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error inserting section data: {e}")
            raise e

if __name__ == '__main__':
    insert_section_data()