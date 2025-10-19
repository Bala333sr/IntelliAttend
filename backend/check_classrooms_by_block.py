#!/usr/bin/env python3
"""
Script to check classroom distribution by block
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_classrooms_by_block():
    """Check classroom distribution by block"""
    
    with app.app_context():
        try:
            result = db.session.execute(text('''
                SELECT building_name, COUNT(*) as classroom_count 
                FROM classrooms 
                GROUP BY building_name 
                ORDER BY building_name
            '''))
            rows = result.fetchall()
            print('Classroom Distribution by Block:')
            print('=' * 50)
            total = 0
            for row in rows:
                print(f"{row[0]:30} | {row[1]:3} classrooms")
                total += row[1]
            print('=' * 50)
            print(f"{'Total':30} | {total:3} classrooms")
            
        except Exception as e:
            print(f"Error checking classroom distribution: {e}")

if __name__ == '__main__':
    check_classrooms_by_block()