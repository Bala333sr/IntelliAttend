# IntelliAttend System Monitor

A comprehensive real-time monitoring and control dashboard for the IntelliAttend system that replaces terminal-based monitoring.

## 🌟 Features

### Real-time System Monitoring
- ✅ **Process Status Tracking** - Monitor all system components
- 📊 **Live Metrics Dashboard** - System uptime, active sessions, QR generation count
- 🔄 **Auto-refreshing Status** - Real-time updates without page refresh
- 🎯 **Service Health Checks** - Database, QR generator, authentication services

### Process Control
- ▶️ **Start/Stop Services** - Control individual system components
- 🔄 **Restart Functionality** - Quick service restart capabilities
- 🛑 **Session Management** - Stop active QR generation sessions
- 🧹 **Cleanup Operations** - Proper resource cleanup and session termination

### Live Logging
- 📺 **Terminal Replacement** - Real-time log viewing in browser
- 🎨 **Color-coded Messages** - Different colors for info, warning, error messages
- 📜 **Log History** - Maintains recent log entries with timestamps
- 🗑️ **Clear Logs** - Manual log clearing functionality

## 🚀 Quick Start

### Method 1: Using the Launcher (Recommended)
```bash
cd "/Users/anji/Desktop/IntelliAttend"
python3 launcher.py
```

Then select option **1** to open the System Monitor Dashboard.

### Method 2: Direct Access
1. Start the server:
   ```bash
   cd "/Users/anji/Desktop/IntelliAttend"
   python3 server/app.py
   ```

2. Open in browser:
   ```
   http://192.168.0.3:5002/monitor
   ```

## 📊 Dashboard Components

### 1. System Metrics
- **System Uptime** - How long the server has been running
- **Active Sessions** - Number of currently running QR generation sessions
- **QR Codes Generated** - Total QR codes created today
- **Total Logins** - Login attempts for the day

### 2. Process Status & Control
**Monitored Processes:**
- 🖥️ **Flask Server** - Main application server (Port 5002)
- 🔲 **QR Code Generator** - Dynamic QR code generation service
- 🗄️ **Database Service** - SQLite database connectivity
- 🛡️ **Authentication Service** - User login and JWT token management
- 👥 **Session Manager** - Attendance session lifecycle management

**Control Actions:**
- ▶️ **Start** - Initialize stopped services
- ⏹️ **Stop** - Gracefully stop running services
- 🔄 **Restart** - Stop and start services

### 3. Live System Logs
- Real-time log streaming
- Color-coded message types
- Automatic scrolling to latest entries
- Manual log clearing

## 🛠️ API Endpoints

The system monitor uses these API endpoints:

### Health & Status
- `GET /api/health` - Overall system health check
- `GET /api/system/metrics` - System metrics and statistics
- `GET /api/qr/status` - QR generation service status
- `GET /api/db/status` - Database connectivity status
- `GET /api/auth/status` - Authentication service status
- `GET /api/session/status` - Session management status

### Process Control
- `POST /api/process/start` - Start a system process
- `POST /api/process/stop` - Stop a system process
- `POST /api/process/restart` - Restart a system process

Example process control request:
```json
{
  "process_id": "qr-generator",
  "action": "stop"
}
```

## 🎯 Use Cases

### 1. Development & Debugging
- Monitor system health during development
- View real-time logs without terminal access
- Quick restart of services after code changes
- Debugging session and QR generation issues

### 2. System Administration
- Monitor system uptime and performance
- Control services without command line access
- View system metrics and usage statistics
- Manage active sessions and cleanup resources

### 3. Demonstration & Presentation
- Professional dashboard for system demonstrations
- Real-time status updates during presentations
- Visual feedback of system operations
- Clean interface without terminal clutter

## 🔧 Configuration

### Auto-refresh Intervals
- **Process Status**: 10 seconds
- **System Metrics**: 30 seconds
- **Uptime Counter**: 1 second
- **Live Logs**: Real-time (as events occur)

### Customization
The dashboard can be customized by modifying:
- `/templates/system_monitor.html` - UI layout and styling
- `/server/app.py` - API endpoints and monitoring logic
- Refresh intervals in JavaScript section

## 🚨 Process Control Features

### QR Generator Control
- **Stop**: Terminates all active QR generation sessions
- **Status**: Shows number of active sessions and session IDs
- **Real-time Updates**: Monitor QR generation activity

### Session Manager Control  
- **Stop**: Completes all active attendance sessions
- **Cleanup**: Removes sessions from memory and updates database
- **Status**: Shows detailed session information

### Database Monitoring
- **Connection Status**: Verifies database connectivity
- **Record Counts**: Shows number of students and faculty
- **Health Checks**: Continuous connectivity monitoring

## 📱 Mobile Friendly

The system monitor is responsive and works on:
- 💻 Desktop browsers
- 📱 Mobile devices
- 📟 Tablets
- 🖥️ Large displays

## 🔐 Security Features

- **Process Isolation**: Safe process control without system access
- **Resource Cleanup**: Proper cleanup of background threads
- **Session Management**: Secure session termination
- **Error Handling**: Graceful error handling and reporting

## 🎨 Visual Features

- **Gradient Background** - Modern visual design
- **Status Indicators** - Color-coded process status (green/red/yellow)
- **Animated Elements** - Pulsing status indicators and live updates
- **Card-based Layout** - Organized information presentation
- **Bootstrap Styling** - Professional and responsive design

## 📈 Monitoring Benefits

### Replaces Terminal Monitoring
Instead of monitoring multiple terminal windows:
- ❌ `tail -f server.log`
- ❌ `ps aux | grep python`
- ❌ Multiple terminal tabs
- ❌ Command-line process management

You get:
- ✅ Single dashboard view
- ✅ Real-time status updates
- ✅ Visual process control
- ✅ Integrated logging
- ✅ Professional presentation

## 🚀 Getting Started Checklist

1. ✅ Server running on port 5002
2. ✅ System monitoring routes active
3. ✅ Database connectivity verified
4. ✅ QR generation system ready
5. ✅ Authentication services running

Access the dashboard at: **http://192.168.0.3:5002/monitor**

## 🆘 Troubleshooting

### Dashboard not loading
- Verify server is running: `curl http://192.168.0.3:5002/api/health`
- Check server logs for errors
- Ensure port 5002 is not blocked

### Process controls not working
- Check API endpoints are responding
- Verify database connectivity
- Review server logs for error messages

### Live logs not updating
- Refresh the page
- Check browser console for JavaScript errors
- Verify server WebSocket connections

---

*Replace terminal monitoring with a modern, professional dashboard!* 🎯