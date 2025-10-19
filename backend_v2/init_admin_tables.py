#!/usr/bin/env python3
"""
Initialize admin tables for IntelliAttend V2
"""

import sqlite3
import bcrypt
from datetime import datetime

def init_admin_tables():
    """Initialize admin tables in the database"""
    conn = sqlite3.connect('intelliattend_v2.db')
    cursor = conn.cursor()
    
    # Create admins table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        admin_id INTEGER PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100),
        role VARCHAR(50) DEFAULT 'admin',
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME
    )
    ''')
    
    # Create timetable_history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS timetable_history (
        history_id INTEGER PRIMARY KEY,
        timetable_id INTEGER,
        action VARCHAR(20),
        old_data TEXT,
        new_data TEXT,
        changed_by INTEGER,
        changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        reason TEXT,
        FOREIGN KEY (timetable_id) REFERENCES timetable(id),
        FOREIGN KEY (changed_by) REFERENCES admins(admin_id)
    )
    ''')
    
    # Create a default admin user if none exists
    cursor.execute("SELECT COUNT(*) FROM admins")
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        # Hash password
        password = "admin123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute('''
        INSERT INTO admins (username, email, password_hash, full_name, role, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ("admin", "admin@intelliattend.com", password_hash, "System Administrator", "super_admin", 1))
        
        print("✅ Created default admin user:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Role: super_admin")
    
    conn.commit()
    conn.close()
    print("✅ Admin tables initialized successfully")

if __name__ == "__main__":
    init_admin_tables()