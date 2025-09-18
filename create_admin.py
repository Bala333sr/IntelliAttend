#!/usr/bin/env python3
"""
Script to create admin user in IntelliAttend database
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Add backend directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(parent_dir, 'backend')
sys.path.insert(0, backend_dir)

from backend.app import app, db, Admin

def create_admin_user():
    """Create admin user"""
    with app.app_context():
        # Check if admin user already exists
        admin = Admin.query.filter_by(username='admin').first()
        if admin:
            print("⚠️  Admin user already exists!")
            return False
        
        # Create new admin user
        admin = Admin(
            username='admin',
            email='admin@intelliattend.com',
            password_hash=generate_password_hash('admin123'),
            first_name='System',
            last_name='Administrator',
            role='super_admin',
            is_active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Admin user created successfully!")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Name: {admin.first_name} {admin.last_name}")
        print(f"Role: {admin.role}")
        return True

def main():
    """Main function"""
    print("🔧 Creating admin user in IntelliAttend database...")
    print("=" * 60)
    
    try:
        if create_admin_user():
            print("\n📝 Admin Portal Access:")
            print("URL: http://localhost:5002/admin")
            print("Username: admin")
            print("Password: admin123")
            print("\n💡 After logging in, you'll be redirected to the admin dashboard")
            print("   where you can manage all aspects of the IntelliAttend system.")
        else:
            print("\n💡 Admin user already exists. No action needed.")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

if __name__ == "__main__":
    main()