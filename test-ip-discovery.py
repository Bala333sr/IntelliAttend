#!/usr/bin/env python3
"""
Test IP Discovery Service
========================

This script tests the IP discovery service functionality.
"""

import requests
import json
import socket
import subprocess
from datetime import datetime

def get_current_ip():
    """Get current IP address"""
    try:
        # Method 1: Use socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            # Method 2: Use hostname command
            result = subprocess.run(['hostname', '-I'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                return result.stdout.strip().split()[0]
        except:
            pass
    return "127.0.0.1"

def test_discovery_service():
    """Test the IP discovery service"""
    current_ip = get_current_ip()
    discovery_url = f"http://{current_ip}:5002/api/discover"
    
    print("🧪 Testing IntelliAttend IP Discovery Service")
    print("=" * 60)
    print(f"📍 Detected IP: {current_ip}")
    print(f"🔗 Discovery URL: {discovery_url}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    try:
        print("🔍 Testing discovery endpoint...")
        response = requests.get(discovery_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                server_data = data['server']
                network_data = server_data['network']
                
                print("✅ Discovery service is working!")
                print("\n📊 Server Information:")
                print(f"   🏷️  Server Name: {server_data['server_name']}")
                print(f"   📡 Server IP: {network_data['primary_ip']}")
                print(f"   🔌 Port: {server_data['port']}")
                print(f"   🌐 API Base: {server_data['api_base']}")
                print(f"   🖥️  Hostname: {network_data['hostname']}")
                print(f"   🔄 Last Updated: {server_data['last_updated']}")
                
                print("\n🔗 Available Endpoints:")
                endpoints = server_data['endpoints']
                for name, url in endpoints.items():
                    print(f"   - {name.capitalize()}: {url}")
                
                print("\n🌐 Network Interfaces:")
                for interface in network_data.get('interfaces', []):
                    print(f"   - {interface.get('interface', 'unknown')}: {interface.get('ip', 'N/A')}")
                
                return True
            else:
                print("❌ Discovery service responded but success=false")
                print(f"Response: {data}")
                return False
        else:
            print(f"❌ Discovery service returned HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectinError:
        print("❌ Could not connect to the server")
        print("💡 Make sure IntelliAttend server is running on port 5002")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        print("💡 Server might be slow to respond or overloaded")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_mobile_config():
    """Test mobile configuration endpoint"""
    current_ip = get_current_ip()
    config_url = f"http://{current_ip}:5002/api/config/mobile"
    
    print("\n📱 Testing Mobile Configuration Endpoint...")
    print("-" * 40)
    
    try:
        response = requests.get(config_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                config = data['config']
                print("✅ Mobile config endpoint working!")
                print(f"   📱 API Base URL: {config['api_base_url']}")
                print(f"   📍 Server IP: {config['server_ip']}")
                print(f"   🔌 Port: {config['server_port']}")
                
                print("\n🔑 Authentication Endpoints:")
                auth_endpoints = config['endpoints']['auth']
                for auth_type, endpoint in auth_endpoints.items():
                    print(f"   - {auth_type}: {endpoint}")
                
                return True
            else:
                print("❌ Mobile config endpoint responded but success=false")
                return False
        else:
            print(f"❌ Mobile config endpoint returned HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Mobile config test failed: {str(e)}")
        return False

def test_server_info_page():
    """Test server info page"""
    current_ip = get_current_ip()
    info_url = f"http://{current_ip}:5002/api/server-info"
    
    print("\n📄 Testing Server Info Page...")
    print("-" * 30)
    
    try:
        response = requests.get(info_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Server info page accessible!")
            print(f"   🔗 URL: {info_url}")
            print(f"   📏 Content Length: {len(response.text)} characters")
            return True
        else:
            print(f"❌ Server info page returned HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Server info page test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all discovery tests"""
    print("🚀 Starting IntelliAttend IP Discovery Tests")
    print("=" * 80)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Discovery service
    if test_discovery_service():
        tests_passed += 1
    
    # Test 2: Mobile configuration
    if test_mobile_config():
        tests_passed += 1
    
    # Test 3: Server info page
    if test_server_info_page():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! Your IP Discovery Service is working perfectly!")
        print("\n💡 You can now use these URLs in your mobile app:")
        current_ip = get_current_ip()
        print(f"   📱 Discovery: http://{current_ip}:5002/api/discover")
        print(f"   🔧 Mobile Config: http://{current_ip}:5002/api/config/mobile")
        print(f"   📄 Info Page: http://{current_ip}:5002/api/server-info")
    else:
        print(f"\n⚠️  Some tests failed. Please check if:")
        print("   1. IntelliAttend server is running")
        print("   2. Server is accessible on port 5002")
        print("   3. IP discovery service is properly integrated")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    run_all_tests()