# 🔧 IntelliAttend - Troubleshooting Guide

This guide helps you resolve common issues when setting up or running IntelliAttend.

## 🚨 Common Setup Issues

### 1. Setup Script Fails

**Problem**: `./setup.sh` exits with errors

**Solutions**:
```bash
# Check prerequisites
python3 --version  # Should be 3.8+
node --version     # Should be 16+
npm --version      # Should be 8+

# Make script executable
chmod +x setup.sh

# Run with verbose output
bash -x setup.sh

# Check specific component setup
cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd frontend && npm install
```

### 2. Permission Denied Errors

**Problem**: Permission errors when running scripts

**Solutions**:
```bash
# Make all scripts executable
find . -name "*.sh" -exec chmod +x {} \;

# Fix Python script permissions
find . -name "*.py" -exec chmod +x {} \;

# Fix ownership (if needed)
sudo chown -R $USER:$USER .
```

### 3. Python Virtual Environment Issues

**Problem**: Virtual environment creation fails

**Solutions**:
```bash
# Install python3-venv (Ubuntu/Debian)
sudo apt install python3-venv

# Install python3-venv (CentOS/RHEL)
sudo yum install python3-venv

# Use alternative virtual environment
pip install virtualenv
cd backend
virtualenv venv
source venv/bin/activate
```

## 🌐 Network and Port Issues

### 1. Port Already in Use

**Problem**: "Address already in use" errors

**Solutions**:
```bash
# Find processes using ports
sudo lsof -i :8080  # Backend
sudo lsof -i :3000  # Frontend
sudo lsof -i :8765  # WebSocket

# Kill processes
sudo kill -9 $(sudo lsof -t -i:8080)
sudo kill -9 $(sudo lsof -t -i:3000)
sudo kill -9 $(sudo lsof -t -i:8765)

# Use alternative ports
# Backend: Edit backend/config.py
# Frontend: Edit frontend/package.json
# WebSocket: Edit realtime_presence/server.py
```

### 2. Cannot Connect to Services

**Problem**: Services start but can't connect

**Solutions**:
```bash
# Check if services are running
curl http://localhost:8080/health
curl http://localhost:3000
telnet localhost 8765

# Check firewall settings
sudo ufw status
sudo ufw allow 8080
sudo ufw allow 3000
sudo ufw allow 8765

# Check network interface binding
netstat -tlnp | grep :8080
```

### 3. Mobile App Cannot Connect to Server

**Problem**: Mobile app shows connection errors

**Solutions**:
```bash
# Find your IP address
# macOS/Linux:
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows:
ipconfig | findstr "IPv4"

# Update mobile app configuration
# Edit mobile/app/app/build.gradle:
buildConfigField "String", "BASE_URL", '"http://YOUR_IP:8080/api/"'

# Ensure devices are on same network
# Test connectivity from mobile device browser:
# http://YOUR_IP:8080/health
```

## 🗄️ Database Issues

### 1. Database Connection Errors

**Problem**: Cannot connect to database

**Solutions**:
```bash
# Check database file exists
ls -la backend/intelliattend.db

# Reset database
cd backend
rm intelliattend.db
python init_db.py
python seed_data.py

# Check database permissions
chmod 664 intelliattend.db

# For PostgreSQL (production)
psql -h localhost -U username -d intelliattend -c "SELECT 1;"
```

### 2. Database Locked Errors

**Problem**: "Database is locked" errors

**Solutions**:
```bash
# Stop all services
./stop-all.sh

# Check for lock files
ls -la backend/*.db-*

# Remove lock files
rm backend/*.db-wal backend/*.db-shm

# Restart services
./start-all.sh
```

### 3. Migration Errors

**Problem**: Database migration fails

**Solutions**:
```bash
# Check current database version
cd backend
python -c "
import sqlite3
conn = sqlite3.connect('intelliattend.db')
cursor = conn.cursor()
cursor.execute('PRAGMA user_version;')
print('Database version:', cursor.fetchone()[0])
conn.close()
"

# Backup and reset
cp intelliattend.db intelliattend.db.backup
rm intelliattend.db
python init_db.py
python seed_data.py
```

## 📱 Mobile App Issues

### 1. Gradle Build Fails

**Problem**: Android build errors

**Solutions**:
```bash
# Check Java version
java -version  # Should be 17

# Clean and rebuild
cd mobile/app
./gradlew clean
./gradlew assembleDebug

# Check Android SDK
echo $ANDROID_HOME
ls $ANDROID_HOME/platforms

# Update local.properties
echo "sdk.dir=$ANDROID_HOME" > local.properties

# Fix Gradle wrapper
chmod +x gradlew
./gradlew wrapper --gradle-version 8.12
```

### 2. KSP/KAPT Errors

**Problem**: Annotation processing fails

**Solutions**:
```bash
# Clean build cache
cd mobile/app
./gradlew clean
rm -rf .gradle
rm -rf app/.gradle

# Check Kotlin version compatibility
grep kotlin_version build.gradle
grep ksp_version build.gradle

# Rebuild
./gradlew assembleDebug --stacktrace
```

### 3. Device Installation Fails

**Problem**: Cannot install APK on device

**Solutions**:
```bash
# Check device connection
adb devices

# Enable USB debugging on device
# Settings > Developer Options > USB Debugging

# Install manually
adb install app/build/outputs/apk/debug/app-debug.apk

# Check device compatibility
adb shell getprop ro.build.version.sdk  # Should be 24+
```

## 🌐 Frontend Issues

### 1. npm Install Fails

**Problem**: Node.js dependency installation errors

**Solutions**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Use yarn instead
npm install -g yarn
yarn install

# Check Node.js version
node --version  # Should be 16+
npm --version   # Should be 8+
```

### 2. Build Errors

**Problem**: Frontend build fails

**Solutions**:
```bash
# Check for syntax errors
cd frontend
npm run lint

# Increase memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build

# Check environment variables
cat .env
```

### 3. Runtime Errors

**Problem**: Frontend loads but has errors

**Solutions**:
```bash
# Check browser console for errors
# Open Developer Tools > Console

# Verify API connectivity
curl http://localhost:8080/api/health

# Check environment configuration
cat frontend/.env

# Test with development server
npm start
```

## 🔧 Backend Issues

### 1. Python Import Errors

**Problem**: Module not found errors

**Solutions**:
```bash
# Activate virtual environment
cd backend
source venv/bin/activate

# Install missing dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall in development mode
pip install -e .
```

### 2. Flask Server Errors

**Problem**: Backend server won't start

**Solutions**:
```bash
# Check Python version
python --version

# Run with debug mode
cd backend
export FLASK_DEBUG=1
python run_server.py

# Check configuration
python -c "from config import *; print(vars())"

# Test minimal server
python -c "
from flask import Flask
app = Flask(__name__)
@app.route('/test')
def test():
    return 'OK'
app.run(port=8081)
"
```

### 3. API Endpoint Errors

**Problem**: API returns 500 errors

**Solutions**:
```bash
# Check logs
tail -f backend/logs/app.log

# Test individual endpoints
curl -v http://localhost:8080/api/health
curl -v http://localhost:8080/api/students

# Check database connection
cd backend
python -c "
from app import app, db
with app.app_context():
    print('Database connection:', db.engine.url)
    print('Tables:', db.engine.table_names())
"
```

## 🔄 Real-time Service Issues

### 1. WebSocket Connection Fails

**Problem**: Real-time updates not working

**Solutions**:
```bash
# Check WebSocket server
cd realtime_presence
python server.py

# Test WebSocket connection
# Use browser console:
# ws = new WebSocket('ws://localhost:8765')
# ws.onopen = () => console.log('Connected')
# ws.onerror = (e) => console.log('Error:', e)

# Check firewall
sudo ufw allow 8765
```

### 2. Message Broadcasting Issues

**Problem**: Messages not reaching all clients

**Solutions**:
```bash
# Check server logs
cd realtime_presence
python server.py --debug

# Test with multiple clients
python test_client.py

# Check memory usage
ps aux | grep python
```

## 🔍 Debugging Tools

### 1. Log Analysis

```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs (browser console)
# Open Developer Tools > Console

# System logs
journalctl -f -u intelliattend

# Database logs
sqlite3 backend/intelliattend.db ".log stdout"
```

### 2. Network Debugging

```bash
# Check open ports
netstat -tlnp

# Monitor network traffic
sudo tcpdump -i any port 8080

# Test API endpoints
curl -v -H "Content-Type: application/json" \
  -d '{"test": "data"}' \
  http://localhost:8080/api/test
```

### 3. Performance Monitoring

```bash
# Check system resources
top
htop
free -h
df -h

# Monitor Python processes
ps aux | grep python

# Check database performance
sqlite3 backend/intelliattend.db ".timer on" "SELECT COUNT(*) FROM students;"
```

## 🆘 Getting Additional Help

### 1. Collect Debug Information

```bash
# System information
uname -a
python3 --version
node --version
java -version

# Service status
curl -s http://localhost:8080/health || echo "Backend down"
curl -s http://localhost:3000 || echo "Frontend down"
nc -z localhost 8765 && echo "WebSocket up" || echo "WebSocket down"

# Log files
ls -la */logs/
ls -la */*.log
```

### 2. Reset Everything

```bash
# Nuclear option - reset everything
./stop-all.sh
rm -rf backend/venv
rm -rf frontend/node_modules
rm -rf backend/intelliattend.db
rm -rf backend/logs/*
./setup.sh
```

### 3. Minimal Test Setup

```bash
# Test with minimal configuration
cd backend
python3 -m venv test_venv
source test_venv/bin/activate
pip install flask
python -c "
from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello():
    return 'IntelliAttend Test Server'
app.run(port=8081)
"
```

---

If none of these solutions work, please:

1. **Check the logs** in each component's directory
2. **Verify prerequisites** are correctly installed
3. **Try the minimal test setup** to isolate issues
4. **Reset everything** and start fresh if needed

Remember: Most issues are related to missing dependencies, port conflicts, or permission problems. The automated setup script handles most of these, but manual intervention may be needed in some environments.