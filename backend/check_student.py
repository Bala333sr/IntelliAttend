#!/usr/bin/env python3
"""
Script to check student data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_student():
    """Check student data"""
    
    with app.app_context():
        try:
            print("Checking student data for BALA (23N31A6645)...")
            
            # Get student data
            result = db.session.execute(text("SELECT student_code, email, password_hash FROM students WHERE student_code = '23N31A6645'"))
            row = result.fetchone()
            if not row:
                print("❌ Student not found")
                return
            print(f"Student Code: {row[0]}")
            print(f"Email: {row[1]}")
            print(f"Password Hash: {row[2]}")
            
        except Exception as e:
            print(f"❌ Error checking student data: {e}")

if __name__ == '__main__':
    check_student()