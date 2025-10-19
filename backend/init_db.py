#!/usr/bin/env python3
"""
Initialize the database tables for IntelliAttend
"""

from app import app, db

def init_database():
    """Initialize all database tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()