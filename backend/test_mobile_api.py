#!/usr/bin/env python3
"""
Test script for mobile API endpoints
"""

import requests
import json
from datetime import datetime

def test_mobile_api():
    """Test the mobile API endpoints"""
    
    # Base URL for the API
    base_url = "http://localhost:5002"
    
    print("=" * 60)
    print("MOBILE API TEST")
    print("=" * 60)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/discover")
        if response.status_code == 200:
            print("✅ Server is running")
            discovery_data = response.json()
            print(f"   Server IP: {discovery_data.get('server', {}).get('network', {}).get('primary_ip')}")
            print(f"   API Base: {discovery_data.get('server', {}).get('api_base')}")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Test mobile config endpoint
    try:
        response = requests.get(f"{base_url}/api/config/mobile")
        if response.status_code == 200:
            print("✅ Mobile config endpoint working")
            config_data = response.json()
            print(f"   API Base URL: {config_data.get('config', {}).get('api_base_url')}")
        else:
            print(f"❌ Mobile config returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing mobile config: {e}")
    
    print("\n" + "=" * 60)
    print("MANUAL TESTING INSTRUCTIONS")
    print("=" * 60)
    print("To test the mobile API endpoints that require authentication:")
    print("1. Use a tool like Postman or curl")
    print("2. First login as a student to get a JWT token:")
    print(f"   POST {base_url}/api/student/login")
    print('   Body: {"email": "alice.williams@student.edu", "password": "student123"}')
    print("3. Use the returned access_token in the Authorization header:")
    print("   Authorization: Bearer <your_token>")
    print("4. Test the mobile endpoints:")
    print(f"   POST {base_url}/api/mobile/location/update")
    print(f"   GET {base_url}/api/mobile/device/status")
    print(f"   GET {base_url}/api/mobile/attendance/status")
    print("\nExample location update payload:")
    print(json.dumps({
        "location": {
            "latitude": 17.5607,
            "longitude": 78.4555,
            "accuracy": 5.0
        },
        "device_info": {
            "device_id": "test_device_001",
            "device_name": "Test Phone",
            "device_type": "android"
        }
    }, indent=2))
    
    print("\n" + "=" * 60)
    print("MOBILE API ENDPOINTS SUMMARY")
    print("=" * 60)
    print("POST  /api/mobile/location/update  - Update student location")
    print("GET   /api/mobile/device/status    - Get device status")
    print("GET   /api/mobile/attendance/status - Get attendance status")
    print("\nAll endpoints require JWT authentication")

if __name__ == '__main__':
    test_mobile_api()