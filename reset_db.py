#!/usr/bin/env python3
"""
Reset database script for IntelliAttend
Drops all tables and recreates them with sample data
"""

import sys
import os

# Add parent directory to path to import app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(parent_dir, 'backend')
sys.path.insert(0, backend_dir)

from backend.app import app, db

def reset_database():
    """Drop all tables and recreate them"""
    with app.app_context():
        print("🗑️  Dropping all tables...")
        db.drop_all()
        print("✅ Tables dropped successfully")
        
        print("🚀 Creating tables...")
        db.create_all()
        print("✅ Tables created successfully")

if __name__ == "__main__":
    print("🔄 Resetting IntelliAttend Database...")
    print("=" * 50)
    
    try:
        reset_database()
        print("=" * 50)
        print("🎉 Database reset completed successfully!")
        print("Now run 'python3 database/simple_database_setup.py' to populate with sample data")
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        sys.exit(1)