#!/usr/bin/env python3
"""
Test script to verify MRCET academic data in the database
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def test_mrcet_academic_data():
    """Test that MRCET academic data was added correctly"""
    
    with app.app_context():
        print("Testing MRCET academic data...")
        
        # Test 1: Check sections data
        print("\n1. Checking MRCET sections:")
        try:
            check_sections_sql = """
            SELECT department_code, section_name, student_count, building_name 
            FROM mrcet_sections 
            ORDER BY department_code, section_name
            """
            result = db.session.execute(text(check_sections_sql))
            rows = result.fetchall()
            
            if rows:
                print(f"   ✅ Found {len(rows)} MRCET sections:")
                # Group by department for better readability
                departments = {}
                for row in rows:
                    dept = row[0]
                    if dept not in departments:
                        departments[dept] = []
                    departments[dept].append(row)
                
                for dept, sections in departments.items():
                    print(f"     {dept}: {len(sections)} sections")
                    for section in sections[:3]:  # Show first 3 of each department
                        print(f"       - Section {section[1]}: {section[2]} students in {section[3]}")
                    if len(sections) > 3:
                        print(f"       ... and {len(sections) - 3} more sections")
            else:
                print("   ❌ No MRCET sections found")
        except Exception as e:
            print(f"   ❌ Error checking MRCET sections: {e}")
        
        # Test 2: Check attendance regulations
        print("\n2. Checking MRCET attendance regulations:")
        try:
            check_regulations_sql = """
            SELECT attendance_level, minimum_percentage, maximum_percentage, action_required 
            FROM mrcet_attendance_regulations 
            ORDER BY minimum_percentage DESC
            """
            result = db.session.execute(text(check_regulations_sql))
            rows = result.fetchall()
            
            if rows:
                print("   ✅ MRCET attendance regulations:")
                for row in rows:
                    if row[2] is not None and row[2] > 0:
                        print(f"     {row[0]}: {row[1]}% - {row[2]}% - {row[3]}")
                    else:
                        print(f"     {row[0]}: {row[1]}%+ - {row[3]}")
            else:
                print("   ❌ No MRCET attendance regulations found")
        except Exception as e:
            print(f"   ❌ Error checking MRCET attendance regulations: {e}")
        
        # Test 3: Check academic calendar
        print("\n3. Checking MRCET academic calendar:")
        try:
            check_calendar_sql = """
            SELECT event_name, event_type, start_date, end_date, duration_days 
            FROM mrcet_academic_calendar 
            ORDER BY start_date
            """
            result = db.session.execute(text(check_calendar_sql))
            rows = result.fetchall()
            
            if rows:
                print("   ✅ MRCET academic calendar events:")
                for row in rows:
                    print(f"     {row[0]} ({row[1]}): {row[2]} to {row[3]} ({row[4]} days)")
            else:
                print("   ❌ No MRCET academic calendar events found")
        except Exception as e:
            print(f"   ❌ Error checking MRCET academic calendar: {e}")
        
        # Test 4: Check mid-term structure
        print("\n4. Checking MRCET mid-term examination structure:")
        try:
            check_structure_sql = """
            SELECT midterm_number, units_covered, weeks_conducted, duration_hours, total_marks 
            FROM mrcet_midterm_structure 
            ORDER BY midterm_number
            """
            result = db.session.execute(text(check_structure_sql))
            rows = result.fetchall()
            
            if rows:
                print("   ✅ MRCET mid-term examination structure:")
                for row in rows:
                    print(f"     Mid {row[0]}: {row[1]} in {row[2]}, {row[3]} hours, {row[4]} marks")
            else:
                print("   ❌ No MRCET mid-term examination structure found")
        except Exception as e:
            print(f"   ❌ Error checking MRCET mid-term examination structure: {e}")
        
        # Test 5: Check grading system
        print("\n5. Checking MRCET grading system:")
        try:
            check_grading_sql = """
            SELECT subject_type, component, total_marks 
            FROM mrcet_grading_system 
            ORDER BY subject_type, component
            """
            result = db.session.execute(text(check_grading_sql))
            rows = result.fetchall()
            
            if rows:
                print("   ✅ MRCET grading system components:")
                for row in rows:
                    print(f"     {row[0]} - {row[1]}: {row[2]} marks")
            else:
                print("   ❌ No MRCET grading system components found")
        except Exception as e:
            print(f"   ❌ Error checking MRCET grading system: {e}")
        
        print("\n✅ MRCET academic data testing completed!")

if __name__ == '__main__':
    test_mrcet_academic_data()