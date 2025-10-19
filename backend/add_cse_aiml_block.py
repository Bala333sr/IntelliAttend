#!/usr/bin/env python3
"""
Script to add CSE-AIML block to the mrcet_blocks table
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def add_cse_aiml_block():
    """Add CSE-AIML block to the mrcet_blocks table"""
    
    with app.app_context():
        try:
            print("Adding CSE-AIML block to mrcet_blocks table...")
            
            # Check if CSE-AIML block already exists
            check_block_sql = """
            SELECT block_id FROM mrcet_blocks 
            WHERE block_name = :block_name OR block_code = :block_code
            LIMIT 1
            """
            result = db.session.execute(text(check_block_sql), {
                'block_name': 'CSE-AIML Block',
                'block_code': 'BLOCK-AIML'
            }).fetchone()
            
            if result:
                print("✅ CSE-AIML block already exists in the database")
                return
            
            # Add CSE-AIML block
            insert_block_sql = """
            INSERT INTO mrcet_blocks (
                block_name, block_code, block_type, floors, total_floors, ground_floor, 
                basement_floors, building_area, departments, facilities, capacity
            ) VALUES (
                :block_name, :block_code, :block_type, :floors, :total_floors, :ground_floor,
                :basement_floors, :building_area, :departments, :facilities, :capacity
            )
            """
            
            cse_aiml_block = {
                'block_name': 'CSE-AIML Block',
                'block_code': 'BLOCK-AIML',
                'block_type': 'Academic',
                'floors': 4,
                'total_floors': 4,
                'ground_floor': True,
                'basement_floors': 0,
                'building_area': 75000.00,
                'departments': '["CSE-AIML", "CSE-DS"]',
                'facilities': '["AI/ML Labs", "Data Science Labs", "Research Centers", "Smart Classrooms"]',
                'capacity': 600
            }
            
            db.session.execute(text(insert_block_sql), cse_aiml_block)
            db.session.commit()
            print("✅ CSE-AIML block added successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT block_name, block_code FROM mrcet_blocks WHERE block_code = 'BLOCK-AIML'"))
            row = result.fetchone()
            if row:
                print(f"✅ Verified: {row[0]} ({row[1]}) added to database")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding CSE-AIML block: {e}")
            raise e

if __name__ == '__main__':
    add_cse_aiml_block()