#!/usr/bin/env python3
"""
Script to populate the hierarchical database structure with sample data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text
import random
from datetime import datetime, timedelta

def populate_hierarchical_data():
    """Populate the hierarchical database with sample data"""
    
    with app.app_context():
        try:
            print("Starting hierarchical data population...")
            
            # 1. Get or create default college
            print("1. Getting/creating default college...")
            check_college_sql = "SELECT id FROM colleges WHERE code = 'MRCET' LIMIT 1"
            result = db.session.execute(text(check_college_sql)).fetchone()
            
            if not result:
                insert_college_sql = """
                INSERT INTO colleges (name, code, address, contact_info) 
                VALUES ('Malla Reddy College of Engineering & Technology', 'MRCET', 
                        'Maisammaguda, Dhulapally Post, Via Hakimpet, Secunderabad–500100', 
                        'contact@mrcet.edu.in')
                """
                db.session.execute(text(insert_college_sql))
                result = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
                college_id = result[0] if result else 1
                print(f"   Created college with ID: {college_id}")
            else:
                college_id = result[0] if result else 1
                print(f"   Using existing college with ID: {college_id}")
            
            # 2. Get or create default department
            print("2. Getting/creating default department...")
            check_department_sql = "SELECT id FROM departments WHERE code = 'CSE' AND college_id = :college_id LIMIT 1"
            result = db.session.execute(text(check_department_sql), {'college_id': college_id}).fetchone()
            
            if not result:
                insert_department_sql = """
                INSERT INTO departments (college_id, name, code, head) 
                VALUES (:college_id, 'Computer Science and Engineering', 'CSE', 'Dr. Kanniaah')
                """
                db.session.execute(text(insert_department_sql), {'college_id': college_id})
                result = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
                department_id = result[0] if result else 1
                print(f"   Created department with ID: {department_id}")
            else:
                department_id = result[0] if result else 1
                print(f"   Using existing department with ID: {department_id}")
            
            # 3. Get or create default branch
            print("3. Getting/creating default branch...")
            check_branch_sql = "SELECT id FROM branches WHERE code = 'B.Tech-CSE' AND department_id = :department_id LIMIT 1"
            result = db.session.execute(text(check_branch_sql), {'department_id': department_id}).fetchone()
            
            if not result:
                insert_branch_sql = """
                INSERT INTO branches (department_id, name, code, degree_type, duration) 
                VALUES (:department_id, 'B.Tech Computer Science and Engineering', 'B.Tech-CSE', 'B.Tech', 4)
                """
                db.session.execute(text(insert_branch_sql), {'department_id': department_id})
                result = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
                branch_id = result[0] if result else 1
                print(f"   Created branch with ID: {branch_id}")
            else:
                branch_id = result[0] if result else 1
                print(f"   Using existing branch with ID: {branch_id}")
            
            # 4. Get or create timetable
            print("4. Getting/creating timetable...")
            check_timetable_sql = """
            SELECT id FROM timetables WHERE branch_id = :branch_id AND academic_year = '2025-26' AND semester = 'Fall' LIMIT 1
            """
            result = db.session.execute(text(check_timetable_sql), {'branch_id': branch_id}).fetchone()
            
            if not result:
                insert_timetable_sql = """
                INSERT INTO timetables (branch_id, academic_year, semester) 
                VALUES (:branch_id, '2025-26', 'Fall')
                """
                db.session.execute(text(insert_timetable_sql), {'branch_id': branch_id})
                result = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
                timetable_id = result[0] if result else 1
                print(f"   Created timetable with ID: {timetable_id}")
            else:
                timetable_id = result[0] if result else 1
                print(f"   Using existing timetable with ID: {timetable_id}")
            
            # 5. Update existing students with branch_id if not set
            print("5. Updating students with branch_id...")
            update_students_sql = """
            UPDATE students SET branch_id = :branch_id WHERE branch_id IS NULL
            """
            result = db.session.execute(text(update_students_sql), {'branch_id': branch_id})
            # Note: rowcount may not be available in all SQLAlchemy versions
            print(f"   Updated students with branch_id")
            
            # 6. Update existing faculty with department_id if not set
            print("6. Updating faculty with department_id...")
            update_faculty_sql = """
            UPDATE faculty SET department_id = :department_id WHERE department_id IS NULL
            """
            result = db.session.execute(text(update_faculty_sql), {'department_id': department_id})
            # Note: rowcount may not be available in all SQLAlchemy versions
            print(f"   Updated faculty with department_id")
            
            # 7. Update existing classes with timetable_id if not set
            print("7. Updating classes with timetable_id...")
            update_classes_sql = """
            UPDATE classes SET timetable_id = :timetable_id WHERE timetable_id IS NULL
            """
            result = db.session.execute(text(update_classes_sql), {'timetable_id': timetable_id})
            # Note: rowcount may not be available in all SQLAlchemy versions
            print(f"   Updated classes with timetable_id")
            
            # 8. Populate schedules table with sample data if empty
            print("8. Populating schedules table...")
            check_schedules_sql = "SELECT COUNT(*) as count FROM schedules"
            result = db.session.execute(text(check_schedules_sql)).fetchone()
            
            if result and result[0] == 0:
                # Get all classes
                get_classes_sql = "SELECT class_id, class_code FROM classes"
                classes_result = db.session.execute(text(get_classes_sql)).fetchall()
                
                # Sample schedule data
                schedule_data = [
                    {"day": "Monday", "start": "09:00:00", "end": "10:30:00", "type": "regular"},
                    {"day": "Monday", "start": "11:00:00", "end": "12:30:00", "type": "regular"},
                    {"day": "Tuesday", "start": "10:00:00", "end": "11:30:00", "type": "regular"},
                    {"day": "Tuesday", "start": "14:00:00", "end": "15:30:00", "type": "regular"},
                    {"day": "Wednesday", "start": "09:30:00", "end": "11:00:00", "type": "regular"},
                    {"day": "Wednesday", "start": "11:30:00", "end": "13:00:00", "type": "lab"},
                    {"day": "Thursday", "start": "10:30:00", "end": "12:00:00", "type": "regular"},
                    {"day": "Friday", "start": "13:00:00", "end": "14:30:00", "type": "regular"},
                    {"day": "Friday", "start": "15:00:00", "end": "16:30:00", "type": "lab"}
                ]
                
                # Insert schedule data for each class
                insert_schedule_sql = """
                INSERT INTO schedules (class_id, day_of_week, start_time, end_time, schedule_type)
                VALUES (:class_id, :day, :start_time, :end_time, :schedule_type)
                """
                
                schedule_count = 0
                for class_row in classes_result:
                    class_id = class_row[0]
                    class_code = class_row[1]
                    
                    # Insert 3-5 random schedules for each class
                    num_schedules = random.randint(3, 5)
                    selected_schedules = random.sample(schedule_data, min(num_schedules, len(schedule_data)))
                    
                    for sched in selected_schedules:
                        db.session.execute(text(insert_schedule_sql), {
                            'class_id': class_id,
                            'day': sched['day'],
                            'start_time': sched['start'],
                            'end_time': sched['end'],
                            'schedule_type': sched['type']
                        })
                        schedule_count += 1
                
                print(f"   Inserted {schedule_count} schedule entries")
            elif result:
                print(f"   Schedules table already contains {result[0]} entries")
            else:
                print("   Could not determine schedule table count")
            
            # 9. Create sample attendance sessions for the next week
            print("9. Creating sample attendance sessions...")
            # Get classes that don't have sessions yet for this week
            get_classes_for_sessions_sql = """
            SELECT c.class_id, c.class_name, c.faculty_id
            FROM classes c
            LEFT JOIN attendance_sessions a ON c.class_id = a.class_id 
                AND a.session_date >= CURDATE() 
                AND a.session_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            WHERE a.class_id IS NULL
            LIMIT 5
            """
            
            classes_for_sessions = db.session.execute(text(get_classes_for_sessions_sql)).fetchall()
            
            if classes_for_sessions:
                insert_session_sql = """
                INSERT INTO attendance_sessions 
                (class_id, faculty_id, session_date, start_time, status)
                VALUES (:class_id, :faculty_id, :session_date, :start_time, 'active')
                """
                
                session_count = 0
                for class_row in classes_for_sessions:
                    class_id, class_name, faculty_id = class_row
                    
                    # Create sessions for the next 3 days
                    for i in range(1, 4):
                        session_date = datetime.now() + timedelta(days=i)
                        start_time = session_date.replace(hour=9, minute=0, second=0)
                        
                        db.session.execute(text(insert_session_sql), {
                            'class_id': class_id,
                            'faculty_id': faculty_id,
                            'session_date': session_date.date(),
                            'start_time': start_time
                        })
                        session_count += 1
                
                print(f"   Created {session_count} attendance sessions")
            else:
                print("   No new attendance sessions needed")
            
            db.session.commit()
            print("✅ Hierarchical data population completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error populating hierarchical data: {e}")
            raise e

if __name__ == '__main__':
    populate_hierarchical_data()