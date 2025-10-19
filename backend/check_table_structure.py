#!/usr/bin/env python3
"""
Script to check table structure
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_table_structure():
    """Check table structure"""
    
    with app.app_context():
        try:
            print("Checking subjects table structure...")
            
            result = db.session.execute(text('DESCRIBE subjects'))
            rows = result.fetchall()
            for row in rows:
                print(row)
                
            print("\nChecking sections table structure...")
            
            result = db.session.execute(text('DESCRIBE sections'))
            rows = result.fetchall()
            for row in rows:
                print(row)
            
        except Exception as e:
            print(f"Error checking table structure: {e}")
            raise e

if __name__ == '__main__':
    check_table_structure()