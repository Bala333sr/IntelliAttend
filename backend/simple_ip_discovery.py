#!/usr/bin/env python3
"""
Simple IP Discovery Service for IntelliAttend
===========================================

A lightweight IP discovery service that uses only built-in Python modules.
No external dependencies required.
"""

import socket
import json
import threading
import time
import subprocess
from datetime import datetime
from flask import jsonify, request

class SimpleIPDiscoveryService:
    """Simple IP discovery service using built-in modules only"""
    
    def __init__(self, app, port=5002):
        self.app = app
        self.port = port
        self.server_info = {}
        self.current_ip = None
        self.update_server_info()
        
        # Register endpoints
        self.register_endpoints()
        
        # Start IP monitoring
        self.start_ip_monitor()
    
    def get_local_ip(self):
        """Get local IP address using built-in socket module"""
        try:
            # Method 1: Connect to external address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            try:
                # Method 2: Use hostname
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                if ip != "127.0.0.1":
                    return ip
            except Exception:
                pass
            
            try:
                # Method 3: Use subprocess to get IP
                result = subprocess.run(['hostname', '-I'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    ip = result.stdout.strip().split()[0]
                    return ip
            except Exception:
                pass
            
            # Fallback
            return "127.0.0.1"
    
    def get_network_interfaces(self):
        """Get network interface info using system commands"""
        interfaces = []
        try:
            # Try to get interface info
            result = subprocess.run(['ip', 'addr'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            if result.returncode == 0:
                # Parse basic interface info
                lines = result.stdout.split('\n')
                current_interface = None
                for line in lines:
                    line = line.strip()
                    if line.startswith('inet ') and 'inet 127.0.0.1' not in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            ip_with_prefix = parts[1]
                            ip = ip_with_prefix.split('/')[0]
                            interfaces.append({
                                'ip': ip,
                                'interface': current_interface or 'unknown'
                            })
                    elif ':' in line and 'lo:' not in line:
                        current_interface = line.split(':')[1].strip().split()[0]
        except Exception:
            # Fallback to just the current IP
            current_ip = self.get_local_ip()
            interfaces = [{'ip': current_ip, 'interface': 'default'}]
        
        return interfaces
    
    def update_server_info(self):
        """Update server information"""
        current_ip = self.get_local_ip()
        self.current_ip = current_ip
        
        self.server_info = {
            'server_name': 'IntelliAttend',
            'version': '1.0.0',
            'port': self.port,
            'api_base': f"http://{current_ip}:{self.port}/api",
            'admin_portal': f"http://{current_ip}:{self.port}/admin",
            'faculty_portal': f"http://{current_ip}:{self.port}",
            'student_portal': f"http://{current_ip}:{self.port}/student",
            'network': {
                'primary_ip': current_ip,
                'hostname': socket.gethostname(),
                'interfaces': self.get_network_interfaces(),
                'timestamp': datetime.now().isoformat()
            },
            'endpoints': {
                'discovery': f"http://{current_ip}:{self.port}/api/discover",
                'health': f"http://{current_ip}:{self.port}/api/health",
                'config': f"http://{current_ip}:{self.port}/api/config/mobile"
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def start_ip_monitor(self):
        """Monitor IP changes in background"""
        def monitor_ip():
            last_ip = None
            while True:
                try:
                    current_ip = self.get_local_ip()
                    if current_ip != last_ip:
                        print(f"🌐 IP changed from {last_ip} to {current_ip}")
                        self.update_server_info()
                        last_ip = current_ip
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    print(f"IP monitor error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_ip, daemon=True)
        monitor_thread.start()
    
    def register_endpoints(self):
        """Register discovery endpoints"""
        
        @self.app.route('/api/discover', methods=['GET'])
        def discover_server():
            """Main discovery endpoint"""
            self.update_server_info()  # Refresh
            return jsonify({
                'success': True,
                'server': self.server_info,
                'message': 'Server discovered successfully'
            })
        
        @self.app.route('/api/config/mobile', methods=['GET'])
        def mobile_config():
            """Mobile app configuration"""
            return jsonify({
                'success': True,
                'config': {
                    'api_base_url': self.server_info['api_base'],
                    'server_ip': self.server_info['network']['primary_ip'],
                    'server_port': self.port,
                    'endpoints': {
                        'auth': {
                            'admin_login': '/api/admin/login',
                            'faculty_login': '/api/faculty/login',
                            'student_login': '/api/student/login'
                        },
                        'attendance': {
                            'mark_attendance': '/api/mark-attendance',
                            'sessions': '/api/sessions',
                            'verify_otp': '/api/verify-otp'
                        },
                        'discovery': '/api/discover'
                    },
                    'last_updated': self.server_info['last_updated']
                }
            })
        
        @self.app.route('/api/network-scan', methods=['GET'])
        def network_scan_info():
            """Network scanning information"""
            return jsonify({
                'success': True,
                'scan_info': {
                    'server_ip': self.current_ip,
                    'server_port': self.port,
                    'network_range': self.get_network_range(),
                    'server_identifier': 'IntelliAttend-Server',
                    'discovery_ports': [self.port]
                }
            })
        
        @self.app.route('/api/server-info', methods=['GET'])
        def server_info_page():
            """Server information page"""
            return f"""
            <html>
            <head>
                <title>IntelliAttend Server Info</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                    .info {{ background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                    .endpoint {{ background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0; font-family: monospace; }}
                    code {{ background: #f8f9fa; padding: 4px 8px; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🌐 IntelliAttend Server</h1>
                        <p>Dynamic IP Discovery Service</p>
                    </div>
                    
                    <div class="info">
                        <h2>📍 Current Configuration</h2>
                        <ul>
                            <li><strong>Server IP:</strong> {self.current_ip}</li>
                            <li><strong>Port:</strong> {self.port}</li>
                            <li><strong>API Base:</strong> {self.server_info['api_base']}</li>
                            <li><strong>Last Updated:</strong> {self.server_info['last_updated']}</li>
                        </ul>
                    </div>
                    
                    <div class="info">
                        <h2>🔗 Discovery Endpoints</h2>
                        <div class="endpoint">
                            <strong>Main Discovery:</strong> <a href="/api/discover">/api/discover</a>
                        </div>
                        <div class="endpoint">
                            <strong>Mobile Config:</strong> <a href="/api/config/mobile">/api/config/mobile</a>
                        </div>
                        <div class="endpoint">
                            <strong>Network Scan:</strong> <a href="/api/network-scan">/api/network-scan</a>
                        </div>
                    </div>
                    
                    <div class="info">
                        <h2>📱 Mobile App Integration</h2>
                        <p>Use this URL in your mobile app:</p>
                        <code>{self.server_info['endpoints']['discovery']}</code>
                        
                        <h3>Example Usage:</h3>
                        <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
// React Native / JavaScript
const response = await fetch('{self.server_info['endpoints']['discovery']}');
const config = await response.json();
const apiBaseUrl = config.server.api_base;

// Use apiBaseUrl for all subsequent API calls
const loginResponse = await fetch(`${{apiBaseUrl}}/student/login`, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{ email: 'student@example.com', password: 'password' }})
}});
                        </pre>
                    </div>
                    
                    <script>
                        // Auto-refresh every 60 seconds
                        setTimeout(() => location.reload(), 60000);
                    </script>
                </div>
            </body>
            </html>
            """
    
    def get_network_range(self):
        """Get network range for scanning"""
        try:
            ip = self.current_ip
            # Assume /24 network
            base_ip = ".".join(ip.split(".")[:-1])
            return f"{base_ip}.1-254"
        except Exception:
            return "192.168.1.1-254"

def setup_simple_ip_discovery(app, port=5002):
    """Setup simple IP discovery service"""
    discovery_service = SimpleIPDiscoveryService(app, port)
    
    print(f"🌐 Simple IP Discovery Service initialized")
    print(f"📍 Current IP: {discovery_service.current_ip}")
    print(f"🔗 Discovery URL: {discovery_service.server_info['endpoints']['discovery']}")
    print(f"📱 Mobile Config: {discovery_service.server_info['endpoints']['config']}")
    
    return discovery_service

# Example usage:
"""
# In your main app.py file, add this:

from simple_ip_discovery import setup_simple_ip_discovery

# After creating your Flask app:
app = Flask(__name__)

# Setup simple IP discovery service
discovery_service = setup_simple_ip_discovery(app, port=5002)

# Your existing routes...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
"""