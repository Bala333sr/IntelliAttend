#!/bin/bash

echo "🌐 Setting up IP Discovery Service for IntelliAttend"
echo "=================================================="

# Check if we're in the right directory
if [[ ! -d "/home/anji/IntelliAttend" ]]; then
    echo "❌ IntelliAttend directory not found!"
    exit 1
fi

# Install required Python packages
echo "📦 Installing required packages..."
pip3 install netifaces qrcode[pil] --quiet

if [[ $? -eq 0 ]]; then
    echo "✅ Packages installed successfully"
else
    echo "❌ Failed to install packages"
    exit 1
fi

# Get current IP
CURRENT_IP=$(hostname -I | awk '{print $1}')
echo "📍 Current IP address: $CURRENT_IP"

# Integrate IP discovery into app.py
echo "🔧 Integrating IP Discovery Service..."

# Check if already integrated
if grep -q "ip_discovery_service" /home/anji/IntelliAttend/backend/app.py; then
    echo "⚠️  IP Discovery Service already integrated"
else
    # Add import and setup to app.py
    cat >> /home/anji/IntelliAttend/backend/app.py << 'EOF'

# ============================================================================
# IP DISCOVERY SERVICE INTEGRATION
# ============================================================================
try:
    from ip_discovery_service import setup_ip_discovery
    
    # Setup IP discovery service
    discovery_service, broadcast_service = setup_ip_discovery(app, port=5002)
    logger.info("🌐 IP Discovery Service initialized successfully")
    
except ImportError as e:
    logger.warning(f"⚠️  IP Discovery Service not available: {e}")
    print("⚠️  IP Discovery Service not available - install 'netifaces' and 'qrcode' packages")
except Exception as e:
    logger.error(f"❌ Failed to initialize IP Discovery Service: {e}")
EOF
    
    echo "✅ IP Discovery Service integrated into app.py"
fi

# Create a simple test script
cat > /home/anji/IntelliAttend/test-discovery.py << EOF
#!/usr/bin/env python3
"""Test IP Discovery Service"""

import requests
import json
from datetime import datetime

def test_discovery():
    current_ip = "$CURRENT_IP"
    discovery_url = f"http://{current_ip}:5002/api/discover"
    
    print(f"🧪 Testing IP Discovery Service")
    print(f"📍 Current IP: {current_ip}")
    print(f"🔗 Discovery URL: {discovery_url}")
    print("-" * 50)
    
    try:
        response = requests.get(discovery_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Discovery service working!")
            print(f"📊 Server Data:")
            print(f"   - API Base: {data['server']['api_base']}")
            print(f"   - Server IP: {data['server']['network']['primary_ip']}")
            print(f"   - Last Updated: {data['server']['last_updated']}")
            return True
        else:
            print(f"❌ Discovery service returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to test discovery service: {e}")
        return False

if __name__ == "__main__":
    test_discovery()
EOF

chmod +x /home/anji/IntelliAttend/test-discovery.py

# Create discovery info page
cat > /home/anji/IntelliAttend/discovery-info.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>IntelliAttend Server Discovery</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .info-box { background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .endpoint { background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; margin: 5px 0; }
        .status { color: #28a745; font-weight: bold; }
        code { background: #f8f9fa; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 IntelliAttend Server Discovery</h1>
            <p>Dynamic IP Discovery Service</p>
        </div>

        <div class="info-box">
            <h2>📍 Current Configuration</h2>
            <ul>
                <li><strong>Server IP:</strong> $CURRENT_IP</li>
                <li><strong>Port:</strong> 5002</li>
                <li><strong>Status:</strong> <span class="status">Online</span></li>
                <li><strong>Last Updated:</strong> $(date)</li>
            </ul>
        </div>

        <div class="info-box">
            <h2>🔗 Discovery Endpoints</h2>
            <div class="endpoint">
                <strong>Main Discovery:</strong><br>
                <a href="http://$CURRENT_IP:5002/api/discover">http://$CURRENT_IP:5002/api/discover</a>
            </div>
            <div class="endpoint">
                <strong>Mobile Config:</strong><br>
                <a href="http://$CURRENT_IP:5002/api/config/mobile">http://$CURRENT_IP:5002/api/config/mobile</a>
            </div>
            <div class="endpoint">
                <strong>QR Code Config:</strong><br>
                <a href="http://$CURRENT_IP:5002/api/config/qr">http://$CURRENT_IP:5002/api/config/qr</a>
            </div>
            <div class="endpoint">
                <strong>Network Scan Info:</strong><br>
                <a href="http://$CURRENT_IP:5002/api/network-scan">http://$CURRENT_IP:5002/api/network-scan</a>
            </div>
        </div>

        <div class="info-box">
            <h2>📱 For Mobile App Developers</h2>
            <p>Use this URL in your mobile app for auto-discovery:</p>
            <code>http://$CURRENT_IP:5002/api/discover</code>
            
            <h3>Example Mobile Implementation:</h3>
            <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto;">
// JavaScript/React Native
const response = await fetch('http://$CURRENT_IP:5002/api/discover');
const config = await response.json();
const apiBaseUrl = config.server.api_base;

// Android (Kotlin)
val response = client.newCall(request).execute()
val json = JSONObject(response.body!!.string())
val apiBase = json.getJSONObject("server").getString("api_base")

// iOS (Swift)
let (data, _) = try await URLSession.shared.data(from: url)
let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
            </pre>
        </div>

        <div class="info-box">
            <h2>🔧 Testing</h2>
            <p>Test the discovery service:</p>
            <code>cd /home/anji/IntelliAttend && python3 test-discovery.py</code>
        </div>

        <script>
            // Auto-refresh every 60 seconds to show current IP
            setTimeout(() => location.reload(), 60000);
        </script>
    </div>
</body>
</html>
EOF

echo "✅ Setup completed successfully!"
echo ""
echo "📊 Summary:"
echo "==========="
echo "📍 Current IP: $CURRENT_IP"
echo "🔗 Discovery URL: http://$CURRENT_IP:5002/api/discover"
echo "📱 Mobile Config: http://$CURRENT_IP:5002/api/config/mobile"
echo "🧪 Test Script: python3 /home/anji/IntelliAttend/test-discovery.py"
echo "📄 Info Page: file:///home/anji/IntelliAttend/discovery-info.html"
echo ""
echo "🚀 Next Steps:"
echo "1. Restart your IntelliAttend server"
echo "2. Test the discovery service: python3 test-discovery.py"
echo "3. Use the discovery URL in your mobile app"
echo "4. Your mobile app will now automatically find the server!"
echo ""
echo "💡 Pro Tip: The IP discovery service will automatically detect when your"
echo "   IP address changes and update all endpoints accordingly!"

# Make the script executable
chmod +x /home/anji/IntelliAttend/setup-ip-discovery.sh