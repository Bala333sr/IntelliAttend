#!/usr/bin/env python3
"""
Test script to verify MRCET infrastructure data in the database
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def test_mrcet_infrastructure():
    """Test that MRCET infrastructure data was added correctly"""
    
    with app.app_context():
        print("Testing MRCET infrastructure data...")
        
        # Test 1: Check blocks data
        print("\n1. Checking MRCET blocks:")
        try:
            check_blocks_sql = """
            SELECT block_name, block_code, block_type, floors, capacity 
            FROM mrcet_blocks 
            ORDER BY block_type, block_name
            """
            result = db.session.execute(text(check_blocks_sql))
            rows = result.fetchall()
            
            if rows:
                print(f"   ✅ Found {len(rows)} MRCET blocks:")
                for row in rows:
                    print(f"     {row[0]} ({row[1]}): {row[2]} block with {row[3]} floors, capacity {row[4]}")
            else:
                print("   ❌ No MRCET blocks found")
        except Exception as e:
            print(f"   ❌ Error checking MRCET blocks: {e}")
        
        # Test 2: Check facilities data
        print("\n2. Checking MRCET facilities:")
        try:
            check_facilities_sql = """
            SELECT facility_name, facility_type, location, capacity 
            FROM mrcet_facilities 
            ORDER BY facility_type, facility_name
            """
            result = db.session.execute(text(check_facilities_sql))
            rows = result.fetchall()
            
            if rows:
                print(f"   ✅ Found {len(rows)} MRCET facilities:")
                # Group by facility type for better readability
                facility_types = {}
                for row in rows:
                    facility_type = row[1]
                    if facility_type not in facility_types:
                        facility_types[facility_type] = []
                    facility_types[facility_type].append(row)
                
                for facility_type, facilities in facility_types.items():
                    print(f"     {facility_type} Facilities ({len(facilities)}):")
                    for facility in facilities[:3]:  # Show first 3 of each type
                        capacity_info = f" (Capacity: {facility[3]})" if facility[3] else ""
                        print(f"       - {facility[0]} at {facility[2]}{capacity_info}")
                    if len(facilities) > 3:
                        print(f"       ... and {len(facilities) - 3} more")
            else:
                print("   ❌ No MRCET facilities found")
        except Exception as e:
            print(f"   ❌ Error checking MRCET facilities: {e}")
        
        # Test 3: Check specific blocks
        print("\n3. Verifying specific blocks:")
        test_blocks = [
            {"name": "Main Academic Block", "code": "BLOCK-1", "type": "Academic"},
            {"name": "CSE-AIML Block", "code": "BLOCK-AIML", "type": "Academic"}
        ]
        
        for block in test_blocks:
            try:
                check_block_sql = """
                SELECT block_name, block_code, block_type 
                FROM mrcet_blocks 
                WHERE block_name = :block_name
                LIMIT 1
                """
                result = db.session.execute(text(check_block_sql), {'block_name': block['name']})
                row = result.fetchone()
                
                if row:
                    print(f"   ✅ {block['name']}: Found in database")
                else:
                    print(f"   ⚠️  {block['name']}: Not found in database (this may be expected for some blocks)")
            except Exception as e:
                print(f"   ❌ Error checking {block['name']}: {e}")
        
        # Test 4: Check count of different facility types
        print("\n4. Checking facility type distribution:")
        try:
            count_sql = """
            SELECT facility_type, COUNT(*) as count 
            FROM mrcet_facilities 
            GROUP BY facility_type 
            ORDER BY count DESC
            """
            result = db.session.execute(text(count_sql))
            rows = result.fetchall()
            
            if rows:
                print("   Facility types distribution:")
                for row in rows:
                    print(f"     {row[0]}: {row[1]} facilities")
            else:
                print("   ❌ No facility types found")
        except Exception as e:
            print(f"   ❌ Error checking facility types: {e}")
        
        print("\n✅ MRCET infrastructure testing completed!")

if __name__ == '__main__':
    test_mrcet_infrastructure()