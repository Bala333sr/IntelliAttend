#!/usr/bin/env python3
"""
Script to check if admin user exists in IntelliAttend database
"""

import os
import sys

# Add backend directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(parent_dir, 'backend')
sys.path.insert(0, backend_dir)

from backend.app import app, db, Admin

def check_admin_user():
    """Check if admin user exists"""
    with app.app_context():
        admin = Admin.query.filter_by(username='admin').first()
        if admin:
            print("✅ Admin user found!")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Name: {admin.first_name} {admin.last_name}")
            print(f"Role: {admin.role}")
            print(f"Active: {admin.is_active}")
            return True
        else:
            print("❌ No admin user found")
            return False

def main():
    """Main function"""
    print("🔍 Checking for admin user in IntelliAttend database...")
    print("=" * 60)
    
    try:
        if check_admin_user():
            print("\n📝 Admin Portal Access:")
            print("URL: http://localhost:5002/admin")
            print("Username: admin")
            print("Password: admin123")
            print("\n💡 After logging in, you'll be redirected to the admin dashboard")
            print("   where you can manage all aspects of the IntelliAttend system.")
        else:
            print("\n⚠️  No admin user found in database.")
            print("   You may need to run the database setup script or create an admin user manually.")
    except Exception as e:
        print(f"❌ Error checking admin user: {e}")

if __name__ == "__main__":
    main()