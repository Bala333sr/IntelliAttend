#!/usr/bin/env python3
"""
Script to update students table to add section_id foreign key according to PRD specifications
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def update_students_table():
    """Update students table to add section_id foreign key"""
    
    with app.app_context():
        try:
            print("Updating students table to add section_id foreign key...")
            
            # Add section_id column to students table
            add_section_id_sql = """
            ALTER TABLE students 
            ADD COLUMN section_id INT,
            ADD FOREIGN KEY (section_id) REFERENCES sections(id);
            """
            
            db.session.execute(text(add_section_id_sql))
            db.session.commit()
            print("✅ Students table updated successfully with section_id foreign key!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating students table: {e}")
            raise e

if __name__ == '__main__':
    update_students_table()