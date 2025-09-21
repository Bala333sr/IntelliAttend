#!/usr/bin/env python3
"""
INTELLIATTEND - Simple Server Startup Script
Smart Attendance Management System

This script starts the Flask server directly without the interactive setup.
Run: python3 start_server.py
"""

import os
import sys
import subprocess
from pathlib import Path

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def main():
    """Start the Flask server directly"""
    print(f"{Colors.BLUE}🚀 Starting IntelliAttend Flask Server...{Colors.ENDC}")
    
    project_root = Path(__file__).parent.absolute()
    backend_dir = project_root / "backend"
    app_script = backend_dir / "app.py"
    
    # Check if app.py exists
    if not app_script.exists():
        print(f"{Colors.FAIL}❌ Error: {app_script} not found{Colors.ENDC}")
        return False
    
    # Check if logs directory exists, create if not
    logs_dir = backend_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    print(f"{Colors.GREEN}✅ Logs directory ready{Colors.ENDC}")
    
    # Check if QR_DATA directories exist, create if not
    qr_data_dir = backend_dir / "QR_DATA"
    for subdir in ["tokens", "keys", "archive"]:
        (qr_data_dir / subdir).mkdir(parents=True, exist_ok=True)
    print(f"{Colors.GREEN}✅ QR_DATA directories ready{Colors.ENDC}")
    
    try:
        print(f"{Colors.BLUE}🌐 Server will be available at: http://localhost:5002{Colors.ENDC}")
        print(f"{Colors.WARNING}💡 Press Ctrl+C to stop the server{Colors.ENDC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.ENDC}")
        
        # Start the Flask server
        os.chdir(str(backend_dir))
        subprocess.run([sys.executable, str(app_script)], check=True)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}🛑 Server stopped by user{Colors.ENDC}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}❌ Server failed to start: {e}{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"{Colors.FAIL}❌ Unexpected error: {e}{Colors.ENDC}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"{Colors.GREEN}✅ Server shutdown completed{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Server startup failed{Colors.ENDC}")
        sys.exit(1)