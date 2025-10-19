import websocket
import json
import time
import threading

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
        "student_id": "STU123",
        "device": "Test Device"
    }
    ws.send(json.dumps(connect_msg))
    print("Sent connect message")
    
    # Start sending ping messages
    def send_pings():
        while True:
            time.sleep(10)  # Send ping every 10 seconds
            ping_msg = {
                "event": "ping",
                "student_id": "STU123"
            }
            ws.send(json.dumps(ping_msg))
            print("Sent ping message")
    
    ping_thread = threading.Thread(target=send_pings)
    ping_thread.daemon = True
    ping_thread.start()

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8765/",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    
    ws.run_forever()