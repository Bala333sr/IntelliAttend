#!/usr/bin/env python3
"""
Script to update MRCET blocks with accurate coordinates from CSV files
"""

import sys
import os
import csv
import json
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def parse_polygon_coordinates(wkt_string):
    """Parse WKT POLYGON string and return coordinates array"""
    # Remove POLYGON prefix and parentheses
    coords_str = wkt_string.replace('POLYGON ((', '').replace('))', '')
    
    # Split coordinates
    coords_pairs = coords_str.split(', ')
    
    # Parse each coordinate pair
    coordinates = []
    for pair in coords_pairs:
        lon, lat = pair.split(' ')
        coordinates.append([float(lon), float(lat)])
    
    # Ensure polygon is closed (first and last points are the same)
    if coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])
    
    return [coordinates]  # GeoJSON format requires nested array

def update_block_coordinates(block_name, csv_file_path):
    """Update block coordinates in database from CSV file"""
    try:
        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            
            # Find the polygon row
            polygon_coords = None
            for row in reader:
                if row[0].startswith('POLYGON'):
                    polygon_coords = parse_polygon_coordinates(row[0])
                    break
            
            if polygon_coords:
                # Update the block in database
                update_sql = """
                UPDATE mrcet_blocks 
                SET coordinates = :coordinates 
                WHERE block_name = :block_name
                """
                
                db.session.execute(text(update_sql), {
                    'coordinates': json.dumps({
                        'type': 'Polygon',
                        'coordinates': polygon_coords
                    }),
                    'block_name': block_name
                })
                
                db.session.commit()
                print(f"✅ Updated coordinates for {block_name}")
                return True
            else:
                print(f"❌ No polygon found for {block_name}")
                return False
                
    except Exception as e:
        print(f"❌ Error updating coordinates for {block_name}: {e}")
        return False

def add_campus_coordinates():
    """Add overall campus coordinates"""
    try:
        # Read MRCET.CSV for campus boundary
        with open('/Users/anji/Desktop/IntelliAttend/MRCET.CSV', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            
            # Find the polygon row
            polygon_coords = None
            for row in reader:
                if row[0].startswith('POLYGON'):
                    polygon_coords = parse_polygon_coordinates(row[0])
                    break
            
            if polygon_coords:
                # Add campus boundary to a special record or update all blocks
                print("✅ Campus boundary coordinates parsed successfully")
                return polygon_coords
            else:
                print("❌ No campus polygon found")
                return None
                
    except Exception as e:
        print(f"❌ Error reading campus coordinates: {e}")
        return None

def mark_remaining_blocks_as_unupdated():
    """Mark remaining blocks as not yet updated with coordinates"""
    with app.app_context():
        try:
            # List of blocks that should be marked as not yet updated
            blocks_to_mark = [
                'CSE Block',
                'MBA Block',
                'Humanities & Sciences Block',
                'ECE Block',
                'EEE Block',
                'Administrative Block',
                'Cafeteria',
                'Playground',
                'Boys Hostel Block',
                'Girls Hostel Block'
            ]
            
            # Update these blocks to have NULL coordinates (not yet updated)
            for block_name in blocks_to_mark:
                update_sql = """
                UPDATE mrcet_blocks 
                SET coordinates = NULL 
                WHERE block_name = :block_name
                """
                
                result = db.session.execute(text(update_sql), {
                    'block_name': block_name
                })
                
                # Just commit without checking row count
                print(f"✅ Marked {block_name} as not yet updated with coordinates")
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error marking blocks as unupdated: {e}")

def update_mrcet_blocks_with_coordinates():
    """Update MRCET blocks with accurate coordinates"""
    
    with app.app_context():
        try:
            print("Updating MRCET blocks with accurate coordinates...")
            
            # First, add a coordinates column to mrcet_blocks table if it doesn't exist
            try:
                db.session.execute(text("ALTER TABLE mrcet_blocks ADD COLUMN coordinates JSON"))
                db.session.commit()
                print("✅ Added coordinates column to mrcet_blocks table")
            except Exception as e:
                # Column might already exist
                print("ℹ️  Coordinates column already exists or error: ", str(e))
            
            # Update AIML Block coordinates
            success_count = 0
            total_count = 0
            
            # Update AIML Block
            total_count += 1
            if update_block_coordinates('AIML Block', '/Users/anji/Desktop/IntelliAttend/AIML.csv'):
                success_count += 1
            
            # Update Placement Block
            total_count += 1
            if update_block_coordinates('Placement Block', '/Users/anji/Desktop/IntelliAttend/Placement.csv'):
                success_count += 1
            
            # Parse campus coordinates (for reference)
            campus_coords = add_campus_coordinates()
            
            # Mark remaining blocks as not yet updated
            mark_remaining_blocks_as_unupdated()
            
            print(f"\n📊 Coordinate Update Summary:")
            print(f"✅ Successfully updated: {success_count}")
            print(f"❌ Failed to update: {total_count - success_count}")
            print(f"📈 Total blocks processed: {total_count}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating MRCET blocks with coordinates: {e}")

if __name__ == '__main__':
    update_mrcet_blocks_with_coordinates()