#!/usr/bin/env python3
"""
Database upgrade script for IntelliAttend
Adds missing fields and tables for mobile app integration
"""

import sqlite3
import os
import sys

# Get the database path
def get_db_path():
    """Get the database path"""
    # Try to find the database file
    possible_paths = [
        '../instance/intelliattend.db',
        'instance/intelliattend.db',
        '../database/intelliattend.db',
        'database/intelliattend.db',
        'intelliattend.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If no existing database found, use a default location
    return '../instance/intelliattend.db'

def upgrade_database():
    """Upgrade the database schema"""
    db_path = get_db_path()
    print(f"Upgrading database at: {db_path}")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add notifications_enabled column to student_devices table if it doesn't exist
        try:
            cursor.execute("ALTER TABLE student_devices ADD COLUMN notifications_enabled BOOLEAN DEFAULT 1")
            print("Added notifications_enabled column to student_devices table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("notifications_enabled column already exists in student_devices table")
            else:
                print(f"Error adding notifications_enabled column: {e}")
        
        # Create security_violations table if it doesn't exist
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_violations (
                    violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    violation_type TEXT NOT NULL,
                    details TEXT,
                    device_info TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_resolved BOOLEAN DEFAULT 0,
                    resolved_at DATETIME,
                    resolved_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students (student_id)
                )
            """)
            print("Created security_violations table")
        except sqlite3.Error as e:
            print(f"Error creating security_violations table: {e}")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("Database upgrade completed successfully!")
        
    except Exception as e:
        print(f"Error upgrading database: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = upgrade_database()
    if not success:
        sys.exit(1)