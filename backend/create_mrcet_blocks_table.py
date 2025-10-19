#!/usr/bin/env python3
"""
Script to create MRCET blocks table and insert blocks data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_mrcet_blocks_table():
    """Create MRCET blocks table and insert data"""
    
    with app.app_context():
        try:
            # Create MRCET blocks table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS mrcet_blocks (
                block_id INT AUTO_INCREMENT PRIMARY KEY,
                block_name VARCHAR(100) NOT NULL,
                block_code VARCHAR(20) UNIQUE NOT NULL,
                block_type ENUM('Academic', 'Administrative', 'Hostel', 'Specialized') NOT NULL,
                floors INT NOT NULL,
                total_floors INT NOT NULL,
                ground_floor BOOLEAN DEFAULT TRUE,
                basement_floors INT DEFAULT 0,
                building_area DECIMAL(10, 2), -- in square feet
                departments TEXT, -- JSON formatted list of departments
                facilities TEXT, -- JSON formatted list of facilities
                capacity INT, -- approximate capacity
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_block_name (block_name),
                INDEX idx_block_code (block_code),
                INDEX idx_block_type (block_type)
            );
            """
            
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("✅ MRCET blocks table created successfully!")
            
            # Insert MRCET blocks data
            blocks_data = [
                # Academic Blocks
                {
                    'block_name': 'CSE Block',
                    'block_code': 'BLOCK-1',
                    'block_type': 'Academic',
                    'floors': 5,
                    'total_floors': 5,
                    'ground_floor': True,
                    'basement_floors': 0,
                    'building_area': 110000.00,
                    'departments': '["CSE", "IT", "General Classrooms"]',
                    'facilities': '["Lecture halls", "Seminar halls", "Faculty rooms", "Conference rooms", "Computer labs", "Smart classrooms"]',
                    'capacity': 1200
                },
                {
                    'block_name': 'MBA Block',
                    'block_code': 'BLOCK-2',
                    'block_type': 'Academic',
                    'floors': 4,
                    'total_floors': 4,
                    'ground_floor': True,
                    'basement_floors': 0,
                    'building_area': 80000.00,
                    'departments': '["MBA", "Management Studies"]',
                    'facilities': '["Case study rooms", "Presentation halls", "Faculty chambers", "Library extension"]',
                    'capacity': 800
                },
                {
                    'block_name': 'Humanities & Sciences Block',
                    'block_code': 'BLOCK-3',
                    'block_type': 'Academic',
                    'floors': 3,
                    'total_floors': 3,
                    'ground_floor': True,
                    'basement_floors': 0,
                    'building_area': 60000.00,
                    'departments': '["Mathematics", "Physics", "Chemistry", "English"]',
                    'facilities': '["Physics labs", "Chemistry labs", "Language labs", "Mathematics resource center"]',
                    'capacity': 600
                },
                {
                    'block_name': 'ECE Block',
                    'block_code': 'BLOCK-4',
                    'block_type': 'Academic',
                    'floors': 4,
                    'total_floors': 4,
                    'ground_floor': True,
                    'basement_floors': 0,
                    'building_area': 80000.00,
                    'departments': '["ECE"]',
                    'facilities': '["Electronics labs", "Communication labs", "VLSI labs", "Microprocessor labs"]',
                    'capacity': 600
                },
                {
                    'block_name': 'EEE Block',
                    'block_code': 'BLOCK-5',
                    'block_type': 'Academic',
                    'floors': 4,
                    'total_floors': 4,
                    'ground_floor': True,
                    'basement_floors': 0,
                    'building_area': 80000.00,
                    'departments': '["EEE"]',
                    'facilities': '["Power systems labs", "Control systems labs", "Electrical machines labs"]',
                    'capacity': 600
                },
                {
                    'block_name': 'AIML Block',
                    'block_code': 'BLOCK-6',
                    'block_type': 'Academic',
                    'floors': 4,
                    'total_floors': 4,
                    'ground_floor': True,
                    'basement_floors': 0,
                    'building_area': 75000.00,
                    'departments': '["CSE-AI&ML", "CSE-Data Science", "CSE-Cyber Security", "CSE-IoT"]',
                    'facilities': '["AI labs", "Data Science labs", "Cyber Security labs", "IoT labs", "High-performance computing center"]',
                    'capacity': 800
                },
                {
                    'block_name': 'Placement Block',
                    'block_code': 'BLOCK-7',
                    'block_type': 'Academic',
                    'floors': 3,
                    'total_floors': 3,
                    'ground_floor': True,
                    'basement_floors': 0,
                    'building_area': 50000.00,
                    'departments': '["Placement & Training"]',
                    'facilities': '["Interview halls", "Group discussion rooms", "Training rooms", "Corporate meeting rooms"]',
                    'capacity': 300
                },
                {
                    'block_name': 'Cafeteria',
                    'block_code': 'BLOCK-8',
                    'block_type': 'Specialized',
                    'floors': 2,
                    'total_floors': 2,
                    'ground_floor': True,
                    'basement_floors': 0,
                    'building_area': 40000.00,
                    'departments': '[]',
                    'facilities': '["Dining halls", "Food counters", "Seating areas", "Kitchen facilities"]',
                    'capacity': 1000
                },
                {
                    'block_name': 'Playground',
                    'block_code': 'BLOCK-9',
                    'block_type': 'Specialized',
                    'floors': 1,
                    'total_floors': 1,
                    'ground_floor': True,
                    'basement_floors': 0,
                    'building_area': 150000.00,
                    'departments': '[]',
                    'facilities': '["Football field", "Basketball court", "Volleyball court", "Athletics track", "Gymnasium"]',
                    'capacity': 2000
                },
                # Administrative Block (same building as CSE but separate entry)
                {
                    'block_name': 'Administrative Block',
                    'block_code': 'BLOCK-ADM',
                    'block_type': 'Administrative',
                    'floors': 5,
                    'total_floors': 5,
                    'ground_floor': True,
                    'basement_floors': 0,
                    'building_area': 110000.00,
                    'departments': '[]',
                    'facilities': '["Principal chamber", "Dean offices", "Administrative officer room", "Accounts section", "Examination branch", "Placement & training centre", "R&D centre", "IQAC office"]',
                    'capacity': 200
                },
                # Hostel Blocks
                {
                    'block_name': 'Boys Hostel Block',
                    'block_code': 'BLOCK-HB',
                    'block_type': 'Hostel',
                    'floors': 5,  # G+4
                    'total_floors': 5,
                    'ground_floor': True,
                    'basement_floors': 0,
                    'building_area': 110000.00,
                    'departments': '[]',
                    'facilities': '["Wi-Fi", "24x7 security", "CCTV surveillance", "Hot water", "Power backup", "Recreation hall", "Multi-gym", "Dining hall"]',
                    'capacity': 676
                },
                {
                    'block_name': 'Girls Hostel Block',
                    'block_code': 'BLOCK-HG',
                    'block_type': 'Hostel',
                    'floors': 5,  # G+4
                    'total_floors': 5,
                    'ground_floor': True,
                    'basement_floors': 0,
                    'building_area': 80000.00,
                    'departments': '[]',
                    'facilities': '["Wi-Fi", "24x7 security", "CCTV surveillance", "Hot water", "Power backup", "Recreation hall", "Yoga room", "Dining hall"]',
                    'capacity': 640
                }
            ]
            
            # Clear existing data
            db.session.execute(text("DELETE FROM mrcet_blocks"))
            
            # Insert blocks data
            insert_sql = """
            INSERT INTO mrcet_blocks (
                block_name, block_code, block_type, floors, total_floors, ground_floor, 
                basement_floors, building_area, departments, facilities, capacity
            ) VALUES (
                :block_name, :block_code, :block_type, :floors, :total_floors, :ground_floor,
                :basement_floors, :building_area, :departments, :facilities, :capacity
            )
            """
            
            for block in blocks_data:
                db.session.execute(text(insert_sql), block)
            
            db.session.commit()
            print("✅ MRCET blocks data inserted successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT COUNT(*) as count FROM mrcet_blocks"))
            row = result.fetchone()
            if row:
                print(f"✅ Total blocks in database: {row[0]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating MRCET blocks table: {e}")
            raise e

if __name__ == '__main__':
    create_mrcet_blocks_table()