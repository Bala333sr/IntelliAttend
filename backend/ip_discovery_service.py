#!/usr/bin/env python3
"""
IntelliAttend IP Discovery Service
=================================

This module provides automatic IP discovery for mobile apps to connect to
the IntelliAttend server even when the IP address changes dynamically.
"""

import socket
import json
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, request
import subprocess
import netifaces
import qrcode
import io
import base64

class IPDiscoveryService:
    """Service to help mobile apps discover the current server IP"""
    
    def __init__(self, app, port=5002):
        self.app = app
        self.port = port
        self.server_info = {}
        self.update_server_info()
        
        # Add discovery endpoints to the main Flask app
        self.register_endpoints()
        
        # Start background IP monitoring
        self.start_ip_monitor()
    
    def get_local_ip(self):
        """Get the current local IP address"""
        try:
            # Try to connect to Google DNS to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            # Fallback method using netifaces
            try:
                # Get default gateway interface
                gws = netifaces.gateways()
                interface = gws['default'][netifaces.AF_INET][1]
                
                # Get IP from that interface
                addrs = netifaces.ifaddresses(interface)
                ip = addrs[netifaces.AF_INET][0]['addr']
                return ip
            except Exception:
                # Final fallback
                return "127.0.0.1"
    
    def get_network_info(self):
        """Get comprehensive network information"""
        try:
            local_ip = self.get_local_ip()
            hostname = socket.gethostname()
            
            # Get network interfaces
            interfaces = []
            for interface in netifaces.interfaces():
                try:
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            if addr['addr'] != '127.0.0.1':
                                interfaces.append({
                                    'interface': interface,
                                    'ip': addr['addr'],
                                    'netmask': addr.get('netmask', ''),
                                    'broadcast': addr.get('broadcast', '')
                                })
                except Exception:
                    continue
            
            # Get gateway info
            gws = netifaces.gateways()
            gateway = gws.get('default', {}).get(netifaces.AF_INET, ['', ''])[0]
            
            return {
                'primary_ip': local_ip,
                'hostname': hostname,
                'gateway': gateway,
                'interfaces': interfaces,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'primary_ip': '127.0.0.1',
                'hostname': 'localhost',
                'gateway': '',
                'interfaces': [],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def update_server_info(self):
        """Update server configuration information"""
        network_info = self.get_network_info()
        
        self.server_info = {
            'server_name': 'IntelliAttend',
            'version': '1.0.0',
            'port': self.port,
            'api_base': f"http://{network_info['primary_ip']}:{self.port}/api",
            'admin_portal': f"http://{network_info['primary_ip']}:{self.port}/admin",
            'faculty_portal': f"http://{network_info['primary_ip']}:{self.port}",
            'student_portal': f"http://{network_info['primary_ip']}:{self.port}/student",
            'network': network_info,
            'endpoints': {
                'discovery': f"http://{network_info['primary_ip']}:{self.port}/api/discover",
                'health': f"http://{network_info['primary_ip']}:{self.port}/api/health",
                'config': f"http://{network_info['primary_ip']}:{self.port}/api/config"
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def generate_qr_config(self):
        """Generate QR code with server configuration"""
        try:
            config_data = {
                'server_ip': self.server_info['network']['primary_ip'],
                'api_base': self.server_info['api_base'],
                'server_name': self.server_info['server_name'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(json.dumps(config_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 for easy transmission
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            return {
                'qr_data': config_data,
                'qr_image': f"data:image/png;base64,{img_str}",
                'text_config': json.dumps(config_data, indent=2)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def start_ip_monitor(self):
        """Start background thread to monitor IP changes"""
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
                    time.sleep(60)  # Wait longer on error
        
        monitor_thread = threading.Thread(target=monitor_ip, daemon=True)
        monitor_thread.start()
    
    def register_endpoints(self):
        """Register discovery endpoints with the Flask app"""
        
        @self.app.route('/api/discover', methods=['GET'])
        def discover_server():
            """Main discovery endpoint for mobile apps"""
            self.update_server_info()  # Refresh info
            return jsonify({
                'success': True,
                'server': self.server_info,
                'message': 'Server discovered successfully'
            })
        
        @self.app.route('/api/network-scan', methods=['GET'])
        def network_scan():
            """Endpoint to help with network scanning"""
            return jsonify({
                'success': True,
                'scan_info': {
                    'server_ip': self.server_info['network']['primary_ip'],
                    'server_port': self.port,
                    'network_range': self.get_network_range(),
                    'server_identifier': 'IntelliAttend-Server',
                    'discovery_port': self.port
                }
            })
        
        @self.app.route('/api/config/qr', methods=['GET'])
        def config_qr():
            """Generate QR code with server configuration"""
            qr_config = self.generate_qr_config()
            return jsonify({
                'success': True,
                'config': qr_config
            })
        
        @self.app.route('/api/config/mobile', methods=['GET'])
        def mobile_config():
            """Mobile app configuration endpoint"""
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
                            'get_sessions': '/api/sessions',
                            'verify_otp': '/api/verify-otp'
                        },
                        'discovery': '/api/discover'
                    },
                    'websocket_url': f"ws://{self.server_info['network']['primary_ip']}:{self.port}",
                    'last_updated': self.server_info['last_updated']
                }
            })
        
        @self.app.route('/discovery-info', methods=['GET'])
        def discovery_info():
            """Human-readable discovery information"""
            return f"""
            <html>
            <head><title>IntelliAttend Server Discovery</title></head>
            <body>
                <h1>🌐 IntelliAttend Server Discovery</h1>
                <h2>Current Configuration</h2>
                <ul>
                    <li><strong>Server IP:</strong> {self.server_info['network']['primary_ip']}</li>
                    <li><strong>API Base:</strong> <a href="{self.server_info['api_base']}">{self.server_info['api_base']}</a></li>
                    <li><strong>Admin Portal:</strong> <a href="{self.server_info['admin_portal']}">{self.server_info['admin_portal']}</a></li>
                    <li><strong>Last Updated:</strong> {self.server_info['last_updated']}</li>
                </ul>
                
                <h2>🔗 Discovery Endpoints</h2>
                <ul>
                    <li><a href="/api/discover">JSON Discovery</a></li>
                    <li><a href="/api/config/mobile">Mobile Config</a></li>
                    <li><a href="/api/config/qr">QR Code Config</a></li>
                </ul>
                
                <h2>📱 For Mobile Apps</h2>
                <p>Use this URL in your mobile app for auto-discovery:</p>
                <code>{self.server_info['endpoints']['discovery']}</code>
                
                <script>
                    // Auto-refresh every 30 seconds
                    setTimeout(() => location.reload(), 30000);
                </script>
            </body>
            </html>
            """
    
    def get_network_range(self):
        """Get the network range for scanning"""
        try:
            ip = self.get_local_ip()
            # Assume /24 network for simplicity
            base_ip = ".".join(ip.split(".")[:-1])
            return f"{base_ip}.1-254"
        except Exception:
            return "192.168.1.1-254"


# Broadcast service for local network discovery
class BroadcastDiscoveryService:
    """UDP broadcast service for network discovery"""
    
    def __init__(self, port=5002, broadcast_port=5003):
        self.port = port
        self.broadcast_port = broadcast_port
        self.running = False
        
    def start_broadcast(self, server_info):
        """Start UDP broadcast service"""
        def broadcast_loop():
            try:
                # Create UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                
                broadcast_data = {
                    'service': 'IntelliAttend',
                    'server_ip': server_info['network']['primary_ip'],
                    'api_port': self.port,
                    'discovery_port': self.broadcast_port,
                    'timestamp': datetime.now().isoformat()
                }
                
                message = json.dumps(broadcast_data).encode('utf-8')
                
                while self.running:
                    try:
                        # Broadcast to local network
                        sock.sendto(message, ('<broadcast>', self.broadcast_port))
                        time.sleep(10)  # Broadcast every 10 seconds
                    except Exception as e:
                        print(f"Broadcast error: {e}")
                        time.sleep(30)
                        
            except Exception as e:
                print(f"Broadcast service error: {e}")
            finally:
                try:
                    sock.close()
                except:
                    pass
        
        self.running = True
        broadcast_thread = threading.Thread(target=broadcast_loop, daemon=True)
        broadcast_thread.start()
        print(f"🔊 Broadcast discovery service started on port {self.broadcast_port}")
    
    def stop_broadcast(self):
        """Stop the broadcast service"""
        self.running = False


def setup_ip_discovery(app, port=5002):
    """Setup IP discovery service for the Flask app"""
    discovery_service = IPDiscoveryService(app, port)
    
    # Optional: Start broadcast service for local network discovery
    broadcast_service = BroadcastDiscoveryService(port)
    broadcast_service.start_broadcast(discovery_service.server_info)
    
    print(f"🌐 IP Discovery Service initialized")
    print(f"📍 Current IP: {discovery_service.server_info['network']['primary_ip']}")
    print(f"🔗 Discovery URL: {discovery_service.server_info['endpoints']['discovery']}")
    
    return discovery_service, broadcast_service

# Usage example:
"""
# In your main app.py file, add this:

from ip_discovery_service import setup_ip_discovery

# After creating your Flask app:
app = Flask(__name__)

# Setup IP discovery service
discovery_service, broadcast_service = setup_ip_discovery(app, port=5002)

# Your existing routes...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
"""