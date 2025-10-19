"""
Integration test for the presence tracking system
"""
import websocket
import json
import time
import threading
import requests

def test_presence_tracking():
    print("Starting presence tracking integration test...")
    
    # Test 1: Check if API is running
    try:
        response = requests.get("http://localhost:5005/health")
        if response.status_code == 200:
            print("✓ API server is running")
        else:
            print("✗ API server is not responding correctly")
            return
    except Exception as e:
        print(f"✗ Failed to connect to API server: {e}")
        return
    
    # Test 2: Connect to WebSocket server
    def on_message(ws, message):
        print(f"WebSocket message received: {message}")
    
    def on_error(ws, error):
        print(f"WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("WebSocket connection closed")
    
    def on_open(ws):
        print("✓ WebSocket connection opened")
        
        # Send connect message
        connect_msg = {
            "event": "connect",
            "student_id": "STU456",
            "device": "Integration Test"
        }
        ws.send(json.dumps(connect_msg))
        print("Sent connect message")
        
        # Send ping message
        time.sleep(2)
        ping_msg = {
            "event": "ping",
            "student_id": "STU456"
        }
        ws.send(json.dumps(ping_msg))
        print("Sent ping message")
        
        # Wait a bit and then close
        time.sleep(3)
        ws.close()
    
    try:
        ws = websocket.WebSocketApp("ws://localhost:8765/",
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)
        
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        
        # Wait for the connection to complete
        time.sleep(10)
        
        # Test 3: Check presence status via API
        response = requests.get("http://localhost:5005/api/presence/STU456")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "online":
                print("✓ Student presence status is correctly reported as online")
            else:
                print(f"✗ Student presence status is {data.get('status')}, expected online")
        else:
            print("✗ Failed to get presence status from API")
            
    except Exception as e:
        print(f"✗ WebSocket test failed: {e}")
    
    print("Integration test completed.")

if __name__ == "__main__":
    test_presence_tracking()