#!/usr/bin/env python3
"""
Test script for admin login functionality
"""

import requests
import json

def test_admin_login():
    """Test admin login endpoint"""
    url = "http://localhost:5002/api/admin/auth/login"
    
    # Test data
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Admin login successful!")
                print(f"Access Token: {data.get('access_token')}")
                return data.get('access_token')
            else:
                print("❌ Admin login failed!")
                print(f"Error: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
    
    return None

if __name__ == "__main__":
    print("Testing Admin Login...")
    token = test_admin_login()
    if token:
        print(f"\n🎉 Got access token: {token[:20]}...")
    else:
        print("\n💥 Failed to get access token")