#!/bin/bash

# ============================================================================
# IntelliAttend V2 - Robust Backend Startup Script
# ============================================================================

echo "=========================================="
echo "IntelliAttend API v2 - Startup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi
echo "✅ Python 3 is available"
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found in current directory"
    echo "Please run this script from the backend_v2 directory"
    exit 1
fi

# Kill any process on port 8080
echo "Checking port 8080..."
PORT_PID=$(lsof -ti:8080)
if [ ! -z "$PORT_PID" ]; then
    echo "⚠️  Port 8080 is in use by PID $PORT_PID"
    echo "Killing process..."
    kill -9 $PORT_PID 2>/dev/null
    sleep 1
    echo "✅ Port 8080 is now free"
fi
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo "✅ Virtual environment activated"
echo ""

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Check if database needs migration
if [ -f "../backend/intelliattend_dev.db" ] && [ ! -f "intelliattend_v2.db" ]; then
    echo "=========================================="
    echo "Database Migration Available"
    echo "=========================================="
    echo "Old database detected. Would you like to migrate data? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Running migration..."
        python3 migrate_data.py
        if [ $? -ne 0 ]; then
            echo "⚠️  Migration had some issues, but continuing..."
        else
            echo "✅ Data migrated successfully"
        fi
    else
        echo "Skipping migration. New database will be created."
    fi
    echo ""
fi

# Start the server
echo "=========================================="
echo "Starting IntelliAttend API v2"
echo "With Multi-Factor Attendance System"
echo "=========================================="
echo ""
echo "🚀 Server starting on http://0.0.0.0:8080"
echo "📚 API Documentation: http://localhost:8080/api/docs"
echo "📖 Alternative Docs: http://localhost:8080/api/redoc"
echo ""
echo "🎯 Attendance Verification:"
echo "   • QR Token:    40% weight (mandatory)"
echo "   • GPS:         25% weight (50m geofence)"
echo "   • WiFi:        20% weight (SSID + BSSID)"
echo "   • Bluetooth:   15% weight (beacon detect)"
echo "   • Minimum:     70% score required"
echo ""
echo "🗄️ Initialize test data: python3 init_attendance_tables.py"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Run the server
python3 main.py
