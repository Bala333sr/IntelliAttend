#!/usr/bin/env python3
"""
Test script for database access
"""

import sys
import os

# Add backend path to sys.path
backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.append(backend_path)

def test_db_access():
    """Test database access"""
    try:
        # Import app and db
        from app import app, db, Admin
        
        print("✅ Successfully imported app, db, and Admin")
        
        # Test database access within app context
        with app.app_context():
            print("✅ Entered app context")
            
            # Try to query the Admin table
            admin_count = Admin.query.count()
            print(f"✅ Found {admin_count} admin users in database")
            
            # Try to get the first admin user
            first_admin = Admin.query.first()
            if first_admin:
                print(f"✅ First admin user: {first_admin.username}")
            else:
                print("⚠️ No admin users found")
                
        return True
        
    except Exception as e:
        print(f"❌ Error accessing database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Database Access...")
    success = test_db_access()
    if success:
        print("\n🎉 Database access test passed!")
    else:
        print("\n💥 Database access test failed!")