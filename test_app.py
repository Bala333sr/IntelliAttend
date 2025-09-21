#!/usr/bin/env python3
"""
Test script for IntelliAttend application
"""

import requests
import time

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5002/api/health')
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_faculty_login():
    """Test faculty login"""
    try:
        login_data = {
            'email': 'john.smith@university.edu',
            'password': 'F@cultY2024!'
        }
        
        response = requests.post('http://localhost:5002/api/faculty/login', json=login_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Faculty login successful")
                print(f"   Faculty: {data['faculty']['name']}")
                return data.get('access_token')
            else:
                print(f"❌ Faculty login failed: {data.get('error')}")
                return None
        else:
            print(f"❌ Faculty login failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Faculty login error: {e}")
        return None

def test_student_login():
    """Test student login"""
    try:
        login_data = {
            'email': 'student1@student.edu',
            'password': 'Stud3nt2024!'
        }
        
        response = requests.post('http://localhost:5002/api/student/login', json=login_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Student login successful")
                print(f"   Student: {data['student']['firstName']} {data['student']['lastName']}")
                return data.get('access_token')
            else:
                print(f"❌ Student login failed: {data.get('error')}")
                return None
        else:
            print(f"❌ Student login failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Student login error: {e}")
        return None

def test_generate_otp(token):
    """Test OTP generation"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        response = requests.post('http://localhost:5002/api/faculty/generate-otp', headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ OTP generation successful")
                print(f"   OTP: {data['otp']}")
                return data['otp']
            else:
                print(f"❌ OTP generation failed: {data.get('error')}")
                return None
        else:
            print(f"❌ OTP generation failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ OTP generation error: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Testing IntelliAttend Application...")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("⚠️  Health check failed. Application may not be running.")
        return
    
    print()
    
    # Test faculty login
    print("Testing Faculty Login...")
    faculty_token = test_faculty_login()
    print()
    
    # Test student login
    print("Testing Student Login...")
    student_token = test_student_login()
    print()
    
    # Test OTP generation if faculty login was successful
    if faculty_token:
        print("Testing OTP Generation...")
        otp = test_generate_otp(faculty_token)
        print()
    
    print("=" * 50)
    print("🎉 Testing completed!")

if __name__ == '__main__':
    main()