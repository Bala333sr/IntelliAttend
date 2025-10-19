#!/usr/bin/env python3
"""
Script to check sections table structure
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_sections_table():
    """Check sections table structure"""
    
    with app.app_context():
        try:
            print("Checking sections table structure...")
            
            # Describe sections table
            describe_sql = "DESCRIBE sections"
            result = db.session.execute(text(describe_sql))
            rows = result.fetchall()
            
            print("Sections table structure:")
            for row in rows:
                print(f"  {row[0]} {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
            
        except Exception as e:
            print(f"❌ Error checking sections table: {e}")

if __name__ == '__main__':
    check_sections_table()