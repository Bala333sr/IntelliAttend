#!/usr/bin/env python3
"""
Data Migration Script
Copies data from old Flask/SQLite database to new FastAPI database
"""

import sqlite3
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLD_DB_PATH = "../backend/instance/intelliattend_dev.db"
NEW_DB_PATH = "./intelliattend_v2.db"

def migrate_data():
    """Migrate data from old database to new database"""
    try:
        # Connect to old database
        logger.info(f"Connecting to old database: {OLD_DB_PATH}")
        old_conn = sqlite3.connect(OLD_DB_PATH)
        old_conn.row_factory = sqlite3.Row
        old_cursor = old_conn.cursor()
        
        # Connect to new database
        logger.info(f"Connecting to new database: {NEW_DB_PATH}")
        new_engine = create_engine(f"sqlite:///{NEW_DB_PATH}")
        Session = sessionmaker(bind=new_engine)
        new_session = Session()
        
        # Migrate Students
        logger.info("Migrating students...")
        # First, check if section_id column exists
        old_cursor.execute("PRAGMA table_info(students)")
        columns = [row[1] for row in old_cursor.fetchall()]
        has_section_id = 'section_id' in columns
        
        if has_section_id:
            old_cursor.execute("""
                SELECT student_id, student_code, first_name, last_name, email, 
                       phone_number, year_of_study, program, password_hash, is_active, 
                       created_at, updated_at, section_id
                FROM students
            """)
        else:
            old_cursor.execute("""
                SELECT student_id, student_code, first_name, last_name, email, 
                       phone_number, year_of_study, program, password_hash, is_active, 
                       created_at, updated_at
                FROM students
            """)
        students = old_cursor.fetchall()
        
        for student in students:
            try:
                student_dict = dict(student)
                # Add section_id if it doesn't exist
                if 'section_id' not in student_dict:
                    student_dict['section_id'] = None
                    
                new_session.execute(text("""
                    INSERT OR IGNORE INTO students 
                    (student_id, student_code, first_name, last_name, email, 
                     phone_number, year_of_study, program, password_hash, is_active, 
                     created_at, updated_at, section_id)
                    VALUES (:student_id, :student_code, :first_name, :last_name, :email,
                            :phone_number, :year_of_study, :program, :password_hash, :is_active,
                            :created_at, :updated_at, :section_id)
                """), student_dict)
            except Exception as e:
                logger.warning(f"Could not migrate student {dict(student)['student_code']}: {e}")
        
        new_session.commit()
        logger.info(f"Migrated {len(students)} students")
        
        # Migrate Faculty
        logger.info("Migrating faculty...")
        old_cursor.execute("""
            SELECT faculty_id, faculty_code, first_name, last_name, email,
                   phone_number, department, password_hash, is_active,
                   created_at, updated_at
            FROM faculty
        """)
        faculty_members = old_cursor.fetchall()
        
        for faculty in faculty_members:
            try:
                new_session.execute(text("""
                    INSERT OR IGNORE INTO faculty
                    (faculty_id, faculty_code, first_name, last_name, email,
                     phone_number, department, password_hash, is_active,
                     created_at, updated_at)
                    VALUES (:faculty_id, :faculty_code, :first_name, :last_name, :email,
                            :phone_number, :department, :password_hash, :is_active,
                            :created_at, :updated_at)
                """), {
                    'faculty_id': faculty['faculty_id'],
                    'faculty_code': faculty['faculty_code'],
                    'first_name': faculty['first_name'],
                    'last_name': faculty['last_name'],
                    'email': faculty['email'],
                    'phone_number': faculty['phone_number'],
                    'department': faculty['department'],
                    'password_hash': faculty['password_hash'],
                    'is_active': faculty['is_active'],
                    'created_at': faculty['created_at'],
                    'updated_at': faculty['updated_at']
                })
            except Exception as e:
                logger.warning(f"Could not migrate faculty {faculty['faculty_code']}: {e}")
        
        new_session.commit()
        logger.info(f"Migrated {len(faculty_members)} faculty members")
        
        # Migrate Sections
        logger.info("Migrating sections...")
        try:
            old_cursor.execute("""
                SELECT id, section_name, course, room_number, created_at
                FROM sections
            """)
            sections = old_cursor.fetchall()
            
            for section in sections:
                try:
                    new_session.execute(text("""
                        INSERT OR IGNORE INTO sections
                        (id, section_name, course, room_number, created_at)
                        VALUES (:id, :section_name, :course, :room_number, :created_at)
                    """), {
                        'id': section['id'],
                        'section_name': section['section_name'],
                        'course': section['course'],
                        'room_number': section['room_number'],
                        'created_at': section['created_at']
                    })
                except Exception as e:
                    logger.warning(f"Could not migrate section {section['section_name']}: {e}")
            
            new_session.commit()
            logger.info(f"Migrated {len(sections)} sections")
        except Exception as e:
            logger.warning(f"Could not migrate sections: {e}")
        
        # Migrate Timetable
        logger.info("Migrating timetable...")
        try:
            old_cursor.execute("""
                SELECT id, section_id, day_of_week, slot_number, slot_type,
                       start_time, end_time, subject_code, subject_name,
                       faculty_name, room_number
                FROM timetable
            """)
            timetable_entries = old_cursor.fetchall()
            
            for entry in timetable_entries:
                try:
                    new_session.execute(text("""
                        INSERT OR IGNORE INTO timetable
                        (id, section_id, day_of_week, slot_number, slot_type,
                         start_time, end_time, subject_code, subject_name,
                         faculty_name, room_number)
                        VALUES (:id, :section_id, :day_of_week, :slot_number, :slot_type,
                                :start_time, :end_time, :subject_code, :subject_name,
                                :faculty_name, :room_number)
                    """), {
                        'id': entry['id'],
                        'section_id': entry['section_id'],
                        'day_of_week': entry['day_of_week'],
                        'slot_number': entry['slot_number'],
                        'slot_type': entry['slot_type'],
                        'start_time': entry['start_time'],
                        'end_time': entry['end_time'],
                        'subject_code': entry['subject_code'],
                        'subject_name': entry['subject_name'],
                        'faculty_name': entry['faculty_name'],
                        'room_number': entry['room_number']
                    })
                except Exception as e:
                    logger.warning(f"Could not migrate timetable entry {entry['id']}: {e}")
            
            new_session.commit()
            logger.info(f"Migrated {len(timetable_entries)} timetable entries")
        except Exception as e:
            logger.warning(f"Could not migrate timetable: {e}")
        
        # Migrate Subjects
        logger.info("Migrating subjects...")
        try:
            old_cursor.execute("""
                SELECT id, subject_code, subject_name, short_name, faculty_name
                FROM subjects
            """)
            subjects = old_cursor.fetchall()
            
            for subject in subjects:
                try:
                    new_session.execute(text("""
                        INSERT OR IGNORE INTO subjects
                        (id, subject_code, subject_name, short_name, faculty_name)
                        VALUES (:id, :subject_code, :subject_name, :short_name, :faculty_name)
                    """), {
                        'id': subject['id'],
                        'subject_code': subject['subject_code'],
                        'subject_name': subject['subject_name'],
                        'short_name': subject['short_name'],
                        'faculty_name': subject['faculty_name']
                    })
                except Exception as e:
                    logger.warning(f"Could not migrate subject {subject['subject_code']}: {e}")
            
            new_session.commit()
            logger.info(f"Migrated {len(subjects)} subjects")
        except Exception as e:
            logger.warning(f"Could not migrate subjects: {e}")
        
        old_conn.close()
        new_session.close()
        
        logger.info("=" * 60)
        logger.info("Migration completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    migrate_data()
