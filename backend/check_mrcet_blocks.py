#!/usr/bin/env python3
"""
Script to check the MRCET blocks in the database
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def check_mrcet_blocks():
    """Check the MRCET blocks in the database"""
    
    with app.app_context():
        try:
            print("Checking MRCET blocks in database...")
            
            # Get all blocks
            result = db.session.execute(text("SELECT block_id, block_name, block_code, block_type FROM mrcet_blocks ORDER BY block_name"))
            rows = result.fetchall()
            
            print("\nMRCET Blocks:")
            print("-" * 80)
            print(f"{'ID':<3} | {'Block Name':<30} | {'Code':<10} | {'Type':<15}")
            print("-" * 80)
            for row in rows:
                print(f"{row[0]:<3} | {row[1]:<30} | {row[2]:<10} | {row[3]:<15}")
            
            print(f"\nTotal blocks: {len(rows)}")
                
        except Exception as e:
            print(f"Error checking MRCET blocks: {e}")

if __name__ == '__main__':
    check_mrcet_blocks()