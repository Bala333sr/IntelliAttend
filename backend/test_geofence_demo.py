#!/usr/bin/env python3
"""
Demo script to show how geofencing works with student location data
"""

import redis
import json
import time
from datetime import datetime

def demo_geofencing():
    """Demonstrate how geofencing works with student location data"""
    
    print("="*60)
    print("GEOFENCING DEMONSTRATION")
    print("="*60)
    
    # Connect to Tile38
    try:
        r = redis.Redis(host='localhost', port=9851, db=0, decode_responses=True)
        result = r.execute_command('PING')
        print("✅ Connected to Tile38 server")
    except Exception as e:
        print(f"❌ Failed to connect to Tile38: {e}")
        return
    
    # Set up a simple geofence for demonstration
    print("\n1. Setting up demonstration geofence...")
    try:
        # Create a circular geofence around the CSE-AIML building
        # Using the centroid: 17.5606883, 78.4554966
        result = r.execute_command(
            'SETCHAN', 'demo_fence',
            'NEARBY', 'demo_students', 'FENCE', 'DETECT', 'enter,exit',
            'POINT', '17.5606883', '78.4554966', '100'  # 100 meter radius
        )
        print("✅ Created demonstration geofence around CSE-AIML building")
    except Exception as e:
        print(f"❌ Failed to create geofence: {e}")
        return
    
    # Subscribe to the geofence channel to receive events
    print("\n2. Setting up event listener...")
    pubsub = r.pubsub()
    pubsub.subscribe('demo_fence')
    
    # Function to simulate student movement
    def simulate_student_movement():
        print("\n3. Simulating student movement...")
        print("   (This will trigger geofence events)")
        print()
        
        # Student starts outside the building
        print("📍 Student starting position: Outside building (17.5620, 78.4570)")
        r.execute_command('SET', 'demo_students', 'student_001', 'POINT', '17.5620', '78.4570')
        time.sleep(2)
        
        # Student moves inside the building
        print("📍 Student moving to: Inside building (17.5607, 78.4555)")
        r.execute_command('SET', 'demo_students', 'student_001', 'POINT', '17.5607', '78.4555')
        time.sleep(2)
        
        # Student moves to another location inside the building
        print("📍 Student moving to: Different spot inside (17.5606, 78.4554)")
        r.execute_command('SET', 'demo_students', 'student_001', 'POINT', '17.5606', '78.4554')
        time.sleep(2)
        
        # Student leaves the building
        print("📍 Student moving to: Outside building (17.5625, 78.4575)")
        r.execute_command('SET', 'demo_students', 'student_001', 'POINT', '17.5625', '78.4575')
        time.sleep(2)
        
        print("\n✅ Student movement simulation complete")
    
    # Start listening for events in a separate thread
    import threading
    event_results = []
    
    def listen_for_events():
        print("📡 Listening for geofence events...")
        print("   (Events will appear as student moves)")
        print()
        
        start_time = time.time()
        while time.time() - start_time < 15:  # Listen for 15 seconds
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                try:
                    event_data = json.loads(message['data'])
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    detect_type = event_data.get('detect', 'unknown')
                    student_id = event_data.get('id', 'unknown')
                    
                    event_msg = f"[{timestamp}] 📡 {detect_type.upper()} event for {student_id}"
                    print(f"   {event_msg}")
                    event_results.append(event_msg)
                except Exception as e:
                    print(f"   Error processing message: {e}")
            time.sleep(0.1)
    
    # Start the event listener
    listener_thread = threading.Thread(target=listen_for_events)
    listener_thread.start()
    
    # Simulate student movement
    time.sleep(1)  # Give listener time to start
    simulate_student_movement()
    
    # Wait for listener to finish
    listener_thread.join()
    
    # Show summary
    print("\n" + "="*60)
    print("DEMONSTRATION SUMMARY")
    print("="*60)
    print("✅ Geofence created around CSE-AIML building")
    print("✅ Student location tracking simulated")
    print(f"✅ {len(event_results)} geofence events detected")
    
    if event_results:
        print("\n📊 Detected Events:")
        for event in event_results:
            print(f"   {event}")
    else:
        print("\n⚠️  No events detected (this might be due to timing)")
    
    print("\n💡 How This Works in the Real System:")
    print("   1. Mobile app sends student GPS location to backend")
    print("   2. Backend forwards location to Tile38")
    print("   3. Tile38 checks if location is within building boundaries")
    print("   4. If boundary crossed, Tile38 generates ENTER/EXIT event")
    print("   5. Event updates attendance database automatically")
    print("   6. Confirmation sent back to mobile app")
    
    print("\n🎯 This is how we know if a student is in the right place!")
    print("="*60)

if __name__ == '__main__':
    demo_geofencing()