#!/usr/bin/env python3
"""
INTELLIATTEND - Complete System Startup Script
Smart Attendance Management System

This script handles the complete startup process:
- Database setup and verification
- Server initialization
- Preview browser setup
- Interactive terminal interface

Run: python3 start_system.py
"""

import os
import sys
import subprocess
import time
import threading
import signal
import webbrowser
from pathlib import Path

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class IntelliAttendStarter:
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.server_process = None
        self.is_running = False
        
    def print_banner(self):
        """Display the startup banner"""
        banner = f"""
{Colors.CYAN}{'='*70}
{Colors.BOLD}🎓 INTELLIATTEND - Smart Attendance Management System{Colors.ENDC}
{Colors.CYAN}{'='*70}{Colors.ENDC}

{Colors.GREEN}🔧 Complete System Startup Script{Colors.ENDC}
{Colors.BLUE}📊 Features:{Colors.ENDC}
• Database Setup & Verification
• Flask Server Initialization  
• QR Code Generation System
• Faculty & SmartBoard Portals
• Automatic Browser Launch

{Colors.WARNING}🚀 Ready to launch the complete INTELLIATTEND system!{Colors.ENDC}
{Colors.CYAN}{'='*70}{Colors.ENDC}
        """
        print(banner)

    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print(f"{Colors.BLUE}🔍 Checking system dependencies...{Colors.ENDC}")
        
        required_packages = [
            ('flask', 'flask'),
            ('flask-sqlalchemy', 'flask_sqlalchemy'), 
            ('flask-jwt-extended', 'flask_jwt_extended'),
            ('pymysql', 'pymysql'),
            ('qrcode', 'qrcode'), 
            ('pillow', 'PIL'),
            ('werkzeug', 'werkzeug'),
            ('apscheduler', 'apscheduler'),
            ('geopy', 'geopy'),
            ('flask-cors', 'flask_cors'),
            ('flask-limiter', 'flask_limiter')
        ]
        
        missing_packages = []
        installed_packages = []
        
        for package_name, import_name in required_packages:
            try:
                __import__(import_name)
                installed_packages.append(package_name)
                print(f"  ✅ {package_name}")
            except ImportError:
                missing_packages.append(package_name)
                print(f"  ❌ {package_name}")
        
        if missing_packages:
            print(f"\n{Colors.WARNING}⚠️  Missing packages detected!{Colors.ENDC}")
            print(f"{Colors.BLUE}🔧 Installing missing packages...{Colors.ENDC}")
            
            # Try to install missing packages
            try:
                import subprocess
                import sys
                
                for package in missing_packages:
                    print(f"  📦 Installing {package}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                
                print(f"{Colors.GREEN}✅ All missing packages installed successfully!{Colors.ENDC}")
                return True
            except Exception as e:
                print(f"{Colors.FAIL}❌ Failed to install packages: {e}{Colors.ENDC}")
                print(f"{Colors.WARNING}💡 Try manually installing with: pip3 install {' '.join(missing_packages)}{Colors.ENDC}")
                return False
        
        print(f"{Colors.GREEN}✅ All dependencies verified!{Colors.ENDC}\n")
        return True

    def check_mysql_connection(self):
        """Check MySQL connection and database"""
        print(f"{Colors.BLUE}🗄️  Checking MySQL database connection...{Colors.ENDC}")
        
        try:
            import pymysql
            
            # Database configuration from .env or defaults
            db_config = {
                'host': 'localhost',
                'user': 'root',
                'password': '',
                'charset': 'utf8mb4',
                'port': 3306
            }
            
            # Test connection
            connection = pymysql.connect(**db_config)
            cursor = connection.cursor()
            
            # Check if database exists
            cursor.execute("SHOW DATABASES LIKE 'IntelliAttend_DataBase'")
            db_exists = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if db_exists:
                print(f"  ✅ MySQL connection successful")
                print(f"  ✅ Database 'IntelliAttend_DataBase' found")
                return True
            else:
                print(f"  ⚠️  Database 'IntelliAttend_DataBase' not found")
                return False
            
        except Exception as e:
            print(f"  ❌ MySQL connection failed: {e}")
            return False

    def check_database_tables(self):
        """Check if required tables exist in the database"""
        print(f"{Colors.BLUE}📋 Checking database tables...{Colors.ENDC}")
        
        try:
            import pymysql
            
            # Database configuration
            db_config = {
                'host': 'localhost',
                'user': 'root',
                'password': '',
                'database': 'IntelliAttend_DataBase',
                'charset': 'utf8mb4',
                'port': 3306
            }
            
            # Connect to database
            connection = pymysql.connect(**db_config)
            cursor = connection.cursor()
            
            # Check required tables
            required_tables = ['faculty', 'students', 'classrooms', 'classes', 'attendance_sessions', 'attendance_records']
            existing_tables = []
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            
            for table in required_tables:
                if table in table_names:
                    existing_tables.append(table)
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table}")
            
            cursor.close()
            connection.close()
            
            if len(existing_tables) == len(required_tables):
                print(f"{Colors.GREEN}✅ All required database tables found!{Colors.ENDC}\n")
                return True
            else:
                print(f"{Colors.WARNING}⚠️  Some database tables are missing{Colors.ENDC}\n")
                return False
                
        except Exception as e:
            print(f"  ❌ Database table check failed: {e}\n")
            return False

    def setup_database(self):
        """Setup the database if needed"""
        print(f"{Colors.BLUE}🏗️  Setting up database...{Colors.ENDC}")
        
        try:
            # Run database setup script
            setup_script = self.project_root.parent / "database" / "simple_database_setup.py"
            
            if setup_script.exists():
                result = subprocess.run(
                    ['python3', str(setup_script)],
                    cwd=str(self.project_root.parent / "database"),
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"  ✅ Database setup completed")
                    print(f"  📧 Faculty: john.smith@university.edu / faculty123")
                    print(f"  📧 Student: alice.williams@student.edu / student123")
                    return True
                else:
                    print(f"  ❌ Database setup failed: {result.stderr}")
                    return False
            else:
                print(f"  ❌ Database setup script not found")
                return False
                
        except Exception as e:
            print(f"  ❌ Database setup error: {e}")
            return False

    def setup_qr_directories(self):
        """Setup QR_DATA directory structure"""
        print(f"{Colors.BLUE}📁 Setting up QR directory structure...{Colors.ENDC}")
        
        qr_directories = [
            self.project_root / "backend" / "QR_DATA",
            self.project_root / "backend" / "QR_DATA" / "tokens",
            self.project_root / "backend" / "QR_DATA" / "keys", 
            self.project_root / "backend" / "QR_DATA" / "archive"
        ]
        
        for directory in qr_directories:
            directory.mkdir(exist_ok=True)
            print(f"  ✅ {directory.name}/")
        
        print(f"{Colors.GREEN}✅ QR directory structure ready!{Colors.ENDC}\n")

    def check_server_status(self):
        """Check if server is already running"""
        print(f"{Colors.BLUE}📡 Checking server status...{Colors.ENDC}")
        
        try:
            import requests
            response = requests.get("http://localhost:5002/api/health", timeout=3)
            if response.status_code == 200:
                print(f"  ⚠️  Server is already running on port 5002")
                return True
            else:
                print(f"  ✅ No server running on port 5002")
                return False
        except:
            print(f"  ✅ No server running on port 5002")
            return False

    def start_server(self):
        """Start the Flask server"""
        print(f"{Colors.BLUE}🚀 Starting Flask server...{Colors.ENDC}")
        
        try:
            server_script = self.project_root / "backend" / "app.py"
            
            if not server_script.exists():
                print(f"  ❌ Server script not found: {server_script}")
                return False
            
            # Use the same Python interpreter as the current script
            python_executable = sys.executable
            
            # Start server in background without capturing stdout/stderr to prevent hanging
            self.server_process = subprocess.Popen(
                [python_executable, str(server_script)],
                cwd=str(self.project_root / "backend")
                # Not capturing stdout/stderr to prevent buffer overflow issues
            )
            
            # Wait for server to start
            print(f"  ⏳ Waiting for server to initialize...")
            time.sleep(15)  # Increased wait time for proper initialization
            
            # Check if server is running by trying to access the health endpoint
            try:
                import requests
                response = requests.get("http://localhost:5002/api/health", timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ Flask server started successfully")
                    print(f"  🌐 Server running on http://localhost:5002")
                    self.is_running = True
                    return True
                else:
                    print(f"  ❌ Server started but not responding correctly")
                    return False
            except Exception as e:
                print(f"  ⚠️  Server process may be running but not responding to requests: {e}")
                # Check if the process is still running
                if self.server_process.poll() is None:
                    print(f"  ✅ Server process is running (PID: {self.server_process.pid})")
                    self.is_running = True
                    return True
                else:
                    print(f"  ❌ Server process has terminated")
                    return False
                
        except Exception as e:
            print(f"  ❌ Server startup error: {e}")
            return False

    def open_portals(self):
        """Open web portals in browser"""
        print(f"{Colors.BLUE}🌐 Opening web portals...{Colors.ENDC}")
        
        portals = [
            ("Faculty Portal", "http://localhost:5002"),
            ("SmartBoard Portal", "http://localhost:5002/smartboard"),
            ("Student Portal", "http://localhost:5002/student")
        ]
        
        for name, url in portals:
            try:
                webbrowser.open(url)
                print(f"  ✅ {name}: {url}")
                time.sleep(1)  # Small delay between opens
            except Exception as e:
                print(f"  ⚠️  Could not auto-open {name}: {e}")
                print(f"     Please manually open: {url}")

    def display_system_info(self):
        """Display system information and URLs"""
        info = f"""
{Colors.GREEN}🎉 INTELLIATTEND SYSTEM IS NOW RUNNING!{Colors.ENDC}

{Colors.BOLD}📱 Web Portals:{Colors.ENDC}
{Colors.CYAN}┌─────────────────────────────────────────────────┐
│  Faculty Portal:    http://localhost:5002       │
│  SmartBoard Portal: http://localhost:5002/smartboard │  
│  Student Portal:    http://localhost:5002/student    │
│  API Base:          http://localhost:5002/api        │
└─────────────────────────────────────────────────┘{Colors.ENDC}

{Colors.BOLD}🔐 Default Login Credentials:{Colors.ENDC}
{Colors.BLUE}Faculty:{Colors.ENDC} john.smith@university.edu / faculty123
{Colors.BLUE}Student:{Colors.ENDC} alice.williams@student.edu / student123

{Colors.BOLD}🔑 SmartBoard Default OTP:{Colors.ENDC} 000000

{Colors.BOLD}⚡ System Features:{Colors.ENDC}
• Dynamic QR Generation (5-second refresh, 2-minute sessions)
• Multi-factor Authentication (Biometric + GPS + Bluetooth)
• Real-time Attendance Tracking
• Centralized QR Management
• Session Management & Cleanup

{Colors.WARNING}💡 Press Ctrl+C to stop the system{Colors.ENDC}
        """
        print(info)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n{Colors.WARNING}🛑 Shutting down INTELLIATTEND system...{Colors.ENDC}")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Cleanup running processes"""
        if self.server_process and self.server_process.poll() is None:
            print(f"  🔄 Stopping Flask server...")
            self.server_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.server_process.wait(timeout=5)
                print(f"  ✅ Server stopped gracefully")
            except subprocess.TimeoutExpired:
                print(f"  ⚠️  Force killing server...")
                self.server_process.kill()
                self.server_process.wait()
        
        self.is_running = False
        print(f"{Colors.GREEN}✅ INTELLIATTEND system stopped successfully{Colors.ENDC}")

    def run_system(self):
        """Main system startup process"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Step 1: Check dependencies
            print(f"{Colors.HEADER}{'='*50}")
            print(f"{Colors.BOLD}Phase 1: System Verification{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}")
            
            if not self.check_dependencies():
                print(f"{Colors.FAIL}❌ Dependency check failed{Colors.ENDC}")
                return False

            # Step 2: Check database connection
            if not self.check_mysql_connection():
                print(f"{Colors.WARNING}⚠️  Database connection issue detected{Colors.ENDC}")
                return False

            # Step 3: Check database tables
            if not self.check_database_tables():
                print(f"{Colors.WARNING}⚠️  Database tables issue detected{Colors.ENDC}")
                return False

            # Step 4: Check server status
            if self.check_server_status():
                print(f"{Colors.WARNING}⚠️  Server is already running{Colors.ENDC}")
                # Kill existing server process
                self.kill_existing_server()

            # Step 5: Setup QR directories
            print(f"\n{Colors.HEADER}{'='*50}")
            print(f"{Colors.BOLD}Phase 2: System Preparation{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}")
            self.setup_qr_directories()

            # Step 6: Start server
            print(f"\n{Colors.HEADER}{'='*50}")
            print(f"{Colors.BOLD}Phase 3: System Startup{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}")
            if not self.start_server():
                print(f"{Colors.FAIL}❌ Server startup failed{Colors.ENDC}")
                return False

            # Step 7: Open portals
            self.open_portals()

            # Step 8: Display system info
            self.display_system_info()

            # Step 9: Keep running
            print(f"{Colors.BLUE}🔄 System monitoring... (Press Ctrl+C to stop){Colors.ENDC}")
            
            while self.is_running:
                time.sleep(1)
                # Check if server is still running
                if self.server_process and self.server_process.poll() is not None:
                    print(f"{Colors.FAIL}❌ Server process stopped unexpectedly{Colors.ENDC}")
                    break

            return True

        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)
        except Exception as e:
            print(f"{Colors.FAIL}❌ System startup error: {e}{Colors.ENDC}")
            self.cleanup()
            return False

    def kill_existing_server(self):
        """Kill any existing server processes"""
        print(f"{Colors.WARNING}🔄 Killing existing server process...{Colors.ENDC}")
        try:
            # Kill processes on port 5002
            import subprocess
            subprocess.run("lsof -i :5002 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null || true", 
                          shell=True, capture_output=True)
            time.sleep(2)  # Wait for process to terminate
            print(f"{Colors.GREEN}✅ Existing server process terminated{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  Could not kill existing server: {e}{Colors.ENDC}")

def main():
    """Main entry point with interactive prompt"""
    starter = IntelliAttendStarter()
    starter.print_banner()
    
    # Phase 1: System verification
    print(f"{Colors.HEADER}{'='*50}")
    print(f"{Colors.BOLD}Phase 1: System Verification{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}")
    
    # Check dependencies
    if not starter.check_dependencies():
        print(f"{Colors.FAIL}❌ Required dependencies are missing{Colors.ENDC}")
        return
    
    # Check database
    if not starter.check_mysql_connection():
        print(f"{Colors.FAIL}❌ Database connection failed{Colors.ENDC}")
        return
    
    # Check database tables
    if not starter.check_database_tables():
        print(f"{Colors.WARNING}⚠️  Some database tables are missing{Colors.ENDC}")
        response = input(f"{Colors.BOLD}🤔 Do you want to setup the database? (yes/no): {Colors.ENDC}").strip().lower()
        if response in ['yes', 'y', '1', 'start']:
            if not starter.setup_database():
                print(f"{Colors.FAIL}❌ Database setup failed{Colors.ENDC}")
                return
            else:
                print(f"{Colors.GREEN}✅ Database setup completed successfully{Colors.ENDC}\n")
        else:
            print(f"{Colors.BLUE}👋 Database setup skipped.{Colors.ENDC}")
            return
    
    # Check if server is already running
    if starter.check_server_status():
        response = input(f"{Colors.BOLD}🤔 Server is already running. Do you want to restart it? (yes/no): {Colors.ENDC}").strip().lower()
        if response not in ['yes', 'y', '1', 'start']:
            print(f"{Colors.BLUE}👋 System startup cancelled.{Colors.ENDC}")
            return
    
    # Interactive prompt for system startup
    print(f"\n{Colors.HEADER}{'='*50}")
    print(f"{Colors.BOLD}System Readiness Check Complete{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}")
    
    while True:
        try:
            response = input(f"{Colors.BOLD}🚀 Start INTELLIATTEND system? (yes/no): {Colors.ENDC}").strip().lower()
            
            if response in ['yes', 'y', '1', 'start']:
                print(f"\n{Colors.GREEN}🚀 Starting INTELLIATTEND system...{Colors.ENDC}\n")
                success = starter.run_system()
                
                if success:
                    print(f"\n{Colors.GREEN}✅ System completed successfully{Colors.ENDC}")
                else:
                    print(f"\n{Colors.FAIL}❌ System startup failed{Colors.ENDC}")
                break
                
            elif response in ['no', 'n', '0', 'exit', 'quit']:
                print(f"\n{Colors.BLUE}👋 Goodbye! INTELLIATTEND startup cancelled.{Colors.ENDC}")
                break
                
            else:
                print(f"{Colors.WARNING}⚠️  Please enter 'yes' or 'no'{Colors.ENDC}")
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.BLUE}👋 Goodbye! INTELLIATTEND startup cancelled.{Colors.ENDC}")
            break
        except EOFError:
            print(f"\n\n{Colors.BLUE}👋 Goodbye! INTELLIATTEND startup cancelled.{Colors.ENDC}")
            break

if __name__ == "__main__":
    main()