#!/usr/bin/env python3
"""
Script to update the existing database with MRCET department information
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def update_mrcet_departments():
    """Update the existing database with MRCET department information"""
    
    with app.app_context():
        try:
            print("Starting MRCET department update...")
            
            # 1. Update existing departments with MRCET specific information
            print("1. Updating departments with MRCET information...")
            departments_data = [
                {"code": "CSE", "head": "Dr. Dandu Sujatha", "intake": 240, "faculty_count": 45},
                {"code": "CSE-AI", "head": "Dr. K Asish Vardhan", "intake": 600, "faculty_count": 31},
                {"code": "CSE-DS", "head": "Dr. Aitharaju Venkata Lakshmi Narasimha Sujith", "intake": 180, "faculty_count": 33},
                {"code": "CSE-CS", "head": "Dr. Lalband Neelu", "intake": 60, "faculty_count": 9},
                {"code": "CSE-IoT", "head": "Dr. Jawahar Muthusamy", "intake": 60, "faculty_count": 3},
                {"code": "IT", "head": "Dr. G. Sharada", "intake": 180, "faculty_count": 15},
                {"code": "ECE", "head": "Dr. K Mallikarjuna Lingam", "intake": 240, "faculty_count": 55},
                {"code": "EEE", "head": "Dr. M. Sharanya", "intake": 60, "faculty_count": 25},
                {"code": "MECH", "head": "Dr. Srikar Potnuru", "intake": 180, "faculty_count": 35},
                {"code": "AERO", "head": "Prof. Misba Mehdi", "intake": 120, "faculty_count": 18},
                {"code": "CIVIL", "head": "TBD", "intake": 30, "faculty_count": 12},
                {"code": "H&S", "head": "Dr. V Madhusudhan Reddy", "intake": 0, "faculty_count": 45}
            ]
            
            # Since we can't add columns to existing tables, we'll store this information in a new table
            # First, create a table to store MRCET department information
            print("2. Creating MRCET department information table...")
            create_dept_info_sql = """
            CREATE TABLE IF NOT EXISTS mrcet_department_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                department_code VARCHAR(50) UNIQUE NOT NULL,
                intake INT,
                faculty_count INT,
                hod_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_department_code (department_code)
            );
            """
            db.session.execute(text(create_dept_info_sql))
            
            # 3. Populate MRCET department information
            print("3. Populating MRCET department information...")
            for dept in departments_data:
                check_dept_info_sql = "SELECT id FROM mrcet_department_info WHERE department_code = :code LIMIT 1"
                result = db.session.execute(text(check_dept_info_sql), {'code': dept['code']}).fetchone()
                
                if not result:
                    insert_dept_info_sql = """
                    INSERT INTO mrcet_department_info (department_code, intake, faculty_count, hod_name)
                    VALUES (:code, :intake, :faculty_count, :head)
                    """
                    db.session.execute(text(insert_dept_info_sql), {
                        'code': dept['code'],
                        'intake': dept['intake'],
                        'faculty_count': dept['faculty_count'],
                        'head': dept['head']
                    })
                    print(f"   Added department info: {dept['code']}")
                else:
                    print(f"   Department info already exists: {dept['code']}")
            
            # 4. Create a view to join department information with MRCET data
            print("4. Creating view for department information...")
            try:
                create_view_sql = """
                CREATE OR REPLACE VIEW department_details AS
                SELECT 
                    d.id,
                    d.name,
                    d.code,
                    d.head,
                    mdi.intake,
                    mdi.faculty_count,
                    mdi.hod_name
                FROM departments d
                LEFT JOIN mrcet_department_info mdi ON d.code = mdi.department_code;
                """
                db.session.execute(text(create_view_sql))
                print("   Created department details view")
            except Exception as e:
                print(f"   Note: Could not create view: {e}")
            
            db.session.commit()
            print("✅ MRCET department update completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating MRCET departments: {e}")
            raise e

if __name__ == '__main__':
    update_mrcet_departments()