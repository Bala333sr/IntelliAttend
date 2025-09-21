#!/usr/bin/env python3
"""
IntelliAttend Security Testing Suite
====================================

This script performs comprehensive security testing including:
- Rate limiting validation
- Authentication bypass attempts
- SQL injection testing
- JWT security testing
- CSRF protection validation
- Password policy enforcement
- Session security testing
- Input validation testing
"""

import requests
import time
import json
import random
import string
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import sys
import os

# Configuration
BASE_URL = "http://localhost:5000"
TEST_RESULTS = []
REPORT_FILE = f"security_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

class SecurityTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.admin_token = None
        self.faculty_token = None
        self.student_token = None
        
    def log_test_result(self, test_name, success, message, severity="medium", details=None):
        """Log test results with severity levels"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'test_name': test_name,
            'success': success,
            'message': message,
            'severity': severity,
            'details': details or {}
        }
        self.test_results.append(result)
        status = "✓ PASS" if success else "✗ FAIL"
        severity_emoji = {"low": "🟡", "medium": "🟠", "high": "🔴", "critical": "💀"}
        print(f"{status} [{severity_emoji.get(severity, '⚪')} {severity.upper()}] {test_name}: {message}")
        
    def test_rate_limiting(self):
        """Test rate limiting on various endpoints"""
        print("\n" + "="*60)
        print("TESTING RATE LIMITING")
        print("="*60)
        
        endpoints_to_test = [
            {
                'url': f'{self.base_url}/api/student/login',
                'method': 'POST',
                'data': {'email': 'test@example.com', 'password': 'wrongpass'},
                'limit': 3,
                'window': 60,
                'name': 'Student Login'
            },
            {
                'url': f'{self.base_url}/api/faculty/login',
                'method': 'POST', 
                'data': {'email': 'test@example.com', 'password': 'wrongpass'},
                'limit': 3,
                'window': 60,
                'name': 'Faculty Login'
            },
            {
                'url': f'{self.base_url}/api/admin/login',
                'method': 'POST',
                'data': {'username': 'admin', 'password': 'wrongpass'},
                'limit': 10,
                'window': 60,
                'name': 'Admin Login'
            }
        ]
        
        for endpoint in endpoints_to_test:
            try:
                print(f"\nTesting rate limiting for {endpoint['name']}...")
                responses = []
                
                # Send requests rapidly
                for i in range(endpoint['limit'] + 3):
                    if endpoint['method'] == 'POST':
                        response = requests.post(
                            endpoint['url'],
                            json=endpoint['data'],
                            timeout=10
                        )
                    else:
                        response = requests.get(endpoint['url'], timeout=10)
                    
                    responses.append({
                        'request_num': i + 1,
                        'status_code': response.status_code,
                        'response_time': response.elapsed.total_seconds()
                    })
                    
                    # Small delay to avoid overwhelming
                    time.sleep(0.1)
                
                # Check if rate limiting is working
                rate_limited_count = sum(1 for r in responses if r['status_code'] == 429)
                
                if rate_limited_count > 0:
                    self.log_test_result(
                        f"Rate Limiting - {endpoint['name']}",
                        True,
                        f"Rate limiting active. {rate_limited_count} requests blocked out of {len(responses)}",
                        "low",
                        {'responses': responses}
                    )
                else:
                    self.log_test_result(
                        f"Rate Limiting - {endpoint['name']}",
                        False,
                        f"No rate limiting detected. All {len(responses)} requests succeeded",
                        "medium",
                        {'responses': responses}
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Rate Limiting - {endpoint['name']}",
                    False,
                    f"Test failed with error: {str(e)}",
                    "high"
                )
    
    def test_sql_injection(self):
        """Test SQL injection vulnerabilities"""
        print("\n" + "="*60)
        print("TESTING SQL INJECTION PROTECTION")
        print("="*60)
        
        # Common SQL injection payloads
        sql_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DROP TABLE students;--",
            "' UNION SELECT * FROM admin--",
            "admin'--",
            "admin' /*",
            "' OR 'x'='x",
            "'; WAITFOR DELAY '00:00:10'--",
            "' AND (SELECT COUNT(*) FROM admin) > 0--"
        ]
        
        endpoints_to_test = [
            {
                'url': f'{self.base_url}/api/student/login',
                'fields': ['email', 'password'],
                'name': 'Student Login'
            },
            {
                'url': f'{self.base_url}/api/faculty/login',
                'fields': ['email', 'password'],
                'name': 'Faculty Login'
            },
            {
                'url': f'{self.base_url}/api/admin/login',
                'fields': ['username', 'password'],
                'name': 'Admin Login'
            }
        ]
        
        for endpoint in endpoints_to_test:
            for payload in sql_payloads:
                try:
                    # Test each field with SQL injection
                    for field in endpoint['fields']:
                        data = {}
                        for f in endpoint['fields']:
                            data[f] = payload if f == field else 'normalvalue'
                        
                        response = requests.post(
                            endpoint['url'],
                            json=data,
                            timeout=10
                        )
                        
                        # Check response for SQL injection success indicators
                        response_text = response.text.lower()
                        suspicious_indicators = [
                            'syntax error',
                            'mysql',
                            'ora-',
                            'sqlstate',
                            'driver',
                            'column',
                            'table'
                        ]
                        
                        if any(indicator in response_text for indicator in suspicious_indicators):
                            self.log_test_result(
                                f"SQL Injection - {endpoint['name']} ({field})",
                                False,
                                f"Possible SQL injection vulnerability detected with payload: {payload}",
                                "critical",
                                {'payload': payload, 'response': response_text[:500]}
                            )
                        elif response.status_code == 200 and 'success' in response_text:
                            # Check if injection bypassed authentication
                            self.log_test_result(
                                f"SQL Injection - {endpoint['name']} ({field})",
                                False,
                                f"Authentication bypass detected with payload: {payload}",
                                "critical",
                                {'payload': payload, 'response': response_text}
                            )
                        else:
                            self.log_test_result(
                                f"SQL Injection - {endpoint['name']} ({field})",
                                True,
                                f"No SQL injection vulnerability with payload: {payload[:20]}...",
                                "low"
                            )
                
                except Exception as e:
                    self.log_test_result(
                        f"SQL Injection - {endpoint['name']}",
                        False,
                        f"Test failed with error: {str(e)}",
                        "medium"
                    )
    
    def test_jwt_security(self):
        """Test JWT token security"""
        print("\n" + "="*60)
        print("TESTING JWT SECURITY")
        print("="*60)
        
        # First get a valid token for testing
        try:
            # Try to get admin token
            response = requests.post(
                f'{self.base_url}/api/admin/login',
                json={'username': 'admin', 'password': 'admin123'},
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                if 'access_token' in token_data:
                    self.admin_token = token_data['access_token']
                    
                    # Test token manipulation
                    self.test_jwt_manipulation()
                    # Test token expiration
                    self.test_jwt_expiration()
                    # Test token blacklisting
                    self.test_jwt_blacklisting()
                else:
                    self.log_test_result(
                        "JWT Security Setup",
                        False,
                        "Could not obtain admin token for JWT testing",
                        "high"
                    )
            else:
                self.log_test_result(
                    "JWT Security Setup",
                    False,
                    "Admin login failed - cannot test JWT security",
                    "medium"
                )
                
        except Exception as e:
            self.log_test_result(
                "JWT Security Setup",
                False,
                f"Failed to setup JWT testing: {str(e)}",
                "high"
            )
    
    def test_jwt_manipulation(self):
        """Test JWT token manipulation attacks"""
        if not self.admin_token:
            return
            
        # Test with manipulated tokens
        manipulated_tokens = [
            self.admin_token[:-5] + "AAAAA",  # Modified signature
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJ1c2VyIjoiYWRtaW4ifQ.",  # None algorithm
            self.admin_token + "extra",  # Appended data
            "Bearer " + self.admin_token,  # Wrong format
        ]
        
        for i, token in enumerate(manipulated_tokens):
            try:
                response = requests.get(
                    f'{self.base_url}/api/admin/faculty',
                    headers={'Authorization': f'Bearer {token}'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.log_test_result(
                        f"JWT Manipulation Test {i+1}",
                        False,
                        "Manipulated JWT token was accepted",
                        "critical",
                        {'token_preview': token[:50] + "..."}
                    )
                else:
                    self.log_test_result(
                        f"JWT Manipulation Test {i+1}",
                        True,
                        f"Manipulated JWT rejected with status {response.status_code}",
                        "low"
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"JWT Manipulation Test {i+1}",
                    False,
                    f"Test failed: {str(e)}",
                    "medium"
                )
    
    def test_jwt_expiration(self):
        """Test JWT token expiration"""
        if not self.admin_token:
            return
            
        try:
            # Use token immediately
            response1 = requests.get(
                f'{self.base_url}/api/admin/faculty',
                headers={'Authorization': f'Bearer {self.admin_token}'},
                timeout=10
            )
            
            if response1.status_code == 200:
                self.log_test_result(
                    "JWT Expiration - Fresh Token",
                    True,
                    "Fresh JWT token works correctly",
                    "low"
                )
            else:
                self.log_test_result(
                    "JWT Expiration - Fresh Token",
                    False,
                    f"Fresh token rejected with status {response1.status_code}",
                    "medium"
                )
                
        except Exception as e:
            self.log_test_result(
                "JWT Expiration Test",
                False,
                f"Test failed: {str(e)}",
                "medium"
            )
    
    def test_jwt_blacklisting(self):
        """Test JWT token blacklisting after logout"""
        if not self.admin_token:
            return
            
        try:
            # Logout to blacklist token
            logout_response = requests.post(
                f'{self.base_url}/api/admin/logout',
                headers={'Authorization': f'Bearer {self.admin_token}'},
                timeout=10
            )
            
            # Try to use token after logout
            test_response = requests.get(
                f'{self.base_url}/api/admin/faculty',
                headers={'Authorization': f'Bearer {self.admin_token}'},
                timeout=10
            )
            
            if test_response.status_code == 401 or test_response.status_code == 403:
                self.log_test_result(
                    "JWT Blacklisting",
                    True,
                    "Token correctly blacklisted after logout",
                    "low"
                )
            else:
                self.log_test_result(
                    "JWT Blacklisting",
                    False,
                    f"Token still valid after logout (status: {test_response.status_code})",
                    "high"
                )
                
        except Exception as e:
            self.log_test_result(
                "JWT Blacklisting Test",
                False,
                f"Test failed: {str(e)}",
                "medium"
            )
    
    def test_input_validation(self):
        """Test input validation on various endpoints"""
        print("\n" + "="*60)
        print("TESTING INPUT VALIDATION")
        print("="*60)
        
        # Test data with various invalid inputs
        invalid_inputs = [
            {"type": "XSS", "value": "<script>alert('XSS')</script>"},
            {"type": "Long String", "value": "A" * 1000},
            {"type": "Special Characters", "value": "!@#$%^&*()_+{}|:<>?[];',./"},
            {"type": "NULL Bytes", "value": "test\x00null"},
            {"type": "Unicode", "value": "тест мöðêł ñāmé"},
            {"type": "Empty", "value": ""},
            {"type": "Whitespace", "value": "   "},
            {"type": "HTML", "value": "<h1>HTML Content</h1>"},
        ]
        
        # Test student registration endpoint
        for test_input in invalid_inputs:
            try:
                data = {
                    'student_code': test_input['value'],
                    'first_name': test_input['value'],
                    'last_name': 'Test',
                    'email': f"test{random.randint(1000,9999)}@example.com",
                    'password': 'Password123!',
                    'program': 'Computer Science',
                    'year_of_study': 1
                }
                
                response = requests.post(
                    f'{self.base_url}/api/admin/students',
                    json=data,
                    headers={'Authorization': f'Bearer {self.admin_token}'} if self.admin_token else {},
                    timeout=10
                )
                
                # Check for proper validation
                if response.status_code == 400:
                    self.log_test_result(
                        f"Input Validation - {test_input['type']}",
                        True,
                        f"Invalid input properly rejected: {test_input['type']}",
                        "low"
                    )
                elif response.status_code == 200 or response.status_code == 201:
                    # Check if dangerous content was sanitized
                    if test_input['type'] in ['XSS', 'HTML'] and test_input['value'] in response.text:
                        self.log_test_result(
                            f"Input Validation - {test_input['type']}",
                            False,
                            f"Dangerous input not sanitized: {test_input['type']}",
                            "high"
                        )
                    else:
                        self.log_test_result(
                            f"Input Validation - {test_input['type']}",
                            True,
                            f"Input accepted but appears sanitized: {test_input['type']}",
                            "low"
                        )
                else:
                    self.log_test_result(
                        f"Input Validation - {test_input['type']}",
                        True,
                        f"Request handled appropriately (status: {response.status_code})",
                        "low"
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Input Validation - {test_input['type']}",
                    False,
                    f"Test failed: {str(e)}",
                    "medium"
                )
    
    def test_password_policies(self):
        """Test password policy enforcement"""
        print("\n" + "="*60)
        print("TESTING PASSWORD POLICIES")
        print("="*60)
        
        weak_passwords = [
            {"password": "123", "type": "Too Short"},
            {"password": "password", "type": "Common Password"},
            {"password": "12345678", "type": "Only Numbers"},
            {"password": "abcdefgh", "type": "Only Lowercase"},
            {"password": "ABCDEFGH", "type": "Only Uppercase"},
            {"password": "Password", "type": "Missing Special Chars"},
            {"password": "", "type": "Empty"},
            {"password": "   ", "type": "Whitespace Only"},
        ]
        
        for pwd_test in weak_passwords:
            try:
                data = {
                    'student_code': f'ST{random.randint(1000,9999)}',
                    'first_name': 'Test',
                    'last_name': 'Student',
                    'email': f"test{random.randint(1000,9999)}@example.com",
                    'password': pwd_test['password'],
                    'program': 'Computer Science',
                    'year_of_study': 1
                }
                
                response = requests.post(
                    f'{self.base_url}/api/admin/students',
                    json=data,
                    headers={'Authorization': f'Bearer {self.admin_token}'} if self.admin_token else {},
                    timeout=10
                )
                
                if response.status_code == 400:
                    response_data = response.json()
                    if 'password' in response_data.get('error', '').lower():
                        self.log_test_result(
                            f"Password Policy - {pwd_test['type']}",
                            True,
                            f"Weak password rejected: {pwd_test['type']}",
                            "low"
                        )
                    else:
                        self.log_test_result(
                            f"Password Policy - {pwd_test['type']}",
                            False,
                            f"Password rejected but not for security reasons: {pwd_test['type']}",
                            "medium"
                        )
                elif response.status_code == 200 or response.status_code == 201:
                    self.log_test_result(
                        f"Password Policy - {pwd_test['type']}",
                        False,
                        f"Weak password accepted: {pwd_test['type']}",
                        "high"
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Password Policy - {pwd_test['type']}",
                    False,
                    f"Test failed: {str(e)}",
                    "medium"
                )
    
    def test_concurrent_access(self):
        """Test concurrent access and race conditions"""
        print("\n" + "="*60)
        print("TESTING CONCURRENT ACCESS")
        print("="*60)
        
        def make_concurrent_request(endpoint, data=None):
            """Make concurrent requests to test race conditions"""
            try:
                if data:
                    response = requests.post(endpoint, json=data, timeout=10)
                else:
                    response = requests.get(endpoint, timeout=10)
                return {
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'content': response.text[:200]
                }
            except Exception as e:
                return {'error': str(e)}
        
        # Test concurrent login attempts
        with ThreadPoolExecutor(max_workers=10) as executor:
            login_futures = []
            for i in range(10):
                future = executor.submit(
                    make_concurrent_request,
                    f'{self.base_url}/api/student/login',
                    {'email': 'nonexistent@example.com', 'password': 'wrongpass'}
                )
                login_futures.append(future)
            
            concurrent_results = []
            for future in as_completed(login_futures):
                result = future.result()
                concurrent_results.append(result)
        
        # Analyze results
        success_count = sum(1 for r in concurrent_results if r.get('status_code') == 200)
        error_count = sum(1 for r in concurrent_results if 'error' in r)
        rate_limited_count = sum(1 for r in concurrent_results if r.get('status_code') == 429)
        
        if success_count == 0 and rate_limited_count > 0:
            self.log_test_result(
                "Concurrent Access Protection",
                True,
                f"System handled concurrent requests well. {rate_limited_count} rate limited, {error_count} errors",
                "low"
            )
        elif error_count > 5:
            self.log_test_result(
                "Concurrent Access Protection",
                False,
                f"System unstable under concurrent load. {error_count} errors out of {len(concurrent_results)} requests",
                "high"
            )
        else:
            self.log_test_result(
                "Concurrent Access Protection",
                True,
                f"System handled concurrent requests adequately. {success_count} successful, {error_count} errors",
                "medium"
            )
    
    def generate_html_report(self):
        """Generate comprehensive HTML security report"""
        print("\n" + "="*60)
        print("GENERATING SECURITY TEST REPORT")
        print("="*60)
        
        # Count results by severity
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = sum(1 for result in self.test_results if not result['success'])
        
        for result in self.test_results:
            severity_counts[result['severity']] += 1
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>IntelliAttend Security Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); flex: 1; }}
        .test-result {{ background: white; margin: 10px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .pass {{ border-left: 5px solid #28a745; }}
        .fail {{ border-left: 5px solid #dc3545; }}
        .severity-critical {{ background-color: #f8d7da; }}
        .severity-high {{ background-color: #fff3cd; }}
        .severity-medium {{ background-color: #d4edda; }}
        .severity-low {{ background-color: #d1ecf1; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        .details {{ background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; font-size: 0.9em; }}
        .recommendations {{ background: #e8f4fd; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .metric {{ text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ IntelliAttend Security Test Report</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Comprehensive security assessment of the IntelliAttend system</p>
    </div>

    <div class="summary">
        <div class="summary-card metric">
            <div class="metric-value">{len(self.test_results)}</div>
            <div>Total Tests</div>
        </div>
        <div class="summary-card metric">
            <div class="metric-value" style="color: #28a745;">{passed_tests}</div>
            <div>Passed</div>
        </div>
        <div class="summary-card metric">
            <div class="metric-value" style="color: #dc3545;">{failed_tests}</div>
            <div>Failed</div>
        </div>
        <div class="summary-card metric">
            <div class="metric-value" style="color: #fd7e14;">{severity_counts['critical'] + severity_counts['high']}</div>
            <div>High/Critical Issues</div>
        </div>
    </div>

    <div class="recommendations">
        <h2>🎯 Key Security Recommendations</h2>
        <ul>
            <li><strong>Rate Limiting:</strong> Ensure all authentication endpoints have appropriate rate limiting</li>
            <li><strong>Input Validation:</strong> Implement comprehensive server-side input validation</li>
            <li><strong>SQL Injection:</strong> Use parameterized queries and ORM properly</li>
            <li><strong>JWT Security:</strong> Implement proper token expiration and blacklisting</li>
            <li><strong>Password Policies:</strong> Enforce strong password requirements</li>
            <li><strong>Concurrent Access:</strong> Monitor system behavior under load</li>
        </ul>
    </div>

    <h2>📊 Detailed Test Results</h2>
"""
        
        for result in self.test_results:
            status_class = "pass" if result['success'] else "fail"
            severity_class = f"severity-{result['severity']}"
            
            html_content += f"""
    <div class="test-result {status_class} {severity_class}">
        <h3>{'✅' if result['success'] else '❌'} {result['test_name']}</h3>
        <p><strong>Message:</strong> {result['message']}</p>
        <p class="timestamp">Severity: {result['severity'].upper()} | {result['timestamp']}</p>
        {f'<div class="details">{json.dumps(result["details"], indent=2)}</div>' if result['details'] else ''}
    </div>
"""
        
        html_content += """
    <div class="header" style="margin-top: 40px;">
        <h2>🏁 Test Summary</h2>
        <p>This report provides a comprehensive assessment of the IntelliAttend system's security posture. 
           Address critical and high-severity issues immediately, and implement recommended security measures 
           to enhance overall system security.</p>
    </div>
</body>
</html>
"""
        
        try:
            with open(REPORT_FILE, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ Security report generated: {REPORT_FILE}")
            return True
        except Exception as e:
            print(f"❌ Failed to generate report: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all security tests"""
        print("🚀 Starting IntelliAttend Security Test Suite")
        print("=" * 80)
        
        start_time = datetime.now()
        
        # Run all test categories
        self.test_rate_limiting()
        self.test_sql_injection()
        self.test_jwt_security()
        self.test_input_validation()
        self.test_password_policies()
        self.test_concurrent_access()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "="*80)
        print("🏁 SECURITY TESTING COMPLETED")
        print("="*80)
        print(f"⏱️  Total Duration: {duration}")
        print(f"📊 Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {sum(1 for r in self.test_results if r['success'])}")
        print(f"❌ Failed: {sum(1 for r in self.test_results if not r['success'])}")
        
        # Generate report
        self.generate_html_report()
        
        return self.test_results

def main():
    """Main function to run security tests"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
    
    print(f"🎯 Testing IntelliAttend at: {base_url}")
    
    tester = SecurityTester(base_url)
    results = tester.run_all_tests()
    
    # Print final summary
    critical_issues = sum(1 for r in results if r['severity'] == 'critical' and not r['success'])
    high_issues = sum(1 for r in results if r['severity'] == 'high' and not r['success'])
    
    if critical_issues > 0:
        print(f"\n🚨 CRITICAL: {critical_issues} critical security issues found!")
    elif high_issues > 0:
        print(f"\n⚠️  WARNING: {high_issues} high-severity issues found!")
    else:
        print(f"\n🎉 Security testing completed with no critical issues!")
    
    print(f"📄 Full report available at: {REPORT_FILE}")

if __name__ == "__main__":
    main()