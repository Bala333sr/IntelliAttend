#!/usr/bin/env python3
"""
Script to check students table structure
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_students_table():
    """Check students table structure"""
    
    with app.app_context():
        try:
            print("Checking students table structure...")
            
            # Describe students table
            describe_sql = "DESCRIBE students"
            result = db.session.execute(text(describe_sql))
            rows = result.fetchall()
            
            print("Students table structure:")
            for row in rows:
                print(f"  {row[0]} {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
            
        except Exception as e:
            print(f"❌ Error checking students table: {e}")

if __name__ == '__main__':
    check_students_table()