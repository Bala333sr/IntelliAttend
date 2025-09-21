# IntelliAttend - Running Instructions

## 🚀 Starting the System

### Option 1: Using the Startup Script (Recommended)
```bash
# Make scripts executable (first time only)
chmod +x start_system.sh stop_system.sh

# Start the entire system
./start_system.sh
```

### Option 2: Manual Start

1. **Start the Backend Server**:
   ```bash
   cd /Users/anji/Desktop/IntelliAttend
   python3 server/app.py
   ```
   The backend will run on port 5002.

2. **Start the Frontend Server (SmartBoard Display)**:
   ```bash
   cd /Users/anji/Desktop/IntelliAttend
   python3 -m http.server 5173
   ```
   The SmartBoard display will run on port 5173.

## 🌐 Accessing the System

Once both servers are running, you can access:

- **Faculty Portal**: http://localhost:5002
- **Student Portal**: http://localhost:5002/student
- **Admin Dashboard**: http://localhost:5002/admin
- **SmartBoard Display**: http://localhost:5173
- **API Base URL**: http://localhost:5002/api

## 🧪 Testing the System

Run the test suite to verify everything is working:
```bash
cd /Users/anji/Desktop/IntelliAttend
python3 test_app.py
```

## 🛑 Stopping the System

### Option 1: Using the Stop Script
```bash
./stop_system.sh
```

### Option 2: Manual Stop

1. **Find and kill the backend process**:
   ```bash
   pkill -f "python3 server/app.py"
   ```

2. **Find and kill the frontend process**:
   ```bash
   pkill -f "http.server 5173"
   ```

## 📁 System Components

### Backend (Port 5002)
- Flask application with all API endpoints
- Database connectivity (MySQL)
- JWT authentication
- QR code generation and management
- Attendance processing

### Frontend (Port 5173)
- SmartBoard QR display interface
- Static file serving
- HTML/CSS/JavaScript frontend

## 🔧 Troubleshooting

### Port Already in Use
If you get an error that port 5002 or 5173 is already in use:
1. Find the process: `lsof -i :5002` or `lsof -i :5173`
2. Kill the process: `kill -9 <PID>`
3. Or start on a different port:
   ```bash
   PORT=5003 python3 server/app.py
   ```

### Database Issues
If you encounter database connection issues:
1. Ensure MySQL is running
2. Check database credentials in `.env` file
3. Reset and recreate the database:
   ```bash
   python3 server/reset_db.py
   python3 server/setup_db.py
   ```

## 📋 Default Credentials

**Faculty Login**:
- Email: `john.smith@university.edu`
- Password: `F@cultY2024!`

**Student Login**:
- Email: `student1@student.edu`
- Password: `Stud3nt2024!`

**SmartBoard Default OTP**: `000000`

## 🎉 System Status

✅ All components are running and verified
✅ Tests are passing
✅ System is ready for use