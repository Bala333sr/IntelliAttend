#!/usr/bin/env python3
"""
Database Setup Script for INTELLIATTEND
This script creates the database, tables, and sample data.
"""

import pymysql
import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Try empty password first, change if needed
    'charset': 'utf8mb4'
}

DATABASE_NAME = 'IntelliAttend_DataBase'

def create_database():
    """Create the database if it doesn't exist"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ Database '{DATABASE_NAME}' created successfully")
        
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False

def execute_sql_file():
    """Execute the SQL schema file"""
    try:
        # Update DB_CONFIG to include the database
        db_config_with_db = DB_CONFIG.copy()
        db_config_with_db['database'] = DATABASE_NAME
        
        connection = pymysql.connect(**db_config_with_db)
        cursor = connection.cursor()
        
        # Read and execute SQL file
        sql_file_path = os.path.join(os.path.dirname(__file__), 'database_schema.sql')
        
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split by delimiter and execute each statement
        statements = sql_content.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except Exception as e:
                    if "Duplicate entry" not in str(e):  # Ignore duplicate entries
                        print(f"Warning: {e}")
        
        connection.commit()
        print("✓ Database schema created successfully")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ Error executing SQL file: {e}")
        return False

def create_sample_data():
    """Create additional sample data for testing"""
    try:
        db_config_with_db = DB_CONFIG.copy()
        db_config_with_db['database'] = DATABASE_NAME
        
        connection = pymysql.connect(**db_config_with_db)
        cursor = connection.cursor()
        
        # Hash passwords for sample users
        faculty_password = generate_password_hash('faculty123')
        student_password = generate_password_hash('student123')
        
        # Update password hashes
        cursor.execute("UPDATE faculty SET password_hash = %s", (faculty_password,))
        cursor.execute("UPDATE students SET password_hash = %s", (student_password,))
        
        # Create sample attendance session
        session_data = {
            'class_id': 1,
            'faculty_id': 1,
            'session_date': datetime.now().date(),
            'start_time': datetime.now(),
            'qr_token': 'sample_token_123',
            'qr_secret_key': 'sample_secret_key_123',
            'qr_expires_at': datetime.now() + timedelta(minutes=2),
            'status': 'active'
        }
        
        cursor.execute("""
            INSERT INTO attendance_sessions (class_id, faculty_id, session_date, start_time, qr_token, qr_secret_key, qr_expires_at, status)
            VALUES (%(class_id)s, %(faculty_id)s, %(session_date)s, %(start_time)s, %(qr_token)s, %(qr_secret_key)s, %(qr_expires_at)s, %(status)s)
            ON DUPLICATE KEY UPDATE qr_token = VALUES(qr_token)
        """, session_data)
        
        # Create sample device records
        devices_data = [
            {
                'student_id': 1,
                'device_uuid': 'DEVICE_001_ALICE',
                'device_name': 'Alice iPhone',
                'device_type': 'ios',
                'device_model': 'iPhone 14',
                'os_version': '17.0',
                'app_version': '1.0.0',
                'biometric_enabled': True,
                'location_permission': True,
                'bluetooth_permission': True
            },
            {
                'student_id': 2,
                'device_uuid': 'DEVICE_002_BOB',
                'device_name': 'Bob Android',
                'device_type': 'android',
                'device_model': 'Samsung Galaxy S23',
                'os_version': '14.0',
                'app_version': '1.0.0',
                'biometric_enabled': True,
                'location_permission': True,
                'bluetooth_permission': True
            }
        ]
        
        for device in devices_data:
            cursor.execute("""
                INSERT INTO student_devices (student_id, device_uuid, device_name, device_type, device_model, os_version, app_version, biometric_enabled, location_permission, bluetooth_permission)
                VALUES (%(student_id)s, %(device_uuid)s, %(device_name)s, %(device_type)s, %(device_model)s, %(os_version)s, %(app_version)s, %(biometric_enabled)s, %(location_permission)s, %(bluetooth_permission)s)
                ON DUPLICATE KEY UPDATE device_name = VALUES(device_name)
            """, device)
        
        connection.commit()
        print("✓ Sample data created successfully")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        return False

def verify_setup():
    """Verify that the database setup was successful"""
    try:
        db_config_with_db = DB_CONFIG.copy()
        db_config_with_db['database'] = DATABASE_NAME
        
        connection = pymysql.connect(**db_config_with_db)
        cursor = connection.cursor()
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"\n✓ Database setup verification:")
        print(f"  - Total tables created: {len(tables)}")
        
        # Check sample data
        cursor.execute("SELECT COUNT(*) FROM faculty")
        faculty_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM classes")
        class_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM classrooms")
        classroom_count = cursor.fetchone()[0]
        
        print(f"  - Faculty records: {faculty_count}")
        print(f"  - Student records: {student_count}")
        print(f"  - Class records: {class_count}")
        print(f"  - Classroom records: {classroom_count}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error verifying setup: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting INTELLIATTEND Database Setup...")
    print("=" * 50)
    
    # Step 1: Create database
    if not create_database():
        sys.exit(1)
    
    # Step 2: Execute SQL schema
    if not execute_sql_file():
        sys.exit(1)
    
    # Step 3: Create sample data
    if not create_sample_data():
        sys.exit(1)
    
    # Step 4: Verify setup
    if not verify_setup():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Database setup completed successfully!")
    print("\nTo start the application, run: python backend/app.py")
    print("\nDefault Credentials:")
    print("Faculty: john.smith@university.edu / faculty123")
    print("Student: alice.williams@student.edu / student123")

if __name__ == "__main__":
    main()