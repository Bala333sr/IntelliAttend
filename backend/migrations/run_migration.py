#!/usr/bin/env python3
"""
IntelliAttend - Migration Runner
Executes database migrations for registration system tables
"""

import os
import sys

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from app import (
    WiFiNetwork, 
    BluetoothBeacon, 
    RegistrationAuditLog, 
    DeviceApprovalQueue, 
    StudentRegistrationQueue
)
from sqlalchemy import text, inspect

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def run_migration():
    """Run the database migration to create new tables"""
    
    print("=" * 80)
    print("IntelliAttend Registration System - Database Migration")
    print("=" * 80)
    print()
    
    with app.app_context():
        # Get database type
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        is_sqlite = 'sqlite' in db_url
        is_mysql = 'mysql' in db_url
        
        print(f"Database Type: {'SQLite' if is_sqlite else 'MySQL' if is_mysql else 'Unknown'}")
        print(f"Database URL: {db_url.split('@')[-1] if '@' in db_url else db_url}")
        print()
        
        # Check which tables already exist
        tables_to_create = [
            'wifi_networks',
            'bluetooth_beacons',
            'registration_audit_log',
            'device_approval_queue',
            'student_registration_queue'
        ]
        
        print("Checking existing tables...")
        existing_tables = []
        for table in tables_to_create:
            exists = check_table_exists(table)
            status = "✓ EXISTS" if exists else "✗ MISSING"
            print(f"  {table:30s} {status}")
            if exists:
                existing_tables.append(table)
        print()
        
        if len(existing_tables) == len(tables_to_create):
            print("✓ All tables already exist. No migration needed.")
            return True
        
        # Create tables using SQLAlchemy
        print("Creating new tables...")
        try:
            # Create all tables defined in models
            db.create_all()
            print("✓ Tables created successfully!")
            print()
            
            # Verify tables were created
            print("Verifying table creation...")
            all_created = True
            for table in tables_to_create:
                exists = check_table_exists(table)
                status = "✓ CREATED" if exists else "✗ FAILED"
                print(f"  {table:30s} {status}")
                if not exists:
                    all_created = False
            print()
            
            if all_created:
                print("=" * 80)
                print("✓ Migration completed successfully!")
                print("=" * 80)
                return True
            else:
                print("=" * 80)
                print("✗ Migration completed with errors. Some tables were not created.")
                print("=" * 80)
                return False
                
        except Exception as e:
            print(f"✗ Error during migration: {e}")
            import traceback
            traceback.print_exc()
            return False

def verify_schema():
    """Verify the schema of created tables"""
    
    print()
    print("=" * 80)
    print("Schema Verification")
    print("=" * 80)
    print()
    
    with app.app_context():
        inspector = inspect(db.engine)
        
        tables_to_verify = [
            'wifi_networks',
            'bluetooth_beacons',
            'registration_audit_log',
            'device_approval_queue',
            'student_registration_queue'
        ]
        
        for table_name in tables_to_verify:
            if not check_table_exists(table_name):
                print(f"✗ Table {table_name} does not exist. Skipping verification.")
                continue
            
            print(f"Table: {table_name}")
            print("-" * 80)
            
            # Get columns
            columns = inspector.get_columns(table_name)
            print(f"Columns ({len(columns)}):")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col['default'] else ""
                print(f"  - {col['name']:25s} {str(col['type']):20s} {nullable}{default}")
            
            # Get foreign keys
            fks = inspector.get_foreign_keys(table_name)
            if fks:
                print(f"Foreign Keys ({len(fks)}):")
                for fk in fks:
                    print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print(f"Indexes ({len(indexes)}):")
                for idx in indexes:
                    unique = "UNIQUE" if idx['unique'] else ""
                    print(f"  - {idx['name']:30s} ({', '.join(idx['column_names'])}) {unique}")
            
            print()

def show_sample_queries():
    """Show sample queries for testing the new tables"""
    
    print("=" * 80)
    print("Sample Queries for Testing")
    print("=" * 80)
    print()
    
    print("1. Count records in each new table:")
    print("-" * 80)
    
    with app.app_context():
        try:
            wifi_count = WiFiNetwork.query.count()
            beacon_count = BluetoothBeacon.query.count()
            audit_count = RegistrationAuditLog.query.count()
            device_queue_count = DeviceApprovalQueue.query.count()
            student_queue_count = StudentRegistrationQueue.query.count()
            
            print(f"  wifi_networks:              {wifi_count} records")
            print(f"  bluetooth_beacons:          {beacon_count} records")
            print(f"  registration_audit_log:     {audit_count} records")
            print(f"  device_approval_queue:      {device_queue_count} records")
            print(f"  student_registration_queue: {student_queue_count} records")
            print()
            
        except Exception as e:
            print(f"✗ Error querying tables: {e}")
            print()

def main():
    """Main migration function"""
    
    # Run migration
    success = run_migration()
    
    if success:
        # Verify schema
        verify_schema()
        
        # Show sample queries
        show_sample_queries()
        
        print("=" * 80)
        print("Next Steps:")
        print("=" * 80)
        print("1. Test the validators module: python -c 'from validators import *; print(validate_gps_coordinates(37.7749, -122.4194))'")
        print("2. Implement the classroom registration API endpoint")
        print("3. Implement the student bulk import API endpoint")
        print("4. Test the APIs with Postman or curl")
        print()
        
        return 0
    else:
        print()
        print("✗ Migration failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
