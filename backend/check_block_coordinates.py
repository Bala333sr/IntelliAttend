#!/usr/bin/env python3
"""
Script to check block coordinates in database
"""

import sys
import os
import json
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_block_coordinates():
    """Check block coordinates in database"""
    
    with app.app_context():
        try:
            # Query blocks with coordinates
            result = db.session.execute(text('''
                SELECT block_name, coordinates 
                FROM mrcet_blocks 
                WHERE coordinates IS NOT NULL
                ORDER BY block_name
            '''))
            rows = result.fetchall()
            
            print('Blocks with Coordinates:')
            print('=' * 80)
            
            for row in rows:
                block_name = row[0]
                coordinates = row[1]
                
                # Parse the coordinates to get count of points
                if coordinates:
                    try:
                        coords_data = json.loads(coordinates)
                        if coords_data and 'coordinates' in coords_data:
                            point_count = len(coords_data['coordinates'][0]) if coords_data['coordinates'] else 0
                            print(f"{block_name:30} | {point_count:2} points")
                        else:
                            print(f"{block_name:30} | Invalid coordinates format")
                    except Exception as e:
                        print(f"{block_name:30} | Error parsing coordinates: {e}")
                else:
                    print(f"{block_name:30} | No coordinates")
            
        except Exception as e:
            print(f"❌ Error checking block coordinates: {e}")

if __name__ == '__main__':
    check_block_coordinates()