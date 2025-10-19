#!/usr/bin/env python3
"""
Script to update student password with correct hash
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def update_student_password():
    """Update student password with correct hash"""
    
    with app.app_context():
        try:
            print("Updating student password for BALA (23N31A6645) with correct hash...")
            
            # Update student password
            update_password_sql = """
            UPDATE students 
            SET password_hash = :password_hash
            WHERE student_code = '23N31A6645'
            """
            
            # Password hash for "pass" - generated with bcrypt
            password_hash = "$2b$12$WJ/0L18KtPb2V9lqPLntOere37rce0YqJZErOiZPZBVXeDRySeO52"
            
            db.session.execute(text(update_password_sql), {"password_hash": password_hash})
            db.session.commit()
            print("✅ Student password updated successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating student password: {e}")
            raise e

if __name__ == '__main__':
    update_student_password()