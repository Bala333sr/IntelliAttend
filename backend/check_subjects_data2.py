#!/usr/bin/env python3
"""
Script to check subjects data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_subjects_data():
    """Check subjects data"""
    
    with app.app_context():
        try:
            print("Checking subjects data...")
            
            result = db.session.execute(text('SELECT id, section_id, subject_code, name, faculty FROM subjects'))
            rows = result.fetchall()
            for row in rows:
                print(row)
                
            print("\nChecking for duplicate subject codes...")
            result = db.session.execute(text('SELECT subject_code, COUNT(*) as count FROM subjects GROUP BY subject_code HAVING COUNT(*) > 1'))
            rows = result.fetchall()
            for row in rows:
                print(f"Duplicate subject code: {row[0]} appears {row[1]} times")
            
        except Exception as e:
            print(f"Error checking subjects data: {e}")
            raise e

if __name__ == '__main__':
    check_subjects_data()