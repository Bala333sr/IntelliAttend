"""
Test script for admin functionality
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add backend path to sys.path
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.append(backend_path)

class TestAdminModule(unittest.TestCase):
    """Test cases for admin module functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Flask app context
        self.app_context = MagicMock()
        
    # Removed admin module import test since we restructured the admin module
    
    def test_faculty_routes_import(self):
        """Test that faculty routes can be imported successfully"""
        try:
            from admin.api.faculty_routes import faculty_bp
            self.assertIsNotNone(faculty_bp)
        except Exception as e:
            self.fail(f"Failed to import faculty routes: {e}")
    
    def test_student_routes_import(self):
        """Test that student routes can be imported successfully"""
        try:
            from admin.api.student_routes import student_bp
            self.assertIsNotNone(student_bp)
        except Exception as e:
            self.fail(f"Failed to import student routes: {e}")
    
    def test_classroom_routes_import(self):
        """Test that classroom routes can be imported successfully"""
        try:
            from admin.api.classroom_routes import classroom_bp
            self.assertIsNotNone(classroom_bp)
        except Exception as e:
            self.fail(f"Failed to import classroom routes: {e}")
    
    def test_class_routes_import(self):
        """Test that class routes can be imported successfully"""
        try:
            from admin.api.class_routes import class_bp
            self.assertIsNotNone(class_bp)
        except Exception as e:
            self.fail(f"Failed to import class routes: {e}")
    
    def test_device_routes_import(self):
        """Test that device routes can be imported successfully"""
        try:
            from admin.api.device_routes import device_bp
            self.assertIsNotNone(device_bp)
        except Exception as e:
            self.fail(f"Failed to import device routes: {e}")
    
    def test_enrollment_routes_import(self):
        """Test that enrollment routes can be imported successfully"""
        try:
            from admin.api.enrollment_routes import enrollment_bp
            self.assertIsNotNone(enrollment_bp)
        except Exception as e:
            self.fail(f"Failed to import enrollment routes: {e}")
    
    def test_auth_routes_import(self):
        """Test that auth routes can be imported successfully"""
        try:
            from admin.api.auth_routes import auth_bp
            self.assertIsNotNone(auth_bp)
        except Exception as e:
            self.fail(f"Failed to import auth routes: {e}")

if __name__ == '__main__':
    # Run tests
    unittest.main()