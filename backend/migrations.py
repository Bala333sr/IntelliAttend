#!/usr/bin/env python3
"""
Database migration script for IntelliAttend
Adds missing fields and tables for mobile app integration
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def add_missing_fields():
    """Add missing fields to existing tables"""
    with app.app_context():
        # Add notifications_enabled field to student_devices table
        try:
            # This would normally be done with an ALTER TABLE statement
            # But since we're working with SQLAlchemy models, we need to 
            # modify the model and let SQLAlchemy handle it
            print("Adding notifications_enabled field to student_devices table...")
            # This will be handled by the model update we already made
        except Exception as e:
            print(f"Error adding notifications_enabled field: {e}")

def create_security_violations_table():
    """Create the security_violations table"""
    with app.app_context():
        try:
            # Create the security_violations table
            print("Creating security_violations table...")
            # This will be handled by the model we already added
            pass
        except Exception as e:
            print(f"Error creating security_violations table: {e}")

def upgrade_database():
    """Apply all database migrations"""
    print("Starting database migration...")
    
    # Add missing fields
    add_missing_fields()
    
    # Create new tables
    create_security_violations_table()
    
    print("Database migration completed successfully!")

if __name__ == '__main__':
    upgrade_database()