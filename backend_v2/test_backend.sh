#!/bin/bash

echo "=========================================="
echo "Testing IntelliAttend API v2"
echo "With Attendance System"
echo "=========================================="
echo ""

# Test health endpoint
echo "1. Testing Health Endpoint..."
curl -s http://localhost:8080/health | python3 -m json.tool
echo ""
echo ""

# Test API status
echo "2. Testing API Status..."
curl -s http://localhost:8080/api/status | python3 -m json.tool
echo ""
echo ""

echo "✅ Basic tests completed!"
echo ""
echo "=========================================="
echo "🧪 Attendance System Test Guide"
echo "=========================================="
echo ""
echo "Step 1: Initialize test data (if not done):"
echo "   python3 init_attendance_tables.py"
echo ""
echo "Step 2: Register/Login a student:"
echo '   curl -X POST http://localhost:8080/api/student/register -H "Content-Type: application/json" -d '"'"'{"student_code":"TEST001","first_name":"Test","last_name":"Student","email":"test@example.com","password":"password123","program":"Computer Science","year_of_study":1}'"'"
echo ""
echo '   curl -X POST http://localhost:8080/api/student/login -H "Content-Type: application/json" -d '"'"'{"email":"test@example.com","password":"password123"}'"'"
echo ""
echo "Step 3: Copy the access_token from login response"
echo ""
echo "Step 4: Test attendance marking:"
echo '   curl -X POST http://localhost:8080/api/attendance/mark \'
echo '     -H "Content-Type: application/json" \'
echo '     -H "Authorization: Bearer YOUR_TOKEN_HERE" \'
echo '     -d '"'{"student_id": 1, "qr_token": "TEST_QR_TOKEN_2024", "gps": {"latitude": 17.4435, "longitude": 78.3489, "accuracy": 10.5}, "wifi": {"ssid": "CampusWiFi-R301", "bssid": "AA:BB:CC:DD:EE:FF", "signal_strength": -55}, "bluetooth": [{"mac": "A1:B2:C3:D4:E5:F6", "rssi": -65}], "timestamp": 1704067200000}'
echo ""
echo "=========================================="
echo "📊 Test Data Summary"
echo "=========================================="
echo "QR Token:        TEST_QR_TOKEN_2024"
echo "GPS Location:    17.4435, 78.3489"
echo "WiFi SSID:       CampusWiFi-R301"
echo "WiFi BSSID:      AA:BB:CC:DD:EE:FF"
echo "Bluetooth MAC:   A1:B2:C3:D4:E5:F6"
echo ""
echo "🎯 Scoring System:"
echo "QR Token:    40% (mandatory)"
echo "GPS:         25% (50m geofence)"
echo "WiFi:        20% (SSID + BSSID match)"
echo "Bluetooth:   15% (beacon detection)"
echo "Minimum:     70% required"
echo ""
echo "📚 Visit API docs: http://localhost:8080/api/docs"
