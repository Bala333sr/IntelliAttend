#!/usr/bin/env python3
"""
Script to check MRCET blocks in database
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_blocks():
    """Check MRCET blocks"""
    
    with app.app_context():
        try:
            result = db.session.execute(text('SELECT block_name, block_code, block_type FROM mrcet_blocks ORDER BY block_code'))
            rows = result.fetchall()
            print('MRCET Blocks:')
            print('=' * 80)
            for row in rows:
                print(f"{row[0]:30} | {row[1]:10} | {row[2]}")
            
        except Exception as e:
            print(f"Error checking blocks: {e}")

if __name__ == '__main__':
    check_blocks()