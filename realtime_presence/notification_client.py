import websocket
import json
import time
import threading

def on_message(ws, message):
    print(f"Notification: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Notification connection closed")

def on_open(ws):
    print("Notification connection opened")
    
    # Subscribe to notifications
    subscribe_msg = {
        "event": "subscribe_notifications"
    }
    ws.send(json.dumps(subscribe_msg))
    print("Subscribed to notifications")

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8765/",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    
    ws.run_forever()