# IntelliAttend API v2 - Modern FastAPI Backend

## 🚀 Overview

This is a complete redesign of the IntelliAttend backend using **FastAPI** - a modern, fast, and robust Python web framework. This version eliminates all port conflicts, configuration issues, and provides superior performance with automatic API documentation.

## ✨ Key Features

- **FastAPI Framework**: Modern, async-capable, high-performance
- **Automatic API Documentation**: Interactive docs at `/api/docs` and `/api/redoc`
- **Port 8080**: No conflicts with macOS Control Center or other services
- **JWT Authentication**: Secure token-based authentication
- **Pydantic Validation**: Automatic request/response validation
- **SQLite Database**: Easy setup, no external dependencies
- **CORS Enabled**: Full mobile app support
- **Health Checks**: Built-in status monitoring
- **Robust Error Handling**: Consistent error responses
- **Easy Migration**: Script to copy data from old database

## 📋 Requirements

- Python 3.8 or higher
- pip (Python package manager)

## 🔧 Installation

### Option 1: Using the startup script (Recommended)

```bash
cd /Users/anji/Desktop/IntelliAttend/backend_v2
chmod +x start_server.sh
./start_server.sh
```

The script will:
- Check Python version
- Clear port 8080 if needed
- Create virtual environment
- Install dependencies
- Offer to migrate data from old database
- Start the server

### Option 2: Manual installation

```bash
cd /Users/anji/Desktop/IntelliAttend/backend_v2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Migrate data from old database
python3 migrate_data.py

# Start server
python3 main.py
```

## 🌐 API Endpoints

Once running, access:

- **API Base URL**: `http://localhost:8080`
- **Interactive Documentation**: `http://localhost:8080/api/docs`
- **Alternative Documentation**: `http://localhost:8080/api/redoc`
- **Health Check**: `http://localhost:8080/health`
- **API Status**: `http://localhost:8080/api/status`

### Authentication Endpoints

- `POST /api/student/login` - Student login
- `POST /api/student/register` - Student registration
- `POST /api/faculty/login` - Faculty login

### Profile Endpoints

- `GET /api/student/profile` - Get student profile (requires auth)
- `GET /api/student/me` - Get current student info (requires auth)

### Timetable Endpoints

- `GET /api/student/timetable/today` - Get today's schedule (requires auth)

### 🎯 Attendance Endpoints (NEW!)

- `POST /api/attendance/mark` - Mark attendance with multi-factor verification (requires auth)

**Multi-Factor Verification System:**
- **QR Token**: 40% weight (mandatory)
- **GPS Geofencing**: 25% weight (50m radius)
- **WiFi Network**: 20% weight (SSID + BSSID match)
- **Bluetooth Beacons**: 15% weight (MAC address detection)
- **Minimum Score**: 70% required to mark attendance

**Example Request:**
```json
POST /api/attendance/mark
Authorization: Bearer YOUR_TOKEN

{
  "student_id": 1,
  "qr_token": "TEST_QR_TOKEN_2024",
  "gps": {
    "latitude": 17.4435,
    "longitude": 78.3489,
    "accuracy": 10.5
  },
  "wifi": {
    "ssid": "CampusWiFi-R301",
    "bssid": "AA:BB:CC:DD:EE:FF",
    "signal_strength": -55
  },
  "bluetooth": [
    {"mac": "A1:B2:C3:D4:E5:F6", "rssi": -65}
  ],
  "timestamp": 1704067200000
}
```

**Example Response:**
```json
{
  "success": true,
  "message": "Attendance marked successfully (Score: 85.0/100)",
  "verification_score": 85.0,
  "score_breakdown": {
    "qr": 40.0,
    "gps": 25.0,
    "wifi": 20.0,
    "bluetooth": 0.0
  },
  "verifications": {
    "qr": {"valid": true, "weight": 40.0},
    "gps": {"valid": true, "distance": 12.3, "weight": 25.0},
    "wifi": {"valid": true, "network": "CampusWiFi-R301", "weight": 20.0},
    "bluetooth": {"valid": false, "beacons": [], "weight": 0.0}
  },
  "attendance_id": 1
}
```

## 📱 Mobile App Configuration

Update your mobile app to use the new backend:

**For Android App** (`ApiClient.kt` or `BuildConfig`):
```kotlin
BASE_URL = "http://10.0.2.2:8080/api/"  // For Android emulator
// OR
BASE_URL = "http://YOUR_LOCAL_IP:8080/api/"  // For physical device
```

**Test the connection**:
```bash
curl http://localhost:8080/health
```

## 🗄️ Database Migration

If you have an existing database, the migration script will automatically copy:
- Students
- Faculty
- Sections
- Timetable
- Subjects

The script is non-destructive and will skip duplicates.

## 🔐 Security Features

- **JWT Tokens**: Secure, stateless authentication
- **Password Hashing**: bcrypt with salt
- **Input Validation**: Automatic via Pydantic
- **CORS**: Configured for mobile access
- **Token Expiry**: 24-hour access tokens

## 📊 Response Format

All API responses follow this standard format:

```json
{
  "success": true,
  "status_code": 200,
  "timestamp": "2025-01-04T08:21:11Z",
  "data": { /* response data */ },
  "message": "Success message",
  "error": null
}
```

## 🗄️ Database Initialization

Initialize the database with test data for attendance system:

```bash
python3 init_attendance_tables.py
```

This creates:
- **5 new tables**: classrooms, classroom_wifi, classroom_beacons, attendance_sessions, attendance_records
- **Test classroom**: R301 at GPS (17.4435, 78.3489)
- **Test WiFi**: CampusWiFi-R301 (AA:BB:CC:DD:EE:FF)
- **Test Bluetooth**: A1:B2:C3:D4:E5:F6
- **Test QR Token**: TEST_QR_TOKEN_2024 (valid for 2 hours)

## 🧪 Testing

### 1. Test the API is running:
```bash
curl http://localhost:8080/health
```

### 2. Test student login:
```bash
curl -X POST http://localhost:8080/api/student/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"password123"}'
```

### 3. Test attendance marking:
```bash
curl -X POST http://localhost:8080/api/attendance/mark \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "student_id": 1,
    "qr_token": "TEST_QR_TOKEN_2024",
    "gps": {
      "latitude": 17.4435,
      "longitude": 78.3489,
      "accuracy": 10.5
    },
    "wifi": {
      "ssid": "CampusWiFi-R301",
      "bssid": "AA:BB:CC:DD:EE:FF",
      "signal_strength": -55
    },
    "bluetooth": [
      {"mac": "A1:B2:C3:D4:E5:F6", "rssi": -65}
    ],
    "timestamp": 1704067200000
  }'
```

### 4. View API documentation:
Open your browser to:
- **Swagger UI**: http://localhost:8080/api/docs
- **ReDoc**: http://localhost:8080/api/redoc

## 🐛 Troubleshooting

### Port 8080 already in use
```bash
# Find process on port 8080
lsof -ti:8080

# Kill the process
kill -9 $(lsof -ti:8080)
```

### Dependencies not installing
```bash
# Upgrade pip first
pip install --upgrade pip

# Try installing dependencies again
pip install -r requirements.txt
```

### Database errors
```bash
# Delete and recreate database
rm intelliattend_v2.db
python3 main.py  # Will create fresh database
```

## 📝 Development

### Add new endpoints

Edit `main.py` and add your route:

```python
@app.get("/api/your/endpoint", tags=["YourTag"])
async def your_endpoint(
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    # Your logic here
    return ResponseModel(
        success=True,
        status_code=200,
        data={"result": "Your data"}
    )
```

### Hot reload

The server runs with auto-reload enabled. Changes to `main.py` will automatically restart the server.

## 🔄 Differences from Old Backend

| Feature | Old (Flask) | New (FastAPI) |
|---------|-------------|---------------|
| Port | 5002 (conflicts!) | 8080 (safe) |
| Docs | Manual | Auto-generated |
| Validation | Manual | Automatic |
| Performance | Good | Excellent |
| Async Support | Limited | Full |
| Type Safety | Partial | Complete |
| Error Handling | Manual | Standardized |

## 📚 Documentation

- **FastAPI**: https://fastapi.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/
- **SQLAlchemy**: https://docs.sqlalchemy.org/

## 🎯 Next Steps

1. Start the new backend with `./start_server.sh`
2. Test endpoints using the interactive docs at `/api/docs`
3. Update mobile app base URL to `http://YOUR_IP:8080/api/`
4. Test login and timetable features
5. Gradually add more endpoints as needed

## 💡 Benefits

- **No More Port Conflicts**: Port 8080 is universally safe
- **Better Error Messages**: Clear, consistent error responses  
- **Auto Documentation**: Always up-to-date API docs
- **Type Safety**: Catch errors before they reach production
- **Performance**: 2-3x faster than Flask
- **Modern Stack**: Built for the future

## 🆘 Support

If you encounter any issues:

1. Check the logs in `backend_v2.log`
2. Visit the interactive docs at `/api/docs`
3. Test the health endpoint: `curl http://localhost:8080/health`
4. Ensure port 8080 is free: `lsof -ti:8080`

---

**Made with ❤️ using FastAPI**
