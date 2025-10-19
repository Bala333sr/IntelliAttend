#!/usr/bin/env python3
"""
Script to update subjects table to match PRD specifications
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def update_prd_subjects_table():
    """Update subjects table to match PRD specifications"""
    
    with app.app_context():
        try:
            print("Updating subjects table to match PRD specifications...")
            
            # Rename 'code' column to 'subject_code' and make it unique
            # First, we need to drop the foreign key constraint from timetable if it exists
            try:
                drop_fk_sql = "ALTER TABLE timetable DROP FOREIGN KEY timetable_ibfk_2;"
                db.session.execute(text(drop_fk_sql))
            except:
                pass  # FK might not exist
            
            # Rename the column
            rename_column_sql = "ALTER TABLE subjects CHANGE code subject_code VARCHAR(20);"
            db.session.execute(text(rename_column_sql))
            
            # Add unique constraint to subject_code
            add_unique_sql = "ALTER TABLE subjects ADD UNIQUE KEY unique_subject_code (subject_code);"
            db.session.execute(text(add_unique_sql))
            
            # Add missing columns according to PRD
            try:
                add_short_name_sql = "ALTER TABLE subjects ADD COLUMN short_name VARCHAR(50);"
                db.session.execute(text(add_short_name_sql))
            except:
                pass  # Column might already exist
            
            try:
                add_faculty_name_sql = "ALTER TABLE subjects ADD COLUMN faculty_name VARCHAR(200);"
                db.session.execute(text(add_faculty_name_sql))
            except:
                pass  # Column might already exist
                
            try:
                add_credits_sql = "ALTER TABLE subjects ADD COLUMN credits INT DEFAULT 3;"
                db.session.execute(text(add_credits_sql))
            except:
                pass  # Column might already exist
                
            try:
                add_department_sql = "ALTER TABLE subjects ADD COLUMN department VARCHAR(100);"
                db.session.execute(text(add_department_sql))
            except:
                pass  # Column might already exist
            
            db.session.commit()
            print("✅ Subjects table updated successfully to match PRD specifications!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating subjects table: {e}")
            raise e

if __name__ == '__main__':
    update_prd_subjects_table()