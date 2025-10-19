#!/usr/bin/env python3
"""
Script to update student email
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def update_student_email():
    """Update student email"""
    
    with app.app_context():
        try:
            print("Updating student email for BALA (23N31A6645)...")
            
            # Update student email
            update_email_sql = """
            UPDATE students 
            SET email = :email
            WHERE student_code = '23N31A6645'
            """
            
            db.session.execute(text(update_email_sql), {"email": "23N31A6645@mrcet.ac.in"})
            db.session.commit()
            print("✅ Student email updated successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating student email: {e}")
            raise e

if __name__ == '__main__':
    update_student_email()