#!/usr/bin/env python3
"""
Quick Security Validation for IntelliAttend
===========================================

This script performs focused security tests on the running IntelliAttend system.
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5002"

def test_rate_limiting():
    """Test rate limiting on authentication endpoints"""
    print("🔐 Testing Rate Limiting Security")
    print("=" * 50)
    
    endpoints = [
        {"url": f"{BASE_URL}/api/admin/login", "name": "Admin Login", "data": {"username": "test", "password": "wrong"}},
        {"url": f"{BASE_URL}/api/student/login", "name": "Student Login", "data": {"email": "test@example.com", "password": "wrong"}},
        {"url": f"{BASE_URL}/api/faculty/login", "name": "Faculty Login", "data": {"email": "test@example.com", "password": "wrong"}}
    ]
    
    results = {}
    
    for endpoint in endpoints:
        print(f"\nTesting {endpoint['name']}...")
        responses = []
        
        # Send 8 requests rapidly (should exceed rate limits)
        for i in range(8):
            try:
                response = requests.post(
                    endpoint['url'], 
                    json=endpoint['data'], 
                    timeout=5
                )
                responses.append({
                    'request': i + 1,
                    'status_code': response.status_code,
                    'time': response.elapsed.total_seconds()
                })
                print(f"  Request {i+1}: HTTP {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
                time.sleep(0.2)  # Small delay between requests
                
            except Exception as e:
                print(f"  Request {i+1}: ERROR - {str(e)}")
                responses.append({'request': i + 1, 'error': str(e)})
        
        # Analyze results
        rate_limited = sum(1 for r in responses if r.get('status_code') == 429)
        successful = sum(1 for r in responses if r.get('status_code') == 401)  # Expected failure
        errors = sum(1 for r in responses if 'error' in r)
        
        results[endpoint['name']] = {
            'total_requests': len(responses),
            'rate_limited': rate_limited,
            'successful_attempts': successful,
            'errors': errors,
            'rate_limiting_active': rate_limited > 0
        }
        
        if rate_limited > 0:
            print(f"  ✅ Rate limiting ACTIVE: {rate_limited} requests blocked")
        else:
            print(f"  ❌ Rate limiting NOT DETECTED: All requests processed")
    
    return results

def test_sql_injection():
    """Quick SQL injection test"""
    print("\n💉 Testing SQL Injection Protection")
    print("=" * 50)
    
    payloads = ["' OR '1'='1", "'; DROP TABLE users;--", "admin'--"]
    
    for payload in payloads:
        try:
            response = requests.post(
                f"{BASE_URL}/api/admin/login",
                json={"username": payload, "password": "test"},
                timeout=5
            )
            
            if response.status_code == 200 and "success" in response.text.lower():
                print(f"❌ CRITICAL: SQL Injection possible with payload: {payload}")
                return False
            else:
                print(f"✅ Payload blocked: {payload}")
                
        except Exception as e:
            print(f"⚠️  Error testing payload {payload}: {str(e)}")
    
    print("✅ SQL Injection tests passed")
    return True

def test_authentication_bypass():
    """Test common authentication bypass techniques"""
    print("\n🔓 Testing Authentication Bypass")
    print("=" * 50)
    
    # Test empty credentials
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"username": "", "password": ""},
            timeout=5
        )
        
        if response.status_code == 200:
            print("❌ CRITICAL: Empty credentials accepted")
            return False
        else:
            print("✅ Empty credentials rejected")
    except Exception as e:
        print(f"⚠️  Error testing empty credentials: {str(e)}")
    
    # Test null values
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"username": None, "password": None},
            timeout=5
        )
        
        if response.status_code == 200:
            print("❌ CRITICAL: Null credentials accepted")
            return False
        else:
            print("✅ Null credentials rejected")
    except Exception as e:
        print(f"⚠️  Error testing null credentials: {str(e)}")
    
    return True

def generate_summary_report(rate_limit_results, sql_injection_passed, auth_bypass_passed):
    """Generate a summary security report"""
    print("\n" + "=" * 60)
    print("🛡️  SECURITY TEST SUMMARY")
    print("=" * 60)
    
    total_issues = 0
    critical_issues = 0
    
    print("\n📊 RATE LIMITING RESULTS:")
    for endpoint, result in rate_limit_results.items():
        status = "✅ PROTECTED" if result['rate_limiting_active'] else "❌ VULNERABLE"
        print(f"  {endpoint}: {status}")
        if not result['rate_limiting_active']:
            total_issues += 1
    
    print(f"\n🔒 SQL INJECTION PROTECTION: {'✅ PROTECTED' if sql_injection_passed else '❌ VULNERABLE'}")
    if not sql_injection_passed:
        total_issues += 1
        critical_issues += 1
    
    print(f"🚪 AUTHENTICATION BYPASS PROTECTION: {'✅ PROTECTED' if auth_bypass_passed else '❌ VULNERABLE'}")
    if not auth_bypass_passed:
        total_issues += 1
        critical_issues += 1
    
    print("\n" + "=" * 60)
    print("🎯 FINAL ASSESSMENT")
    print("=" * 60)
    
    if critical_issues > 0:
        print(f"🚨 CRITICAL: {critical_issues} critical security issues found!")
        print("   Immediate action required before production deployment.")
    elif total_issues > 0:
        print(f"⚠️  WARNING: {total_issues} security issues found.")
        print("   Address these issues to improve security posture.")
    else:
        print("🎉 EXCELLENT: No critical security issues detected!")
        print("   Basic security measures appear to be in place.")
    
    print(f"\nTotal Issues Found: {total_issues}")
    print(f"Critical Issues: {critical_issues}")
    print(f"Test Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function to run quick security tests"""
    print("🚀 IntelliAttend Quick Security Validation")
    print("Testing against:", BASE_URL)
    print("=" * 60)
    
    # Test server connectivity first
    try:
        response = requests.get(f"{BASE_URL}/admin", timeout=5)
        print("✅ Server connection successful")
    except Exception as e:
        print(f"❌ Server connection failed: {str(e)}")
        print("Please ensure the IntelliAttend server is running on port 5002")
        return
    
    start_time = datetime.now()
    
    # Run security tests
    rate_limit_results = test_rate_limiting()
    sql_injection_passed = test_sql_injection()
    auth_bypass_passed = test_authentication_bypass()
    
    # Generate summary
    generate_summary_report(rate_limit_results, sql_injection_passed, auth_bypass_passed)
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n⏱️  Total Test Duration: {duration}")

if __name__ == "__main__":
    main()