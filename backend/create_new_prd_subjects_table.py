#!/usr/bin/env python3
"""
Script to create a new subjects table according to PRD specifications
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_new_prd_subjects_table():
    """Create a new subjects table according to PRD specifications"""
    
    with app.app_context():
        try:
            print("Creating new subjects table according to PRD specifications...")
            
            # Drop the existing subjects table
            drop_table_sql = "DROP TABLE IF EXISTS subjects;"
            db.session.execute(text(drop_table_sql))
            
            # Create new subjects table with PRD structure
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS subjects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                subject_code VARCHAR(20) UNIQUE NOT NULL,
                subject_name VARCHAR(200) NOT NULL,
                short_name VARCHAR(50),
                faculty_name VARCHAR(200),
                credits INT DEFAULT 3,
                department VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("✅ New subjects table created successfully according to PRD specifications!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating new subjects table: {e}")
            raise e

if __name__ == '__main__':
    create_new_prd_subjects_table()