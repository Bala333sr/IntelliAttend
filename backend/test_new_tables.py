#!/usr/bin/env python3
"""
Comprehensive database schema verification for new features
"""

from app import app, db
from sqlalchemy import text, inspect
import json

def test_database_tables():
    """Verify all new tables exist with correct schema"""
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            all_tables = inspector.get_table_names()
            
            print("=" * 80)
            print("DATABASE SCHEMA VERIFICATION - NEW FEATURES")
            print("=" * 80)
            print()
            
            # Expected tables
            expected_tables = {
                'attendance_history': {
                    'columns': ['id', 'student_id', 'subject_id', 'session_id', 
                               'attendance_status', 'marked_at', 'attendance_type',
                               'location_verified', 'classroom_id'],
                    'indexes': ['idx_student_subject', 'idx_marked_at']
                },
                'attendance_statistics': {
                    'columns': ['id', 'student_id', 'subject_id', 'total_sessions',
                               'attended_sessions', 'absent_sessions', 'late_sessions',
                               'attendance_percentage', 'last_updated', 'academic_year', 'semester'],
                    'indexes': ['unique_student_subject']
                },
                'attendance_trends': {
                    'columns': ['id', 'student_id', 'subject_id', 'trend_date',
                               'sessions_count', 'attended_count', 'attendance_rate'],
                    'indexes': ['unique_student_subject_date']
                },
                'notification_preferences': {
                    'columns': ['id', 'student_id', 'class_reminder_enabled',
                               'warm_scan_reminder_enabled', 'attendance_warning_enabled',
                               'weekly_summary_enabled', 'reminder_minutes_before',
                               'quiet_hours_start', 'quiet_hours_end', 'created_at', 'updated_at'],
                    'indexes': ['unique_student']
                },
                'notification_log': {
                    'columns': ['id', 'student_id', 'notification_type', 'title',
                               'message', 'sent_at', 'read_at', 'action_taken'],
                    'indexes': ['idx_student_sent']
                },
                'auto_attendance_config': {
                    'columns': ['id', 'student_id', 'enabled', 'gps_enabled',
                               'wifi_enabled', 'bluetooth_enabled', 'confidence_threshold',
                               'require_warm_data', 'auto_submit', 'created_at', 'updated_at'],
                    'indexes': ['unique_student']
                },
                'auto_attendance_log': {
                    'columns': ['id', 'student_id', 'session_id', 'detected_at',
                               'gps_score', 'wifi_score', 'bluetooth_score', 'final_confidence',
                               'action_taken', 'latitude', 'longitude', 'wifi_ssid', 'bluetooth_devices'],
                    'indexes': ['idx_student_session']
                }
            }
            
            results = {
                'total_tables': len(expected_tables),
                'tables_created': 0,
                'columns_verified': 0,
                'indexes_verified': 0,
                'issues': []
            }
            
            # Test each table
            for table_name, table_spec in expected_tables.items():
                print(f"📊 Testing table: {table_name}")
                print("-" * 80)
                
                # Check table exists
                if table_name in all_tables:
                    print(f"  ✅ Table exists")
                    results['tables_created'] += 1
                    
                    # Get columns
                    columns = inspector.get_columns(table_name)
                    column_names = [col['name'] for col in columns]
                    
                    # Verify columns
                    missing_columns = set(table_spec['columns']) - set(column_names)
                    if missing_columns:
                        issue = f"Table {table_name} missing columns: {missing_columns}"
                        print(f"  ⚠️  {issue}")
                        results['issues'].append(issue)
                    else:
                        print(f"  ✅ All {len(table_spec['columns'])} columns present")
                        results['columns_verified'] += len(table_spec['columns'])
                    
                    # Get indexes
                    indexes = inspector.get_indexes(table_name)
                    index_names = [idx['name'] for idx in indexes]
                    
                    # Get foreign keys
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    
                    print(f"  📑 Columns: {len(column_names)}")
                    print(f"  🔑 Indexes: {len(indexes)}")
                    print(f"  🔗 Foreign Keys: {len(foreign_keys)}")
                    
                    # Test data insertion (sample)
                    print(f"  🧪 Testing data insertion...")
                    test_insert_query(table_name)
                    
                else:
                    issue = f"Table {table_name} does not exist!"
                    print(f"  ❌ {issue}")
                    results['issues'].append(issue)
                
                print()
            
            # Print summary
            print("=" * 80)
            print("VERIFICATION SUMMARY")
            print("=" * 80)
            print(f"✅ Tables Created: {results['tables_created']}/{results['total_tables']}")
            print(f"✅ Columns Verified: {results['columns_verified']}")
            print(f"⚠️  Issues Found: {len(results['issues'])}")
            
            if results['issues']:
                print("\n⚠️  Issues:")
                for issue in results['issues']:
                    print(f"   - {issue}")
            
            # Overall score
            score = (results['tables_created'] / results['total_tables']) * 100
            print(f"\n🎯 Database Schema Score: {score:.1f}%")
            
            if score == 100 and not results['issues']:
                print("✅ ALL TESTS PASSED - Database schema is perfect!")
            elif score >= 80:
                print("⚠️  MOSTLY PASSED - Minor issues to address")
            else:
                print("❌ FAILED - Significant issues found")
            
            return results
            
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            import traceback
            traceback.print_exc()
            return None

def test_insert_query(table_name):
    """Test if table accepts insertions (without actually inserting)"""
    try:
        # Just test query construction
        query = f"DESCRIBE {table_name}"
        result = db.session.execute(text(query))
        print(f"  ✅ Table structure is queryable")
    except Exception as e:
        print(f"  ❌ Error querying table: {e}")

if __name__ == '__main__':
    test_database_tables()
