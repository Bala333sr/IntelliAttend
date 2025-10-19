#!/usr/bin/env python3
"""
Script to populate the MRCET database with department, faculty, and initial data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def populate_mrcet_data():
    """Populate the MRCET database with initial data"""
    
    with app.app_context():
        try:
            print("Starting MRCET data population...")
            
            # 1. Create or get college
            print("1. Creating/updating college...")
            check_college_sql = "SELECT id FROM colleges WHERE code = 'MRCET' LIMIT 1"
            result = db.session.execute(text(check_college_sql)).fetchone()
            
            if not result:
                insert_college_sql = """
                INSERT INTO colleges (name, code, address) 
                VALUES ('Malla Reddy College of Engineering & Technology', 'MRCET', 
                        'Maisammaguda, Dhulapally Post, Via Hakimpet, Secunderabad–500100')
                """
                db.session.execute(text(insert_college_sql))
                result = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
                college_id = result[0] if result else 1
                print(f"   Created college with ID: {college_id}")
            else:
                college_id = result[0] if result else 1
                print(f"   Using existing college with ID: {college_id}")
            
            # 2. Populate departments
            print("2. Populating departments...")
            departments_data = [
                {"name": "Computer Science Engineering", "code": "CSE", "head": "Dr. Dandu Sujatha"},
                {"name": "CSE - AI & ML", "code": "CSE-AI", "head": "Dr. K Asish Vardhan"},
                {"name": "CSE - Data Science", "code": "CSE-DS", "head": "Dr. Aitharaju Venkata Lakshmi Narasimha Sujith"},
                {"name": "CSE - Cyber Security", "code": "CSE-CS", "head": "Dr. Lalband Neelu"},
                {"name": "CSE - IoT", "code": "CSE-IoT", "head": "Dr. Jawahar Muthusamy"},
                {"name": "Information Technology", "code": "IT", "head": "Dr. G. Sharada"},
                {"name": "Electronics & Communication Engineering", "code": "ECE", "head": "Dr. K Mallikarjuna Lingam"},
                {"name": "Electrical & Electronics Engineering", "code": "EEE", "head": "Dr. M. Sharanya"},
                {"name": "Mechanical Engineering", "code": "MECH", "head": "Dr. Srikar Potnuru"},
                {"name": "Aeronautical Engineering", "code": "AERO", "head": "Prof. Misba Mehdi"},
                {"name": "Civil Engineering", "code": "CIVIL", "head": "TBD"},
                {"name": "Humanities & Sciences", "code": "H&S", "head": "Dr. V Madhusudhan Reddy"}
            ]
            
            # Dictionary to store department codes for reference
            department_codes = {
                "CSE": "31", "CSE-AI": "31", "CSE-DS": "31", "CSE-CS": "31", "CSE-IoT": "31",
                "IT": "35", "ECE": "32", "EEE": "33", "MECH": "34", "AERO": "36", "CIVIL": "37", "H&S": "38"
            }
            
            for dept in departments_data:
                check_dept_sql = "SELECT id FROM departments WHERE code = :code AND college_id = :college_id LIMIT 1"
                result = db.session.execute(text(check_dept_sql), {'code': dept['code'], 'college_id': college_id}).fetchone()
                
                if not result:
                    insert_dept_sql = """
                    INSERT INTO departments (college_id, name, code, head)
                    VALUES (:college_id, :name, :code, :head)
                    """
                    db.session.execute(text(insert_dept_sql), {
                        'college_id': college_id,
                        'name': dept['name'],
                        'code': dept['code'],
                        'head': dept['head']
                    })
                    print(f"   Created department: {dept['name']}")
                else:
                    print(f"   Department already exists: {dept['name']}")
            
            # 3. Create sample courses
            print("3. Creating sample courses...")
            courses_data = [
                {"name": "Database Management Systems", "code": "R22A0504", "credits": 3, "course_type": "Theory"},
                {"name": "Software Engineering", "code": "R22A0505", "credits": 3, "course_type": "Theory"},
                {"name": "Design and Analysis of Algorithms", "code": "R22A0506", "credits": 3, "course_type": "Theory"},
                {"name": "Data Structures", "code": "R22A0507", "credits": 3, "course_type": "Theory"},
                {"name": "Probability and Statistical Theory", "code": "R22A0508", "credits": 3, "course_type": "Theory"},
                {"name": "Professional Practice Guide", "code": "R22A0509", "credits": 1, "course_type": "Theory"},
                {"name": "Database Management Systems Lab", "code": "R22A0514", "credits": 2, "course_type": "Lab"},
                {"name": "Software Engineering Lab", "code": "R22A0515", "credits": 2, "course_type": "Lab"}
            ]
            
            for course in courses_data:
                check_course_sql = "SELECT id FROM courses WHERE code = :code LIMIT 1"
                result = db.session.execute(text(check_course_sql), {'code': course['code']}).fetchone()
                
                if not result:
                    insert_course_sql = """
                    INSERT INTO courses (name, code, credits, course_type)
                    VALUES (:name, :code, :credits, :course_type)
                    """
                    db.session.execute(text(insert_course_sql), course)
                    print(f"   Created course: {course['name']}")
                else:
                    print(f"   Course already exists: {course['name']}")
            
            # 4. Create sample rooms
            print("4. Creating sample rooms...")
            rooms_data = [
                # CSE rooms (2nd and 3rd floors)
                {"room_number": "2201", "room_type": "Lecture Hall", "floor_number": 2, "capacity": 70, "building_name": "CSE Building"},
                {"room_number": "2202", "room_type": "Lecture Hall", "floor_number": 2, "capacity": 70, "building_name": "CSE Building"},
                {"room_number": "2203", "room_type": "Laboratory", "floor_number": 2, "capacity": 40, "building_name": "CSE Building"},
                {"room_number": "2204", "room_type": "Laboratory", "floor_number": 2, "capacity": 40, "building_name": "CSE Building"},
                {"room_number": "3201", "room_type": "Lecture Hall", "floor_number": 3, "capacity": 70, "building_name": "CSE Building"},
                {"room_number": "3202", "room_type": "Lecture Hall", "floor_number": 3, "capacity": 70, "building_name": "CSE Building"},
                {"room_number": "3203", "room_type": "Laboratory", "floor_number": 3, "capacity": 40, "building_name": "CSE Building"},
                {"room_number": "3204", "room_type": "Laboratory", "floor_number": 3, "capacity": 40, "building_name": "CSE Building"},
                
                # ECE rooms (4th and 5th floors)
                {"room_number": "4201", "room_type": "Lecture Hall", "floor_number": 4, "capacity": 70, "building_name": "ECE Building"},
                {"room_number": "4202", "room_type": "Lecture Hall", "floor_number": 4, "capacity": 70, "building_name": "ECE Building"},
                {"room_number": "5201", "room_type": "Lecture Hall", "floor_number": 5, "capacity": 70, "building_name": "ECE Building"},
                {"room_number": "5202", "room_type": "Laboratory", "floor_number": 5, "capacity": 40, "building_name": "ECE Building"},
                
                # MECH rooms (1st and 2nd floors)
                {"room_number": "1201", "room_type": "Lecture Hall", "floor_number": 1, "capacity": 70, "building_name": "MECH Building"},
                {"room_number": "1202", "room_type": "Laboratory", "floor_number": 1, "capacity": 40, "building_name": "MECH Building"},
                {"room_number": "2401", "room_type": "Lecture Hall", "floor_number": 2, "capacity": 70, "building_name": "MECH Building"},
                
                # Common rooms
                {"room_number": "1101", "room_type": "Seminar Hall", "floor_number": 1, "capacity": 150, "building_name": "Main Building"},
                {"room_number": "1102", "room_type": "Seminar Hall", "floor_number": 1, "capacity": 100, "building_name": "Main Building"}
            ]
            
            for room in rooms_data:
                check_room_sql = "SELECT id FROM rooms WHERE room_number = :room_number LIMIT 1"
                result = db.session.execute(text(check_room_sql), {'room_number': room['room_number']}).fetchone()
                
                if not result:
                    insert_room_sql = """
                    INSERT INTO rooms (room_number, room_type, floor_number, capacity, building_name)
                    VALUES (:room_number, :room_type, :floor_number, :capacity, :building_name)
                    """
                    db.session.execute(text(insert_room_sql), room)
                    print(f"   Created room: {room['room_number']}")
                else:
                    print(f"   Room already exists: {room['room_number']}")
            
            # 5. Create academic calendar for 2024-25
            print("5. Creating academic calendar...")
            check_calendar_sql = "SELECT id FROM academic_calendars WHERE academic_year = '2024-25' LIMIT 1"
            result = db.session.execute(text(check_calendar_sql)).fetchone()
            
            if not result:
                insert_calendar_sql = """
                INSERT INTO academic_calendars (academic_year, start_date, end_date)
                VALUES ('2024-25', '2024-12-09', '2025-04-26')
                """
                db.session.execute(text(insert_calendar_sql))
                result = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
                calendar_id = result[0] if result else 1
                print(f"   Created academic calendar with ID: {calendar_id}")
            else:
                calendar_id = result[0] if result else 1
                print(f"   Using existing academic calendar with ID: {calendar_id}")
            
            # 6. Create semesters
            print("6. Creating semesters...")
            semesters_data = [
                {"academic_calendar_id": calendar_id, "semester_name": "I Spell", "start_date": "2024-12-09", "end_date": "2025-02-01", "spell": "I Spell"},
                {"academic_calendar_id": calendar_id, "semester_name": "I Mid Exams", "start_date": "2025-02-03", "end_date": "2025-02-05", "spell": "I Spell"},
                {"academic_calendar_id": calendar_id, "semester_name": "II Spell", "start_date": "2025-02-06", "end_date": "2025-04-01", "spell": "II Spell"},
                {"academic_calendar_id": calendar_id, "semester_name": "II Mid Exams", "start_date": "2025-04-02", "end_date": "2025-04-05", "spell": "II Spell"},
                {"academic_calendar_id": calendar_id, "semester_name": "End Semester Exams", "start_date": "2025-04-14", "end_date": "2025-04-26", "spell": "II Spell"}
            ]
            
            for semester in semesters_data:
                check_semester_sql = """
                SELECT id FROM semesters 
                WHERE academic_calendar_id = :academic_calendar_id AND semester_name = :semester_name 
                LIMIT 1
                """
                result = db.session.execute(text(check_semester_sql), {
                    'academic_calendar_id': semester['academic_calendar_id'],
                    'semester_name': semester['semester_name']
                }).fetchone()
                
                if not result:
                    insert_semester_sql = """
                    INSERT INTO semesters (academic_calendar_id, semester_name, start_date, end_date, spell)
                    VALUES (:academic_calendar_id, :semester_name, :start_date, :end_date, :spell)
                    """
                    db.session.execute(text(insert_semester_sql), semester)
                    print(f"   Created semester: {semester['semester_name']}")
                else:
                    print(f"   Semester already exists: {semester['semester_name']}")
            
            db.session.commit()
            print("✅ MRCET data population completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error populating MRCET data: {e}")
            raise e

if __name__ == '__main__':
    populate_mrcet_data()