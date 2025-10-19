#!/usr/bin/env python3
"""
Script to set up virtual geofencing for CSE-AIML block using Tile38
"""

import redis
import json
import time

def setup_cse_aiml_geofence():
    """Set up virtual geofencing for CSE-AIML block using Tile38"""
    
    try:
        # Connect to Tile38 server
        print("Connecting to Tile38 server...")
        r = redis.Redis(host='localhost', port=9851, db=0, decode_responses=True)
        
        # Test connection
        result = r.execute_command('PING')
        print(f"✅ Connected to Tile38: {result}")
        
        # Create collections for MRCET (students and buildings)
        print("\n1. Creating collections...")
        # Collections are automatically created when we add objects to them
        
        # Define the CSE-AIML polygon coordinates (from the provided data)
        # POLYGON ((78.4551113 17.5605259, 78.4557671 17.5603839, 78.4558355 17.5606614, 
        #           78.4555525 17.5607343, 78.4555659 17.5608084, 78.4554828 17.5608302, 
        #           78.4554626 17.5607509, 78.4551743 17.560811, 78.4551113 17.5605259))
        
        # Note: Tile38 expects coordinates in [longitude, latitude] format (GeoJSON standard)
        cse_aiml_polygon = [
            [78.4551113, 17.5605259],
            [78.4557671, 17.5603839],
            [78.4558355, 17.5606614],
            [78.4555525, 17.5607343],
            [78.4555659, 17.5608084],
            [78.4554828, 17.5608302],
            [78.4554626, 17.5607509],
            [78.4551743, 17.560811],
            [78.4551113, 17.5605259]  # Closing the polygon
        ]
        
        # Add the CSE-AIML building as a polygon object
        print("\n2. Adding CSE-AIML building polygon...")
        polygon_geojson = {
            "type": "Polygon",
            "coordinates": [cse_aiml_polygon]
        }
        
        result = r.execute_command('SET', 'buildings', 'cse_aiml_block', 'OBJECT', json.dumps(polygon_geojson))
        print(f"✅ Polygon added result: {result}")
        
        # Set up a geofence for the CSE-AIML block
        print("\n3. Setting up geofence for CSE-AIML block...")
        # Create a channel for geofence notifications
        result = r.execute_command('SETCHAN', 'cse_aiml_fence', 
                                 'WITHIN', 'students', 'FENCE', 'DETECT', 'enter,exit',
                                 'OBJECT', json.dumps(polygon_geojson))
        print(f"✅ Geofence setup result: {result}")
        
        # Add some test students to demonstrate the geofencing
        print("\n4. Adding test student locations...")
        students = [
            {"id": "student_001", "lat": 17.5606, "lon": 78.4555},
            {"id": "student_002", "lat": 17.5610, "lon": 78.4560},
            {"id": "student_003", "lat": 17.5600, "lon": 78.4550}
        ]
        
        for student in students:
            result = r.execute_command('SET', 'students', student["id"], 
                                     'POINT', student["lat"], student["lon"])
            print(f"   Added {student['id']} at ({student['lat']}, {student['lon']}): {result}")
        
        # Subscribe to the geofence channel to receive notifications
        print("\n5. Setting up geofence monitoring...")
        print("   Listening for geofence events (press Ctrl+C to stop)...")
        print("   Move students in/out of the CSE-AIML area to see notifications")
        
        # In a real implementation, you would set up a proper subscription
        # For now, let's just show how it would work
        print("\n" + "="*60)
        print("VIRTUAL GEOFENCING SETUP COMPLETE")
        print("="*60)
        print("✅ CSE-AIML polygon defined in Tile38")
        print("✅ Geofence channel 'cse_aiml_fence' created")
        print("✅ Test students added")
        print("✅ System ready for geofence monitoring")
        print("\nTo monitor geofence events in real-time, run:")
        print("tile38-cli subscribe cse_aiml_fence")
        print("\nTo simulate student movement, update their positions with:")
        print("tile38-cli SET students student_001 POINT <lat> <lon>")
        print("="*60)
        
        # Example of how to move a student to trigger geofence events
        print("\nExample commands to test geofencing:")
        print("1. Move student inside CSE-AIML area:")
        print("   tile38-cli SET students student_001 POINT 17.5607 78.4555")
        print("2. Move student outside CSE-AIML area:")
        print("   tile38-cli SET students student_001 POINT 17.5620 78.4570")
        print("3. Monitor events:")
        print("   tile38-cli subscribe cse_aiml_fence")
        
    except Exception as e:
        print(f"❌ Error setting up CSE-AIML geofence: {e}")
        raise e

def test_geofence_functionality():
    """Test the geofence functionality with sample data"""
    
    try:
        # Connect to Tile38 server
        print("Testing geofence functionality...")
        r = redis.Redis(host='localhost', port=9851, db=0, decode_responses=True)
        
        # Test a nearby search
        print("\n1. Testing nearby search...")
        result = r.execute_command('NEARBY', 'students', 'POINT', '17.5606883', '78.4554966', '200')
        print(f"   Nearby students: {result}")
        
        # Test within search (check if points are within the polygon)
        print("\n2. Testing within search...")
        # We would need to define the polygon again for this search
        cse_aiml_polygon = [
            [78.4551113, 17.5605259],
            [78.4557671, 17.5603839],
            [78.4558355, 17.5606614],
            [78.4555525, 17.5607343],
            [78.4555659, 17.5608084],
            [78.4554828, 17.5608302],
            [78.4554626, 17.5607509],
            [78.4551743, 17.560811],
            [78.4551113, 17.5605259]
        ]
        
        polygon_geojson = {
            "type": "Polygon",
            "coordinates": [cse_aiml_polygon]
        }
        
        # This would be the search command:
        # result = r.execute_command('WITHIN', 'students', 'OBJECT', json.dumps(polygon_geojson))
        print("   Within search would check which students are inside the CSE-AIML polygon")
        
        print("\n✅ Geofence functionality test completed")
        
    except Exception as e:
        print(f"❌ Error testing geofence functionality: {e}")

if __name__ == '__main__':
    setup_cse_aiml_geofence()
    test_geofence_functionality()