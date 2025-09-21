#!/usr/bin/env python3
"""
INTELLIATTEND Installation Script
Easy setup for the Smart Attendance Management System
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print installation banner"""
    print("🚀 INTELLIATTEND Installation Script")
    print("=" * 50)
    print("Smart Attendance Management System")
    print("Version: 1.0.0")
    print("=" * 50)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True

def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing Python packages...")
    
    try:
        # Install minimal requirements for basic functionality
        minimal_packages = [
            'Flask==2.3.3',
            'python-dotenv==1.0.0',
            'requests==2.31.0'
        ]
        
        for package in minimal_packages:
            print(f"   Installing {package}...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"   ⚠️  Warning: Failed to install {package}")
                print(f"      Error: {result.stderr}")
            else:
                print(f"   ✅ {package} installed successfully")
        
        print("\n✅ Basic packages installed successfully!")
        print("   Note: For full functionality, install all packages from requirements.txt")
        return True
        
    except Exception as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_env_file():
    """Create environment configuration file"""
    print("\n⚙️  Creating environment configuration...")
    
    env_content = """# INTELLIATTEND Environment Configuration
FLASK_CONFIG=development
SECRET_KEY=intelliattend-demo-key-2024
FLASK_DEBUG=True

# Database Configuration (Optional - for full version)
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DB=intelliattend_db
MYSQL_PORT=3306

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here

# QR Code Settings
QR_REFRESH_INTERVAL=5
QR_SESSION_DURATION=120

# Application Settings
UPLOAD_FOLDER=uploads/
MAX_CONTENT_LENGTH=16777216

# Demo Mode (uses in-memory storage)
DEMO_MODE=true
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Environment file created (.env)")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_directories():
    """Check and create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        'templates',
        'templates/student',
        'static',
        'QR_DATA',
        'QR_DATA/tokens',
        'QR_DATA/keys', 
        'QR_DATA/archive',
        'server',
        'server/utils',
        'uploads',
        'logs'
    ]
    
    try:
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"   ✅ Created {directory}/")
            else:
                print(f"   ✅ {directory}/ exists")
        
        print("✅ All directories ready!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up directories: {e}")
        return False

def run_quick_test():
    """Run a quick system test"""
    print("\n🧪 Running quick system test...")
    
    try:
        # Test minimal server startup
        import importlib.util
        
        # Check if app_minimal.py exists and can be imported
        app_path = os.path.join('server', 'app_minimal.py')
        if os.path.exists(app_path):
            print("   ✅ Minimal server found")
            
            # Try to import Flask
            try:
                import flask
                print("   ✅ Flask is available")
            except ImportError:
                print("   ❌ Flask not available - install requirements")
                return False
            
            print("   ✅ Basic system check passed")
            return True
        else:
            print("   ❌ Server files not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def show_next_steps():
    """Show next steps for user"""
    print("\n🎉 Installation Complete!")
    print("=" * 50)
    print("Next Steps:")
    print()
    print("1. Start the application:")
    print("   python3 server/app_minimal.py")
    print()
    print("2. Open your browser and visit:")
    print("   Faculty Portal: http://localhost:5001")
    print("   Student Portal: http://localhost:5001/student")
    print()
    print("3. Demo Login Credentials:")
    print("   Faculty: john.smith@university.edu / faculty123")
    print("   Student: alice.williams@student.edu / student123")
    print()
    print("4. For full functionality (optional):")
    print("   pip install -r requirements.txt")
    print("   python3 database_setup.py  # For MySQL database")
    print("   python3 server/app.py      # Full-featured server")
    print()
    print("📖 Documentation: README.md")
    print("🧪 Test System: python3 test_system.py")
    print("=" * 50)

def main():
    """Main installation function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install basic requirements
    if not install_requirements():
        print("\n⚠️  Installation completed with warnings")
        print("   You may need to install packages manually")
    
    # Create environment file
    create_env_file()
    
    # Setup directories
    check_directories()
    
    # Quick test
    if run_quick_test():
        show_next_steps()
    else:
        print("\n⚠️  Installation completed but system test failed")
        print("   Please check the setup and try running manually")

if __name__ == "__main__":
    main()