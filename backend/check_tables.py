#!/usr/bin/env python3
"""
Script to check table structures
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_table_structure(table_name):
    """Check table structure"""
    print(f"\n{table_name} table structure:")
    describe_sql = f"DESCRIBE {table_name}"
    result = db.session.execute(text(describe_sql))
    rows = result.fetchall()
    
    for row in rows:
        print(f"  {row[0]} {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")

def check_tables():
    """Check all relevant table structures"""
    
    with app.app_context():
        try:
            print("Checking table structures...")
            
            # Check students table
            check_table_structure("students")
            
            # Check prd_subjects table
            check_table_structure("prd_subjects")
            
            # Check timetable table
            check_table_structure("timetable")
            
        except Exception as e:
            print(f"❌ Error checking table structures: {e}")

if __name__ == '__main__':
    check_tables()