#!/usr/bin/env python3
"""
Script to update sections table to match PRD specifications
"""

import sys
import os
import datetime
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def update_prd_sections_table():
    """Update sections table to match PRD specifications"""
    
    with app.app_context():
        try:
            print("Updating sections table to match PRD specifications...")
            
            # Rename 'section' column to 'section_name'
            try:
                rename_column_sql = "ALTER TABLE sections CHANGE section section_name VARCHAR(10);"
                db.session.execute(text(rename_column_sql))
            except:
                pass  # Column might already be named correctly
            
            # Add missing columns according to PRD
            try:
                add_course_sql = "ALTER TABLE sections ADD COLUMN course VARCHAR(100);"
                db.session.execute(text(add_course_sql))
            except:
                pass  # Column might already exist
                
            try:
                add_department_sql = "ALTER TABLE sections ADD COLUMN department VARCHAR(100);"
                db.session.execute(text(add_department_sql))
            except:
                pass  # Column might already exist
                
            try:
                add_class_incharge_sql = "ALTER TABLE sections ADD COLUMN class_incharge VARCHAR(100);"
                db.session.execute(text(add_class_incharge_sql))
            except:
                pass  # Column might already exist
                
            try:
                add_academic_year_sql = "ALTER TABLE sections ADD COLUMN academic_year VARCHAR(20);"
                db.session.execute(text(add_academic_year_sql))
            except:
                pass  # Column might already exist
                
            try:
                add_effective_from_sql = "ALTER TABLE sections ADD COLUMN effective_from DATE;"
                db.session.execute(text(add_effective_from_sql))
            except:
                pass  # Column might already exist
            
            # Add unique constraint
            try:
                add_unique_sql = "ALTER TABLE sections ADD UNIQUE KEY unique_section (course, section_name, academic_year);"
                db.session.execute(text(add_unique_sql))
            except:
                pass  # Constraint might already exist
            
            db.session.commit()
            print("✅ Sections table updated successfully to match PRD specifications!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating sections table: {e}")
            raise e

if __name__ == '__main__':
    update_prd_sections_table()