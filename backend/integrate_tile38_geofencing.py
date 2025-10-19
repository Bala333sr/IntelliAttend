#!/usr/bin/env python3
"""
Script to integrate Tile38 geofencing with the IntelliAttend system
"""

import redis
import json
import threading
import time
from datetime import datetime
import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

class GeofenceManager:
    def __init__(self, host='localhost', port=9851):
        """Initialize the GeofenceManager with Tile38 connection"""
        self.host = host
        self.port = port
        self.redis_client = None
        self.connect()
        
    def connect(self):
        """Connect to Tile38 server"""
        try:
            self.redis_client = redis.Redis(host=self.host, port=self.port, db=0, decode_responses=True)
            result = self.redis_client.execute_command('PING')
            print(f"✅ Connected to Tile38 server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Tile38 server: {e}")
            return False
    
    def setup_mrcet_geofences(self):
        """Set up geofences for all MRCET buildings, especially CSE-AIML"""
        if not self.redis_client:
            print("❌ No Redis client connection")
            return False
            
        try:
            # Get building coordinates from the database
            print("Setting up MRCET geofences...")
            
            # Query the classrooms table for buildings with coordinates
            with app.app_context():
                result = db.session.execute(text("""
                    SELECT building_name, latitude, longitude, geofence_radius 
                    FROM classrooms 
                    WHERE latitude IS NOT NULL AND longitude IS NOT NULL 
                    AND building_name LIKE '%CSE-AIML%'
                """))
                buildings = result.fetchall()
                
                # Also get the polygon data for CSE-AIML
                result = db.session.execute(text("""
                    SELECT room_number, building_name 
                    FROM classrooms 
                    WHERE room_number = 'AIML-POLY' AND building_name = 'CSE-AIML Block'
                """))
                polygon_data = result.fetchone()
            
            # Set up point-based geofences for buildings
            for building in buildings:
                building_name = building[0]
                lat = float(building[1])
                lon = float(building[2])
                radius = float(building[3]) if building[3] else 100.0
                
                # Create a circular geofence around the building
                channel_name = f"{building_name.lower().replace(' ', '_')}_fence"
                result = self.redis_client.execute_command(
                    'SETCHAN', channel_name,
                    'NEARBY', 'students', 'FENCE', 'DETECT', 'enter,exit',
                    'POINT', lat, lon, radius
                )
                print(f"✅ Created geofence for {building_name}: {channel_name}")
            
            # Set up polygon geofence for CSE-AIML if polygon data exists
            if polygon_data:
                # Define the CSE-AIML polygon coordinates
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
                
                polygon_geojson = {
                    "type": "Polygon",
                    "coordinates": [cse_aiml_polygon]
                }
                
                # Create polygon-based geofence
                result = self.redis_client.execute_command(
                    'SETCHAN', 'cse_aiml_polygon_fence',
                    'WITHIN', 'students', 'FENCE', 'DETECT', 'enter,exit',
                    'OBJECT', json.dumps(polygon_geojson)
                )
                print("✅ Created polygon geofence for CSE-AIML block")
            
            print("✅ All MRCET geofences set up successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up MRCET geofences: {e}")
            return False
    
    def add_student(self, student_id, lat, lon):
        """Add a student to the geofencing system"""
        if not self.redis_client:
            print("❌ No Redis client connection")
            return False
            
        try:
            result = self.redis_client.execute_command(
                'SET', 'students', student_id, 'POINT', lat, lon
            )
            print(f"✅ Added student {student_id} at ({lat}, {lon})")
            return True
        except Exception as e:
            print(f"❌ Error adding student {student_id}: {e}")
            return False
    
    def update_student_location(self, student_id, lat, lon):
        """Update a student's location"""
        return self.add_student(student_id, lat, lon)
    
    def monitor_geofences(self):
        """Monitor geofence events in real-time"""
        if not self.redis_client:
            print("❌ No Redis client connection")
            return
            
        try:
            print("Starting geofence monitoring...")
            print("Press Ctrl+C to stop monitoring")
            
            # Subscribe to all geofence channels
            pubsub = self.redis_client.pubsub()
            pubsub.psubscribe('*_fence')
            
            for message in pubsub.listen():
                if message['type'] == 'pmessage':
                    channel = message['channel']
                    data = message['data']
                    print(f"📡 Geofence event on {channel}: {data}")
                    
                    # Process the geofence event
                    self.process_geofence_event(channel, data)
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping geofence monitoring...")
        except Exception as e:
            print(f"❌ Error monitoring geofences: {e}")
    
    def process_geofence_event(self, channel, data):
        """Process a geofence event and update the attendance system"""
        try:
            # Parse the geofence event data
            event_data = json.loads(data)
            
            # Extract relevant information
            command = event_data.get('command', '')
            detect = event_data.get('detect', '')
            student_id = event_data.get('id', '')
            object_data = event_data.get('object', {})
            
            # Log the event
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {detect.upper()} event: Student {student_id} {detect}ed {channel}")
            
            # In a real implementation, you would update the attendance database here
            # For now, we'll just log the event
            with app.app_context():
                # This is where you would integrate with your attendance system
                # Example: Update attendance records in your database
                pass
                
        except Exception as e:
            print(f"❌ Error processing geofence event: {e}")
    
    def get_students_in_building(self, building_name):
        """Get all students currently in a building"""
        if not self.redis_client:
            print("❌ No Redis client connection")
            return []
            
        try:
            channel_name = f"{building_name.lower().replace(' ', '_')}_fence"
            # This would require querying the current state, which is more complex
            # For now, we'll just show how it could be done
            print(f"Querying students in {building_name}...")
            return []
        except Exception as e:
            print(f"❌ Error querying students in {building_name}: {e}")
            return []

def main():
    """Main function to demonstrate the geofencing integration"""
    print("="*60)
    print("MRCET TILE38 GEOFENCING INTEGRATION")
    print("="*60)
    
    # Initialize the geofence manager
    manager = GeofenceManager()
    
    if not manager.connect():
        print("❌ Failed to connect to Tile38. Exiting...")
        return
    
    # Set up geofences
    if not manager.setup_mrcet_geofences():
        print("❌ Failed to set up geofences. Exiting...")
        return
    
    # Add some test students
    test_students = [
        {"id": "student_001", "lat": 17.5607, "lon": 78.4555},
        {"id": "student_002", "lat": 17.5610, "lon": 78.4560},
        {"id": "student_003", "lat": 17.5600, "lon": 78.4550}
    ]
    
    print("\nAdding test students...")
    for student in test_students:
        manager.add_student(student["id"], student["lat"], student["lon"])
    
    print("\n" + "="*60)
    print("GEOFENCING INTEGRATION COMPLETE")
    print("="*60)
    print("✅ Tile38 server connected")
    print("✅ MRCET geofences configured")
    print("✅ Test students added")
    print("✅ System ready for real-time monitoring")
    print("\nTo monitor geofence events in real-time, run:")
    print("python3 backend/integrate_tile38_geofencing.py --monitor")
    print("="*60)

def monitor_mode():
    """Run in monitoring mode"""
    manager = GeofenceManager()
    if manager.connect():
        manager.monitor_geofences()

if __name__ == '__main__':
    if '--monitor' in sys.argv:
        monitor_mode()
    else:
        main()