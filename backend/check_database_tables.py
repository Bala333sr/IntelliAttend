#!/usr/bin/env python3
"""
Script to check all database tables
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_database_tables():
    """Check all database tables"""
    
    with app.app_context():
        try:
            print("Checking database tables...")
            
            # Get all tables
            result = db.session.execute(text("SHOW TABLES"))
            rows = result.fetchall()
            
            print("\nDatabase Tables:")
            print("-" * 30)
            table_names = []
            for row in rows:
                table_names.append(row[0])
                print(row[0])
            
            # Check if classes table exists and references classrooms
            if 'classes' in table_names:
                print("\nChecking classes table structure...")
                result = db.session.execute(text("DESCRIBE classes"))
                rows = result.fetchall()
                
                print("\nClasses table columns:")
                print("-" * 50)
                for row in rows:
                    null_status = "NULL" if row[2] == 'YES' else "NOT NULL"
                    print(f"{row[0]:20} {row[1]:15} {null_status}")
                
                # Check for foreign key constraints
                print("\nChecking foreign key constraints...")
                result = db.session.execute(text("SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_NAME = 'classrooms'"))
                rows = result.fetchall()
                
                if rows:
                    print("Foreign key constraints referencing classrooms:")
                    for row in rows:
                        print(f"  {row[0]}: {row[1]}.{row[2]} -> {row[3]}.{row[4]}")
                else:
                    print("No foreign key constraints referencing classrooms")
            
        except Exception as e:
            print(f"Error checking database tables: {e}")

if __name__ == '__main__':
    check_database_tables()