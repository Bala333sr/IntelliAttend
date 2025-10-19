import websocket
import json
import time
import threading
import random

def create_client(client_id):
    def on_message(ws, message):
        print(f"Client {client_id} received: {message}")

    def on_error(ws, error):
        print(f"Client {client_id} error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print(f"Client {client_id} connection closed")

    def on_open(ws):
        print(f"Client {client_id} connection opened")
        
        # Send connect message
        connect_msg = {
            "event": "connect",
            "student_id": f"STU_STRESS_{client_id}",
            "device": f"StressTestDevice_{client_id}"
        }
        ws.send(json.dumps(connect_msg))
        print(f"Client {client_id} sent connect message")
        
        # Send periodic pings
        def send_pings():
            for i in range(10):  # Send 10 pings
                time.sleep(random.uniform(1, 3))  # Random interval between 1-3 seconds
                ping_msg = {
                    "event": "ping",
                    "student_id": f"STU_STRESS_{client_id}"
                }
                ws.send(json.dumps(ping_msg))
                print(f"Client {client_id} sent ping {i+1}")
        
        ping_thread = threading.Thread(target=send_pings)
        ping_thread.daemon = True
        ping_thread.start()

    ws = websocket.WebSocketApp("ws://localhost:8765/",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    return ws

def run_stress_test():
    print("Starting stress test with 10 concurrent clients...")
    
    clients = []
    
    # Create and start 10 clients
    for i in range(10):
        client = create_client(i)
        clients.append(client)
        
        # Start client in background thread
        thread = threading.Thread(target=client.run_forever)
        thread.daemon = True
        thread.start()
        
        # Stagger client connections
        time.sleep(0.5)
    
    # Let clients run for 30 seconds
    time.sleep(30)
    
    # Close all connections
    print("Closing all connections...")
    for client in clients:
        client.close()
    
    print("Stress test completed.")

if __name__ == "__main__":
    run_stress_test()