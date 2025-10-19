# IntelliAttend - Intelligent Attendance Management System

A comprehensive attendance management system for educational institutions featuring mobile apps, web dashboards, and real-time tracking capabilities.

## System Components

### 📱 Mobile Application (`mobile/app/`)
- **Android App**: Modern Kotlin app with Jetpack Compose UI
- **Device Fingerprinting**: Unique device identification for secure attendance
- **Location-based Attendance**: GPS and WiFi-based location verification
- **Biometric Authentication**: Fingerprint and face recognition support
- **Real-time Sync**: Instant attendance data synchronization
- **Offline Support**: Works without internet connectivity

### 🖥️ Backend API (`backend/`)
- **Python Flask API**: RESTful API server for mobile and web clients
- **Database Management**: SQLite/PostgreSQL with migration support
- **QR Code Generation**: Dynamic QR codes for attendance sessions
- **Device Registration**: Secure device enrollment and management
- **Attendance Processing**: Real-time attendance validation and storage

### 🌐 Web Dashboard (`frontend/`)
- **Admin Interface**: Comprehensive dashboard for administrators
- **Student Management**: Enrollment, device registration, and profile management
- **Faculty Tools**: Class management and attendance monitoring
- **Analytics**: Attendance statistics and reporting
- **Real-time Updates**: Live attendance tracking and notifications

### 📊 Real-time Presence (`realtime_presence/`)
- **WebSocket Server**: Real-time presence tracking and notifications
- **Live Updates**: Instant attendance status updates
- **Session Management**: Active session monitoring and coordination

### 🗄️ Database (`database/`)
- **Schema Definition**: Complete database structure and relationships
- **Migration Scripts**: Database setup and upgrade utilities
- **Sample Data**: Test data for development and testing

## Tech Stack

### Mobile (Android)
- **Language**: Kotlin
- **UI Framework**: Jetpack Compose
- **Architecture**: MVVM with Clean Architecture
- **Dependency Injection**: Hilt
- **Networking**: Retrofit + OkHttp
- **Database**: Room (SQLite)
- **Authentication**: Biometric API
- **Location**: Google Play Services Location
- **Build System**: Gradle with KSP

### Backend
- **Language**: Python 3.8+
- **Framework**: Flask
- **Database**: SQLite/PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT tokens
- **QR Codes**: qrcode library
- **API Documentation**: Flask-RESTX

### Frontend
- **Framework**: React.js
- **Styling**: Tailwind CSS
- **Build Tool**: Webpack
- **State Management**: React Context
- **HTTP Client**: Axios

### Real-time
- **WebSocket**: Python WebSocket server
- **Protocol**: WebSocket with JSON messaging
- **Coordination**: Session-based presence tracking

## Project Structure

```
IntelliAttend/
├── mobile/app/                 # Android Mobile Application
│   ├── app/src/main/java/com/intelliattend/student/
│   │   ├── ui/                # Jetpack Compose UI screens
│   │   ├── data/              # Repository and data sources
│   │   ├── domain/            # Use cases and business logic
│   │   ├── network/           # API services and models
│   │   ├── utils/             # Utility classes
│   │   └── auto/              # Auto-attendance features
│   └── build.gradle           # Android build configuration
├── backend/                   # Python Flask API Server
│   ├── api/                   # API route handlers
│   ├── models/                # Database models
│   ├── services/              # Business logic services
│   ├── utils/                 # Utility functions
│   ├── app.py                 # Main Flask application
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React Web Dashboard
│   ├── public/                # Static assets
│   ├── templates/             # HTML templates
│   │   ├── admin/             # Admin dashboard pages
│   │   └── student/           # Student portal pages
│   ├── package.json           # Node.js dependencies
│   └── tailwind.config.js     # Tailwind CSS configuration
├── database/                  # Database Schema & Scripts
│   ├── database_schema.sql    # Complete database structure
│   └── README.md              # Database documentation
├── realtime_presence/         # Real-time Tracking Service
│   ├── server.py              # WebSocket server
│   ├── api.py                 # REST API endpoints
│   └── demo.py                # Demo client
├── backend_v2/                # Alternative Backend Implementation
├── scripts/                   # Deployment & Utility Scripts
├── docs/                      # Documentation
└── README.md                  # This file
```

## 🚀 Getting Started

### ⚡ Quick Start (Recommended)

```bash
# 1. Download the ZIP file from GitHub
# 2. Extract and navigate to the folder
# 3. Run the automated setup:

chmod +x setup.sh
./setup.sh

# 4. Start all services:
./start-all.sh
```

**That's it!** 🎉 Your system will be running at:
- **Web Dashboard**: http://localhost:3000
- **API Server**: http://localhost:8080
- **Mobile App**: Build with Android Studio

### 📚 Detailed Guides

- **🚀 [Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
- **🔧 [Complete Setup Guide](SETUP.md)** - Detailed installation instructions
- **🌐 [Deployment Guide](DEPLOYMENT.md)** - Production deployment options

### 📋 Prerequisites

- **Python 3.8+** - Backend API server
- **Node.js 16+** - Frontend web application
- **Java 17** - Mobile app development (optional)
- **Android Studio** - Mobile app development (optional)

### 🎯 Quick Test

After setup, test your installation:

```bash
# Test backend API
curl http://localhost:8080/health

# Test frontend (open in browser)
open http://localhost:3000

# Build mobile app
cd mobile/app && ./gradlew assembleDebug
```

## Build

```bash
./gradlew assembleDebug      # Debug build
./gradlew assembleRelease    # Release build
./gradlew test              # Run tests
```

## Contributing

1. Follow Kotlin coding conventions
2. Use Jetpack Compose for UI
3. Implement proper error handling
4. Add unit tests for business logic
5. Update documentation

## License

This project is part of the IntelliAttend system for educational institutions.