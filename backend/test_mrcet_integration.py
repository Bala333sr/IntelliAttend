#!/usr/bin/env python3
"""
Test script to verify the MRCET integration
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def test_mrcet_integration():
    """Test the MRCET integration"""
    
    with app.app_context():
        print("Testing MRCET integration...")
        
        # Test 1: Check if MRCET department info table exists and has data
        print("\n1. Checking MRCET department info table:")
        try:
            result = db.session.execute(text("SELECT COUNT(*) as count FROM mrcet_department_info"))
            row = result.fetchone()
            count = row[0] if row else 0
            print(f"   ✅ mrcet_department_info table: {count} records")
            
            if count > 0:
                # Show sample data
                result = db.session.execute(text("SELECT department_code, intake, faculty_count, hod_name FROM mrcet_department_info LIMIT 5"))
                rows = result.fetchall()
                print("   Sample department info:")
                for row in rows:
                    print(f"     {row[0]}: Intake={row[1]}, Faculty={row[2]}, HOD={row[3]}")
        except Exception as e:
            print(f"   ❌ mrcet_department_info table check: Error - {e}")
        
        # Test 2: Check if department_details view exists
        print("\n2. Checking department_details view:")
        try:
            result = db.session.execute(text("SELECT COUNT(*) as count FROM department_details"))
            row = result.fetchone()
            count = row[0] if row else 0
            print(f"   ✅ department_details view: {count} records")
            
            if count > 0:
                # Show sample data
                result = db.session.execute(text("SELECT code, name, hod_name, intake FROM department_details WHERE intake IS NOT NULL LIMIT 5"))
                rows = result.fetchall()
                print("   Sample department details:")
                for row in rows:
                    print(f"     {row[0]} ({row[1]}): Intake={row[3]}, HOD={row[2]}")
        except Exception as e:
            print(f"   ❌ department_details view check: Error - {e}")
        
        # Test 3: Check existing departments table
        print("\n3. Checking existing departments table:")
        try:
            result = db.session.execute(text("SELECT COUNT(*) as count FROM departments"))
            row = result.fetchone()
            count = row[0] if row else 0
            print(f"   ✅ departments table: {count} records")
            
            if count > 0:
                # Show sample departments
                result = db.session.execute(text("SELECT code, name, head FROM departments LIMIT 5"))
                rows = result.fetchall()
                print("   Sample departments:")
                for row in rows:
                    print(f"     {row[0]}: {row[1]}, Head={row[2]}")
        except Exception as e:
            print(f"   ❌ departments table check: Error - {e}")
        
        # Test 4: Check existing faculty table
        print("\n4. Checking faculty table:")
        try:
            result = db.session.execute(text("SELECT COUNT(*) as count FROM faculty"))
            row = result.fetchone()
            count = row[0] if row else 0
            print(f"   ✅ faculty table: {count} records")
        except Exception as e:
            print(f"   ❌ faculty table check: Error - {e}")
        
        # Test 5: Check existing students table
        print("\n5. Checking students table:")
        try:
            result = db.session.execute(text("SELECT COUNT(*) as count FROM students"))
            row = result.fetchone()
            count = row[0] if row else 0
            print(f"   ✅ students table: {count} records")
        except Exception as e:
            print(f"   ❌ students table check: Error - {e}")
        
        print("\n✅ MRCET integration testing completed!")

if __name__ == '__main__':
    test_mrcet_integration()