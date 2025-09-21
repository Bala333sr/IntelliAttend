#!/usr/bin/env python3
"""
Security Investigation and Edge Case Testing
Deep dive into security vulnerabilities and system edge cases
"""

import sys
import os
import requests
import time
import json
from datetime import datetime

# Add the backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

BASE_URL = "http://localhost:5002"

def test_sql_injection_detailed():
    """Detailed SQL injection testing"""
    print("🔍 DETAILED SQL INJECTION TESTING")
    print("=" * 50)
    
    # Wait for rate limit to reset
    print("Waiting for rate limit reset...")
    time.sleep(65)  # Wait 65 seconds for rate limit to reset
    
    payloads = [
        {"username": "admin", "password": "admin123"},  # Valid login first
        {"username": "admin' --", "password": "anything"},
        {"username": "admin'/*", "password": "anything"},
        {"username": "admin';--", "password": "anything"},
        {"username": "' OR 1=1 --", "password": "anything"},
        {"username": "' UNION SELECT 1,2,3 --", "password": "anything"},
    ]
    
    for i, payload in enumerate(payloads):
        try:
            print(f"\nTest {i+1}: {payload}")
            response = requests.post(f"{BASE_URL}/api/admin/login", 
                                   json=payload, timeout=10)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200 and i > 0:  # First one should succeed
                print("🚨 POTENTIAL SQL INJECTION VULNERABILITY!")
                return True
            elif response.status_code == 429:
                print("⚠️  Rate limited - waiting...")
                time.sleep(10)
                continue
                
            time.sleep(2)  # Avoid rate limiting
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("✅ No SQL injection vulnerabilities confirmed")
    return False

def test_authentication_edge_cases():
    """Test authentication edge cases"""
    print("\n🔍 AUTHENTICATION EDGE CASES")
    print("=" * 50)
    
    edge_cases = [
        # Empty credentials
        {"username": "", "password": ""},
        {"username": None, "password": None},
        
        # Very long strings
        {"username": "A" * 1000, "password": "B" * 1000},
        
        # Special characters
        {"username": "admin\x00", "password": "admin123"},
        {"username": "admin", "password": "admin123\x00"},
        
        # Unicode attacks
        {"username": "ادmin", "password": "admin123"},  # Contains Arabic characters
        
        # JSON injection
        {"username": '{"admin": true}', "password": "admin123"},
    ]
    
    vulnerabilities_found = []
    
    for i, payload in enumerate(edge_cases):
        try:
            print(f"\nEdge Case {i+1}: Testing with {str(payload)[:100]}...")
            response = requests.post(f"{BASE_URL}/api/admin/login", 
                                   json=payload, timeout=5)
            
            if response.status_code == 200:
                print("🚨 AUTHENTICATION BYPASSED!")
                vulnerabilities_found.append(f"Edge case {i+1}")
            elif response.status_code == 500:
                print("⚠️  Server error - potential vulnerability")
                vulnerabilities_found.append(f"Server error in edge case {i+1}")
            else:
                print(f"✅ Properly rejected: {response.status_code}")
                
            time.sleep(1)
            
        except requests.exceptions.Timeout:
            print("⚠️  Request timeout - potential DoS vulnerability")
        except Exception as e:
            print(f"⚠️  Exception: {e}")
    
    return vulnerabilities_found

def test_business_logic_edge_cases():
    """Test business logic edge cases"""
    print("\n🔍 BUSINESS LOGIC EDGE CASES")
    print("=" * 50)
    
    # Get valid tokens first
    try:
        admin_response = requests.post(f"{BASE_URL}/api/admin/login", 
                                     json={"username": "admin", "password": "admin123"}, timeout=5)
        admin_token = admin_response.json().get('access_token') if admin_response.status_code == 200 else None
    except:
        admin_token = None
    
    issues_found = []
    
    # Test 1: Negative IDs
    if admin_token:
        test_cases = [
            ("/api/admin/faculty/-1", "Negative faculty ID"),
            ("/api/admin/students/-1", "Negative student ID"), 
            ("/api/admin/classes/-1", "Negative class ID"),
            ("/api/qr/current/-1", "Negative session ID"),
        ]
        
        for endpoint, description in test_cases:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", 
                                      headers={"Authorization": f"Bearer {admin_token}"}, timeout=5)
                
                if response.status_code == 500:
                    print(f"⚠️  {description}: Server error (500)")
                    issues_found.append(description)
                elif response.status_code == 200:
                    print(f"🚨 {description}: Unexpected success")
                    issues_found.append(f"{description} - unexpected success")
                else:
                    print(f"✅ {description}: Properly handled ({response.status_code})")
                    
            except Exception as e:
                print(f"⚠️  {description}: Exception - {e}")
    
    # Test 2: Very large numbers
    try:
        large_number = 999999999999999999
        response = requests.get(f"{BASE_URL}/api/qr/current/{large_number}", timeout=5)
        
        if response.status_code == 500:
            print("⚠️  Large number handling: Server error")
            issues_found.append("Large number causes server error")
        else:
            print("✅ Large numbers handled properly")
    except Exception as e:
        print(f"⚠️  Large number test failed: {e}")
    
    return issues_found

def test_data_validation():
    """Test input data validation"""
    print("\n🔍 DATA VALIDATION TESTING")
    print("=" * 50)
    
    # Get admin token
    try:
        admin_response = requests.post(f"{BASE_URL}/api/admin/login", 
                                     json={"username": "admin", "password": "admin123"}, timeout=5)
        admin_token = admin_response.json().get('access_token') if admin_response.status_code == 200 else None
    except:
        admin_token = None
    
    if not admin_token:
        print("❌ Cannot get admin token for testing")
        return []
    
    validation_issues = []
    
    # Test creating entities with invalid data
    invalid_faculty_data = {
        "faculty_code": "A" * 100,  # Too long
        "first_name": "",  # Empty
        "last_name": None,  # Null
        "email": "invalid-email",  # Invalid format
        "phone_number": "123",  # Too short
        "department": "<script>alert('xss')</script>",  # XSS attempt
        "password": "weak"  # Too weak
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/admin/faculty", 
                               headers={"Authorization": f"Bearer {admin_token}"},
                               json=invalid_faculty_data, timeout=5)
        
        if response.status_code == 201:
            print("🚨 Created faculty with invalid data!")
            validation_issues.append("Faculty validation bypass")
        elif response.status_code == 500:
            print("⚠️  Server error with invalid faculty data")
            validation_issues.append("Faculty validation causes server error")
        else:
            print("✅ Faculty validation working properly")
            
    except Exception as e:
        print(f"⚠️  Faculty validation test failed: {e}")
    
    # Test invalid class data
    invalid_class_data = {
        "class_code": "",  # Empty
        "class_name": "A" * 1000,  # Very long
        "faculty_id": "not-a-number",  # Invalid type
        "classroom_id": -1,  # Negative
        "semester": "InvalidSemester",  # Invalid value
        "academic_year": "not-a-year",  # Invalid format
        "credits": -5,  # Negative credits
        "max_students": 0,  # Zero students
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/admin/classes", 
                               headers={"Authorization": f"Bearer {admin_token}"},
                               json=invalid_class_data, timeout=5)
        
        if response.status_code == 201:
            print("🚨 Created class with invalid data!")
            validation_issues.append("Class validation bypass")
        elif response.status_code == 500:
            print("⚠️  Server error with invalid class data")
            validation_issues.append("Class validation causes server error")
        else:
            print("✅ Class validation working properly")
            
    except Exception as e:
        print(f"⚠️  Class validation test failed: {e}")
    
    return validation_issues

def test_session_security():
    """Test session security and token handling"""
    print("\n🔍 SESSION SECURITY TESTING")
    print("=" * 50)
    
    security_issues = []
    
    # Test with expired/invalid tokens
    invalid_tokens = [
        "invalid.token.here",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.INVALID.SIGNATURE",
        "",
        None,
        "Bearer " * 100,  # Very long token
    ]
    
    for i, token in enumerate(invalid_tokens):
        try:
            headers = {}
            if token is not None:
                headers["Authorization"] = f"Bearer {token}"
                
            response = requests.get(f"{BASE_URL}/api/admin/faculty", 
                                  headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"🚨 Invalid token {i+1} accepted!")
                security_issues.append(f"Invalid token {i+1} bypass")
            elif response.status_code == 500:
                print(f"⚠️  Invalid token {i+1} caused server error")
                security_issues.append(f"Invalid token {i+1} server error")
            else:
                print(f"✅ Invalid token {i+1} properly rejected")
                
        except Exception as e:
            print(f"⚠️  Token test {i+1} failed: {e}")
    
    return security_issues

def generate_detailed_report():
    """Generate a comprehensive security report"""
    print("\n" + "=" * 70)
    print("📋 COMPREHENSIVE SECURITY & LOGIC AUDIT REPORT")
    print("=" * 70)
    print(f"Audit Date: {datetime.now().isoformat()}")
    print(f"System: IntelliAttend v1.0")
    print(f"Target: {BASE_URL}")
    print("=" * 70)
    
    # Run all tests
    sql_issues = test_sql_injection_detailed()
    auth_issues = test_authentication_edge_cases()
    logic_issues = test_business_logic_edge_cases()
    validation_issues = test_data_validation()
    session_issues = test_session_security()
    
    # Compile issues
    all_issues = []
    
    if sql_issues:
        all_issues.extend(["SQL Injection vulnerability detected"])
    
    all_issues.extend(auth_issues)
    all_issues.extend(logic_issues)
    all_issues.extend(validation_issues)
    all_issues.extend(session_issues)
    
    # Generate final report
    print(f"\n📊 AUDIT SUMMARY")
    print("=" * 50)
    print(f"Total Issues Found: {len(all_issues)}")
    
    if not all_issues:
        print("✅ No critical security vulnerabilities detected!")
        print("🎉 System appears to be secure and well-implemented")
    else:
        print("⚠️  Issues Identified:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
    
    return all_issues

if __name__ == '__main__':
    try:
        issues = generate_detailed_report()
        
        print(f"\n" + "=" * 70)
        print("🎯 RECOMMENDATIONS")
        print("=" * 70)
        
        if issues:
            print("1. Address identified vulnerabilities immediately")
            print("2. Implement additional input validation")
            print("3. Add comprehensive error handling")
            print("4. Consider security code review")
            print("5. Implement automated security testing")
        else:
            print("1. Continue regular security audits")
            print("2. Monitor for new vulnerabilities")
            print("3. Keep dependencies updated")
            print("4. Implement security monitoring")
            print("5. Document security procedures")
            
    except Exception as e:
        print(f"Security audit failed: {e}")
        sys.exit(1)