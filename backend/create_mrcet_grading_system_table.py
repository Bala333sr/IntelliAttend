#!/usr/bin/env python3
"""
Script to create MRCET grading and evaluation system table and insert grading data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_mrcet_grading_system_table():
    """Create MRCET grading and evaluation system table and insert data"""
    
    with app.app_context():
        try:
            print("Creating MRCET grading and evaluation system table...")
            
            # Create grading system table
            create_grading_table_sql = """
            CREATE TABLE IF NOT EXISTS mrcet_grading_system (
                grading_id INT AUTO_INCREMENT PRIMARY KEY,
                subject_type ENUM('Theory', 'Practical') NOT NULL,
                component VARCHAR(100) NOT NULL,
                total_marks INT NOT NULL,
                passing_criteria TEXT,
                academic_year VARCHAR(9) NOT NULL, -- Format: 2024-2025
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_subject_type (subject_type),
                INDEX idx_component (component),
                INDEX idx_academic_year (academic_year)
            );
            """
            
            db.session.execute(text(create_grading_table_sql))
            db.session.commit()
            print("✅ MRCET grading system table created successfully!")
            
            # Insert MRCET grading system data
            grading_data = [
                # Theory Subjects
                {
                    "subject_type": "Theory",
                    "component": "Total Marks",
                    "total_marks": 100,
                    "passing_criteria": "N/A",
                    "academic_year": "2024-2025"
                },
                {
                    "subject_type": "Theory",
                    "component": "Internal Evaluation",
                    "total_marks": 30,
                    "passing_criteria": "35% (14/40 marks minimum for internal + external combined)",
                    "academic_year": "2024-2025"
                },
                {
                    "subject_type": "Theory",
                    "component": "End Examination",
                    "total_marks": 70,
                    "passing_criteria": "35% (21/60 marks minimum for internal + external combined)",
                    "academic_year": "2024-2025"
                },
                
                # Practical Subjects
                {
                    "subject_type": "Practical",
                    "component": "Total Marks",
                    "total_marks": 75,
                    "passing_criteria": "N/A",
                    "academic_year": "2024-2025"
                },
                {
                    "subject_type": "Practical",
                    "component": "Internal Evaluation",
                    "total_marks": 25,
                    "passing_criteria": "Continuous assessment",
                    "academic_year": "2024-2025"
                },
                {
                    "subject_type": "Practical",
                    "component": "End Examination",
                    "total_marks": 50,
                    "passing_criteria": "End practical",
                    "academic_year": "2024-2025"
                },
                
                # Passing Criteria
                {
                    "subject_type": "Theory",
                    "component": "Internal Minimum",
                    "total_marks": 14,
                    "passing_criteria": "35% of 40 marks (internal + external combined)",
                    "academic_year": "2024-2025"
                },
                {
                    "subject_type": "Theory",
                    "component": "External Minimum",
                    "total_marks": 21,
                    "passing_criteria": "35% of 60 marks (internal + external combined)",
                    "academic_year": "2024-2025"
                },
                {
                    "subject_type": "Theory",
                    "component": "Aggregate Minimum",
                    "total_marks": 40,
                    "passing_criteria": "40% of 100 marks total",
                    "academic_year": "2024-2025"
                }
            ]
            
            # Clear existing data
            db.session.execute(text("DELETE FROM mrcet_grading_system"))
            
            # Insert grading data
            insert_sql = """
            INSERT INTO mrcet_grading_system (
                subject_type, component, total_marks, passing_criteria, academic_year
            ) VALUES (
                :subject_type, :component, :total_marks, :passing_criteria, :academic_year
            )
            """
            
            for grading in grading_data:
                db.session.execute(text(insert_sql), grading)
            
            db.session.commit()
            print("✅ MRCET grading system data inserted successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT COUNT(*) as count FROM mrcet_grading_system"))
            row = result.fetchone()
            if row:
                print(f"✅ Total grading components in database: {row[0]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating MRCET grading system table: {e}")
            raise e

if __name__ == '__main__':
    create_mrcet_grading_system_table()