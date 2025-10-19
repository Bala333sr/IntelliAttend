#!/usr/bin/env python3
"""
Test script for new mobile API endpoints
"""

import requests
import json
from datetime import datetime

def test_new_mobile_endpoints():
    """Test the new mobile API endpoints"""
    
    # Base URL for the API
    base_url = "http://localhost:5002"
    
    print("=" * 60)
    print("NEW MOBILE API ENDPOINTS TEST")
    print("=" * 60)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Test mobile login to get JWT token
    login_data = {
        "email": "alice.williams@student.edu",
        "password": "student123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/mobile/student/login", json=login_data)
        if response.status_code == 200:
            login_result = response.json()
            access_token = login_result.get('access_token')
            if access_token:
                print("✅ Mobile login successful")
                print(f"   Access token: {access_token[:20]}...")
            else:
                print("❌ Login failed - no access token")
                return
        else:
            print(f"❌ Mobile login failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error during mobile login: {e}")
        return
    
    # Set up headers for authenticated requests
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test 3: Test session status endpoint
    print("\nTesting session status endpoint...")
    try:
        # Test with a non-existent session ID
        response = requests.get(f"{base_url}/api/mobile/session/status/999999", headers=headers)
        if response.status_code == 404:
            print("✅ Session status endpoint working (session not found as expected)")
        else:
            print(f"⚠️  Session status returned unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing session status: {e}")
    
    # Test 4: Test attendance history endpoint
    print("\nTesting attendance history endpoint...")
    try:
        response = requests.get(f"{base_url}/api/mobile/attendance/history?filter=month", headers=headers)
        if response.status_code == 200:
            history_data = response.json()
            if history_data.get('success'):
                print("✅ Attendance history endpoint working")
                print(f"   Total classes: {history_data.get('total_classes', 0)}")
                print(f"   Attendance percentage: {history_data.get('attendance_percentage', 0)}%")
            else:
                print(f"⚠️  Attendance history returned success=False: {history_data.get('error')}")
        else:
            print(f"❌ Attendance history failed with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing attendance history: {e}")
    
    # Test 5: Test monthly overview endpoint
    print("\nTesting monthly overview endpoint...")
    try:
        response = requests.get(f"{base_url}/api/mobile/attendance/monthly-overview", headers=headers)
        if response.status_code == 200:
            overview_data = response.json()
            if overview_data.get('success'):
                print("✅ Monthly overview endpoint working")
                print(f"   Month: {overview_data.get('month')}")
                weeks_data = overview_data.get('weeks', [])
                print(f"   Weeks data: {len(weeks_data)} weeks")
            else:
                print(f"⚠️  Monthly overview returned success=False: {overview_data.get('error')}")
        else:
            print(f"❌ Monthly overview failed with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing monthly overview: {e}")
    
    # Test 6: Test FCM token registration
    print("\nTesting FCM token registration...")
    fcm_data = {
        "device_uuid": "test_device_123",
        "fcm_token": "test_fcm_token_abc123"
    }
    try:
        response = requests.post(f"{base_url}/api/mobile/notifications/register", headers=headers, json=fcm_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ FCM token registration endpoint working")
            else:
                print(f"⚠️  FCM token registration returned success=False")
        elif response.status_code == 404:
            print("⚠️  FCM token registration - device not found (expected if device not registered)")
        else:
            print(f"❌ FCM token registration failed with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing FCM token registration: {e}")
    
    # Test 7: Test notification toggle
    print("\nTesting notification toggle...")
    toggle_data = {
        "enabled": True
    }
    try:
        response = requests.post(f"{base_url}/api/mobile/notifications/toggle", headers=headers, json=toggle_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Notification toggle endpoint working")
                print(f"   Notifications enabled: {result.get('notifications_enabled')}")
            else:
                print(f"⚠️  Notification toggle returned success=False")
        else:
            print(f"❌ Notification toggle failed with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing notification toggle: {e}")
    
    # Test 8: Test security violation logging
    print("\nTesting security violation logging...")
    violation_data = {
        "type": "test_violation",
        "details": "Test security violation report"
    }
    try:
        response = requests.post(f"{base_url}/api/mobile/security/violation", headers=headers, json=violation_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Security violation logging endpoint working")
            else:
                print(f"⚠️  Security violation logging returned success=False")
        else:
            print(f"❌ Security violation logging failed with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing security violation logging: {e}")
    
    # Test 9: Test mobile logout
    print("\nTesting mobile logout...")
    logout_data = {
        "device_uuid": "test_device_123"
    }
    try:
        response = requests.post(f"{base_url}/api/mobile/logout", headers=headers, json=logout_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Mobile logout endpoint working")
            else:
                print(f"⚠️  Mobile logout returned success=False")
        else:
            print(f"❌ Mobile logout failed with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing mobile logout: {e}")
    
    print("\n" + "=" * 60)
    print("NEW MOBILE API ENDPOINTS TEST COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    test_new_mobile_endpoints()