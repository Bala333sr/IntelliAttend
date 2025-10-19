#!/usr/bin/env python3
"""
Production server startup without debug mode
"""
import sys
import os

# Set Flask to production mode
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Import and modify the app
from app import app, scheduler

if __name__ == '__main__':
    # Start scheduler
    if not scheduler.running:
        scheduler.start()
    
    print("🚀 Starting INTELLIATTEND Server (Production Mode)...")
    print("=" * 50)
    print("Faculty Portal: http://localhost:5002")
    print("Student Portal: http://localhost:5002/student")
    print("API Base URL: http://localhost:5002/api")
    print("📱 Mobile App URL: http://localhost:5002/api/")
    print("🌐 Public Access: http://192.168.0.7:5002")
    print("=" * 50)
    
    # Run without debug mode
    app.run(debug=False, host='0.0.0.0', port=5002, threaded=True)
