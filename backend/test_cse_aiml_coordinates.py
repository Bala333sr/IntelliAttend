#!/usr/bin/env python3
"""
Test script to verify CSE-AIML coordinates in the classrooms table
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def test_cse_aiml_coordinates():
    """Test that CSE-AIML coordinates were added correctly"""
    
    with app.app_context():
        print("Testing CSE-AIML coordinates...")
        
        # Test 1: Check if CSE-AIML points exist
        print("\n1. Checking CSE-AIML points:")
        try:
            check_points_sql = """
            SELECT room_number, building_name, latitude, longitude 
            FROM classrooms 
            WHERE building_name = 'CSE-AIML Block'
            ORDER BY room_number
            """
            result = db.session.execute(text(check_points_sql))
            rows = result.fetchall()
            
            if rows:
                print(f"   ✅ Found {len(rows)} CSE-AIML locations:")
                for row in rows:
                    print(f"     {row[0]}: ({row[2]}, {row[3]}) in {row[1]}")
            else:
                print("   ❌ No CSE-AIML locations found")
        except Exception as e:
            print(f"   ❌ Error checking CSE-AIML points: {e}")
        
        # Test 2: Check specific coordinates
        print("\n2. Verifying specific coordinates:")
        test_coordinates = [
            {"room": "AIML-01", "lat": 17.5605259, "lon": 78.4551113},
            {"room": "AIML-02", "lat": 17.560811, "lon": 78.4551743},
            {"room": "AIML-03", "lat": 17.5606614, "lon": 78.4558355},
            {"room": "AIML-04", "lat": 17.5603839, "lon": 78.4557671},
            {"room": "AIML-BLDG", "lat": 17.5606883, "lon": 78.4554966},
            {"room": "AIML-POLY", "lat": 17.5606883, "lon": 78.4554966}
        ]
        
        for coord in test_coordinates:
            try:
                check_coord_sql = """
                SELECT room_number, latitude, longitude 
                FROM classrooms 
                WHERE room_number = :room_number AND building_name = 'CSE-AIML Block'
                LIMIT 1
                """
                result = db.session.execute(text(check_coord_sql), {'room_number': coord['room']})
                row = result.fetchone()
                
                if row:
                    # Check if coordinates match (within a small tolerance)
                    lat_match = abs(float(row[1]) - coord['lat']) < 0.0000001
                    lon_match = abs(float(row[2]) - coord['lon']) < 0.0000001
                    
                    if lat_match and lon_match:
                        print(f"   ✅ {coord['room']}: Coordinates match")
                    else:
                        print(f"   ⚠️  {coord['room']}: Coordinates don't match - DB({row[1]}, {row[2]}) vs Expected({coord['lat']}, {coord['lon']})")
                else:
                    print(f"   ❌ {coord['room']}: Not found in database")
            except Exception as e:
                print(f"   ❌ Error checking {coord['room']}: {e}")
        
        # Test 3: Check total count of classrooms
        print("\n3. Checking total classroom count:")
        try:
            count_sql = "SELECT COUNT(*) as count FROM classrooms"
            result = db.session.execute(text(count_sql))
            row = result.fetchone()
            count = row[0] if row else 0
            print(f"   ✅ Total classrooms in database: {count}")
        except Exception as e:
            print(f"   ❌ Error checking classroom count: {e}")
        
        print("\n✅ CSE-AIML coordinates testing completed!")

if __name__ == '__main__':
    test_cse_aiml_coordinates()