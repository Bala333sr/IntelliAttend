#!/usr/bin/env python3
"""
Script to check subjects table structure
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_subjects_table():
    """Check subjects table structure"""
    
    with app.app_context():
        try:
            print("Checking subjects table structure...")
            
            # Describe subjects table
            describe_sql = "DESCRIBE subjects"
            result = db.session.execute(text(describe_sql))
            rows = result.fetchall()
            
            print("Subjects table structure:")
            for row in rows:
                print(f"  {row[0]} {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
            
        except Exception as e:
            print(f"❌ Error checking subjects table: {e}")

if __name__ == '__main__':
    check_subjects_table()