#!/usr/bin/env python3
"""
Test script to verify data persistence in IntelliAttend database
"""

import os
import sys
from datetime import datetime, time
from werkzeug.security import generate_password_hash

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.app import app, db, Faculty

def test_faculty_creation():
    """Test faculty creation and persistence"""
    with app.app_context():
        # Count existing faculty
        initial_count = Faculty.query.count()
        print(f"Initial faculty count: {initial_count}")
        
        # Create new faculty
        faculty = Faculty(
            faculty_code="TEST001",
            first_name="Test",
            last_name="Faculty",
            email="test.faculty@university.edu",
            phone_number="+1234567899",
            department="Testing",
            password_hash=generate_password_hash("test123"),
            is_active=True
        )
        
        db.session.add(faculty)
        db.session.commit()
        
        # Count after creation
        after_count = Faculty.query.count()
        print(f"Faculty count after creation: {after_count}")
        
        # Verify the faculty was created
        created_faculty = Faculty.query.filter_by(faculty_code="TEST001").first()
        if created_faculty:
            print(f"✅ Faculty created successfully: {created_faculty.first_name} {created_faculty.last_name}")
        else:
            print("❌ Faculty not found after creation")
        
        # Clean up test data
        if created_faculty:
            db.session.delete(created_faculty)
            db.session.commit()
            print("🧹 Test faculty cleaned up")
        
        final_count = Faculty.query.count()
        print(f"Final faculty count: {final_count}")
        
        if initial_count == final_count:
            print("✅ Data persistence test passed")
        else:
            print("❌ Data persistence test failed")

if __name__ == "__main__":
    test_faculty_creation()