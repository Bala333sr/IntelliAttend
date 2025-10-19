#!/usr/bin/env python3
"""
Script to create MRCET attendance regulations table and insert regulation data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_mrcet_attendance_regulations_table():
    """Create MRCET attendance regulations table and insert data"""
    
    with app.app_context():
        try:
            print("Creating MRCET attendance regulations table...")
            
            # Create attendance regulations table
            create_regulations_table_sql = """
            CREATE TABLE IF NOT EXISTS mrcet_attendance_regulations (
                regulation_id INT AUTO_INCREMENT PRIMARY KEY,
                attendance_level VARCHAR(50) NOT NULL,
                minimum_percentage DECIMAL(5, 2) NOT NULL,
                maximum_percentage DECIMAL(5, 2),
                action_required TEXT,
                consequences TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_attendance_level (attendance_level),
                INDEX idx_minimum_percentage (minimum_percentage)
            );
            """
            
            db.session.execute(text(create_regulations_table_sql))
            db.session.commit()
            print("✅ MRCET attendance regulations table created successfully!")
            
            # Insert MRCET attendance regulations data
            regulations_data = [
                {
                    "attendance_level": "Eligible for exams",
                    "minimum_percentage": 75.00,
                    "maximum_percentage": 100.00,
                    "action_required": "No action needed",
                    "consequences": "Eligible for examinations"
                },
                {
                    "attendance_level": "Condonation required",
                    "minimum_percentage": 65.00,
                    "maximum_percentage": 74.99,
                    "action_required": "Academic Committee condonation + fee",
                    "consequences": "Eligible after approval"
                },
                {
                    "attendance_level": "Non-condonable",
                    "minimum_percentage": 0.00,
                    "maximum_percentage": 64.99,
                    "action_required": "Not condonable",
                    "consequences": "Registration cancelled, exam ineligible"
                },
                {
                    "attendance_level": "Mid-exam bonus",
                    "minimum_percentage": 0.00,
                    "maximum_percentage": 0.00,
                    "action_required": "Appear in mid-term examination",
                    "consequences": "+2 periods attendance credit"
                }
            ]
            
            # Clear existing data
            db.session.execute(text("DELETE FROM mrcet_attendance_regulations"))
            
            # Insert regulations data
            insert_sql = """
            INSERT INTO mrcet_attendance_regulations (
                attendance_level, minimum_percentage, maximum_percentage, action_required, consequences
            ) VALUES (
                :attendance_level, :minimum_percentage, :maximum_percentage, :action_required, :consequences
            )
            """
            
            for regulation in regulations_data:
                db.session.execute(text(insert_sql), regulation)
            
            db.session.commit()
            print("✅ MRCET attendance regulations data inserted successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT COUNT(*) as count FROM mrcet_attendance_regulations"))
            row = result.fetchone()
            if row:
                print(f"✅ Total regulations in database: {row[0]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating MRCET attendance regulations table: {e}")
            raise e

if __name__ == '__main__':
    create_mrcet_attendance_regulations_table()