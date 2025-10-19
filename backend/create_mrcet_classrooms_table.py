#!/usr/bin/env python3
"""
Script to create MRCET classrooms for all blocks
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_mrcet_classrooms():
    """Create MRCET classrooms for all blocks"""
    
    with app.app_context():
        try:
            print("Creating MRCET classrooms for all blocks...")
            
            # Clear existing data first - need to handle foreign key constraints
            print("Clearing existing classroom data...")
            # First, clear any classes that reference classrooms
            db.session.execute(text("UPDATE classes SET classroom_id = NULL"))
            # Then clear the classrooms
            db.session.execute(text("DELETE FROM classrooms WHERE classroom_id > 0"))
            db.session.commit()
            print("✅ Existing classroom data cleared!")
            
            # Define classroom data for each block
            classrooms_data = []
            
            # CSE Block (BLOCK-1) - CSE, IT, General Classrooms
            for floor in range(1, 6):  # Floors 1-5
                # CSE Department Classrooms (10 per floor)
                for i in range(1, 11):
                    room_num = f"CSE{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'CSE Block',
                        'floor_number': floor,
                        'capacity': 60
                    })
                
                # IT Department Classrooms (5 per floor)
                for i in range(1, 6):
                    room_num = f"IT{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'CSE Block',
                        'floor_number': floor,
                        'capacity': 60
                    })
                
                # General Classrooms (3 per floor)
                for i in range(1, 4):
                    room_num = f"G{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'CSE Block',
                        'floor_number': floor,
                        'capacity': 100
                    })
            
            # MBA Block (BLOCK-2) - MBA, Management Studies
            for floor in range(1, 5):  # Floors 1-4
                # MBA Classrooms (8 per floor)
                for i in range(1, 9):
                    room_num = f"MBA{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'MBA Block',
                        'floor_number': floor,
                        'capacity': 50
                    })
                
                # Case Study Rooms (2 per floor)
                for i in range(1, 3):
                    room_num = f"CSR{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'MBA Block',
                        'floor_number': floor,
                        'capacity': 30
                    })
            
            # Humanities & Sciences Block (BLOCK-3)
            for floor in range(1, 4):  # Floors 1-3
                # Physics Labs (3 per floor)
                for i in range(1, 4):
                    room_num = f"PHY{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'Humanities & Sciences Block',
                        'floor_number': floor,
                        'capacity': 25
                    })
                
                # Chemistry Labs (3 per floor)
                for i in range(1, 4):
                    room_num = f"CHEM{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'Humanities & Sciences Block',
                        'floor_number': floor,
                        'capacity': 25
                    })
                
                # Mathematics Classrooms (4 per floor)
                for i in range(1, 5):
                    room_num = f"MATH{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'Humanities & Sciences Block',
                        'floor_number': floor,
                        'capacity': 60
                    })
            
            # ECE Block (BLOCK-4)
            for floor in range(1, 5):  # Floors 1-4
                # ECE Labs (8 per floor)
                for i in range(1, 9):
                    room_num = f"ECE{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'ECE Block',
                        'floor_number': floor,
                        'capacity': 30
                    })
            
            # EEE Block (BLOCK-5)
            for floor in range(1, 5):  # Floors 1-4
                # EEE Labs (8 per floor)
                for i in range(1, 9):
                    room_num = f"EEE{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'EEE Block',
                        'floor_number': floor,
                        'capacity': 30
                    })
            
            # AIML Block (BLOCK-6)
            for floor in range(1, 5):  # Floors 1-4
                # CSE-AI&ML Classrooms (10 per floor)
                for i in range(1, 11):
                    room_num = f"AIML{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'AIML Block',
                        'floor_number': floor,
                        'capacity': 60
                    })
                
                # CSE-Data Science Classrooms (5 per floor)
                for i in range(1, 6):
                    room_num = f"DS{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'AIML Block',
                        'floor_number': floor,
                        'capacity': 60
                    })
                
                # CSE-Cyber Security Classrooms (3 per floor)
                for i in range(1, 4):
                    room_num = f"CS{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'AIML Block',
                        'floor_number': floor,
                        'capacity': 60
                    })
                
                # CSE-IoT Classrooms (2 per floor)
                for i in range(1, 3):
                    room_num = f"IoT{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'AIML Block',
                        'floor_number': floor,
                        'capacity': 60
                    })
            
            # Placement Block (BLOCK-7)
            for floor in range(1, 4):  # Floors 1-3
                # Interview Halls (3 per floor)
                for i in range(1, 4):
                    room_num = f"INT{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'Placement Block',
                        'floor_number': floor,
                        'capacity': 20
                    })
                
                # Group Discussion Rooms (4 per floor)
                for i in range(1, 5):
                    room_num = f"GD{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'Placement Block',
                        'floor_number': floor,
                        'capacity': 15
                    })
            
            # Cafeteria (BLOCK-8)
            # Cafeteria areas
            for floor in range(1, 3):  # Floors 1-2
                # Dining halls (2 per floor)
                for i in range(1, 3):
                    room_num = f"CAF{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'Cafeteria',
                        'floor_number': floor,
                        'capacity': 200
                    })
                
                # Food counters (3 per floor)
                for i in range(1, 4):
                    room_num = f"FC{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'Cafeteria',
                        'floor_number': floor,
                        'capacity': 50
                    })
            
            # Playground (BLOCK-9)
            # Sports areas
            playground_areas = [
                {'room_number': 'PLAY-FOOTBALL', 'building_name': 'Playground', 'floor_number': 1, 'capacity': 100},
                {'room_number': 'PLAY-BASKETBALL', 'building_name': 'Playground', 'floor_number': 1, 'capacity': 50},
                {'room_number': 'PLAY-VOLLEYBALL', 'building_name': 'Playground', 'floor_number': 1, 'capacity': 30},
                {'room_number': 'PLAY-TRACK', 'building_name': 'Playground', 'floor_number': 1, 'capacity': 200},
                {'room_number': 'PLAY-GYM', 'building_name': 'Playground', 'floor_number': 1, 'capacity': 80}
            ]
            for area in playground_areas:
                classrooms_data.append(area)
            
            # Administrative Block (BLOCK-ADM) - Same building as CSE but separate entry
            # Administrative offices
            for floor in range(1, 6):  # Floors 1-5
                # Office rooms (5 per floor)
                for i in range(1, 6):
                    room_num = f"ADM{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'Administrative Block',
                        'floor_number': floor,
                        'capacity': 10
                    })
            
            # Hostel Blocks - Common Areas
            # Boys Hostel
            for floor in range(0, 5):  # Ground + 4 floors
                # Common Rooms (2 per floor)
                for i in range(1, 3):
                    room_num = f"BH{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'Boys Hostel Block',
                        'floor_number': floor,
                        'capacity': 20
                    })
            
            # Girls Hostel
            for floor in range(0, 5):  # Ground + 4 floors
                # Common Rooms (2 per floor)
                for i in range(1, 3):
                    room_num = f"GH{floor}{i:02d}"
                    classrooms_data.append({
                        'room_number': room_num,
                        'building_name': 'Girls Hostel Block',
                        'floor_number': floor,
                        'capacity': 20
                    })
            
            print(f"Generated {len(classrooms_data)} classrooms")
            
            # Insert classrooms data
            insert_sql = """
            INSERT INTO classrooms (
                room_number, building_name, floor_number, capacity
            ) VALUES (
                :room_number, :building_name, :floor_number, :capacity
            )
            """
            
            for classroom in classrooms_data:
                db.session.execute(text(insert_sql), classroom)
            
            db.session.commit()
            print("✅ MRCET classrooms data inserted successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT COUNT(*) as count FROM classrooms"))
            row = result.fetchone()
            if row:
                print(f"✅ Total classrooms in database: {row[0]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating MRCET classrooms: {e}")
            raise e

if __name__ == '__main__':
    create_mrcet_classrooms()