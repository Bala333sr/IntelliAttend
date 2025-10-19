#!/usr/bin/env python3
"""
Script to insert timetable data for Section A
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def insert_timetable_data():
    """Insert timetable data for Section A"""
    
    with app.app_context():
        try:
            print("Inserting timetable data for Section A...")
            
            # Get section ID for Section A of III CSE (AIML)
            result = db.session.execute(text("SELECT id FROM sections WHERE section_name = 'A' AND course = 'III CSE (AIML)'"))
            row = result.fetchone()
            if not row:
                print("❌ Section A not found")
                return
            section_id = row[0]
            print(f"Section ID: {section_id}")
            
            # Insert timetable data
            insert_timetable_sql = """
            INSERT INTO timetable (section_id, day_of_week, slot_number, start_time, end_time, subject_code, slot_type, room_number)
            VALUES (:section_id, :day_of_week, :slot_number, :start_time, :end_time, :subject_code, :slot_type, :room_number)
            """
            
            # MONDAY
            monday_data = [
                {"section_id": section_id, "day_of_week": "MONDAY", "slot_number": 1, "start_time": "09:20:00", "end_time": "10:30:00", "subject_code": "R22A0512", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "MONDAY", "slot_number": 2, "start_time": "10:30:00", "end_time": "11:40:00", "subject_code": "R22A0351", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "MONDAY", "slot_number": 3, "start_time": "11:40:00", "end_time": "11:50:00", "subject_code": None, "slot_type": "break", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "MONDAY", "slot_number": 4, "start_time": "11:50:00", "end_time": "13:00:00", "subject_code": "R22A6602", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "MONDAY", "slot_number": 5, "start_time": "13:00:00", "end_time": "13:50:00", "subject_code": None, "slot_type": "lunch", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "MONDAY", "slot_number": 6, "start_time": "13:50:00", "end_time": "14:50:00", "subject_code": "R22A6681", "slot_type": "lab", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "MONDAY", "slot_number": 7, "start_time": "14:50:00", "end_time": "15:50:00", "subject_code": None, "slot_type": "regular", "room_number": "4208"}
            ]
            
            # TUESDAY
            tuesday_data = [
                {"section_id": section_id, "day_of_week": "TUESDAY", "slot_number": 1, "start_time": "09:20:00", "end_time": "10:30:00", "subject_code": "R22A6617", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "TUESDAY", "slot_number": 2, "start_time": "10:30:00", "end_time": "11:40:00", "subject_code": "R22A0512", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "TUESDAY", "slot_number": 3, "start_time": "11:40:00", "end_time": "11:50:00", "subject_code": None, "slot_type": "break", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "TUESDAY", "slot_number": 4, "start_time": "11:50:00", "end_time": "13:00:00", "subject_code": "R22A6702", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "TUESDAY", "slot_number": 5, "start_time": "13:00:00", "end_time": "13:50:00", "subject_code": None, "slot_type": "lunch", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "TUESDAY", "slot_number": 6, "start_time": "13:50:00", "end_time": "14:50:00", "subject_code": "R22A0084", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "TUESDAY", "slot_number": 7, "start_time": "14:50:00", "end_time": "15:50:00", "subject_code": "R22A6602", "slot_type": "regular", "room_number": "4208"}
            ]
            
            # WEDNESDAY
            wednesday_data = [
                {"section_id": section_id, "day_of_week": "WEDNESDAY", "slot_number": 1, "start_time": "09:20:00", "end_time": "10:30:00", "subject_code": "R22A0351", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "WEDNESDAY", "slot_number": 2, "start_time": "10:30:00", "end_time": "11:40:00", "subject_code": "R22A6702", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "WEDNESDAY", "slot_number": 3, "start_time": "11:40:00", "end_time": "11:50:00", "subject_code": None, "slot_type": "break", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "WEDNESDAY", "slot_number": 4, "start_time": "11:50:00", "end_time": "13:00:00", "subject_code": "R22A6617", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "WEDNESDAY", "slot_number": 5, "start_time": "13:00:00", "end_time": "13:50:00", "subject_code": None, "slot_type": "lunch", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "WEDNESDAY", "slot_number": 6, "start_time": "13:50:00", "end_time": "14:50:00", "subject_code": "R22A0596", "slot_type": "lab", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "WEDNESDAY", "slot_number": 7, "start_time": "14:50:00", "end_time": "15:50:00", "subject_code": "R22A6692", "slot_type": "regular", "room_number": "4208"}
            ]
            
            # THURSDAY
            thursday_data = [
                {"section_id": section_id, "day_of_week": "THURSDAY", "slot_number": 1, "start_time": "09:20:00", "end_time": "10:30:00", "subject_code": "R22A6602", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "THURSDAY", "slot_number": 2, "start_time": "10:30:00", "end_time": "11:40:00", "subject_code": "R22A0084", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "THURSDAY", "slot_number": 3, "start_time": "11:40:00", "end_time": "11:50:00", "subject_code": None, "slot_type": "break", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "THURSDAY", "slot_number": 4, "start_time": "11:50:00", "end_time": "13:00:00", "subject_code": "R22A0351", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "THURSDAY", "slot_number": 5, "start_time": "13:00:00", "end_time": "13:50:00", "subject_code": None, "slot_type": "lunch", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "THURSDAY", "slot_number": 6, "start_time": "13:50:00", "end_time": "14:50:00", "subject_code": "R22A6617", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "THURSDAY", "slot_number": 7, "start_time": "14:50:00", "end_time": "15:50:00", "subject_code": "R22A6702", "slot_type": "regular", "room_number": "4208"}
            ]
            
            # FRIDAY
            friday_data = [
                {"section_id": section_id, "day_of_week": "FRIDAY", "slot_number": 1, "start_time": "09:20:00", "end_time": "10:30:00", "subject_code": "R22A6702", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "FRIDAY", "slot_number": 2, "start_time": "10:30:00", "end_time": "11:40:00", "subject_code": "R22A6692", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "FRIDAY", "slot_number": 3, "start_time": "11:40:00", "end_time": "11:50:00", "subject_code": None, "slot_type": "break", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "FRIDAY", "slot_number": 4, "start_time": "11:50:00", "end_time": "13:00:00", "subject_code": "R22A0512", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "FRIDAY", "slot_number": 5, "start_time": "13:00:00", "end_time": "13:50:00", "subject_code": None, "slot_type": "lunch", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "FRIDAY", "slot_number": 6, "start_time": "13:50:00", "end_time": "14:50:00", "subject_code": "R22A0596", "slot_type": "lab", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "FRIDAY", "slot_number": 7, "start_time": "14:50:00", "end_time": "15:50:00", "subject_code": "R22A6602", "slot_type": "regular", "room_number": "4208"}
            ]
            
            # SATURDAY
            saturday_data = [
                {"section_id": section_id, "day_of_week": "SATURDAY", "slot_number": 1, "start_time": "09:20:00", "end_time": "10:30:00", "subject_code": "R22A0351", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "SATURDAY", "slot_number": 2, "start_time": "10:30:00", "end_time": "11:40:00", "subject_code": "R22A6617", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "SATURDAY", "slot_number": 3, "start_time": "11:40:00", "end_time": "11:50:00", "subject_code": None, "slot_type": "break", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "SATURDAY", "slot_number": 4, "start_time": "11:50:00", "end_time": "13:00:00", "subject_code": "R22A6692", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "SATURDAY", "slot_number": 5, "start_time": "13:00:00", "end_time": "13:50:00", "subject_code": None, "slot_type": "lunch", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "SATURDAY", "slot_number": 6, "start_time": "13:50:00", "end_time": "14:50:00", "subject_code": "R22A0084", "slot_type": "regular", "room_number": "4208"},
                {"section_id": section_id, "day_of_week": "SATURDAY", "slot_number": 7, "start_time": "14:50:00", "end_time": "15:50:00", "subject_code": "R22A0512", "slot_type": "regular", "room_number": "4208"}
            ]
            
            # Insert all timetable data
            all_data = monday_data + tuesday_data + wednesday_data + thursday_data + friday_data + saturday_data
            
            for entry in all_data:
                db.session.execute(text(insert_timetable_sql), entry)
            
            db.session.commit()
            print("✅ Timetable data inserted successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error inserting timetable data: {e}")
            raise e

if __name__ == '__main__':
    insert_timetable_data()