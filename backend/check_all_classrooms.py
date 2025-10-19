#!/usr/bin/env python3
"""
Script to check all classrooms in the database
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_all_classrooms():
    """Check all classrooms in the database"""
    
    with app.app_context():
        try:
            print("Checking all classrooms in database...")
            
            # Get all classrooms
            result = db.session.execute(text("SELECT classroom_id, room_number, building_name, floor_number, capacity FROM classrooms ORDER BY building_name, room_number"))
            rows = result.fetchall()
            
            print("\nAll Classrooms:")
            print("-" * 100)
            print(f"{'ID':<3} | {'Room Number':<12} | {'Building Name':<30} | {'Floor':<5} | {'Capacity':<8}")
            print("-" * 100)
            for row in rows:
                floor = row[3] if row[3] is not None else "N/A"
                capacity = row[4] if row[4] is not None else "N/A"
                print(f"{row[0]:<3} | {row[1]:<12} | {row[2]:<30} | {floor:<5} | {capacity:<8}")
            
            print(f"\nTotal classrooms: {len(rows)}")
                
        except Exception as e:
            print(f"Error checking classrooms: {e}")

if __name__ == '__main__':
    check_all_classrooms()