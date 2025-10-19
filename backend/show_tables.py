#!/usr/bin/env python3
"""
Script to show all tables
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def show_tables():
    """Show all tables"""
    
    with app.app_context():
        try:
            print("Showing all tables...")
            
            # Show tables
            show_sql = "SHOW TABLES"
            result = db.session.execute(text(show_sql))
            rows = result.fetchall()
            
            print("Tables:")
            for row in rows:
                print(f"  {row[0]}")
            
        except Exception as e:
            print(f"❌ Error showing tables: {e}")

if __name__ == '__main__':
    show_tables()