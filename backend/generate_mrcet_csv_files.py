#!/usr/bin/env python3
"""
Script to generate CSV files for MRCET academic data
"""

import sys
import os
import csv
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def generate_mrcet_csv_files():
    """Generate CSV files for MRCET academic data"""
    
    with app.app_context():
        try:
            print("Generating MRCET CSV files...")
            
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'CSV_DATA')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate sections CSV
            print("1. Generating mrcet_section_wise_students.csv...")
            sections_sql = """
            SELECT department_code, section_name, student_count, building_name 
            FROM mrcet_sections 
            ORDER BY department_code, section_name
            """
            result = db.session.execute(text(sections_sql))
            rows = result.fetchall()
            
            sections_csv_path = os.path.join(output_dir, 'mrcet_section_wise_students.csv')
            with open(sections_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Department', 'Section', 'Students/Section', 'Building'])
                for row in rows:
                    writer.writerow([row[0], row[1], row[2], row[3]])
            print(f"   ✅ Generated {sections_csv_path}")
            
            # Generate attendance regulations CSV
            print("2. Generating mrcet_attendance_regulations.csv...")
            regulations_sql = """
            SELECT attendance_level, minimum_percentage, maximum_percentage, action_required, consequences
            FROM mrcet_attendance_regulations 
            ORDER BY minimum_percentage DESC
            """
            result = db.session.execute(text(regulations_sql))
            rows = result.fetchall()
            
            regulations_csv_path = os.path.join(output_dir, 'mrcet_attendance_regulations.csv')
            with open(regulations_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Attendance Level', 'Minimum Percentage', 'Maximum Percentage', 'Action Required', 'Consequences'])
                for row in rows:
                    writer.writerow([row[0], row[1], row[2], row[3], row[4]])
            print(f"   ✅ Generated {regulations_csv_path}")
            
            # Generate academic calendar CSV
            print("3. Generating mrcet_examination_schedule.csv...")
            calendar_sql = """
            SELECT event_name, event_type, start_date, end_date, duration_days, notes
            FROM mrcet_academic_calendar 
            ORDER BY start_date
            """
            result = db.session.execute(text(calendar_sql))
            rows = result.fetchall()
            
            calendar_csv_path = os.path.join(output_dir, 'mrcet_examination_schedule.csv')
            with open(calendar_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Event Name', 'Event Type', 'Start Date', 'End Date', 'Duration (Days)', 'Notes'])
                for row in rows:
                    writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5]])
            print(f"   ✅ Generated {calendar_csv_path}")
            
            print(f"\n✅ All MRCET CSV files generated successfully in {output_dir}")
            
        except Exception as e:
            print(f"❌ Error generating MRCET CSV files: {e}")
            raise e

if __name__ == '__main__':
    generate_mrcet_csv_files()