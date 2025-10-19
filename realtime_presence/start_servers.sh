#!/bin/bash

# IntelliAttend Real-Time Presence Tracking Servers Startup Script

echo "Starting IntelliAttend Real-Time Presence Tracking Servers..."

# Check if Redis is running
if ! command -v redis-cli &> /dev/null; then
    echo "Error: Redis is not installed. Please install Redis first."
    exit 1
fi

# Check if Redis server is running
if ! redis-cli ping &> /dev/null; then
    echo "Error: Redis server is not running. Please start Redis server first."
    exit 1
fi

echo "✓ Redis server is running"

# Start WebSocket server in background
echo "Starting WebSocket server on port 8765..."
python3 server.py &
WEBSOCKET_PID=$!

# Start REST API server in background
echo "Starting REST API server on port 5005..."
python3 api.py &
API_PID=$!

echo "✓ WebSocket server started (PID: $WEBSOCKET_PID)"
echo "✓ REST API server started (PID: $API_PID)"

echo ""
echo "Servers are now running:"
echo "  WebSocket Server: ws://localhost:8765"
echo "  REST API Server: http://localhost:5005"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait $WEBSOCKET_PID $API_PID

echo "Servers stopped."