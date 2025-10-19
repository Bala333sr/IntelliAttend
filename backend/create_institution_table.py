#!/usr/bin/env python3
"""
Script to create institution table and insert institution data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text
import json

def create_institution_table():
    """Create institution table and insert data"""
    
    with app.app_context():
        try:
            # Create institution table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS institution (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                affiliation VARCHAR(255),
                approvals TEXT,
                address TEXT,
                department VARCHAR(255),
                academic_year VARCHAR(20),
                effective_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("✅ Institution table created successfully!")
            
            # Read institution data from JSON file
            with open('institution_data.json', 'r') as f:
                institution_data = json.load(f)
            
            # Insert institution data
            insert_sql = """
            INSERT INTO institution (name, affiliation, approvals, address, department, academic_year, effective_date)
            VALUES (:name, :affiliation, :approvals, :address, :department, :academic_year, :effective_date)
            """
            
            # Convert approvals list to string
            approvals_str = ', '.join(institution_data['institution']['approvals'])
            
            institution_values = {
                'name': institution_data['institution']['name'],
                'affiliation': institution_data['institution']['affiliation'],
                'approvals': approvals_str,
                'address': institution_data['institution']['address'],
                'department': institution_data['department'],
                'academic_year': institution_data['academic_year'],
                'effective_date': institution_data['effective_date']
            }
            
            db.session.execute(text(insert_sql), institution_values)
            db.session.commit()
            
            print("✅ Institution data inserted successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT * FROM institution"))
            row = result.fetchone()
            if row:
                print(f"✅ Institution details: {row[1]} - {row[2]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating institution table: {e}")

if __name__ == '__main__':
    create_institution_table()