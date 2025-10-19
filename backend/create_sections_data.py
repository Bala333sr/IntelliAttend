#!/usr/bin/env python3
"""
Script to create sections and subjects tables and insert data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text
import json

# Sections data
sections_data = [
    {
        "section": "A",
        "room_number": "4208",
        "class_incharge": "Dr. Kanniaah"
    },
    {
        "section": "B",
        "room_number": "4210",
        "class_incharge": "Mrs. Jayasri"
    },
    {
        "section": "C",
        "room_number": "4211",
        "class_incharge": "Mr. N. Mahesh Babu"
    },
    {
        "section": "D",
        "room_number": "4213",
        "class_incharge": "Ms. Radhika"
    }
]

# Subjects data for all sections
subjects_data = [
    {
        "section": "A",
        "subjects": [
            {"code": "R22A6602", "name": "Machine Learning", "faculty": "Dr. Kanniaah"},
            {"code": "R22A6617", "name": "Design and Analysis of Computer Algorithms", "faculty": "Dr. Padmalatha"},
            {"code": "R22A0512", "name": "Computer Networks", "faculty": "Mr. D. Santhosh Kumar"},
            {"code": "R22A6702", "name": "Introduction to Data Science", "faculty": "Mr. N. Sateesh"},
            {"code": "R22A6681", "name": "Machine Learning Lab", "faculty": "Dr. Kanniaah / Mr. Sateesh"},
            {"code": "R22A0596", "name": "Computer Networks Lab", "faculty": "Radhika / N. Mahesh Babu"},
            {"code": "R22A6692", "name": "Application Development – 1", "faculty": "Dr. Kanniaah / Vamsi"},
            {"code": "R22A0351", "name": "Robotics and Automation", "faculty": "Dr. Arun Kumar"},
            {"code": "R22A0084", "name": "Professional Skill Development", "faculty": "Dr. Paromitha"}
        ]
    },
    {
        "section": "B",
        "subjects": [
            {"code": "R22A6602", "name": "Machine Learning", "faculty": "Dr. Rakesh"},
            {"code": "R22A6617", "name": "Design and Analysis of Computer Algorithms", "faculty": "Mrs. Jayasri"},
            {"code": "R22A0512", "name": "Computer Networks", "faculty": "Mr. D. Santhosh Kumar"},
            {"code": "R22A6702", "name": "Introduction to Data Science", "faculty": "Mr. Chandra Sekhar"},
            {"code": "R22A6681", "name": "Machine Learning Lab", "faculty": "Dr. Rakesh / Mrs. S.K. Subhani"},
            {"code": "R22A0596", "name": "Computer Networks Lab", "faculty": "Dr. Gayatri / Dr. Venkata Ramudu"},
            {"code": "R22A6692", "name": "Application Development – 1", "faculty": "Dr. Saiprasad / Dr. Venkata Ramudu"},
            {"code": "R22A0351", "name": "Robotics and Automation", "faculty": "Dr. Arun Kumar"},
            {"code": "R22A0084", "name": "Professional Skill Development", "faculty": "Mr. B. Anjaneyulu"}
        ]
    },
    {
        "section": "C",
        "subjects": [
            {"code": "R22A6602", "name": "Machine Learning", "faculty": "Dr. Rakesh"},
            {"code": "R22A6617", "name": "Design and Analysis of Computer Algorithms", "faculty": "Mr. Mahesh Babu"},
            {"code": "R22A0512", "name": "Computer Networks", "faculty": "Ms. S. Deepika"},
            {"code": "R22A6702", "name": "Introduction to Data Science", "faculty": "Dr. D. Sujatha"},
            {"code": "R22A6681", "name": "Machine Learning Lab", "faculty": "Dr. Rakesh / Shubani"},
            {"code": "R22A0596", "name": "Computer Networks Lab", "faculty": "Mr. Chandra Sekhar / Ms. B. Jyothi"},
            {"code": "R22A6692", "name": "Application Development – 1", "faculty": "Dr. Melinda / D. Chandrasekhar Reddy"},
            {"code": "R22A0351", "name": "Robotics and Automation", "faculty": "Dr. Sadanand"},
            {"code": "R22A0084", "name": "Professional Skill Development", "faculty": "Mrs. K.S Rajsri"}
        ]
    },
    {
        "section": "D",
        "subjects": [
            {"code": "R22A6602", "name": "Machine Learning", "faculty": "Ms. Radhika"},
            {"code": "R22A6617", "name": "Design and Analysis of Computer Algorithms", "faculty": "Mr. Hari Babu"},
            {"code": "R22A0512", "name": "Computer Networks", "faculty": "Ms. S. Revathi"},
            {"code": "R22A6702", "name": "Introduction to Data Science", "faculty": "Ms. Shubani"},
            {"code": "R22A6681", "name": "Machine Learning Lab", "faculty": "Ms. Radhika / Sateesh"},
            {"code": "R22A0596", "name": "Computer Networks Lab", "faculty": "Dr. Gayatri / Mr. Venkatewara Raju"},
            {"code": "R22A6692", "name": "Application Development - 1", "faculty": "Dr. Padmalatha / V. Babu Rao"}
        ]
    }
]

def create_sections_tables():
    """Create sections and subjects tables and insert data"""
    
    with app.app_context():
        try:
            # Create sections table
            create_sections_table_sql = """
            CREATE TABLE IF NOT EXISTS sections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                section VARCHAR(10) NOT NULL,
                room_number VARCHAR(20),
                class_incharge VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            db.session.execute(text(create_sections_table_sql))
            db.session.commit()
            print("✅ Sections table created successfully!")
            
            # Create subjects table
            create_subjects_table_sql = """
            CREATE TABLE IF NOT EXISTS subjects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                section_id INT,
                code VARCHAR(20),
                name VARCHAR(255),
                faculty VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (section_id) REFERENCES sections(id)
            );
            """
            
            db.session.execute(text(create_subjects_table_sql))
            db.session.commit()
            print("✅ Subjects table created successfully!")
            
            # Insert sections data
            insert_section_sql = """
            INSERT INTO sections (section, room_number, class_incharge)
            VALUES (:section, :room_number, :class_incharge)
            """
            
            for section in sections_data:
                db.session.execute(text(insert_section_sql), section)
            
            db.session.commit()
            print("✅ Sections data inserted successfully!")
            
            # Insert subjects data
            insert_subject_sql = """
            INSERT INTO subjects (section_id, code, name, faculty)
            VALUES (:section_id, :code, :name, :faculty)
            """
            
            # Get all sections with their IDs
            result = db.session.execute(text("SELECT id, section FROM sections"))
            sections_dict = {row[1]: row[0] for row in result}
            
            # Insert subjects for each section
            for section_subjects in subjects_data:
                section_id = sections_dict.get(section_subjects["section"])
                if section_id:
                    for subject in section_subjects["subjects"]:
                        subject_data = {
                            "section_id": section_id,
                            "code": subject["code"],
                            "name": subject["name"],
                            "faculty": subject["faculty"]
                        }
                        db.session.execute(text(insert_subject_sql), subject_data)
            
            db.session.commit()
            print("✅ Subjects data inserted successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT COUNT(*) FROM sections"))
            sections_row = result.fetchone()
            sections_count = sections_row[0] if sections_row else 0
            print(f"✅ Total sections: {sections_count}")
            
            result = db.session.execute(text("SELECT COUNT(*) FROM subjects"))
            subjects_row = result.fetchone()
            subjects_count = subjects_row[0] if subjects_row else 0
            print(f"✅ Total subjects: {subjects_count}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sections tables: {e}")

if __name__ == '__main__':
    create_sections_tables()