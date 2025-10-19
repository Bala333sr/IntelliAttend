#!/usr/bin/env python3
"""
Complete End-to-End Verification Test
Tests database, API, and mobile app integration for IntelliAttend
"""

from app import create_app, db
from datetime import datetime
from sqlalchemy import text
import requests
import json

app = create_app()

def print_header(title):
    print('=' * 80)
    print(f'🔍 {title}')
    print('=' * 80)
    print()

def print_section(title):
    print(f'\n{title}')
    print('-' * 80)

def test_database():
    """Test 1: Database Connection and Data"""
    with app.app_context():
        print_section('TEST 1: Database Connection')
        try:
            db.session.execute(text('SELECT 1')).fetchone()
            print('✅ Database connection: SUCCESSFUL')
        except Exception as e:
            print(f'❌ Database connection: FAILED - {e}')
            return False
        
        print_section('TEST 2: Student Data')
        student_code = '23N31A6645'
        student = db.session.execute(text('''
            SELECT student_id, student_code, first_name, last_name, section_id, email
            FROM students 
            WHERE student_code = :code
        '''), {'code': student_code}).fetchone()
        
        if student:
            print(f'✅ Student found:')
            print(f'   Student ID: {student.student_id}')
            print(f'   Student Code: {student.student_code}')
            print(f'   Name: {student.first_name} {student.last_name}')
            print(f'   Section ID: {student.section_id}')
            print(f'   Email: {student.email}')
        else:
            print(f'❌ Student {student_code} not found!')
            return False
        
        print_section('TEST 3: Section Information')
        section = db.session.execute(text('''
            SELECT id, section_name, room_number, class_incharge, course
            FROM sections
            WHERE id = :id
        '''), {'id': student.section_id}).fetchone()
        
        if section:
            print(f'✅ Section found:')
            print(f'   Section ID: {section.id}')
            print(f'   Section Name: {section.section_name}')
            print(f'   Course: {section.course}')
            print(f'   Room: {section.room_number}')
            print(f'   Class Incharge: {section.class_incharge}')
        else:
            print(f'❌ Section {student.section_id} not found!')
            return False
        
        print_section('TEST 4: Today\'s Timetable')
        today = datetime.now()
        day_name = today.strftime('%A').upper()
        print(f'📅 Today: {day_name}, {today.strftime("%Y-%m-%d %H:%M:%S")}')
        print()
        
        timetable = db.session.execute(text('''
            SELECT 
                t.id,
                t.day_of_week,
                t.start_time,
                t.end_time,
                t.subject_code,
                t.room_number,
                t.slot_type,
                s.subject_name,
                s.faculty_name
            FROM timetable t
            LEFT JOIN subjects s ON t.subject_code = s.subject_code
            WHERE t.section_id = :section_id
              AND t.day_of_week = :day_name
              AND t.slot_type != 'break'
            ORDER BY t.start_time
        '''), {'section_id': student.section_id, 'day_name': day_name}).fetchall()
        
        if timetable:
            print(f'✅ Found {len(timetable)} class(es) for {day_name}:')
            print()
            for i, session in enumerate(timetable, 1):
                print(f'   {i}. {session.start_time} - {session.end_time}')
                print(f'      Subject: {session.subject_name or "N/A"} ({session.subject_code})')
                print(f'      Faculty: {session.faculty_name or "TBA"}')
                print(f'      Room: {session.room_number}')
                print()
        else:
            print(f'❌ No classes scheduled for {day_name}')
            print('⚠️  Checking all days for this section...')
            all_days = db.session.execute(text('''
                SELECT DISTINCT day_of_week 
                FROM timetable 
                WHERE section_id = :section_id
                ORDER BY FIELD(day_of_week, 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY')
            '''), {'section_id': student.section_id}).fetchall()
            print(f'   Available days: {[d[0] for d in all_days]}')
            return False
        
        return True, student, section, timetable

def test_api_endpoint(student_code):
    """Test 5: API Endpoint"""
    print_section('TEST 5: API Endpoint Test')
    
    # First, we need to get an auth token
    print('Step 1: Login to get auth token...')
    login_url = 'http://192.168.0.7:5002/api/auth/login'
    login_data = {
        'email': '23N31A6645@mrcet.ac.in',
        'password': 'password'  # Update with actual password if different
    }
    
    try:
        login_response = requests.post(login_url, json=login_data, timeout=5)
        if login_response.status_code == 200:
            login_json = login_response.json()
            if login_json.get('success'):
                token = login_json.get('data', {}).get('access_token')
                print(f'✅ Login successful, token received')
                
                # Test the timetable endpoint
                print('\nStep 2: Fetching today\'s timetable...')
                timetable_url = 'http://192.168.0.7:5002/api/student/timetable/today'
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                timetable_response = requests.get(timetable_url, headers=headers, timeout=5)
                if timetable_response.status_code == 200:
                    timetable_json = timetable_response.json()
                    if timetable_json.get('success'):
                        data = timetable_json.get('data', {})
                        sessions = data.get('sessions', [])
                        student_info = data.get('student_info', {})
                        
                        print(f'✅ API Response received successfully')
                        print(f'\n📊 API Response Summary:')
                        print(f'   Date: {data.get("date")}')
                        print(f'   Day: {data.get("day_of_week")}')
                        print(f'   Student: {student_info.get("name")} ({student_info.get("student_id")})')
                        print(f'   Section: {student_info.get("section")}')
                        print(f'   Classes: {len(sessions)} sessions')
                        
                        print(f'\n📚 Classes Retrieved:')
                        for i, session in enumerate(sessions[:3], 1):  # Show first 3
                            print(f'\n   {i}. {session.get("subject_name")}')
                            print(f'      Code: {session.get("subject_code")}')
                            print(f'      Time: {session.get("start_time")} - {session.get("end_time")}')
                            print(f'      Teacher: {session.get("teacher_name")}')
                            print(f'      Room: {session.get("room_number")}')
                        
                        if len(sessions) > 3:
                            print(f'\n   ... and {len(sessions) - 3} more classes')
                        
                        print(f'\n✅ API Test: PASSED')
                        return True
                    else:
                        print(f'❌ API returned success=false: {timetable_json.get("message")}')
                        return False
                else:
                    print(f'❌ API request failed with status {timetable_response.status_code}')
                    print(f'Response: {timetable_response.text}')
                    return False
            else:
                print(f'❌ Login failed: {login_json.get("message")}')
                return False
        else:
            print(f'❌ Login request failed with status {login_response.status_code}')
            return False
    except requests.exceptions.RequestException as e:
        print(f'❌ Network error: {e}')
        print(f'⚠️  Make sure the backend server is running on http://192.168.0.7:5002')
        return False

def main():
    print_header('COMPLETE END-TO-END VERIFICATION TEST')
    
    # Test Database
    result = test_database()
    if not result:
        print('\n❌ Database tests failed. Exiting.')
        return
    
    success, student, section, timetable = result
    
    # Test API
    api_success = test_api_endpoint(student.student_code)
    
    # Final Summary
    print()
    print_header('📊 VERIFICATION SUMMARY')
    print(f'✅ Database: Connected')
    print(f'✅ Student: {student.first_name} {student.last_name} ({student.student_code})')
    print(f'✅ Section: {section.section_name} ({section.course})')
    print(f'✅ Today: {datetime.now().strftime("%A").upper()}')
    print(f'✅ Classes: {len(timetable)} sessions found in database')
    print(f'{"✅" if api_success else "❌"} API: {"WORKING" if api_success else "FAILED"}')
    print()
    
    if success and api_success:
        print('🎯 STATUS: ALL TESTS PASSED ✅')
        print()
        print('📱 MOBILE APP STATUS:')
        print('   The swipeable classes feature should now work correctly!')
        print('   Open the IntelliAttend app and navigate to the Home screen.')
        print()
    else:
        print('⚠️  STATUS: SOME TESTS FAILED')
        print('   Please fix the issues above before testing the mobile app.')
        print()
    
    print('=' * 80)

if __name__ == '__main__':
    main()
