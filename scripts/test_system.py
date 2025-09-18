#!/usr/bin/env python3
"""
INTELLIATTEND System Test Script
Tests QR generation, validation, and overall system functionality
"""

import os
import sys
import time
import requests
import json
from datetime import datetime

# Add the server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

def test_server_connection():
    """Test if the Flask server is running"""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def test_faculty_login():
    """Test faculty login functionality"""
    login_data = {
        'email': 'john.smith@university.edu',
        'password': 'faculty123'
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/faculty/login',
            json=login_data,
            timeout=10
        )
        
        data = response.json()
        
        if data.get('success'):
            return {
                'success': True,
                'token': data.get('access_token'),
                'user': data.get('faculty')
            }
        else:
            return {
                'success': False,
                'error': data.get('error', 'Unknown error')
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Request failed: {str(e)}'
        }

def test_student_login():
    """Test student login functionality"""
    login_data = {
        'email': 'alice.williams@student.edu',
        'password': 'student123'
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/student/login',
            json=login_data,
            timeout=10
        )
        
        data = response.json()
        
        if data.get('success'):
            return {
                'success': True,
                'token': data.get('access_token'),
                'user': data.get('student')
            }
        else:
            return {
                'success': False,
                'error': data.get('error', 'Unknown error')
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Request failed: {str(e)}'
        }

def test_otp_generation(auth_token):
    """Test OTP generation"""
    try:
        response = requests.post(
            'http://localhost:5000/api/faculty/generate-otp',
            headers={'Authorization': f'Bearer {auth_token}'},
            timeout=10
        )
        
        data = response.json()
        
        if data.get('success'):
            return {
                'success': True,
                'otp': data.get('otp'),
                'expires_at': data.get('expires_at')
            }
        else:
            return {
                'success': False,
                'error': data.get('error', 'Unknown error')
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Request failed: {str(e)}'
        }

def test_attendance_session(otp):
    """Test starting attendance session with OTP"""
    session_data = {
        'otp': otp,
        'class_id': 1
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/verify-otp',
            json=session_data,
            timeout=10
        )
        
        data = response.json()
        
        if data.get('success'):
            return {
                'success': True,
                'session_id': data.get('session_id'),
                'expires_at': data.get('expires_at')
            }
        else:
            return {
                'success': False,
                'error': data.get('error', 'Unknown error')
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Request failed: {str(e)}'
        }

def test_qr_retrieval(session_id):
    """Test QR code retrieval"""
    try:
        response = requests.get(
            f'http://localhost:5000/api/qr/current/{session_id}',
            timeout=10
        )
        
        data = response.json()
        
        if data.get('success'):
            return {
                'success': True,
                'qr_filename': data.get('qr_filename'),
                'qr_url': data.get('qr_url'),
                'sequence': data.get('sequence')
            }
        else:
            return {
                'success': False,
                'error': data.get('error', 'Unknown error')
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Request failed: {str(e)}'
        }

def run_comprehensive_test():
    """Run comprehensive system test"""
    print("🚀 INTELLIATTEND System Test")
    print("=" * 50)
    
    # Test 1: Server Connection
    print("1. Testing server connection...")
    if test_server_connection():
        print("   ✅ Server is running")
    else:
        print("   ❌ Server is not running")
        print("\n❗ Please start the server first:")
        print("   python server/app.py")
        return False
    
    # Test 2: Faculty Login
    print("\n2. Testing faculty login...")
    faculty_result = test_faculty_login()
    if faculty_result['success']:
        print(f"   ✅ Faculty login successful")
        print(f"   👤 Logged in as: {faculty_result['user']['name']}")
        faculty_token = faculty_result['token']
    else:
        print(f"   ❌ Faculty login failed: {faculty_result['error']}")
        return False
    
    # Test 3: Student Login
    print("\n3. Testing student login...")
    student_result = test_student_login()
    if student_result['success']:
        print(f"   ✅ Student login successful")
        print(f"   👤 Logged in as: {student_result['user']['name']}")
        student_token = student_result['token']
    else:
        print(f"   ❌ Student login failed: {student_result['error']}")
        return False
    
    # Test 4: OTP Generation
    print("\n4. Testing OTP generation...")
    otp_result = test_otp_generation(faculty_token)
    if otp_result['success']:
        print(f"   ✅ OTP generated successfully")
        print(f"   🔑 OTP: {otp_result['otp']}")
        otp_code = otp_result['otp']
    else:
        print(f"   ❌ OTP generation failed: {otp_result['error']}")
        return False
    
    # Test 5: Attendance Session
    print("\n5. Testing attendance session creation...")
    session_result = test_attendance_session(otp_code)
    if session_result['success']:
        print(f"   ✅ Attendance session created")
        print(f"   📅 Session ID: {session_result['session_id']}")
        session_id = session_result['session_id']
    else:
        print(f"   ❌ Session creation failed: {session_result['error']}")
        return False
    
    # Test 6: QR Code Generation (wait a moment for QR to be generated)
    print("\n6. Testing QR code generation...")
    print("   ⏳ Waiting for QR code generation...")
    time.sleep(3)  # Wait for QR generation
    
    qr_result = test_qr_retrieval(session_id)
    if qr_result['success']:
        print(f"   ✅ QR code retrieved successfully")
        print(f"   🎯 QR File: {qr_result['qr_filename']}")
        print(f"   🔄 Sequence: {qr_result['sequence']}")
    else:
        print(f"   ❌ QR retrieval failed: {qr_result['error']}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed successfully!")
    print("\n📱 System is ready for use:")
    print("   • Faculty Portal: http://localhost:5000")
    print("   • Student Portal: http://localhost:5000/student")
    print("\n🔐 Test Credentials:")
    print("   Faculty: john.smith@university.edu / faculty123")
    print("   Student: alice.williams@student.edu / student123")
    
    return True

def test_qr_generation_only():
    """Test only QR generation functionality"""
    print("🎯 Testing QR Generation Module")
    print("=" * 40)
    
    try:
        from generate_qr import QRCodeManager
        
        config = {
            'QR_CODE_SIZE': 10,
            'QR_CODE_BORDER': 4,
            'QR_REFRESH_INTERVAL': 5,
            'QR_TOKENS_FOLDER': 'QR_DATA/tokens',
            'QR_KEYS_FOLDER': 'QR_DATA/keys'
        }
        
        manager = QRCodeManager(config)
        print("✅ QR Manager initialized")
        
        # Test QR generation
        print("📱 Generating test QR sequence...")
        session_info = manager.generate_qr_sequence(999, "test_token_123", 15)
        
        print(f"✅ QR generation started for session {session_info['session_id']}")
        print("⏳ Waiting for QR generation...")
        
        # Wait and check
        time.sleep(8)
        current_qr = manager.get_current_qr(999)
        
        if current_qr and current_qr['filename']:
            print(f"✅ QR generated: {current_qr['filename']}")
            print(f"🔄 Sequence: {current_qr['sequence']}")
        else:
            print("❌ No QR code generated")
            return False
        
        # Wait for completion
        print("⏳ Waiting for sequence completion...")
        time.sleep(10)
        
        history = manager.get_session_history(999)
        print(f"📊 Total QR codes generated: {len(history)}")
        
        for entry in history:
            print(f"   - Sequence {entry['sequence']}: {entry['filename']}")
        
        print("🎉 QR generation test completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "qr":
            test_qr_generation_only()
        elif sys.argv[1] == "full":
            run_comprehensive_test()
        else:
            print("Usage: python test_system.py [qr|full]")
            print("  qr   - Test QR generation only")
            print("  full - Test complete system (requires running server)")
    else:
        print("INTELLIATTEND System Test Script")
        print("=" * 40)
        print("Available tests:")
        print("  python test_system.py qr    - Test QR generation")
        print("  python test_system.py full  - Test complete system")
        print("\nNote: For full system test, make sure to:")
        print("  1. Set up MySQL database (run database_setup.py)")
        print("  2. Start the Flask server (python server/app.py)")