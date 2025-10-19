#!/usr/bin/env python3
"""
Script to check classes table
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_classes():
    """Check classes table"""
    
    with app.app_context():
        try:
            result = db.session.execute(text('SELECT COUNT(*) FROM classes'))
            count = result.fetchone()[0]
            print(f'Classes count: {count}')
            
            # Check some sample data
            if count > 0:
                result = db.session.execute(text('SELECT class_id, class_name, classroom_id FROM classes LIMIT 5'))
                rows = result.fetchall()
                print("\nSample classes data:")
                for row in rows:
                    print(f"  {row[0]}: {row[1]} (classroom_id: {row[2]})")
            
        except Exception as e:
            print(f"Error checking classes table: {e}")

if __name__ == '__main__':
    check_classes()