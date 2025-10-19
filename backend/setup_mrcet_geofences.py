#!/usr/bin/env python3
"""
Script to set up geofences for MRCET blocks
"""

import sys
import os
import requests
import json
sys.path.append('.')

from app import app, db
from sqlalchemy import text

# Sample coordinates for MRCET campus (these would need to be replaced with actual coordinates)
MRCET_COORDINATES = {
    'CSE Block': {
        'type': 'Polygon',
        'coordinates': [[
            [78.4551113, 17.5605259],  # Southwest corner
            [78.4557671, 17.5603839],  # Southeast corner
            [78.4558355, 17.5606614],  # Northeast corner
            [78.4555525, 17.5607343],  # Northwest corner
            [78.4551113, 17.5605259]   # Closing point (same as first)
        ]]
    },
    'ECE Block': {
        'type': 'Polygon',
        'coordinates': [[
            [78.4558355, 17.5606614],  # Southwest corner
            [78.4562000, 17.5605500],  # Southeast corner
            [78.4562500, 17.5608000],  # Northeast corner
            [78.4559000, 17.5609000],  # Northwest corner
            [78.4558355, 17.5606614]   # Closing point
        ]]
    },
    'EEE Block': {
        'type': 'Polygon',
        'coordinates': [[
            [78.4562500, 17.5608000],  # Southwest corner
            [78.4566000, 17.5607000],  # Southeast corner
            [78.4566500, 17.5609500],  # Northeast corner
            [78.4563000, 17.5610500],  # Northwest corner
            [78.4562500, 17.5608000]   # Closing point
        ]]
    },
    'AIML Block': {
        'type': 'Polygon',
        'coordinates': [[
            [78.4551113, 17.5605259],  # Southwest corner
            [78.4557671, 17.5603839],  # Southeast corner
            [78.4558355, 17.5606614],  # Northeast corner
            [78.4555525, 17.5607343],  # Northwest corner
            [78.4551113, 17.5605259]   # Closing point
        ]]
    },
    'MBA Block': {
        'type': 'Polygon',
        'coordinates': [[
            [78.4566500, 17.5609500],  # Southwest corner
            [78.4570000, 17.5608500],  # Southeast corner
            [78.4570500, 17.5611000],  # Northeast corner
            [78.4567000, 17.5612000],  # Northwest corner
            [78.4566500, 17.5609500]   # Closing point
        ]]
    },
    'Administrative Block': {
        'type': 'Polygon',
        'coordinates': [[
            [78.4550000, 17.5610000],  # Southwest corner
            [78.4554000, 17.5609000],  # Southeast corner
            [78.4554500, 17.5611500],  # Northeast corner
            [78.4550500, 17.5612500],  # Northwest corner
            [78.4550000, 17.5610000]   # Closing point
        ]]
    },
    'Cafeteria': {
        'type': 'Polygon',
        'coordinates': [[
            [78.4554000, 17.5613000],  # Southwest corner
            [78.4557000, 17.5612000],  # Southeast corner
            [78.4557500, 17.5614000],  # Northeast corner
            [78.4554500, 17.5615000],  # Northwest corner
            [78.4554000, 17.5613000]   # Closing point
        ]]
    },
    'Playground': {
        'type': 'Polygon',
        'coordinates': [[
            [78.4558000, 17.5614000],  # Southwest corner
            [78.4565000, 17.5612000],  # Southeast corner
            [78.4566000, 17.5616000],  # Northeast corner
            [78.4559000, 17.5618000],  # Northwest corner
            [78.4558000, 17.5614000]   # Closing point
        ]]
    }
}

def create_geofence(block_name, coordinates):
    """Create a geofence for a block in Tile38"""
    try:
        # Format the geofence name
        fence_name = f"{block_name.lower().replace(' ', '_')}_fence"
        
        # Create the geofence using proper Tile38 format
        data = {
            "name": fence_name,
            "key": "students",
            "detect": "enter,exit",
            "commands": ["WITHIN"]
        }
        
        # Send the command to Tile38
        response = requests.post(
            "http://localhost:9851/setchan",
            data={
                "name": fence_name,
                "key": "students",
                "detect": "enter,exit",
                "commands": "WITHIN"
            },
            json={
                "type": "Polygon",
                "coordinates": coordinates["coordinates"]
            }
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

def setup_mrcet_geofences():
    """Set up geofences for all MRCET blocks"""
    
    print("Setting up geofences for MRCET blocks...")
    
    success_count = 0
    total_count = 0
    
    # Create geofences for each block
    for block_name, coordinates in MRCET_COORDINATES.items():
        total_count += 1
        if create_geofence(block_name, coordinates):
            success_count += 1
    
    print(f"\n📊 Geofence Setup Summary:")
    print(f"✅ Successfully created: {success_count}")
    print(f"❌ Failed to create: {total_count - success_count}")
    print(f"📈 Total blocks processed: {total_count}")

def test_simple_geofence():
    """Test with a simple geofence command"""
    try:
        # Test with a simple circular geofence
        fence_name = "test_cse_fence"
        
        # Using requests with proper Tile38 command format
        response = requests.post(
            "http://localhost:9851/",
            data="SETPCHAN test_cse_fence NEARBY students FENCE DETECT enter,exit POINT 17.5606883 78.4554966 150.0"
        )
        
        print(f"Test response: {response.text}")
        
    except Exception as e:
        print(f"Error in test: {e}")

if __name__ == '__main__':
    # First test with a simple command
    test_simple_geofence()
    
    # Then try to set up all geofences
    setup_mrcet_geofences()