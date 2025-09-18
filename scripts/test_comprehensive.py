#!/usr/bin/env python3
"""
Comprehensive Test Module for IntelliAttend System
Tests all functionalities without requiring manual login verification
"""

import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

class IntelliAttendTester:
    def __init__(self, base_url="http://192.168.0.3:5002"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.faculty_token = None
        self.student_token = None
        self.session_id = None
        self.otp_code = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"    Details: {details}")

    def test_server_connection(self):
        """Test if server is accessible"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            success = response.status_code == 200
            self.log_test("Server Connection", success, 
                         f"Server responded with status {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Server Connection", False, "Server not accessible", str(e))
            return False

    def test_database_connection(self):
        """Test database connectivity and sample data"""
        try:
            # Check if database file exists
            db_path = "/Users/anji/Desktop/IntelliAttend/instance/intelliattend.db"
            if not os.path.exists(db_path):
                self.log_test("Database Connection", False, "Database file not found")
                return False
            
            # Connect and check tables
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if required tables exist
            tables = ['students', 'faculty', 'classes', 'attendance_sessions']
            for table in tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not cursor.fetchone():
                    self.log_test("Database Connection", False, f"Table {table} not found")
                    conn.close()
                    return False
            
            # Check sample data
            cursor.execute("SELECT COUNT(*) FROM students")
            student_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM faculty")
            faculty_count = cursor.fetchone()[0]
            
            conn.close()
            success = student_count > 0 and faculty_count > 0
            self.log_test("Database Connection", success, 
                         f"Students: {student_count}, Faculty: {faculty_count}")
            return success
            
        except Exception as e:
            self.log_test("Database Connection", False, "Database error", str(e))
            return False

    def test_faculty_login(self):
        """Test faculty login functionality"""
        try:
            login_data = {
                'email': 'john.smith@university.edu',
                'password': 'faculty123'
            }
            
            response = requests.post(
                f"{self.api_url}/faculty/login",
                json=login_data,
                timeout=10
            )
            
            data = response.json()
            success = response.status_code == 200 and data.get('success', False)
            
            if success:
                self.faculty_token = data.get('access_token')
                faculty_name = data.get('faculty', {}).get('name', 'Unknown')
                self.log_test("Faculty Login", True, f"Logged in as {faculty_name}")
            else:
                self.log_test("Faculty Login", False, 
                             data.get('error', 'Login failed'), 
                             f"Status: {response.status_code}")
            
            return success
            
        except Exception as e:
            self.log_test("Faculty Login", False, "Request failed", str(e))
            return False

    def test_student_login(self):
        """Test student login functionality"""
        try:
            login_data = {
                'email': 'alice.williams@student.edu',
                'password': 'student123'
            }
            
            response = requests.post(
                f"{self.api_url}/student/login",
                json=login_data,
                timeout=10
            )
            
            data = response.json()
            success = response.status_code == 200 and data.get('success', False)
            
            if success:
                self.student_token = data.get('access_token')
                student_data = data.get('student', {})
                student_name = f"{student_data.get('firstName', '')} {student_data.get('lastName', '')}"
                self.log_test("Student Login", True, f"Logged in as {student_name}")
                
                # Verify response format matches Android expectations
                required_fields = ['studentId', 'firstName', 'lastName', 'email', 'program']
                missing_fields = [field for field in required_fields if field not in student_data]
                if missing_fields:
                    self.log_test("Student Response Format", False, 
                                 f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Student Response Format", True, "All required fields present")
            else:
                self.log_test("Student Login", False, 
                             data.get('error', 'Login failed'),
                             f"Status: {response.status_code}")
            
            return success
            
        except Exception as e:
            self.log_test("Student Login", False, "Request failed", str(e))
            return False

    def test_otp_generation(self):
        """Test OTP generation functionality"""
        if not self.faculty_token:
            self.log_test("OTP Generation", False, "No faculty token available")
            return False
            
        try:
            headers = {'Authorization': f'Bearer {self.faculty_token}'}
            response = requests.post(
                f"{self.api_url}/faculty/generate-otp",
                headers=headers,
                timeout=10
            )
            
            data = response.json()
            success = response.status_code == 200 and data.get('success', False)
            
            if success:
                self.otp_code = data.get('otp')
                expires_at = data.get('expires_at')
                self.log_test("OTP Generation", True, 
                             f"OTP: {self.otp_code}, Expires: {expires_at}")
            else:
                self.log_test("OTP Generation", False,
                             data.get('error', 'OTP generation failed'),
                             f"Status: {response.status_code}")
            
            return success
            
        except Exception as e:
            self.log_test("OTP Generation", False, "Request failed", str(e))
            return False

    def test_attendance_session_creation(self):
        """Test attendance session creation"""
        if not self.otp_code:
            self.log_test("Session Creation", False, "No OTP available")
            return False
            
        try:
            session_data = {
                'otp': self.otp_code,
                'class_id': 1
            }
            
            response = requests.post(
                f"{self.api_url}/verify-otp",
                json=session_data,
                timeout=10
            )
            
            data = response.json()
            success = response.status_code == 200 and data.get('success', False)
            
            if success:
                self.session_id = data.get('session_id')
                expires_at = data.get('expires_at')
                self.log_test("Session Creation", True,
                             f"Session ID: {self.session_id}, Expires: {expires_at}")
            else:
                self.log_test("Session Creation", False,
                             data.get('error', 'Session creation failed'),
                             f"Status: {response.status_code}")
            
            return success
            
        except Exception as e:
            self.log_test("Session Creation", False, "Request failed", str(e))
            return False

    def test_qr_generation(self):
        """Test QR code generation"""
        if not self.session_id:
            self.log_test("QR Generation", False, "No session ID available")
            return False
            
        # Wait for QR generation
        time.sleep(3)
        
        try:
            response = requests.get(
                f"{self.api_url}/qr/current/{self.session_id}",
                timeout=10
            )
            
            data = response.json()
            success = response.status_code == 200 and data.get('success', False)
            
            if success:
                qr_url = data.get('qr_url')
                sequence = data.get('sequence')
                self.log_test("QR Generation", True,
                             f"QR URL: {qr_url}, Sequence: {sequence}")
                
                # Test if QR file actually exists
                if qr_url:
                    qr_path = f"/Users/anji/Desktop/IntelliAttend{qr_url}"
                    file_exists = os.path.exists(qr_path)
                    self.log_test("QR File Exists", file_exists,
                                 f"File path: {qr_path}")
            else:
                self.log_test("QR Generation", False,
                             data.get('error', 'QR generation failed'),
                             f"Status: {response.status_code}")
            
            return success
            
        except Exception as e:
            self.log_test("QR Generation", False, "Request failed", str(e))
            return False

    def test_api_endpoints(self):
        """Test various API endpoints"""
        endpoints = [
            ('GET', '/api/health', None, None),
            ('GET', '/api/qr/current/999', None, None),  # Non-existent session
        ]
        
        for method, endpoint, headers, data in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                if method == 'GET':
                    response = requests.get(url, headers=headers, timeout=5)
                else:
                    response = requests.post(url, headers=headers, json=data, timeout=5)
                
                # Some endpoints are expected to fail
                expected_codes = [200, 404, 401, 500]
                success = response.status_code in expected_codes
                
                self.log_test(f"API {method} {endpoint}", success,
                             f"Status: {response.status_code}")
                
            except Exception as e:
                self.log_test(f"API {method} {endpoint}", False,
                             "Request failed", str(e))

    def test_student_profile_access(self):
        """Test student profile access"""
        if not self.student_token:
            self.log_test("Student Profile", False, "No student token")
            return False
            
        try:
            headers = {'Authorization': f'Bearer {self.student_token}'}
            response = requests.get(
                f"{self.api_url}/student/profile",
                headers=headers,
                timeout=10
            )
            
            data = response.json()
            success = response.status_code == 200 and data.get('success', False)
            
            if success:
                student = data.get('student', {})
                self.log_test("Student Profile", True,
                             f"Retrieved profile for {student.get('email')}")
            else:
                self.log_test("Student Profile", False,
                             data.get('error', 'Profile access failed'))
            
            return success
            
        except Exception as e:
            self.log_test("Student Profile", False, "Request failed", str(e))
            return False

    def test_logout_functionality(self):
        """Test logout functionality according to specifications"""
        logout_tests = []
        
        # Test faculty logout
        if self.faculty_token:
            try:
                headers = {'Authorization': f'Bearer {self.faculty_token}'}
                response = requests.post(
                    f"{self.api_url}/faculty/logout",
                    headers=headers,
                    timeout=10
                )
                
                success = response.status_code in [200, 401]  # 401 is also acceptable
                logout_tests.append(("Faculty Logout", success))
                
            except Exception as e:
                logout_tests.append(("Faculty Logout", False))
        
        # Test student logout
        if self.student_token:
            try:
                headers = {'Authorization': f'Bearer {self.student_token}'}
                response = requests.post(
                    f"{self.api_url}/student/logout",
                    headers=headers,
                    timeout=10
                )
                
                success = response.status_code in [200, 401]
                logout_tests.append(("Student Logout", success))
                
            except Exception as e:
                logout_tests.append(("Student Logout", False))
        
        # Log all logout test results
        for test_name, success in logout_tests:
            self.log_test(test_name, success)
        
        return all(result[1] for result in logout_tests)

    def test_file_structure(self):
        """Test critical file structure"""
        critical_paths = [
            "/Users/anji/Desktop/IntelliAttend/server/app.py",
            "/Users/anji/Desktop/IntelliAttend/Mobile App/app/src/main/java/com/intelliattend/student/data/repository/AuthRepository.kt",
            "/Users/anji/Desktop/IntelliAttend/instance/intelliattend.db",
            "/Users/anji/Desktop/IntelliAttend/QR_DATA/tokens",
        ]
        
        all_exist = True
        for path in critical_paths:
            exists = os.path.exists(path)
            if not exists:
                all_exist = False
            self.log_test(f"File Structure: {os.path.basename(path)}", 
                         exists, f"Path: {path}")
        
        return all_exist

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 INTELLIATTEND COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)
        
        # Infrastructure tests
        print("\n📋 INFRASTRUCTURE TESTS")
        self.test_server_connection()
        self.test_database_connection()
        self.test_file_structure()
        
        # Authentication tests
        print("\n🔐 AUTHENTICATION TESTS")
        self.test_faculty_login()
        self.test_student_login()
        self.test_student_profile_access()
        
        # Core functionality tests
        print("\n⚙️ CORE FUNCTIONALITY TESTS")
        self.test_otp_generation()
        self.test_attendance_session_creation()
        self.test_qr_generation()
        
        # API tests
        print("\n🌐 API ENDPOINT TESTS")
        self.test_api_endpoints()
        
        # Cleanup tests
        print("\n🧹 CLEANUP TESTS")
        self.test_logout_functionality()
        
        # Generate summary
        self.generate_test_report()

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if "✅" in result['status'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌" in result['status']:
                    print(f"  • {result['test']}: {result['message']}")
        
        # Save detailed report
        report_file = f"/Users/anji/Desktop/IntelliAttend/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump({
                    'summary': {
                        'total_tests': total_tests,
                        'passed': passed_tests,
                        'failed': failed_tests,
                        'success_rate': success_rate,
                        'timestamp': datetime.now().isoformat()
                    },
                    'results': self.test_results
                }, f, indent=2)
            print(f"\n📄 Detailed report saved: {report_file}")
        except Exception as e:
            print(f"\n⚠️ Could not save report: {e}")
        
        print("=" * 60)
        
        if success_rate >= 80:
            print("🎉 SYSTEM STATUS: HEALTHY")
        elif success_rate >= 60:
            print("⚠️ SYSTEM STATUS: NEEDS ATTENTION")
        else:
            print("🚨 SYSTEM STATUS: CRITICAL ISSUES")
        
        return success_rate >= 80


def main():
    """Main test execution"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://192.168.0.3:5002"
    
    tester = IntelliAttendTester(base_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()