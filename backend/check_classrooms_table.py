#!/usr/bin/env python3
"""
Script to check the structure of the classrooms table
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_classrooms_table():
    """Check the structure of the classrooms table"""
    
    with app.app_context():
        try:
            print("Checking classrooms table structure...")
            
            # Get table structure
            result = db.session.execute(text("DESCRIBE classrooms"))
            rows = result.fetchall()
            
            print("\nClassrooms table columns:")
            print("-" * 60)
            for row in rows:
                null_status = "NULL" if row[2] == 'YES' else "NOT NULL"
                print(f"{row[0]:20} {row[1]:15} {null_status}")
            
            # Check if we have any data
            result = db.session.execute(text("SELECT COUNT(*) as count FROM classrooms"))
            row = result.fetchone()
            if row is not None:
                print(f"\nTotal classrooms in database: {row[0]}")
                
                if row[0] > 0:
                    print("\nSample classrooms:")
                    result = db.session.execute(text("SELECT classroom_id, room_number, building_name FROM classrooms LIMIT 5"))
                    rows = result.fetchall()
                    for row in rows:
                        print(f"  {row[0]:2} | {row[1]:12} | {row[2]}")
            else:
                print("\nNo data found in classrooms table")
                
        except Exception as e:
            print(f"Error checking classrooms table: {e}")

if __name__ == '__main__':
    check_classrooms_table()