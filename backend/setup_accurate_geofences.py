#!/usr/bin/env python3
"""
Script to set up accurate geofences for MRCET blocks using CSV coordinates
"""

import sys
import os
import csv
import json
import requests
sys.path.append('.')

def parse_polygon_coordinates(wkt_string):
    """Parse WKT POLYGON string and return coordinates array"""
    # Remove POLYGON prefix and parentheses
    coords_str = wkt_string.replace('POLYGON ((', '').replace('))', '')
    
    # Split coordinates
    coords_pairs = coords_str.split(', ')
    
    # Parse each coordinate pair (note: WKT uses lon lat, but GeoJSON needs lat lon)
    coordinates = []
    for pair in coords_pairs:
        lon, lat = pair.split(' ')
        coordinates.append([float(lon), float(lat)])
    
    # Ensure polygon is closed (first and last points are the same)
    if coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])
    
    return coordinates

def create_geofence_from_csv(block_name, csv_file_path):
    """Create a geofence for a block using coordinates from CSV file"""
    try:
        # Read the CSV file
        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            
            # Find the polygon row
            polygon_coords = None
            for row in reader:
                if row[0].startswith('POLYGON'):
                    polygon_coords = parse_polygon_coordinates(row[0])
                    break
            
            if not polygon_coords:
                print(f"❌ No polygon found in {csv_file_path}")
                return False
            
            # Format the geofence name
            fence_name = f"{block_name.lower().replace(' ', '_')}_fence"
            
            # Convert coordinates to GeoJSON format (lat, lon -> lon, lat for GeoJSON)
            geojson_coords = []
            for coord in polygon_coords:
                geojson_coords.append([coord[0], coord[1]])  # Already in lon, lat format
            
            # Create the geofence object
            geofence_object = {
                "type": "Polygon",
                "coordinates": [geojson_coords]
            }
            
            # Send command to Tile38 using HTTP API
            command = f"WITHIN students FENCE DETECT enter,exit OBJECT {json.dumps(geofence_object)}"
            
            response = requests.post(
                "http://localhost:9851/setchan",
                params={
                    "name": fence_name
                },
                data=command
            )
            
            if response.json().get("ok"):
                print(f"✅ Created geofence for {block_name}")
                return True
            else:
                print(f"❌ Failed to create geofence for {block_name}: {response.json().get('err')}")
                return False
                
    except Exception as e:
        print(f"❌ Error creating geofence for {block_name}: {e}")
        return False

def setup_accurate_geofences():
    """Set up accurate geofences using CSV coordinates"""
    
    print("Setting up accurate geofences using CSV coordinates...")
    
    success_count = 0
    total_count = 0
    
    # Create geofence for AIML Block
    total_count += 1
    if create_geofence_from_csv('AIML Block', '/Users/anji/Desktop/IntelliAttend/AIML.csv'):
        success_count += 1
    
    # Create geofence for Placement Block
    total_count += 1
    if create_geofence_from_csv('Placement Block', '/Users/anji/Desktop/IntelliAttend/Placement.csv'):
        success_count += 1
    
    print(f"\n📊 Geofence Setup Summary:")
    print(f"✅ Successfully created: {success_count}")
    print(f"❌ Failed to create: {total_count - success_count}")
    print(f"📈 Total blocks processed: {total_count}")

def test_tile38_connection():
    """Test connection to Tile38"""
    try:
        response = requests.get("http://localhost:9851/server")
        if response.json().get("ok"):
            print("✅ Connected to Tile38 successfully")
            return True
        else:
            print("❌ Failed to connect to Tile38")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Tile38: {e}")
        return False

if __name__ == '__main__':
    # Test Tile38 connection first
    if test_tile38_connection():
        # Set up accurate geofences
        setup_accurate_geofences()
    else:
        print("❌ Cannot proceed without Tile38 connection")