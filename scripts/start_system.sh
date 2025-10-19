#!/bin/bash

# IntelliAttend - System Startup Script

echo "🚀 Starting IntelliAttend System..."

# Start backend server in background
echo "Starting backend server on port 5002..."
cd /Users/anji/Desktop/IntelliAttend
python3 server/app.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server for SmartBoard display
echo "Starting SmartBoard display on port 5173..."
python3 -m http.server 5173 > frontend.log 2>&1 &
FRONTEND_PID=$!

# Display status
echo ""
echo "✅ IntelliAttend System Started Successfully!"
echo "=========================================="
echo "Backend Server (API & Portals): http://localhost:5002"
echo "SmartBoard Display: http://localhost:5173"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Logs are being written to backend.log and frontend.log"
echo "To stop the system, run: pkill -f 'python3 server/app.py' && pkill -f 'http.server 5173'"