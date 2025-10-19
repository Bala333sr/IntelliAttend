#!/bin/bash

# IntelliAttend - System Stop Script

echo "🛑 Stopping IntelliAttend System..."

# Kill backend server
echo "Stopping backend server..."
pkill -f "python3 server/app.py"

# Kill frontend server
echo "Stopping SmartBoard display server..."
pkill -f "http.server 5173"

# Wait a moment for processes to terminate
sleep 2

# Verify processes are stopped
if pgrep -f "python3 server/app.py" > /dev/null; then
    echo "⚠️  Backend server may still be running"
else
    echo "✅ Backend server stopped"
fi

if pgrep -f "http.server 5173" > /dev/null; then
    echo "⚠️  Frontend server may still be running"
else
    echo "✅ Frontend server stopped"
fi

echo ""
echo "✅ IntelliAttend System Stopped"