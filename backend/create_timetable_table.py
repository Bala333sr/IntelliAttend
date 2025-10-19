#!/usr/bin/env python3
"""
Script to create timetable table in the database
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_timetable_table():
    """Create timetable table in the database"""
    
    with app.app_context():
        # Drop timetable table if it exists
        drop_table_sql = "DROP TABLE IF EXISTS timetable;"
        
        # Create timetable table
        create_table_sql = """
        CREATE TABLE timetable (
            id INT AUTO_INCREMENT PRIMARY KEY,
            day_of_week VARCHAR(10),   -- e.g. Monday
            slot INT,                  -- 1 to 6
            start_time TIME,
            end_time TIME,
            subject_code VARCHAR(20),
            subject_name VARCHAR(100),
            faculty_name VARCHAR(100)
        );
        """
        
        try:
            # Drop the table if it exists
            db.session.execute(text(drop_table_sql))
            
            # Create the table
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("✅ Timetable table created successfully!")
            
            # Insert sample data based on the timetable you provided
            sample_data = [
                # Monday
                ("Monday", 1, "09:30:00", "10:20:00", "R22A6602", "ML", "Mr. Rizwan Begh"),
                ("Monday", 2, "10:20:00", "11:10:00", "R22A0512", "CN", "Dr. M. D. Santosh"),
                ("Monday", 3, "11:20:00", "12:10:00", "R22A6702", "IDS", "Dr. N. Sateesh"),
                ("Monday", 4, "12:10:00", "12:50:00", "", "—", ""),
                ("Monday", 5, "12:50:00", "13:50:00", "R22A6681", "ML LAB", "Dr. M. Gayatri"),
                ("Monday", 6, "13:50:00", "14:50:00", "", "—", ""),
                
                # Tuesday
                ("Tuesday", 1, "09:30:00", "10:20:00", "R22A6617", "DAA", "Dr. V. L. Padmalatha"),
                ("Tuesday", 2, "10:20:00", "11:10:00", "R22A0512", "CN", "Dr. M. D. Santosh"),
                ("Tuesday", 3, "11:20:00", "12:10:00", "R22A6702", "IDS", "Dr. N. Sateesh"),
                ("Tuesday", 4, "12:10:00", "12:50:00", "—", "PSD", "—"),
                ("Tuesday", 5, "12:50:00", "13:50:00", "R22A6602", "ML", "Mr. Rizwan Begh"),
                ("Tuesday", 6, "13:50:00", "14:50:00", "—", "Seminar", "—"),
                
                # Wednesday
                ("Wednesday", 1, "09:30:00", "10:20:00", "R22A6602", "ML", "Mr. Rizwan Begh"),
                ("Wednesday", 2, "10:20:00", "11:10:00", "R22A0351", "R&A", "Dr. Arun Kumar"),
                ("Wednesday", 3, "11:20:00", "12:10:00", "", "—", "BIO BREAK"),
                ("Wednesday", 4, "12:10:00", "12:50:00", "R22A6617", "DAA", "Dr. V. L. Padmalatha"),
                ("Wednesday", 5, "12:50:00", "13:50:00", "R22A6617", "DAA", "Dr. V. L. Padmalatha"),
                ("Wednesday", 6, "13:50:00", "14:50:00", "—", "NEOPAT", "—"),
                
                # Thursday
                ("Thursday", 1, "09:30:00", "10:20:00", "R22A0512", "CN", "Dr. M. D. Santosh"),
                ("Thursday", 2, "10:20:00", "11:10:00", "—", "NEOPAT", "—"),
                ("Thursday", 3, "11:20:00", "12:10:00", "R22A0351", "R&A", "Dr. Arun Kumar"),
                ("Thursday", 4, "12:10:00", "12:50:00", "R22A6617", "DAA", "Dr. V. L. Padmalatha"),
                ("Thursday", 5, "12:50:00", "13:50:00", "R22A6702", "IDS", "Dr. N. Sateesh"),
                ("Thursday", 6, "13:50:00", "14:50:00", "—", "Tutorial", "—"),
                
                # Friday
                ("Friday", 1, "09:30:00", "10:20:00", "R22A6617", "DAA", "Dr. V. L. Padmalatha"),
                ("Friday", 2, "10:20:00", "11:10:00", "R22A0351", "R&A", "Dr. Arun Kumar"),
                ("Friday", 3, "11:20:00", "12:10:00", "R22A6702", "IDS", "Dr. N. Sateesh"),
                ("Friday", 4, "12:10:00", "12:50:00", "", "—", ""),
                ("Friday", 5, "12:50:00", "13:50:00", "R22A0596", "CN LAB", "Aruna / Chandra Sekhar"),
                ("Friday", 6, "13:50:00", "14:50:00", "", "—", ""),
                
                # Saturday
                ("Saturday", 1, "09:30:00", "10:20:00", "R22A0351", "R&A", "Dr. Arun Kumar"),
                ("Saturday", 2, "10:20:00", "11:10:00", "R22A6692", "AD-1", "Ms. T. Jayasree"),
                ("Saturday", 3, "11:20:00", "12:10:00", "R22A6692", "AD-1", "Ms. T. Jayasree"),
                ("Saturday", 4, "12:10:00", "12:50:00", "R22A6602", "ML", "Mr. Rizwan Begh"),
                ("Saturday", 5, "12:50:00", "13:50:00", "—", "PSD", "—"),
                ("Saturday", 6, "13:50:00", "14:50:00", "R22A6702", "IDS", "Dr. N. Sateesh")
            ]
            
            # Insert sample data
            for row in sample_data:
                db.session.execute(
                    text("INSERT INTO timetable (day_of_week, slot, start_time, end_time, subject_code, subject_name, faculty_name) VALUES (:day_of_week, :slot, :start_time, :end_time, :subject_code, :subject_name, :faculty_name)"),
                    {
                        'day_of_week': row[0], 
                        'slot': row[1], 
                        'start_time': row[2],
                        'end_time': row[3], 
                        'subject_code': row[4], 
                        'subject_name': row[5],
                        'faculty_name': row[6]
                    }
                )
            
            db.session.commit()
            print("✅ Sample timetable data inserted successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT COUNT(*) as count FROM timetable"))
            count_row = result.fetchone()
            if count_row:
                count = count_row[0]
                print(f"✅ Total records in timetable: {count}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating timetable table: {e}")

if __name__ == '__main__':
    create_timetable_table()