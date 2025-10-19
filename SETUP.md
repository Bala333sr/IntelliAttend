# IntelliAttend - Complete Setup Guide

This guide will help you set up the entire IntelliAttend system from a fresh download. Follow these steps to get everything running.

## 🚀 Quick Start (Automated Setup)

For the fastest setup, run our automated installation script:

```bash
# Make the setup script executable
chmod +x setup.sh

# Run the complete setup
./setup.sh
```

This will automatically:
- Install all dependencies
- Set up the database
- Configure environment variables
- Start all services

## 📋 Prerequisites

### System Requirements
- **Operating System**: macOS, Linux, or Windows (with WSL)
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **Java**: JDK 17 (for Android development)
- **Android Studio**: Latest version (for mobile development)
- **Git**: Latest version

### Development Tools
- **Android Studio**: For mobile app development
- **VS Code**: Recommended for backend/frontend development
- **Postman**: For API testing (optional)

## 🔧 Manual Setup Instructions

### 1. Backend Setup (Python Flask API)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python init_db.py

# Populate with sample data
python seed_data.py

# Start the server
python run_server.py
```

The backend API will be available at: `http://localhost:8080`

### 2. Frontend Setup (React Web Dashboard)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The web dashboard will be available at: `http://localhost:3000`

### 3. Mobile App Setup (Android)

```bash
# Navigate to mobile app directory
cd mobile/app

# Make gradlew executable
chmod +x gradlew

# Build the app
./gradlew assembleDebug

# Install on connected device/emulator
./gradlew installDebug
```

### 4. Real-time Presence Setup

```bash
# Navigate to realtime presence directory
cd realtime_presence

# Install dependencies
pip install -r requirements.txt

# Start the WebSocket server
python server.py
```

The WebSocket server will be available at: `ws://localhost:8765`

### 5. Database Setup

```bash
# Navigate to database directory
cd database

# Run database setup script
python simple_database_setup.py
```

## 🌐 Environment Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///intelliattend.db
SECRET_KEY=your-secret-key-here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8080
DEBUG=True

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-here
JWT_ACCESS_TOKEN_EXPIRES=3600

# QR Code Configuration
QR_CODE_EXPIRY_MINUTES=5

# Geofencing Configuration
TILE38_HOST=localhost
TILE38_PORT=9851
```

### Frontend Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8080/api
REACT_APP_WEBSOCKET_URL=ws://localhost:8765

# Development Configuration
REACT_APP_DEBUG=true
```

### Mobile App Configuration

Update `mobile/app/app/build.gradle` with your server URL:

```gradle
buildTypes {
    debug {
        buildConfigField "String", "BASE_URL", '"http://YOUR_SERVER_IP:8080/api/"'
        buildConfigField "Boolean", "AUTO_DISCOVERY", "true"
    }
}
```

## 🔄 Starting All Services

### Option 1: Use the Start Script

```bash
# Make the script executable
chmod +x scripts/start_system.sh

# Start all services
./scripts/start_system.sh
```

### Option 2: Manual Start (Separate Terminals)

**Terminal 1 - Backend:**
```bash
cd backend && source venv/bin/activate && python run_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend && npm start
```

**Terminal 3 - Real-time Service:**
```bash
cd realtime_presence && python server.py
```

**Terminal 4 - Mobile App (if developing):**
```bash
cd mobile/app && ./gradlew installDebug
```

## 📱 Mobile App Development

### Android Studio Setup

1. Open Android Studio
2. Select "Open an existing project"
3. Navigate to `mobile/app/` directory
4. Wait for Gradle sync to complete
5. Connect an Android device or start an emulator
6. Click "Run" to install and launch the app

### Building APK

```bash
cd mobile/app

# Debug APK
./gradlew assembleDebug

# Release APK (requires signing configuration)
./gradlew assembleRelease
```

APK files will be generated in: `mobile/app/app/build/outputs/apk/`

## 🧪 Testing the Setup

### 1. Test Backend API

```bash
# Test health endpoint
curl http://localhost:8080/health

# Test student login
curl -X POST http://localhost:8080/api/student/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### 2. Test Frontend

1. Open `http://localhost:3000` in your browser
2. Navigate to admin login
3. Try logging in with test credentials

### 3. Test Mobile App

1. Install the app on your device
2. Open the app
3. Try registering a new device
4. Test attendance marking

### 4. Test Real-time Features

1. Open multiple browser tabs with the web dashboard
2. Mark attendance on mobile app
3. Verify real-time updates appear in web dashboard

## 🔧 Troubleshooting

### Common Issues

**Backend not starting:**
- Check if Python virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8080 is available

**Frontend not loading:**
- Verify Node.js version: `node --version` (should be 16+)
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

**Mobile app build fails:**
- Ensure JDK 17 is installed and configured
- Check Android SDK installation
- Verify Gradle wrapper permissions: `chmod +x gradlew`

**Database issues:**
- Delete existing database: `rm backend/intelliattend.db`
- Reinitialize: `cd backend && python init_db.py`
- Reseed data: `python seed_data.py`

### Port Conflicts

If default ports are in use, update these files:

- **Backend**: `backend/config.py` - change `PORT = 8080`
- **Frontend**: `frontend/package.json` - add `"start": "PORT=3001 react-scripts start"`
- **WebSocket**: `realtime_presence/server.py` - change `PORT = 8765`

## 📚 Additional Resources

- **API Documentation**: Available at `http://localhost:8080/docs` when backend is running
- **Database Schema**: See `database/database_schema.sql`
- **Mobile App Architecture**: See `mobile/app/README.md`
- **Deployment Guide**: See `docs/DEPLOYMENT.md`

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review log files in respective `logs/` directories
3. Ensure all prerequisites are installed
4. Verify environment variables are set correctly

## 🎯 Next Steps

After successful setup:

1. **Customize Configuration**: Update server URLs, database settings
2. **Add Test Data**: Use provided scripts to populate with your institution's data
3. **Configure Security**: Update secret keys and JWT settings for production
4. **Set Up Monitoring**: Enable logging and monitoring for production deployment

---

**Note**: This setup guide assumes a development environment. For production deployment, additional security and performance configurations are required.