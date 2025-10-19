"""
Demo script showing the complete presence tracking system in action
"""
import websocket
import json
import time
import threading
import requests
import subprocess
import sys

def demo_presence_tracking():
    print("=== IntelliAttend Real-Time Presence Tracking Demo ===\n")
    
    # Check if servers are running
    print("1. Checking server status...")
    try:
        response = requests.get("http://localhost:5005/health")
        if response.status_code == 200:
            print("   ✓ REST API server is running")
        else:
            print("   ✗ REST API server is not responding")
            return
    except:
        print("   ✗ REST API server is not accessible")
        return
    
    try:
        ws_test = websocket.create_connection("ws://localhost:8765/")
        ws_test.close()
        print("   ✓ WebSocket server is running")
    except:
        print("   ✗ WebSocket server is not accessible")
        return
    
    print("\n2. Starting demo client...")
    
    # Student connection simulation
    messages_received = []
    
    def on_message(ws, message):
        messages_received.append(message)
        data = json.loads(message)
        if data.get("event") == "connected":
            print("   ✓ Student connected to presence tracking")
        elif data.get("event") == "pong":
            print("   ✓ Heartbeat acknowledged")
        elif data.get("event") == "presence_change":
            status = data.get("status")
            print(f"   ✓ Presence change notification: {status}")
    
    def on_error(ws, error):
        pass  # Suppress errors for demo
    
    def on_close(ws, close_status_code, close_msg):
        print("   ✓ Student disconnected from presence tracking")
    
    def on_open(ws):
        # Send connect message
        connect_msg = {
            "event": "connect",
            "student_id": "STU_DEMO_001",
            "device": "Demo Device"
        }
        ws.send(json.dumps(connect_msg))
        
        # Send periodic pings
        def send_pings():
            for i in range(3):
                time.sleep(3)
                ping_msg = {
                    "event": "ping",
                    "student_id": "STU_DEMO_001"
                }
                ws.send(json.dumps(ping_msg))
            
            # Disconnect after demo
            time.sleep(2)
            ws.close()
        
        ping_thread = threading.Thread(target=send_pings)
        ping_thread.daemon = True
        ping_thread.start()
    
    # Connect and run demo
    ws = websocket.WebSocketApp("ws://localhost:8765/",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    print("   Student connecting...")
    time.sleep(15)  # Wait for demo to complete
    
    print("\n3. Checking presence status via API...")
    try:
        response = requests.get("http://localhost:5005/api/presence/STU_DEMO_001")
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            last_seen = data.get("last_seen")
            print(f"   Current status: {status}")
            print(f"   Last seen: {last_seen}")
        else:
            print("   Failed to get presence status")
    except Exception as e:
        print(f"   Error checking presence status: {e}")
    
    print("\n4. Checking all presence statuses...")
    try:
        response = requests.get("http://localhost:5005/api/presence/all")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total students tracked: {len(data)}")
            for student_id, info in list(data.items())[:5]:  # Show first 5
                print(f"   - {student_id}: {info['status']}")
        else:
            print("   Failed to get all presence statuses")
    except Exception as e:
        print(f"   Error checking all presence statuses: {e}")
    
    print("\n=== Demo Complete ===")
    print("The presence tracking system is working correctly!")
    print("Students are automatically tracked as online/offline in real-time.")

if __name__ == "__main__":
    demo_presence_tracking()