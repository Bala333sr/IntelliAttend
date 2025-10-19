#!/usr/bin/env python3
"""
Script to insert subject data for III CSE (AIML) SEC-A
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def insert_subject_data():
    """Insert subject data for III CSE (AIML) SEC-A"""
    
    with app.app_context():
        try:
            print("Inserting subject data for III CSE (AIML) SEC-A...")
            
            # Insert subject data
            insert_subject_sql = """
            INSERT INTO subjects (subject_code, subject_name, short_name, faculty_name, credits, department)
            VALUES (:subject_code, :subject_name, :short_name, :faculty_name, :credits, :department)
            """
            
            subjects_data = [
                {
                    "subject_code": "R22A6602",
                    "subject_name": "MACHINE LEARNING",
                    "short_name": "ML",
                    "faculty_name": "Dr. KANNAIAH",
                    "credits": 3,
                    "department": "DEPARTMENT OF COMPUTATIONAL INTELLIGENCE"
                },
                {
                    "subject_code": "R22A6617",
                    "subject_name": "DESIGN AND ANALYSIS OF COMPUTER ALGORITHMS",
                    "short_name": "DAA",
                    "faculty_name": "Dr. PADMALATHA",
                    "credits": 3,
                    "department": "DEPARTMENT OF COMPUTATIONAL INTELLIGENCE"
                },
                {
                    "subject_code": "R22A0512",
                    "subject_name": "COMPUTER NETWORKS",
                    "short_name": "CN",
                    "faculty_name": "Mr. D. SANTHOSH KUMAR",
                    "credits": 3,
                    "department": "DEPARTMENT OF COMPUTATIONAL INTELLIGENCE"
                },
                {
                    "subject_code": "R22A6702",
                    "subject_name": "INTRODUCTION TO DATA SCIENCE",
                    "short_name": "IDS",
                    "faculty_name": "Mr. N. SATEESH",
                    "credits": 3,
                    "department": "DEPARTMENT OF COMPUTATIONAL INTELLIGENCE"
                },
                {
                    "subject_code": "R22A6681",
                    "subject_name": "MACHINE LEARNING LAB",
                    "short_name": "ML LAB",
                    "faculty_name": "Dr. KANNAIAH / Mr. SATEESH",
                    "credits": 2,
                    "department": "DEPARTMENT OF COMPUTATIONAL INTELLIGENCE"
                },
                {
                    "subject_code": "R22A0596",
                    "subject_name": "COMPUTER NETWORKS LAB",
                    "short_name": "CN LAB",
                    "faculty_name": "RADHIKA / N. MAHESH BABU",
                    "credits": 2,
                    "department": "DEPARTMENT OF COMPUTATIONAL INTELLIGENCE"
                },
                {
                    "subject_code": "R22A6692",
                    "subject_name": "APPLICATION DEVELOPMENT – 1",
                    "short_name": "AD-1",
                    "faculty_name": "Dr. KANNAIAH / VAMSI",
                    "credits": 2,
                    "department": "DEPARTMENT OF COMPUTATIONAL INTELLIGENCE"
                },
                {
                    "subject_code": "R22A0351",
                    "subject_name": "ROBOTICS and AUTOMATION",
                    "short_name": "R&A",
                    "faculty_name": "Dr. ARUN KUMAR",
                    "credits": 3,
                    "department": "DEPARTMENT OF COMPUTATIONAL INTELLIGENCE"
                },
                {
                    "subject_code": "R22A0084",
                    "subject_name": "PROFESSIONAL SKILL DEVELOPMENT",
                    "short_name": "PSD",
                    "faculty_name": "Dr. PAROMITHA",
                    "credits": 1,
                    "department": "DEPARTMENT OF COMPUTATIONAL INTELLIGENCE"
                }
            ]
            
            for subject in subjects_data:
                db.session.execute(text(insert_subject_sql), subject)
            
            db.session.commit()
            print("✅ Subject data inserted successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error inserting subject data: {e}")
            raise e

if __name__ == '__main__':
    insert_subject_data()