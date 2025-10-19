#!/usr/bin/env python3
"""
Script to check timetable table structure
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_timetable_table():
    """Check timetable table structure"""
    
    with app.app_context():
        try:
            print("Checking timetable table structure...")
            
            # Describe timetable table
            describe_sql = "DESCRIBE timetable"
            result = db.session.execute(text(describe_sql))
            rows = result.fetchall()
            
            print("Timetable table structure:")
            for row in rows:
                print(f"  {row[0]} {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
            
        except Exception as e:
            print(f"❌ Error checking timetable table: {e}")

if __name__ == '__main__':
    check_timetable_table()