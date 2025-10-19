#!/usr/bin/env python3
"""
Dynamic URL Update Script for IntelliAttend
Automatically updates ngrok URLs across all project files
"""

import json
import re
import os
import sys
import requests
from pathlib import Path

def get_current_ngrok_url():
    """Get current ngrok URL from local API"""
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        data = response.json()
        
        if data.get('tunnels') and len(data['tunnels']) > 0:
            tunnel_url = data['tunnels'][0]['public_url']
            return tunnel_url
        else:
            print("❌ No active ngrok tunnels found")
            return None
    except Exception as e:
        print(f"❌ Could not get ngrok URL: {e}")
        return None

def update_mobile_build_gradle(new_url):
    """Update mobile app build.gradle file"""
    build_gradle_path = Path("../mobile/app/app/build.gradle")
    
    if not build_gradle_path.exists():
        print(f"⚠️  Mobile build.gradle not found at {build_gradle_path}")
        return False
    
    try:
        with open(build_gradle_path, 'r') as f:
            content = f.read()
        
        # Update BASE_URL for release, debug, and staging
        content = re.sub(
            r'buildConfigField "String", "BASE_URL", \'"[^"]*"\'',
            f'buildConfigField "String", "BASE_URL", \'"{new_url}/api/"\'',
            content
        )
        
        # Update FALLBACK_URLS
        fallback_urls = f"{new_url}/api/,http://192.168.0.5:5002/api/,http://localhost:5002/api/"
        content = re.sub(
            r'buildConfigField "String", "FALLBACK_URLS", \'"[^"]*"\'',
            f'buildConfigField "String", "FALLBACK_URLS", \'"{fallback_urls}"\'',
            content
        )
        
        with open(build_gradle_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated mobile build.gradle")
        return True
    except Exception as e:
        print(f"❌ Failed to update mobile build.gradle: {e}")
        return False

def update_app_preferences(new_url):
    """Update mobile app AppPreferences.kt file"""
    preferences_path = Path("../mobile/app/app/src/main/java/com/intelliattend/student/data/preferences/AppPreferences.kt")
    
    if not preferences_path.exists():
        print(f"⚠️  AppPreferences.kt not found at {preferences_path}")
        return False
    
    try:
        with open(preferences_path, 'r') as f:
            content = f.read()
        
        # Update default base URL
        pattern = r'sharedPreferences\.getString\(KEY_BASE_URL, "[^"]*"\) \?\: "[^"]*"'
        replacement = f'sharedPreferences.getString(KEY_BASE_URL, "{new_url}/api/") ?: "{new_url}/api/"'
        content = re.sub(pattern, replacement, content)
        
        with open(preferences_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated mobile AppPreferences.kt")
        return True
    except Exception as e:
        print(f"❌ Failed to update mobile AppPreferences.kt: {e}")
        return False

def update_mobile_config_html(new_url):
    """Update frontend mobile_config.html template"""
    config_html_path = Path("../frontend/templates/mobile_config.html")
    
    if not config_html_path.exists():
        print(f"⚠️  mobile_config.html not found at {config_html_path}")
        return False
    
    try:
        with open(config_html_path, 'r') as f:
            content = f.read()
        
        # Update server URLs in manual configuration section
        content = re.sub(
            r'<p><strong>Server URL:</strong> [^<]*</p>',
            f'<p><strong>Server URL:</strong> {new_url}</p>',
            content
        )
        
        content = re.sub(
            r'<p><strong>API Base:</strong> [^<]*</p>',
            f'<p><strong>API Base:</strong> {new_url}/api/</p>',
            content
        )
        
        content = re.sub(
            r'<p><strong>Discovery Endpoint:</strong> [^<]*</p>',
            f'<p><strong>Discovery Endpoint:</strong> {new_url}/api/discover</p>',
            content
        )
        
        with open(config_html_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated frontend mobile_config.html")
        return True
    except Exception as e:
        print(f"❌ Failed to update frontend mobile_config.html: {e}")
        return False

def update_backend_app_py(new_url):
    """Update backend app.py startup messages"""
    app_py_path = Path("app.py")
    
    if not app_py_path.exists():
        print(f"⚠️  app.py not found at {app_py_path}")
        return False
    
    try:
        with open(app_py_path, 'r') as f:
            content = f.read()
        
        # Update mobile app URL in startup messages
        content = re.sub(
            r'logger\.info\("📱 Mobile App URL: [^"]*"\)',
            f'logger.info("📱 Mobile App URL: {new_url}/api/")',
            content
        )
        
        content = re.sub(
            r'logger\.info\("🌐 Public Access: [^"]*"\)',
            f'logger.info("🌐 Public Access: {new_url}")',
            content
        )
        
        with open(app_py_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated backend app.py")
        return True
    except Exception as e:
        print(f"❌ Failed to update backend app.py: {e}")
        return False

def update_tunnel_url_file(new_url):
    """Update the tunnel_url.txt file"""
    try:
        with open("tunnel_url.txt", 'w') as f:
            f.write(f"{new_url}/api/\n")
        print(f"✅ Updated tunnel_url.txt")
        return True
    except Exception as e:
        print(f"❌ Failed to update tunnel_url.txt: {e}")
        return False

def main():
    print("🔄 IntelliAttend URL Update Script")
    print("=" * 50)
    
    # Check if URL is provided as argument
    if len(sys.argv) > 1:
        new_url = sys.argv[1].rstrip('/')
        print(f"📝 Using provided URL: {new_url}")
    else:
        # Try to get URL from ngrok API
        new_url = get_current_ngrok_url()
        if not new_url:
            print("❌ Could not get ngrok URL. Please provide URL as argument:")
            print("   python3 update_urls.py https://your-ngrok-url.ngrok-free.dev")
            return False
        
        new_url = new_url.rstrip('/')
        print(f"🌐 Found ngrok URL: {new_url}")
    
    print("\n🔄 Updating project files...")
    
    success_count = 0
    total_updates = 5
    
    # Update all files
    if update_mobile_build_gradle(new_url):
        success_count += 1
    
    if update_app_preferences(new_url):
        success_count += 1
    
    if update_mobile_config_html(new_url):
        success_count += 1
    
    if update_backend_app_py(new_url):
        success_count += 1
    
    if update_tunnel_url_file(new_url):
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Update complete: {success_count}/{total_updates} files updated successfully")
    
    if success_count == total_updates:
        print("\n📱 Updated URLs:")
        print(f"   Mobile App: {new_url}/api/")
        print(f"   Web Portal: {new_url}")
        print(f"   Health Check: {new_url}/api/health")
        print("\n💡 Next steps:")
        print("   1. Rebuild your mobile app")
        print("   2. Test the connection")
        print("   3. Update any additional config files if needed")
        return True
    else:
        print(f"\n⚠️  Some updates failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)