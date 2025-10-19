#!/usr/bin/env python3
"""
Test script to verify the hierarchical database structure
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def test_hierarchy():
    """Test the hierarchical database structure"""
    
    with app.app_context():
        print("Testing hierarchical database structure...")
        
        # Test 1: Check if all new tables exist and have data
        print("\n1. Checking new tables:")
        tables = ['colleges', 'departments', 'branches', 'timetables', 'schedules']
        for table in tables:
            try:
                result = db.session.execute(text(f"SELECT COUNT(*) as count FROM {table}"))
                row = result.fetchone()
                count = row[0] if row else 0
                print(f"   ✅ {table}: {count} records")
            except Exception as e:
                print(f"   ❌ {table}: Error - {e}")
        
        # Test 2: Check foreign key relationships
        print("\n2. Checking foreign key relationships:")
        try:
            # Check students branch_id
            result = db.session.execute(text("SELECT COUNT(*) as count FROM students WHERE branch_id IS NOT NULL"))
            row = result.fetchone()
            count = row[0] if row else 0
            print(f"   ✅ Students with branch_id: {count}")
        except Exception as e:
            print(f"   ❌ Students branch_id check: Error - {e}")
        
        try:
            # Check faculty department_id
            result = db.session.execute(text("SELECT COUNT(*) as count FROM faculty WHERE department_id IS NOT NULL"))
            row = result.fetchone()
            count = row[0] if row else 0
            print(f"   ✅ Faculty with department_id: {count}")
        except Exception as e:
            print(f"   ❌ Faculty department_id check: Error - {e}")
        
        try:
            # Check classes timetable_id
            result = db.session.execute(text("SELECT COUNT(*) as count FROM classes WHERE timetable_id IS NOT NULL"))
            row = result.fetchone()
            count = row[0] if row else 0
            print(f"   ✅ Classes with timetable_id: {count}")
        except Exception as e:
            print(f"   ❌ Classes timetable_id check: Error - {e}")
        
        # Test 3: Check hierarchical relationships
        print("\n3. Checking hierarchical relationships:")
        try:
            # Get a sample hierarchy
            query = """
            SELECT 
                c.name as college_name,
                d.name as department_name,
                b.name as branch_name,
                t.academic_year,
                t.semester
            FROM colleges c
            JOIN departments d ON c.id = d.college_id
            JOIN branches b ON d.id = b.department_id
            JOIN timetables t ON b.id = t.branch_id
            LIMIT 1
            """
            result = db.session.execute(text(query))
            row = result.fetchone()
            if row:
                print(f"   ✅ Hierarchy sample:")
                print(f"      College: {row[0]}")
                print(f"      Department: {row[1]}")
                print(f"      Branch: {row[2]}")
                print(f"      Academic Year: {row[3]}")
                print(f"      Semester: {row[4]}")
            else:
                print(f"   ⚠️  No hierarchy data found")
        except Exception as e:
            print(f"   ❌ Hierarchy check: Error - {e}")
        
        # Test 4: Check schedule integration
        print("\n4. Checking schedule integration:")
        try:
            # Get class schedules
            query = """
            SELECT 
                c.class_name,
                s.day_of_week,
                s.start_time,
                s.end_time
            FROM classes c
            JOIN schedules s ON c.class_id = s.class_id
            LIMIT 3
            """
            result = db.session.execute(text(query))
            rows = result.fetchall()
            if rows:
                print(f"   ✅ Class schedules found:")
                for row in rows:
                    print(f"      {row[0]}: {row[1]} {row[2]}-{row[3]}")
            else:
                print(f"   ⚠️  No schedule data found")
        except Exception as e:
            print(f"   ❌ Schedule check: Error - {e}")
        
        print("\n✅ Hierarchy testing completed!")

if __name__ == '__main__':
    test_hierarchy()