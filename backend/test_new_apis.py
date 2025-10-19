#!/usr/bin/env python3
"""
Comprehensive API Testing for New Features
Tests all endpoints for:
1. Attendance Statistics Dashboard
2. Notifications & Reminders
3. Smart Attendance Automation
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5002"

class APITester:
    def __init__(self):
        self.token = None
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def print_header(self, text):
        print("\n" + "=" * 80)
        print(text)
        print("=" * 80)
    
    def print_test(self, endpoint, method, status):
        symbol = "✅" if status == "PASS" else "❌"
        print(f"{symbol} {method} {endpoint}: {status}")
    
    def test_endpoint(self, name, method, endpoint, data=None, headers=None, expected_status=200):
        """Generic endpoint tester"""
        self.results['total_tests'] += 1
        
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=data, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Check status code
            status_match = response.status_code == expected_status
            
            # Check response format
            try:
                json_response = response.json()
                has_valid_json = True
            except:
                has_valid_json = False
            
            # Determine pass/fail
            if status_match and has_valid_json:
                self.results['passed'] += 1
                self.print_test(endpoint, method, "PASS")
                return True, response
            else:
                self.results['failed'] += 1
                error_msg = f"{name}: Expected {expected_status}, got {response.status_code}"
                self.results['errors'].append(error_msg)
                self.print_test(endpoint, method, "FAIL")
                return False, response
                
        except requests.exceptions.ConnectionError:
            self.results['failed'] += 1
            error_msg = f"{name}: Connection error - Backend not running"
            self.results['errors'].append(error_msg)
            self.print_test(endpoint, method, "CONNECTION ERROR")
            return False, None
        except Exception as e:
            self.results['failed'] += 1
            error_msg = f"{name}: {str(e)}"
            self.results['errors'].append(error_msg)
            self.print_test(endpoint, method, f"ERROR: {str(e)}")
            return False, None
    
    def login_student(self):
        """Login as test student to get JWT token"""
        print("\n🔐 Logging in as test student (BALA - 23N31A6645)...")
        
        success, response = self.test_endpoint(
            "Student Login",
            "POST",
            "/api/mobile/auth/login",
            data={
                "roll_number": "23N31A6645",
                "password": "Bala@123"
            }
        )
        
        if success and response:
            try:
                token = response.json().get('token') or response.json().get('access_token')
                if token:
                    self.token = token
                    print(f"✅ Login successful! Token obtained.")
                    return True
                else:
                    print("❌ Login failed: No token in response")
                    return False
            except:
                print("❌ Login failed: Invalid response format")
                return False
        else:
            print("❌ Login failed: Request unsuccessful")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}
    
    def test_attendance_statistics_apis(self):
        """Test Attendance Statistics Dashboard APIs"""
        self.print_header("TESTING: ATTENDANCE STATISTICS DASHBOARD APIs")
        
        headers = self.get_auth_headers()
        
        # Test 1: Get overall statistics
        self.test_endpoint(
            "Get Attendance Statistics",
            "GET",
            "/api/student/attendance/statistics",
            headers=headers
        )
        
        # Test 2: Get attendance history
        self.test_endpoint(
            "Get Attendance History",
            "GET",
            "/api/student/attendance/history",
            headers=headers
        )
        
        # Test 3: Get attendance history with filters
        self.test_endpoint(
            "Get Attendance History (Filtered)",
            "GET",
            "/api/student/attendance/history?start_date=2025-01-01",
            headers=headers
        )
        
        # Test 4: Get attendance trends
        self.test_endpoint(
            "Get Attendance Trends (Weekly)",
            "GET",
            "/api/student/attendance/trends?period=weekly",
            headers=headers
        )
        
        # Test 5: Get attendance summary
        self.test_endpoint(
            "Get Attendance Summary",
            "GET",
            "/api/student/attendance/summary",
            headers=headers
        )
        
        # Test 6: Get attendance predictions
        self.test_endpoint(
            "Get Attendance Predictions",
            "GET",
            "/api/student/attendance/predictions",
            headers=headers
        )
    
    def test_notifications_apis(self):
        """Test Notifications & Reminders APIs"""
        self.print_header("TESTING: NOTIFICATIONS & REMINDERS APIs")
        
        headers = self.get_auth_headers()
        
        # Test 1: Get notification preferences (should return default)
        self.test_endpoint(
            "Get Notification Preferences",
            "GET",
            "/api/student/notifications/preferences",
            headers=headers
        )
        
        # Test 2: Update notification preferences
        self.test_endpoint(
            "Update Notification Preferences",
            "PUT",
            "/api/student/notifications/preferences",
            data={
                "class_reminder_enabled": True,
                "warm_scan_reminder_enabled": True,
                "attendance_warning_enabled": True,
                "weekly_summary_enabled": False,
                "reminder_minutes_before": 15,
                "quiet_hours_start": None,
                "quiet_hours_end": None
            },
            headers=headers
        )
        
        # Test 3: Get notification preferences again (should return updated)
        self.test_endpoint(
            "Get Updated Notification Preferences",
            "GET",
            "/api/student/notifications/preferences",
            headers=headers
        )
        
        # Test 4: Get notification history
        self.test_endpoint(
            "Get Notification History",
            "GET",
            "/api/student/notifications/history",
            headers=headers
        )
        
        # Test 5: Test notification
        self.test_endpoint(
            "Send Test Notification",
            "POST",
            "/api/student/notifications/test",
            data={"message": "Test notification from API test suite"},
            headers=headers
        )
    
    def test_auto_attendance_apis(self):
        """Test Smart Attendance Automation APIs"""
        self.print_header("TESTING: SMART ATTENDANCE AUTOMATION APIs")
        
        headers = self.get_auth_headers()
        
        # Test 1: Get auto-attendance configuration (should return default)
        self.test_endpoint(
            "Get Auto-Attendance Config",
            "GET",
            "/api/student/auto-attendance/config",
            headers=headers
        )
        
        # Test 2: Update auto-attendance configuration
        self.test_endpoint(
            "Update Auto-Attendance Config",
            "PUT",
            "/api/student/auto-attendance/config",
            data={
                "enabled": True,
                "gps_enabled": True,
                "wifi_enabled": True,
                "bluetooth_enabled": True,
                "confidence_threshold": 0.85,
                "require_warm_data": True,
                "auto_submit": False
            },
            headers=headers
        )
        
        # Test 3: Get auto-attendance configuration again (should return updated)
        self.test_endpoint(
            "Get Updated Auto-Attendance Config",
            "GET",
            "/api/student/auto-attendance/config",
            headers=headers
        )
        
        # Test 4: Verify presence (with sample sensor data)
        self.test_endpoint(
            "Verify Presence",
            "POST",
            "/api/student/auto-attendance/verify",
            data={
                "session_id": 1,
                "gps_data": {
                    "latitude": 17.2403,
                    "longitude": 78.4294,
                    "accuracy": 20
                },
                "wifi_data": {
                    "ssid": "MRCET_4208",
                    "bssid": "00:11:22:33:44:55",
                    "rssi": -50
                },
                "bluetooth_data": [
                    {
                        "address": "AA:BB:CC:DD:EE:FF",
                        "name": "Room4208_Beacon",
                        "rssi": -55
                    }
                ]
            },
            headers=headers
        )
        
        # Test 5: Get auto-attendance activity log
        self.test_endpoint(
            "Get Auto-Attendance Activity",
            "GET",
            "/api/student/auto-attendance/activity",
            headers=headers
        )
        
        # Test 6: Get auto-attendance statistics
        self.test_endpoint(
            "Get Auto-Attendance Stats",
            "GET",
            "/api/student/auto-attendance/stats",
            headers=headers
        )
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['failed'] > 0:
            print("\n⚠️  Failed Tests:")
            for error in self.results['errors']:
                print(f"   - {error}")
        
        # Calculate score
        if self.results['total_tests'] > 0:
            score = (self.results['passed'] / self.results['total_tests']) * 100
            print(f"\n🎯 API Test Score: {score:.1f}%")
            
            if score == 100:
                print("✅ ALL API TESTS PASSED!")
            elif score >= 80:
                print("⚠️  MOSTLY PASSED - Some endpoints need attention")
            else:
                print("❌ MULTIPLE FAILURES - Significant issues found")
        
        return self.results

def main():
    """Main test runner"""
    print("=" * 80)
    print("INTELLIATTEND - NEW FEATURES API TESTING SUITE")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing against: {BASE_URL}")
    
    tester = APITester()
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ Backend is running")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running!")
        print("Please start the backend server first: python app.py")
        return
    
    # Login to get token
    if not tester.login_student():
        print("\n⚠️  Cannot proceed without authentication token")
        print("Continuing with unauthenticated tests...")
    
    # Run all API tests
    tester.test_attendance_statistics_apis()
    tester.test_notifications_apis()
    tester.test_auto_attendance_apis()
    
    # Print summary
    results = tester.print_summary()
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return results

if __name__ == '__main__':
    main()
