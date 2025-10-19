# 🚀 IntelliAttend - Quick Start Guide

Get IntelliAttend running in **5 minutes** with this quick start guide!

## ⚡ Super Quick Setup (Automated)

```bash
# 1. Download and extract the ZIP file from GitHub
# 2. Open terminal in the extracted folder
# 3. Run the automated setup:

chmod +x setup.sh
./setup.sh

# 4. Start all services:
./start-all.sh
```

**That's it!** 🎉 Your system is now running at:
- **Web Dashboard**: http://localhost:3000
- **API Server**: http://localhost:8080
- **Mobile App**: Build with Android Studio

## 📱 Mobile App Quick Setup

1. **Install Android Studio** (if not already installed)
2. **Open the project**:
   ```bash
   # Open Android Studio and select:
   # File > Open > Navigate to: mobile/app/
   ```
3. **Build and run**:
   - Connect your Android device or start an emulator
   - Click the "Run" button in Android Studio

## 🧪 Test Your Setup

### Test the Web Dashboard
1. Open http://localhost:3000
2. Click "Admin Login"
3. Use test credentials (created during setup)

### Test the API
```bash
curl http://localhost:8080/health
```

### Test Mobile App
1. Install the app on your device
2. Open the app
3. Try device registration

## 🔧 Manual Setup (If Automated Fails)

### Prerequisites
- **Python 3.8+**: `python3 --version`
- **Node.js 16+**: `node --version`
- **Java 17**: `java -version` (for mobile)

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py
python seed_data.py
python run_server.py
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
npm start
```

### Mobile Setup
```bash
cd mobile/app
cp local.properties.example local.properties
# Edit local.properties with your Android SDK path
chmod +x gradlew
./gradlew assembleDebug
```

## 🌐 Access Your System

| Component | URL | Description |
|-----------|-----|-------------|
| **Web Dashboard** | http://localhost:3000 | Admin and faculty interface |
| **API Server** | http://localhost:8080 | Backend API |
| **API Docs** | http://localhost:8080/docs | Interactive API documentation |
| **WebSocket** | ws://localhost:8765 | Real-time updates |

## 👥 Default Test Accounts

The setup creates these test accounts:

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@intelliattend.com | admin123 |
| **Faculty** | faculty@intelliattend.com | faculty123 |
| **Student** | student@intelliattend.com | student123 |

## 📱 Mobile App Configuration

Update the server URL in your mobile app:

1. **For Development**: Edit `mobile/app/app/build.gradle`
   ```gradle
   buildConfigField "String", "BASE_URL", '"http://YOUR_IP:8080/api/"'
   ```

2. **Find Your IP Address**:
   ```bash
   # On macOS/Linux:
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # On Windows:
   ipconfig | findstr "IPv4"
   ```

## 🛠️ Development Commands

```bash
# Start all services
./start-all.sh

# Stop all services
./stop-all.sh

# Reset database
cd backend && python reset_db.py

# Build mobile app
cd mobile/app && ./gradlew assembleDebug

# Run tests
cd backend && python -m pytest
cd frontend && npm test
```

## 🆘 Troubleshooting

### Common Issues

**"Port already in use"**
```bash
# Kill processes on ports
sudo lsof -ti:8080 | xargs kill -9  # Backend
sudo lsof -ti:3000 | xargs kill -9  # Frontend
sudo lsof -ti:8765 | xargs kill -9  # WebSocket
```

**"Module not found"**
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && rm -rf node_modules && npm install
```

**"Database locked"**
```bash
cd backend && rm intelliattend.db && python init_db.py
```

**Mobile app won't connect**
- Check if backend is running: `curl http://localhost:8080/health`
- Update IP address in mobile app configuration
- Ensure device and computer are on same network

### Getting Help

1. **Check logs**: Each service creates logs in its directory
2. **Verify prerequisites**: Run `./setup.sh` again
3. **Reset everything**: Delete generated files and run setup again

## 🎯 Next Steps

After successful setup:

1. **Customize**: Update configuration files with your settings
2. **Add Data**: Import your institution's students and faculty
3. **Configure**: Set up proper server URLs for production
4. **Deploy**: See `DEPLOYMENT.md` for production setup

---

**🎉 Congratulations!** You now have a fully functional IntelliAttend system running locally. Start exploring the features and customizing it for your needs!