#!/usr/bin/env python3
"""
Script to check blocks with NULL coordinates
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_null_coordinates():
    """Check blocks with NULL coordinates"""
    
    with app.app_context():
        try:
            # Query blocks with NULL coordinates
            result = db.session.execute(text('''
                SELECT block_name 
                FROM mrcet_blocks 
                WHERE coordinates IS NULL
                ORDER BY block_name
            '''))
            rows = result.fetchall()
            
            print('Blocks with NULL coordinates (not yet updated):')
            print('=' * 50)
            
            for row in rows:
                block_name = row[0]
                print(f"• {block_name}")
                
            print(f"\n📊 Total blocks not yet updated: {len(rows)}")
            
        except Exception as e:
            print(f"❌ Error checking NULL coordinates: {e}")

if __name__ == '__main__':
    check_null_coordinates()