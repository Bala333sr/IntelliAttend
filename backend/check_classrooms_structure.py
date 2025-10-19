#!/usr/bin/env python3
"""
Script to check the structure of the classrooms table
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_classrooms_structure():
    """Check the structure of the classrooms table"""
    
    with app.app_context():
        try:
            print("Checking classrooms table structure...")
            
            # Get table structure
            result = db.session.execute(text("SHOW COLUMNS FROM classrooms"))
            rows = result.fetchall()
            
            print("Classrooms table columns:")
            for row in rows:
                print(f"  - {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
                
        except Exception as e:
            print(f"Error checking classrooms structure: {e}")

if __name__ == '__main__':
    check_classrooms_structure()