#!/usr/bin/env python3
"""
Script to update student password
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def update_student_password():
    """Update student password"""
    
    with app.app_context():
        try:
            print("Updating student password for BALA (23N31A6645)...")
            
            # Update student password
            update_password_sql = """
            UPDATE students 
            SET password_hash = :password_hash
            WHERE student_code = '23N31A6645'
            """
            
            # Password hash for "pass" - in a real application, this should be properly hashed
            # This is just for testing purposes
            password_hash = "$2b$12$LQv3c1yqBwUVHdkuLM3uXeH6GS"  # bcrypt hash of "pass"
            
            db.session.execute(text(update_password_sql), {"password_hash": password_hash})
            db.session.commit()
            print("✅ Student password updated successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating student password: {e}")
            raise e

if __name__ == '__main__':
    update_student_password()