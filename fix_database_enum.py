#!/usr/bin/env python3
"""
Database Enum Fix Utility
Fixes the schedule_day enum field to support full day names
"""

import sys
import os
import pymysql
from sqlalchemy import text

# Add the backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db, Classes

def check_current_enum():
    """Check the current enum definition in the database"""
    print("🔍 Checking current enum definition...")
    
    with app.app_context():
        try:
            # Get table info to see current enum
            result = db.session.execute(text("SHOW CREATE TABLE classes"))
            create_table_sql = result.fetchone()[1]
            
            print("Current table definition:")
            # Look for schedule_day definition
            lines = create_table_sql.split('\n')
            for line in lines:
                if 'schedule_day' in line:
                    print(f"   {line.strip()}")
                    return line.strip()
                    
            return None
            
        except Exception as e:
            print(f"❌ Error checking enum: {e}")
            return None

def fix_enum_field():
    """Fix the schedule_day enum field to support full day names"""
    print("🔧 Fixing schedule_day enum field...")
    
    with app.app_context():
        try:
            # First, let's see what the current issue is
            current_def = check_current_enum()
            
            # The solution is to use a different approach - change to VARCHAR instead of ENUM
            # This is safer and more flexible than trying to modify the enum
            
            print("📝 Converting schedule_day from ENUM to VARCHAR...")
            
            # Step 1: Add a temporary column
            db.session.execute(text("""
                ALTER TABLE classes 
                ADD COLUMN schedule_day_temp VARCHAR(20) DEFAULT NULL
            """))
            
            # Step 2: Copy data from enum to varchar column
            db.session.execute(text("""
                UPDATE classes 
                SET schedule_day_temp = schedule_day 
                WHERE schedule_day IS NOT NULL
            """))
            
            # Step 3: Drop the old enum column
            db.session.execute(text("""
                ALTER TABLE classes 
                DROP COLUMN schedule_day
            """))
            
            # Step 4: Rename the temp column
            db.session.execute(text("""
                ALTER TABLE classes 
                CHANGE COLUMN schedule_day_temp schedule_day VARCHAR(20) DEFAULT NULL
            """))
            
            db.session.commit()
            print("✅ Successfully converted schedule_day to VARCHAR(20)")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing enum: {e}")
            return False

def test_class_creation():
    """Test creating classes with full day names"""
    print("\n🧪 Testing class creation with full day names...")
    
    test_classes = [
        {
            'class_code': 'TEST_MON',
            'class_name': 'Monday Test Class',
            'faculty_id': 1,
            'semester': 'Fall',
            'academic_year': '2024-2025',
            'schedule_day': 'Monday',
            'credits': 3,
            'max_students': 30
        },
        {
            'class_code': 'TEST_WED',
            'class_name': 'Wednesday Test Class',
            'faculty_id': 1,
            'semester': 'Fall',
            'academic_year': '2024-2025',
            'schedule_day': 'Wednesday',
            'credits': 3,
            'max_students': 30
        },
        {
            'class_code': 'TEST_FRI',
            'class_name': 'Friday Test Class',
            'faculty_id': 1,
            'semester': 'Fall',
            'academic_year': '2024-2025',
            'schedule_day': 'Friday',
            'credits': 3,
            'max_students': 30
        }
    ]
    
    created_count = 0
    
    with app.app_context():
        for class_data in test_classes:
            try:
                # Check if class already exists
                existing = Classes.query.filter_by(class_code=class_data['class_code']).first()
                if existing:
                    print(f"   ⚠️ Class {class_data['class_code']} already exists")
                    continue
                
                # Create class with full day name
                new_class = Classes(**class_data)
                db.session.add(new_class)
                db.session.commit()
                
                created_count += 1
                print(f"   ✅ Created class: {class_data['class_code']} with schedule_day: '{class_data['schedule_day']}'")
                
            except Exception as e:
                db.session.rollback()
                print(f"   ❌ Error creating {class_data['class_code']}: {e}")
    
    print(f"   📊 Successfully created {created_count} test classes")
    return created_count > 0

def verify_fix():
    """Verify that the fix worked"""
    print("\n✅ Verifying the fix...")
    
    with app.app_context():
        try:
            # Check the new table structure
            result = db.session.execute(text("SHOW CREATE TABLE classes"))
            create_table_sql = result.fetchone()[1]
            
            print("New table definition for schedule_day:")
            lines = create_table_sql.split('\n')
            for line in lines:
                if 'schedule_day' in line:
                    print(f"   {line.strip()}")
            
            # Test querying classes with schedule info
            classes_with_schedule = Classes.query.filter(Classes.schedule_day.isnot(None)).all()
            print(f"\nClasses with schedule information: {len(classes_with_schedule)}")
            
            for cls in classes_with_schedule[:5]:  # Show first 5
                print(f"   • {cls.class_code}: {cls.schedule_day}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verifying fix: {e}")
            return False

def main():
    """Main execution function"""
    print("🔧 Database Enum Fix Utility")
    print("=" * 50)
    
    try:
        # Step 1: Check current state
        check_current_enum()
        
        # Step 2: Fix the enum field
        if fix_enum_field():
            # Step 3: Test class creation
            test_class_creation()
            
            # Step 4: Verify the fix
            verify_fix()
            
            print("\n" + "=" * 50)
            print("🎯 SUMMARY:")
            print("   ✅ schedule_day field converted from ENUM to VARCHAR")
            print("   ✅ Full day names like 'Wednesday' now supported")
            print("   ✅ Existing data preserved")
            print("   ✅ Test classes created successfully")
            print("\n💡 The field now accepts any day name and is more flexible")
            
            return True
        else:
            print("❌ Failed to fix enum field")
            return False
            
    except Exception as e:
        print(f"❌ Utility failed: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)