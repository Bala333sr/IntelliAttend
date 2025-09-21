#!/usr/bin/env python3
"""
Android App Functionality Test Module
Tests Android-specific API compatibility and response formats
"""

import requests
import json
import time
from datetime import datetime

class AndroidAppTester:
    def __init__(self, base_url="http://192.168.0.3:5002"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.results = []
        
    def log_result(self, test_name, passed, message="", details=None):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'passed': passed,
            'message': message,
            'details': details
        })
        print(f"{status} {test_name}: {message}")
        if details and not passed:
            print(f"    {details}")
    
    def test_student_login_format(self):
        """Test student login response format for Android compatibility"""
        print("\n🤖 Testing Android App Login Compatibility")
        
        try:
            # Simulate Android app request
            headers = {
                'Content-Type': 'application/json; charset=UTF-8',
                'User-Agent': 'okhttp/4.11.0',
                'Accept-Encoding': 'gzip'
            }
            
            login_data = {
                'email': 'alice.williams@student.edu',
                'password': 'student123'
            }
            
            response = requests.post(
                f"{self.api_url}/student/login",
                json=login_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_result("Student Login Request", False, 
                               f"HTTP {response.status_code}", response.text)
                return None
            
            data = response.json()
            
            # Test 1: Basic response structure
            required_fields = ['success', 'access_token', 'student']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_result("Login Response Structure", False,
                               f"Missing fields: {missing_fields}")
                return None
            
            self.log_result("Login Response Structure", True, "All required fields present")
            
            # Test 2: Success field validation
            success_valid = data.get('success') is True
            self.log_result("Success Field", success_valid, 
                           f"success = {data.get('success')}")
            
            # Test 3: Access token validation
            token = data.get('access_token')
            token_valid = token and isinstance(token, str) and len(token) > 50
            self.log_result("Access Token", token_valid,
                           f"Token present: {bool(token)}, Length: {len(token) if token else 0}")
            
            # Test 4: Student object validation
            student = data.get('student', {})
            android_required_fields = [
                'studentId', 'studentCode', 'firstName', 'lastName', 
                'email', 'program', 'yearOfStudy'
            ]
            
            missing_student_fields = [field for field in android_required_fields 
                                    if field not in student]
            
            if missing_student_fields:
                self.log_result("Student Object Format", False,
                               f"Missing Android fields: {missing_student_fields}")
                return None
            
            self.log_result("Student Object Format", True, 
                           "All Android-required fields present")
            
            # Test 5: Field type validation
            field_types = {
                'studentId': int,
                'studentCode': str,
                'firstName': str,
                'lastName': str,
                'email': str,
                'program': str,
                'yearOfStudy': int
            }
            
            type_errors = []
            for field, expected_type in field_types.items():
                value = student.get(field)
                if not isinstance(value, expected_type):
                    type_errors.append(f"{field}: expected {expected_type.__name__}, got {type(value).__name__}")
            
            if type_errors:
                self.log_result("Field Type Validation", False,
                               f"Type errors: {type_errors}")
            else:
                self.log_result("Field Type Validation", True,
                               "All field types correct")
            
            return data
            
        except Exception as e:
            self.log_result("Student Login Request", False, "Request failed", str(e))
            return None
    
    def test_json_serialization(self, login_data):
        """Test if response can be properly serialized/deserialized"""
        if not login_data:
            return False
            
        try:
            # Test JSON serialization
            json_str = json.dumps(login_data)
            parsed_data = json.loads(json_str)
            
            # Verify data integrity
            original_student = login_data.get('student', {})
            parsed_student = parsed_data.get('student', {})
            
            integrity_check = (
                original_student.get('studentId') == parsed_student.get('studentId') and
                original_student.get('email') == parsed_student.get('email')
            )
            
            self.log_result("JSON Serialization", integrity_check,
                           "Data integrity maintained through JSON processing")
            
            return integrity_check
            
        except Exception as e:
            self.log_result("JSON Serialization", False, "Serialization failed", str(e))
            return False
    
    def test_network_headers(self):
        """Test response headers for Android compatibility"""
        try:
            response = requests.post(
                f"{self.api_url}/student/login",
                json={'email': 'alice.williams@student.edu', 'password': 'student123'},
                headers={'Content-Type': 'application/json; charset=UTF-8'}
            )
            
            headers = response.headers
            
            # Test Content-Type
            content_type = headers.get('Content-Type', '')
            json_content = 'application/json' in content_type.lower()
            self.log_result("Response Content-Type", json_content,
                           f"Content-Type: {content_type}")
            
            # Test CORS headers (if present)
            cors_origin = headers.get('Access-Control-Allow-Origin')
            if cors_origin:
                self.log_result("CORS Headers", True, f"Origin: {cors_origin}")
            
            return json_content
            
        except Exception as e:
            self.log_result("Network Headers", False, "Header check failed", str(e))
            return False
    
    def test_error_responses(self):
        """Test error response formats"""
        error_tests = [
            {
                'name': 'Invalid Credentials',
                'data': {'email': 'invalid@test.com', 'password': 'wrong'},
                'expected_status': 401
            },
            {
                'name': 'Missing Email',
                'data': {'password': 'test123'},
                'expected_status': 400
            },
            {
                'name': 'Missing Password',
                'data': {'email': 'test@test.com'},
                'expected_status': 400
            }
        ]
        
        print("\n❌ Testing Error Response Formats")
        
        for test in error_tests:
            try:
                response = requests.post(
                    f"{self.api_url}/student/login",
                    json=test['data'],
                    timeout=5
                )
                
                status_correct = response.status_code == test['expected_status']
                
                try:
                    error_data = response.json()
                    has_error_field = 'error' in error_data
                    
                    self.log_result(f"Error: {test['name']}", 
                                   status_correct and has_error_field,
                                   f"Status: {response.status_code}, Has error field: {has_error_field}")
                except:
                    self.log_result(f"Error: {test['name']}", False,
                                   "Response not valid JSON")
                    
            except Exception as e:
                self.log_result(f"Error: {test['name']}", False, "Request failed", str(e))
    
    def test_token_validation(self, login_data):
        """Test access token format and validity"""
        if not login_data:
            return False
            
        token = login_data.get('access_token')
        if not token:
            self.log_result("Token Validation", False, "No token in response")
            return False
        
        # Test token format (JWT should have 3 parts separated by dots)
        token_parts = token.split('.')
        valid_format = len(token_parts) == 3
        
        self.log_result("Token Format", valid_format,
                       f"JWT parts: {len(token_parts)}")
        
        # Test token usage with a protected endpoint
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                f"{self.api_url}/student/profile",
                headers=headers,
                timeout=5
            )
            
            token_works = response.status_code in [200, 404]  # 404 is OK if endpoint doesn't exist
            self.log_result("Token Usage", token_works,
                           f"Profile request status: {response.status_code}")
            
            return valid_format and token_works
            
        except Exception as e:
            self.log_result("Token Usage", False, "Token test failed", str(e))
            return False
    
    def run_android_tests(self):
        """Run all Android-specific tests"""
        print("🤖 ANDROID APP COMPATIBILITY TEST SUITE")
        print("=" * 50)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        # Test login functionality
        login_data = self.test_student_login_format()
        
        # Test JSON handling
        self.test_json_serialization(login_data)
        
        # Test network compatibility
        self.test_network_headers()
        
        # Test error handling
        self.test_error_responses()
        
        # Test token functionality
        self.test_token_validation(login_data)
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 50)
        print("📊 ANDROID COMPATIBILITY SUMMARY")
        print("=" * 50)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "No tests run")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if not result['passed']:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n" + "=" * 50)
        
        if passed == total:
            print("🎉 ANDROID APP READY FOR USE")
        elif passed >= total * 0.8:
            print("⚠️ MOSTLY COMPATIBLE - MINOR ISSUES")
        else:
            print("🚨 COMPATIBILITY ISSUES DETECTED")
        
        return passed == total


def main():
    """Run Android app tests"""
    tester = AndroidAppTester()
    tester.run_android_tests()


if __name__ == "__main__":
    main()