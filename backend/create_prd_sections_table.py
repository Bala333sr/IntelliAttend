#!/usr/bin/env python3
"""
Script to create sections table according to PRD specifications
"""

import sys
import os
import datetime
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_prd_sections_table():
    """Create sections table according to PRD specifications"""
    
    with app.app_context():
        try:
            print("Creating sections table according to PRD specifications...")
            
            # Create sections table
            create_sections_table_sql = """
            CREATE TABLE IF NOT EXISTS sections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                section_name VARCHAR(10) NOT NULL,
                course VARCHAR(100) NOT NULL,
                room_number VARCHAR(20),
                department VARCHAR(100),
                class_incharge VARCHAR(100),
                academic_year VARCHAR(20),
                effective_from DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_section (course, section_name, academic_year)
            );
            """
            
            db.session.execute(text(create_sections_table_sql))
            db.session.commit()
            print("✅ Sections table created successfully according to PRD specifications!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sections table: {e}")
            raise e

if __name__ == '__main__':
    create_prd_sections_table()