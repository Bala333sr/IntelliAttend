#!/bin/bash

# ============================================================================
# IntelliAttend V2 - One-Command Quick Start
# Complete setup and launch with attendance system
# ============================================================================

echo "======================================================================"
echo "🎓 IntelliAttend V2 - Quick Start with Attendance System"
echo "======================================================================"
echo ""

# Check if we're in the correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found"
    echo "Please run this script from the backend_v2 directory"
    exit 1
fi

echo "📦 Step 1: Installing dependencies..."
echo "======================================================================"
pip3 install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Dependency installation failed"
    exit 1
fi
echo ""

echo "🗄️  Step 2: Initializing database with attendance system..."
echo "======================================================================"
python3 init_attendance_tables.py
if [ $? -eq 0 ]; then
    echo "✅ Database initialized"
else
    echo "⚠️  Database initialization had issues"
fi
echo ""

echo "🔌 Step 3: Checking port 8080..."
echo "======================================================================"
PORT_PID=$(lsof -ti:8080)
if [ ! -z "$PORT_PID" ]; then
    echo "⚠️  Port 8080 is in use by PID $PORT_PID"
    echo "Killing process..."
    kill -9 $PORT_PID 2>/dev/null
    sleep 1
    echo "✅ Port 8080 is now free"
else
    echo "✅ Port 8080 is available"
fi
echo ""

echo "🚀 Step 4: Starting server..."
echo "======================================================================"
echo ""
echo "🌐 Server URL:      http://localhost:8080"
echo "📚 API Docs:        http://localhost:8080/api/docs"
echo "📖 ReDoc:           http://localhost:8080/api/redoc"
echo ""
echo "🎯 Attendance Verification System:"
echo "   • QR Token:    40% (mandatory)"
echo "   • GPS:         25% (50m geofence)"
echo "   • WiFi:        20% (SSID + BSSID match)"
echo "   • Bluetooth:   15% (beacon detection)"
echo "   • Minimum:     70% score required"
echo ""
echo "🧪 Test Data:"
echo "   QR Token:     TEST_QR_TOKEN_2024"
echo "   GPS:          17.4435, 78.3489"
echo "   WiFi SSID:    CampusWiFi-R301"
echo "   WiFi BSSID:   AA:BB:CC:DD:EE:FF"
echo "   Bluetooth:    A1:B2:C3:D4:E5:F6"
echo ""
echo "======================================================================"
echo "✅ SYSTEM READY! Press CTRL+C to stop"
echo "======================================================================"
echo ""

# Start the server
python3 main.py
