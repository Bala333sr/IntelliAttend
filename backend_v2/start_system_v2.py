#!/usr/bin/env python3
"""
INTELLIATTEND V2 - Complete System Startup Script
Modern FastAPI Backend with Attendance System

This script handles:
- Dependency verification
- Database initialization
- Attendance system setup
- Server startup
- Health checks
- Interactive monitoring

Run: python3 start_system_v2.py
"""

import os
import sys
import subprocess
import time
import signal
import webbrowser
from pathlib import Path

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class IntelliAttendV2Starter:
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.server_process = None
        self.is_running = False
        
    def print_banner(self):
        """Display startup banner"""
        banner = f"""
{Colors.CYAN}{'='*70}
{Colors.BOLD}🎓 INTELLIATTEND V2 - Smart Attendance System{Colors.ENDC}
{Colors.CYAN}{'='*70}{Colors.ENDC}

{Colors.GREEN}🚀 FastAPI Backend with Multi-Factor Verification{Colors.ENDC}
{Colors.BLUE}📊 Features:{Colors.ENDC}
• QR Token Verification (40% weight)
• GPS Geofencing (25% weight)
• WiFi Network Detection (20% weight)
• Bluetooth Beacon Detection (15% weight)
• Real-time Attendance Marking
• Automatic API Documentation

{Colors.WARNING}🎯 Ready to launch INTELLIATTEND V2!{Colors.ENDC}
{Colors.CYAN}{'='*70}{Colors.ENDC}
        """
        print(banner)

    def check_python_version(self):
        """Check Python version"""
        print(f"{Colors.BLUE}🐍 Checking Python version...{Colors.ENDC}")
        
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            print(f"  ❌ Python 3.8+ required, found {version.major}.{version.minor}")
            return False

    def check_dependencies(self):
        """Check required packages"""
        print(f"\n{Colors.BLUE}📦 Checking dependencies...{Colors.ENDC}")
        
        required = [
            ('fastapi', 'FastAPI'),
            ('uvicorn', 'Uvicorn'),
            ('pydantic', 'Pydantic'),
            ('sqlalchemy', 'SQLAlchemy'),
            ('bcrypt', 'Bcrypt'),
            ('pyjwt', 'PyJWT'),
            ('geopy', 'Geopy')
        ]
        
        missing = []
        for package, display_name in required:
            try:
                __import__(package)
                print(f"  ✅ {display_name}")
            except ImportError:
                missing.append(package)
                print(f"  ❌ {display_name}")
        
        if missing:
            print(f"\n{Colors.WARNING}📥 Installing missing packages...{Colors.ENDC}")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', 
                    '-r', str(self.project_root / 'requirements.txt'),
                    '--quiet'
                ])
                print(f"{Colors.GREEN}✅ All packages installed!{Colors.ENDC}")
                return True
            except Exception as e:
                print(f"{Colors.FAIL}❌ Installation failed: {e}{Colors.ENDC}")
                return False
        
        print(f"{Colors.GREEN}✅ All dependencies satisfied!{Colors.ENDC}")
        return True

    def check_database(self):
        """Check database file"""
        print(f"\n{Colors.BLUE}🗄️  Checking database...{Colors.ENDC}")
        
        db_file = self.project_root / "intelliattend_v2.db"
        
        if db_file.exists():
            size_mb = db_file.stat().st_size / (1024 * 1024)
            print(f"  ✅ Database found: intelliattend_v2.db ({size_mb:.2f} MB)")
            return True, True
        else:
            print(f"  ⚠️  Database not found: intelliattend_v2.db")
            return True, False

    def init_database(self):
        """Initialize database with tables and test data"""
        print(f"\n{Colors.BLUE}🏗️  Initializing database...{Colors.ENDC}")
        
        init_script = self.project_root / "init_attendance_tables.py"
        
        if not init_script.exists():
            print(f"  ❌ Initialization script not found")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(init_script)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"  ✅ Database initialized successfully!")
                # Extract and display key info from output
                if "QR Token:" in result.stdout:
                    for line in result.stdout.split('\n'):
                        if "QR Token:" in line or "GPS Location:" in line:
                            print(f"  {Colors.CYAN}{line.strip()}{Colors.ENDC}")
                return True
            else:
                print(f"  ❌ Initialization failed")
                if result.stderr:
                    print(f"  Error: {result.stderr[:200]}")
                return False
                
        except Exception as e:
            print(f"  ❌ Initialization error: {e}")
            return False

    def check_port(self, port=8080):
        """Check if port is available"""
        print(f"\n{Colors.BLUE}🔌 Checking port {port}...{Colors.ENDC}")
        
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"  ⚠️  Port {port} is in use")
                return False
            else:
                print(f"  ✅ Port {port} is available")
                return True
        except Exception as e:
            print(f"  ⚠️  Port check failed: {e}")
            return True

    def kill_port(self, port=8080):
        """Kill process on port"""
        print(f"  🔄 Attempting to free port {port}...")
        
        try:
            # macOS/Linux
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                pid = result.stdout.strip()
                subprocess.run(['kill', '-9', pid])
                time.sleep(1)
                print(f"  ✅ Killed process on port {port}")
                return True
            else:
                print(f"  ℹ️  No process found on port {port}")
                return True
                
        except Exception as e:
            print(f"  ⚠️  Could not kill process: {e}")
            return False

    def start_server(self):
        """Start FastAPI server"""
        print(f"\n{Colors.BLUE}🚀 Starting FastAPI server...{Colors.ENDC}")
        
        main_py = self.project_root / "main.py"
        
        if not main_py.exists():
            print(f"  ❌ main.py not found")
            return False
        
        try:
            # Start server in background
            self.server_process = subprocess.Popen(
                [sys.executable, str(main_py)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            print(f"  ⏳ Waiting for server to start...")
            time.sleep(3)
            
            # Check if process is still running
            if self.server_process.poll() is not None:
                print(f"  ❌ Server process terminated")
                return False
            
            # Test health endpoint
            max_retries = 5
            for i in range(max_retries):
                try:
                    import requests
                    response = requests.get("http://localhost:8080/health", timeout=2)
                    if response.status_code == 200:
                        print(f"  ✅ Server started successfully!")
                        self.is_running = True
                        return True
                except:
                    if i < max_retries - 1:
                        time.sleep(2)
                    else:
                        print(f"  ⚠️  Server started but not responding yet")
                        self.is_running = True
                        return True
            
            return False
            
        except Exception as e:
            print(f"  ❌ Server startup failed: {e}")
            return False

    def open_documentation(self):
        """Open API documentation in browser"""
        print(f"\n{Colors.BLUE}🌐 Opening API documentation...{Colors.ENDC}")
        
        urls = [
            ("Swagger UI", "http://localhost:8080/api/docs"),
            ("ReDoc", "http://localhost:8080/api/redoc")
        ]
        
        for name, url in urls:
            try:
                webbrowser.open(url)
                print(f"  ✅ {name}: {url}")
                time.sleep(1)
            except Exception as e:
                print(f"  ⚠️  Could not open {name}: {e}")

    def display_system_info(self):
        """Display system information"""
        info = f"""
{Colors.GREEN}{'='*70}
🎉 INTELLIATTEND V2 IS RUNNING!
{'='*70}{Colors.ENDC}

{Colors.BOLD}📡 API Endpoints:{Colors.ENDC}
{Colors.CYAN}┌────────────────────────────────────────────────────────┐
│  Health Check:        http://localhost:8080/health     │
│  API Status:          http://localhost:8080/api/status │
│  Student Login:       POST /api/student/login          │
│  Student Profile:     GET /api/student/profile         │
│  Today's Timetable:   GET /api/student/timetable/today │
│  Mark Attendance:     POST /api/attendance/mark        │
│                                                         │
│  📚 API Docs:         http://localhost:8080/api/docs   │
│  📖 ReDoc:            http://localhost:8080/api/redoc  │
└────────────────────────────────────────────────────────┘{Colors.ENDC}

{Colors.BOLD}🧪 Test Data:{Colors.ENDC}
{Colors.BLUE}QR Token:{Colors.ENDC} TEST_QR_TOKEN_2024
{Colors.BLUE}GPS Location:{Colors.ENDC} 17.4435, 78.3489
{Colors.BLUE}WiFi SSID:{Colors.ENDC} CampusWiFi-R301
{Colors.BLUE}WiFi BSSID:{Colors.ENDC} AA:BB:CC:DD:EE:FF
{Colors.BLUE}Bluetooth MAC:{Colors.ENDC} A1:B2:C3:D4:E5:F6

{Colors.BOLD}🎯 Attendance Verification:{Colors.ENDC}
• QR Token:    40% (mandatory)
• GPS:         25% (50m geofence)
• WiFi:        20% (SSID + BSSID match)
• Bluetooth:   15% (beacon detection)
• Minimum:     70% score required

{Colors.BOLD}📱 Mobile App:{Colors.ENDC}
• Configure backend URL: http://YOUR_IP:8080
• Use demo student credentials to login
• Scan QR code: TEST_QR_TOKEN_2024
• Wait for warm scan (GPS, WiFi, Bluetooth)
• Submit and see instant verification!

{Colors.WARNING}💡 Press Ctrl+C to stop the system{Colors.ENDC}
        """
        print(info)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n{Colors.WARNING}🛑 Shutting down...{Colors.ENDC}")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Cleanup running processes"""
        if self.server_process and self.server_process.poll() is None:
            print(f"  🔄 Stopping server...")
            self.server_process.terminate()
            
            try:
                self.server_process.wait(timeout=5)
                print(f"  ✅ Server stopped gracefully")
            except subprocess.TimeoutExpired:
                print(f"  ⚠️  Force killing server...")
                self.server_process.kill()
                self.server_process.wait()
        
        self.is_running = False
        print(f"{Colors.GREEN}✅ System stopped successfully{Colors.ENDC}")

    def run(self):
        """Main execution flow"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Phase 1: System verification
            print(f"\n{Colors.HEADER}{'='*70}")
            print(f"{Colors.BOLD}Phase 1: System Verification{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
            
            if not self.check_python_version():
                return False
            
            if not self.check_dependencies():
                return False
            
            db_ok, db_exists = self.check_database()
            if not db_ok:
                return False
            
            # Phase 2: Database setup
            if not db_exists:
                print(f"\n{Colors.HEADER}{'='*70}")
                print(f"{Colors.BOLD}Phase 2: Database Initialization{Colors.ENDC}")
                print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
                
                response = input(f"\n{Colors.BOLD}🤔 Initialize database with test data? (yes/no): {Colors.ENDC}").strip().lower()
                
                if response in ['yes', 'y']:
                    if not self.init_database():
                        print(f"{Colors.FAIL}❌ Database initialization failed{Colors.ENDC}")
                        return False
                else:
                    print(f"{Colors.WARNING}⚠️  Database not initialized. Server will create empty database.{Colors.ENDC}")
            
            # Phase 3: Port check
            print(f"\n{Colors.HEADER}{'='*70}")
            print(f"{Colors.BOLD}Phase 3: Port Check{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
            
            if not self.check_port():
                response = input(f"{Colors.BOLD}🤔 Port 8080 is in use. Kill process? (yes/no): {Colors.ENDC}").strip().lower()
                if response in ['yes', 'y']:
                    if not self.kill_port():
                        return False
                else:
                    print(f"{Colors.FAIL}❌ Cannot start server on busy port{Colors.ENDC}")
                    return False
            
            # Phase 4: Server startup
            print(f"\n{Colors.HEADER}{'='*70}")
            print(f"{Colors.BOLD}Phase 4: Server Startup{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
            
            if not self.start_server():
                print(f"{Colors.FAIL}❌ Server startup failed{Colors.ENDC}")
                return False
            
            # Phase 5: Open documentation
            self.open_documentation()
            
            # Phase 6: Display info and monitor
            self.display_system_info()
            
            print(f"\n{Colors.BLUE}🔄 System monitoring... (Press Ctrl+C to stop){Colors.ENDC}\n")
            
            while self.is_running:
                time.sleep(1)
                if self.server_process and self.server_process.poll() is not None:
                    print(f"{Colors.FAIL}❌ Server process stopped unexpectedly{Colors.ENDC}")
                    break
            
            return True
            
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)
        except Exception as e:
            print(f"{Colors.FAIL}❌ System error: {e}{Colors.ENDC}")
            self.cleanup()
            return False

def main():
    """Entry point"""
    starter = IntelliAttendV2Starter()
    starter.print_banner()
    
    # Quick verification
    print(f"{Colors.HEADER}{'='*70}")
    print(f"{Colors.BOLD}Quick System Check{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    if not starter.check_python_version():
        return
    
    # Prompt to start
    print(f"\n{Colors.HEADER}{'='*70}")
    print(f"{Colors.BOLD}Ready to Start{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    response = input(f"\n{Colors.BOLD}🚀 Start INTELLIATTEND V2? (yes/no): {Colors.ENDC}").strip().lower()
    
    if response in ['yes', 'y']:
        print(f"\n{Colors.GREEN}🚀 Starting system...{Colors.ENDC}")
        success = starter.run()
        
        if success:
            print(f"\n{Colors.GREEN}✅ System shutdown complete{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}❌ System startup failed{Colors.ENDC}")
    else:
        print(f"\n{Colors.BLUE}👋 Startup cancelled{Colors.ENDC}")

if __name__ == "__main__":
    main()
