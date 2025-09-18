#!/usr/bin/env python3
"""
QR Code Generation Module for INTELLIATTEND
Handles dynamic QR code generation with 5-second refresh intervals
"""

import os
import json
import time
import secrets
import threading
from datetime import datetime, timedelta
import qrcode
from PIL import Image, ImageDraw, ImageFont
import hashlib
import base64

class QRCodeManager:
    """Manages QR code generation and lifecycle"""
    
    def __init__(self, config):
        self.config = config
        self.active_sessions = {}
        self.qr_history = {}
        
        # Ensure directories exist (Centralized QR_DATA structure)
        os.makedirs(self.config.get('QR_TOKENS_FOLDER', 'QR_DATA/tokens'), exist_ok=True)
        os.makedirs(self.config.get('QR_KEYS_FOLDER', 'QR_DATA/keys'), exist_ok=True)
        os.makedirs(self.config.get('QR_ARCHIVE_FOLDER', 'QR_DATA/archive'), exist_ok=True)
    
    def generate_secure_token(self, session_id, timestamp, sequence):
        """Generate a cryptographically secure token"""
        data = f"{session_id}:{timestamp}:{sequence}:{secrets.token_hex(16)}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def create_qr_data(self, session_id, base_token, sequence):
        """Create QR code data payload"""
        timestamp = int(time.time())
        secure_token = self.generate_secure_token(session_id, timestamp, sequence)
        
        qr_payload = {
            'v': '1.0',  # Version
            'sid': session_id,  # Session ID
            'tok': base_token,  # Base token
            'seq': sequence,  # Sequence number
            'ts': timestamp,  # Timestamp
            'sec': secure_token,  # Security token
            'exp': timestamp + self.config.get('QR_REFRESH_INTERVAL', 5) + 2  # Expiry with 2s buffer
        }
        
        return json.dumps(qr_payload, separators=(',', ':'))
    
    def create_qr_image(self, data, session_id, sequence):
        """Create QR code image with styling"""
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=self.config.get('QR_CODE_SIZE', 10),
                border=self.config.get('QR_CODE_BORDER', 4),
            )
            
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to RGB for additional styling
            img = img.convert('RGB')
            
            # Add timestamp and sequence watermark
            draw = ImageDraw.Draw(img)
            
            try:
                # Try to use a font (might not be available on all systems)
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            # Add sequence number in corner
            watermark_text = f"#{sequence:03d}"
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Position in bottom right
            x = img.width - text_width - 5
            y = img.height - text_height - 5
            
            # Add semi-transparent background
            draw.rectangle([x-2, y-2, x+text_width+2, y+text_height+2], fill=(255, 255, 255, 200))
            draw.text((x, y), watermark_text, fill=(128, 128, 128), font=font)
            
            return img
            
        except Exception as e:
            print(f"Error creating QR image: {e}")
            return None
    
    def save_qr_image(self, img, session_id, sequence):
        """Save QR image to multiple locations"""
        if not img:
            return None
            
        try:
            timestamp = int(time.time())
            filename = f"qr_s{session_id}_seq{sequence:03d}_{timestamp}.png"
            
            # Save to centralized QR_DATA folder
            web_path = os.path.join(self.config.get('QR_TOKENS_FOLDER', 'QR_DATA/tokens'), filename)
            img.save(web_path, 'PNG', optimize=True)
            
            return filename
            
        except Exception as e:
            print(f"Error saving QR image: {e}")
            return None
    
    def save_secret_key(self, session_id, sequence, secret_data):
        """Save secret key for validation"""
        try:
            key_filename = f"key_s{session_id}_seq{sequence:03d}.json"
            key_path = os.path.join(self.config.get('QR_KEYS_FOLDER', 'QR_DATA/keys'), key_filename)
            
            with open(key_path, 'w') as f:
                json.dump(secret_data, f, indent=2)
                
            return key_filename
            
        except Exception as e:
            print(f"Error saving secret key: {e}")
            return None
    
    def generate_qr_sequence(self, session_id, base_token, duration_seconds):
        """Generate QR code sequence for a session"""
        
        session_info = {
            'session_id': session_id,
            'base_token': base_token,
            'start_time': datetime.utcnow(),
            'end_time': datetime.utcnow() + timedelta(seconds=duration_seconds),
            'sequence': 0,
            'current_qr': None,
            'qr_files': [],
            'active': True
        }
        
        self.active_sessions[session_id] = session_info
        self.qr_history[session_id] = []
        
        def qr_generation_loop():
            """Main QR generation loop"""
            print(f"🎯 Starting QR generation for session {session_id}")
            print(f"📅 Duration: {duration_seconds} seconds")
            print(f"🔄 Refresh interval: {self.config.get('QR_REFRESH_INTERVAL', 5)} seconds")
            
            while (datetime.utcnow() < session_info['end_time'] and 
                   session_info['active'] and 
                   session_id in self.active_sessions):
                
                try:
                    # Generate QR data
                    sequence = session_info['sequence']
                    qr_data = self.create_qr_data(session_id, base_token, sequence)
                    
                    # Create QR image
                    img = self.create_qr_image(qr_data, session_id, sequence)
                    
                    if img:
                        # Save QR image
                        filename = self.save_qr_image(img, session_id, sequence)
                        
                        if filename:
                            # Save secret key for validation
                            secret_data = {
                                'session_id': session_id,
                                'base_token': base_token,
                                'sequence': sequence,
                                'timestamp': int(time.time()),
                                'qr_data': qr_data,
                                'filename': filename,
                                'expires_at': (datetime.utcnow() + 
                                             timedelta(seconds=self.config.get('QR_REFRESH_INTERVAL', 5) + 2)).isoformat()
                            }
                            
                            key_filename = self.save_secret_key(session_id, sequence, secret_data)
                            
                            # Update session info
                            session_info['current_qr'] = filename
                            session_info['sequence'] += 1
                            session_info['qr_files'].append(filename)
                            
                            # Add to history
                            self.qr_history[session_id].append({
                                'sequence': sequence,
                                'filename': filename,
                                'key_file': key_filename,
                                'generated_at': datetime.utcnow().isoformat(),
                                'qr_data_hash': hashlib.md5(qr_data.encode()).hexdigest()
                            })
                            
                            print(f"✅ Generated QR #{sequence + 1} for session {session_id}: {filename}")
                        else:
                            print(f"❌ Failed to save QR image for session {session_id}, sequence {sequence}")
                    else:
                        print(f"❌ Failed to create QR image for session {session_id}, sequence {sequence}")
                    
                    # Wait for next refresh
                    time.sleep(self.config.get('QR_REFRESH_INTERVAL', 5))
                    
                except Exception as e:
                    print(f"❌ Error in QR generation loop for session {session_id}: {e}")
                    time.sleep(1)  # Short delay before retry
            
            # Mark session as completed
            session_info['active'] = False
            session_info['end_time'] = datetime.utcnow()
            
            print(f"🏁 QR generation completed for session {session_id}")
            print(f"📊 Total QR codes generated: {session_info['sequence']}")
        
        # Start generation in background thread
        thread = threading.Thread(target=qr_generation_loop, daemon=True)
        thread.start()
        
        return session_info
    
    def get_current_qr(self, session_id):
        """Get current QR code for a session"""
        session_info = self.active_sessions.get(session_id)
        
        if not session_info:
            return None
        
        if not session_info['active'] or datetime.utcnow() > session_info['end_time']:
            return None
        
        return {
            'filename': session_info.get('current_qr'),
            'sequence': session_info['sequence'],
            'expires_at': session_info['end_time'].isoformat(),
            'active': session_info['active']
        }
    
    def stop_session(self, session_id):
        """Stop QR generation for a session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['active'] = False
            print(f"🛑 Stopped QR generation for session {session_id}")
            return True
        return False
    
    def get_session_history(self, session_id):
        """Get QR generation history for a session"""
        return self.qr_history.get(session_id, [])
    
    def cleanup_old_files(self, max_age_hours=24):
        """Clean up old QR files"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            # Clean up QR token files from centralized location
            qr_dir = self.config.get('QR_TOKENS_FOLDER', 'QR_DATA/tokens')
            for filename in os.listdir(qr_dir):
                if filename.startswith('qr_s') and filename.endswith('.png'):
                    file_path = os.path.join(qr_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time < cutoff_time:
                        os.remove(file_path)
            
            # Clean up key files from centralized location
            key_dir = self.config.get('QR_KEYS_FOLDER', 'QR_DATA/keys')
            for filename in os.listdir(key_dir):
                if filename.startswith('key_s') and filename.endswith('.json'):
                    file_path = os.path.join(key_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time < cutoff_time:
                        os.remove(file_path)
            
            print(f"🧹 Cleaned up files older than {max_age_hours} hours")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

# ============================================================================
# STANDALONE SCRIPT FUNCTIONALITY
# ============================================================================

def generate_test_qr(session_id=1, duration=120):
    """Generate a test QR sequence (for testing purposes)"""
    config = {
        'QR_CODE_SIZE': 10,
        'QR_CODE_BORDER': 4,
        'QR_REFRESH_INTERVAL': 5,
        'QR_TOKENS_FOLDER': 'QR_DATA/tokens',
        'QR_KEYS_FOLDER': 'QR_DATA/keys'
    }
    
    manager = QRCodeManager(config)
    base_token = secrets.token_urlsafe(32)
    
    print(f"🚀 Starting test QR generation...")
    print(f"Session ID: {session_id}")
    print(f"Base Token: {base_token}")
    print(f"Duration: {duration} seconds")
    print("=" * 50)
    
    session_info = manager.generate_qr_sequence(session_id, base_token, duration)
    
    # Wait for completion
    while session_info['active']:
        time.sleep(1)
    
    print("=" * 50)
    print("🎉 Test QR generation completed!")
    
    history = manager.get_session_history(session_id)
    print(f"📊 Generated {len(history)} QR codes")
    
    for entry in history[-3:]:  # Show last 3
        print(f"  - Sequence {entry['sequence']}: {entry['filename']}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            session_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            duration = int(sys.argv[3]) if len(sys.argv) > 3 else 30
            generate_test_qr(session_id, duration)
        else:
            print("Usage: python generate_qr.py test [session_id] [duration_seconds]")
    else:
        print("QR Code Manager - Import this module to use in your Flask app")
        print("For testing: python generate_qr.py test [session_id] [duration]")