#!/usr/bin/env python3
"""
Script to populate timetable with detailed schedule data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

# Timetable data for all sections
timetable_data = {
    "A": {
        "room_number": "4208",
        "days": {
            "Monday": [
                {"slot": 1, "time": "9:20-10:30", "subject": "CN", "subject_full": "Computer Networks"},
                {"slot": 2, "time": "10:30-11:40", "subject": "R&A", "subject_full": "Robotics and Automation"},
                {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                {"slot": 3, "time": "11:50-13:00", "subject": "ML", "subject_full": "Machine Learning"},
                {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                {"slot": 4, "time": "13:50-14:50", "subject": "ML LAB", "subject_full": "Machine Learning Lab"},
                {"slot": 5, "time": "14:50-15:50", "subject": None, "subject_full": None}
            ],
            "Tuesday": [
                {"slot": 1, "time": "9:20-10:30", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                {"slot": 2, "time": "10:30-11:40", "subject": "CN", "subject_full": "Computer Networks"},
                {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                {"slot": 3, "time": "11:50-13:00", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                {"slot": 4, "time": "13:50-14:50", "subject": "PSD", "subject_full": "Professional Skill Development"},
                {"slot": 5, "time": "14:50-15:50", "subject": "ML", "subject_full": "Machine Learning"}
            ],
            "Wednesday": [
                {"slot": 1, "time": "9:20-10:30", "subject": "ML", "subject_full": "Machine Learning"},
                {"slot": 2, "time": "10:30-11:40", "subject": "R&A", "subject_full": "Robotics and Automation"},
                {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                {"slot": 3, "time": "11:50-13:00", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                {"slot": 4, "time": "13:50-14:50", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                {"slot": 5, "time": "14:50-15:50", "subject": "NEOPAT", "subject_full": None}
            ],
            "Thursday": [
                {"slot": 1, "time": "9:20-10:30", "subject": "CN", "subject_full": "Computer Networks"},
                {"slot": 2, "time": "10:30-11:40", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                {"slot": 3, "time": "11:50-13:00", "subject": "R&A", "subject_full": "Robotics and Automation"},
                {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                {"slot": 4, "time": "13:50-14:50", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                {"slot": 5, "time": "14:50-15:50", "subject": "CN", "subject_full": "Computer Networks"}
            ],
            "Friday": [
                {"slot": 1, "time": "9:20-10:30", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                {"slot": 2, "time": "10:30-11:40", "subject": "R&A", "subject_full": "Robotics and Automation"},
                {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                {"slot": 3, "time": "11:50-13:00", "subject": "NEOPAT", "subject_full": None},
                {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                {"slot": 4, "time": "13:50-14:50", "subject": "CN LAB", "subject_full": "Computer Networks Lab"},
                {"slot": 5, "time": "14:50-15:50", "subject": None, "subject_full": None}
            ],
            "Saturday": [
                {"slot": 1, "time": "9:20-10:30", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                {"slot": 2, "time": "10:30-11:40", "subject": "AD-1", "subject_full": "Application Development – 1"},
                {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                {"slot": 3, "time": "11:50-13:00", "subject": "AD-1", "subject_full": "Application Development – 1"},
                {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                {"slot": 4, "time": "13:50-14:50", "subject": "ML", "subject_full": "Machine Learning"},
                {"slot": 5, "time": "14:50-15:50", "subject": "PSD", "subject_full": "Professional Skill Development"}
            ]
        }
    },
    "B": {
        "room_number": "4210",
        "days": {
            "Monday": [
                {"slot": 1, "time": "9:20-10:30", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                {"slot": 2, "time": "10:30-11:40", "subject": "PSD", "subject_full": "Professional Skill Development"},
                {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                {"slot": 3, "time": "11:50-13:00", "subject": "ML", "subject_full": "Machine Learning"},
                {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                {"slot": 4, "time": "13:50-14:50", "subject": "NEOPAT", "subject_full": None},
                {"slot": 5, "time": "14:50-15:50", "subject": "R&A", "subject_full": "Robotics and Automation"}
            ],
            "Tuesday": [
                {"slot": 1, "time": "9:20-10:30", "subject": "R&A", "subject_full": "Robotics and Automation"},
                {"slot": 2, "time": "10:30-11:40", "subject": "ML LAB", "subject_full": "Machine Learning Lab"},
                {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                {"slot": 3, "time": "11:50-13:00", "subject": "ML LAB", "subject_full": "Machine Learning Lab"},
                {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                {"slot": 4, "time": "13:50-14:50", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                {"slot": 5, "time": "14:50-15:50", "subject": "CN", "subject_full": "Computer Networks"}
            ],
            "Wednesday": [
                {"slot": 1, "time": "9:20-10:30", "subject": "ML", "subject_full": "Machine Learning"},
                {"slot": 2, "time": "10:30-11:40", "subject": "CN LAB", "subject_full": "Computer Networks Lab"},
                {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                {"slot": 3, "time": "11:50-13:00", "subject": "CN LAB", "subject_full": "Computer Networks Lab"},
                {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                {"slot": 4, "time": "13:50-14:50", "subject": "ML", "subject_full": "Machine Learning"},
                {"slot": 5, "time": "14:50-15:50", "subject": "IDS", "subject_full": "Introduction to Data Science"}
            ],
            "Thursday": [
                {"slot": 1, "time": "9:20-10:30", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                {"slot": 2, "time": "10:30-11:40", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                {"slot": 3, "time": "11:50-13:00", "subject": "CN", "subject_full": "Computer Networks"},
                {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                {"slot": 4, "time": "13:50-14:50", "subject": "NEOPAT", "subject_full": None},
                {"slot": 5, "time": "14:50-15:50", "subject": "PSD", "subject_full": "Professional Skill Development"}
            ],
            "Friday": [
                {"slot": 1, "time": "9:20-10:30", "subject": "CN", "subject_full": "Computer Networks"},
                {"slot": 2, "time": "10:30-11:40", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                {"slot": 3, "time": "11:50-13:00", "subject": "R&A", "subject_full": "Robotics and Automation"},
                {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                {"slot": 4, "time": "13:50-14:50", "subject": "AD-1", "subject_full": "Application Development – 1"},
                {"slot": 5, "time": "14:50-15:50", "subject": None, "subject_full": None}
            ],
            "Saturday": [
                {"slot": 1, "time": "9:20-10:30", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                {"slot": 2, "time": "10:30-11:40", "subject": "CN", "subject_full": "Computer Networks"},
                {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                {"slot": 3, "time": "11:50-13:00", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                {"slot": 4, "time": "13:50-14:50", "subject": "ML", "subject_full": "Machine Learning"},
                {"slot": 5, "time": "14:50-15:50", "subject": "R&A", "subject_full": "Robotics and Automation"}
            ]
        }
    }
}

def populate_timetable():
    """Populate timetable with detailed schedule data"""
    
    with app.app_context():
        try:
            # Get all sections with their IDs
            result = db.session.execute(text("SELECT id, section FROM sections"))
            sections_dict = {row[1]: row[0] for row in result}
            
            # Insert timetable data
            insert_sql = """
            INSERT INTO timetable (section_id, day_of_week, slot_number, slot_type, start_time, end_time, subject_code, subject_name, faculty_name, room_number)
            VALUES (:section_id, :day_of_week, :slot_number, :slot_type, :start_time, :end_time, :subject_code, :subject_name, :faculty_name, :room_number)
            """
            
            total_entries = 0
            
            for section, data in timetable_data.items():
                section_id = sections_dict.get(section)
                if not section_id:
                    print(f"⚠️  Section {section} not found in database")
                    continue
                
                room_number = data["room_number"]
                
                for day, slots in data["days"].items():
                    for slot in slots:
                        # Parse time range
                        if "-" in slot["time"]:
                            start_time, end_time = slot["time"].split("-")
                        else:
                            start_time = end_time = slot["time"]
                        
                        # Determine slot type
                        slot_type = "regular"
                        if "break" in slot["subject"].lower() if slot["subject"] else False:
                            slot_type = "break"
                        elif "lunch" in slot["subject"].lower() if slot["subject"] else False:
                            slot_type = "lunch"
                        
                        # Get slot number (if it's a break, use the slot name as slot number)
                        slot_number = slot["slot"] if isinstance(slot["slot"], int) else None
                        
                        timetable_entry = {
                            "section_id": section_id,
                            "day_of_week": day,
                            "slot_number": slot_number,
                            "slot_type": slot_type,
                            "start_time": start_time,
                            "end_time": end_time,
                            "subject_code": slot["subject"],
                            "subject_name": slot["subject_full"],
                            "faculty_name": None,  # Will be populated from subjects table
                            "room_number": room_number
                        }
                        
                        db.session.execute(text(insert_sql), timetable_entry)
                        total_entries += 1
            
            db.session.commit()
            print(f"✅ Timetable data populated successfully with {total_entries} entries!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error populating timetable data: {e}")

if __name__ == '__main__':
    populate_timetable()