#!/usr/bin/env python3
"""
QR Data Management Script for INTELLIATTEND
Centralized QR code and key management in QR_DATA folder
"""

import os
import json
import shutil
from datetime import datetime, timedelta

class QRDataManager:
    """Manages centralized QR data in QR_DATA folder"""
    
    def __init__(self, base_path="QR_DATA"):
        self.base_path = base_path
        self.tokens_path = os.path.join(base_path, "tokens")
        self.keys_path = os.path.join(base_path, "keys") 
        self.archive_path = os.path.join(base_path, "archive")
        
        # Ensure directories exist
        os.makedirs(self.tokens_path, exist_ok=True)
        os.makedirs(self.keys_path, exist_ok=True)
        os.makedirs(self.archive_path, exist_ok=True)
    
    def list_qr_data(self):
        """List all QR data files"""
        print("📊 QR Data Inventory")
        print("=" * 50)
        
        # List tokens
        token_files = [f for f in os.listdir(self.tokens_path) if f.endswith('.png')]
        print(f"\n🎯 QR Tokens ({len(token_files)} files):")
        for token_file in sorted(token_files):
            file_path = os.path.join(self.tokens_path, token_file)
            file_size = os.path.getsize(file_path)
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            print(f"  📄 {token_file} ({file_size:,} bytes) - {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # List keys
        key_files = [f for f in os.listdir(self.keys_path) if f.endswith('.json')]
        print(f"\n🔑 Secret Keys ({len(key_files)} files):")
        for key_file in sorted(key_files):
            file_path = os.path.join(self.keys_path, key_file)
            file_size = os.path.getsize(file_path)
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            
            # Read key data
            try:
                with open(file_path, 'r') as f:
                    key_data = json.load(f)
                session_id = key_data.get('session_id', 'Unknown')
                sequence = key_data.get('sequence', 'Unknown')
                print(f"  🔐 {key_file} - Session {session_id}, Seq {sequence} ({file_size:,} bytes)")
            except:
                print(f"  🔐 {key_file} ({file_size:,} bytes) - {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # List archive
        archive_files = os.listdir(self.archive_path)
        print(f"\n📦 Archived Files ({len(archive_files)} files):")
        for archive_file in sorted(archive_files):
            file_path = os.path.join(self.archive_path, archive_file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                print(f"  📁 {archive_file} ({file_size:,} bytes) - {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def cleanup_old_files(self, max_age_hours=24):
        """Archive old QR files"""
        print(f"\n🧹 Cleaning up files older than {max_age_hours} hours...")
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        archived_count = 0
        
        # Process tokens
        for filename in os.listdir(self.tokens_path):
            if filename.endswith('.png'):
                file_path = os.path.join(self.tokens_path, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_time:
                    # Move to archive
                    archive_path = os.path.join(self.archive_path, f"archived_{filename}")
                    shutil.move(file_path, archive_path)
                    print(f"  📦 Archived: {filename}")
                    archived_count += 1
        
        # Process keys
        for filename in os.listdir(self.keys_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.keys_path, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_time:
                    # Move to archive
                    archive_path = os.path.join(self.archive_path, f"archived_{filename}")
                    shutil.move(file_path, archive_path)
                    print(f"  📦 Archived: {filename}")
                    archived_count += 1
        
        print(f"✅ Archived {archived_count} files")
    
    def verify_qr_pairs(self):
        """Verify that each QR token has a corresponding key"""
        print("\n🔍 Verifying QR Token-Key Pairs...")
        
        token_files = set(f.replace('.png', '') for f in os.listdir(self.tokens_path) if f.endswith('.png'))
        key_files = set(f.replace('.json', '') for f in os.listdir(self.keys_path) if f.endswith('.json'))
        
        # Check for tokens without keys
        orphaned_tokens = []
        for token in token_files:
            # Convert token filename to expected key filename
            if token.startswith('qr_s'):
                # Extract session and sequence from token filename
                parts = token.split('_')
                if len(parts) >= 3:
                    session_part = parts[1]  # s999
                    seq_part = parts[2]      # seq000
                    expected_key = f"key_{session_part}_{seq_part}"
                    
                    if expected_key not in key_files:
                        orphaned_tokens.append(token + '.png')
        
        # Check for keys without tokens  
        orphaned_keys = []
        for key in key_files:
            if key.startswith('key_s'):
                # Convert key filename to expected token filename pattern
                parts = key.split('_')
                if len(parts) >= 3:
                    session_part = parts[1]  # s999
                    seq_part = parts[2]      # seq000
                    # Token files have timestamp suffix, so check by prefix
                    expected_prefix = f"qr_{session_part}_{seq_part}"
                    
                    found_token = False
                    for token in token_files:
                        if token.startswith(expected_prefix):
                            found_token = True
                            break
                    
                    if not found_token:
                        orphaned_keys.append(key + '.json')
        
        if orphaned_tokens:
            print(f"  ⚠️  Orphaned tokens (no key): {orphaned_tokens}")
        else:
            print("  ✅ All tokens have corresponding keys")
        
        if orphaned_keys:
            print(f"  ⚠️  Orphaned keys (no token): {orphaned_keys}")
        else:
            print("  ✅ All keys have corresponding tokens")
    
    def show_storage_stats(self):
        """Show storage statistics"""
        print("\n📈 Storage Statistics")
        print("=" * 30)
        
        # Calculate sizes
        tokens_size = sum(os.path.getsize(os.path.join(self.tokens_path, f)) 
                         for f in os.listdir(self.tokens_path) if os.path.isfile(os.path.join(self.tokens_path, f)))
        
        keys_size = sum(os.path.getsize(os.path.join(self.keys_path, f)) 
                       for f in os.listdir(self.keys_path) if os.path.isfile(os.path.join(self.keys_path, f)))
        
        archive_size = sum(os.path.getsize(os.path.join(self.archive_path, f)) 
                          for f in os.listdir(self.archive_path) if os.path.isfile(os.path.join(self.archive_path, f)))
        
        total_size = tokens_size + keys_size + archive_size
        
        print(f"Tokens:  {tokens_size:8,} bytes ({tokens_size/1024:.1f} KB)")
        print(f"Keys:    {keys_size:8,} bytes ({keys_size/1024:.1f} KB)")  
        print(f"Archive: {archive_size:8,} bytes ({archive_size/1024:.1f} KB)")
        print(f"Total:   {total_size:8,} bytes ({total_size/1024:.1f} KB)")

def main():
    """Main function"""
    print("🗂️  QR Data Manager - INTELLIATTEND")
    print("=" * 50)
    
    manager = QRDataManager()
    
    # Show current data
    manager.list_qr_data()
    
    # Verify pairs
    manager.verify_qr_pairs()
    
    # Show statistics
    manager.show_storage_stats()
    
    # Optional cleanup (uncomment to enable)
    # manager.cleanup_old_files(24)

if __name__ == "__main__":
    main()