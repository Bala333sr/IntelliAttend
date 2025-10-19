import websocket
import json
import time

def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")
    # Send connect message
    connect_msg = {
        "event": "connect",
        "student_id": "STU_REMOTE_TEST_001",
        "device": "Remote Test Device"
    }
    ws.send(json.dumps(connect_msg))
    print("Sent connect message")

if __name__ == "__main__":
    # Test connection to the WebSocket server using the correct IP
    ws = websocket.WebSocketApp("ws://192.168.0.6:8765/",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    
    ws.run_forever()