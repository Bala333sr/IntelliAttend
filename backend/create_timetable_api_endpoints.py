#!/usr/bin/env python3
"""
Script to add timetable API endpoints according to PRD specifications
This script will add the required functions to the app.py file
"""

import sys
import os
sys.path.append('.')

def create_api_endpoints():
    """Create API endpoints for student timetable and current/next session"""
    
    # API endpoint for student timetable (weekly view)
    timetable_endpoint = '''
@app.route('/api/student/timetable', methods=['GET'])
@jwt_required()
def get_student_timetable():
    """Get complete timetable for the current student"""
    try:
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return standardize_response(
                success=False,
                error='Student access required',
                status_code=403
            )
        
        student_id = claims.get('student_id')
        
        # Get student details including section
        student_query = text("""
            SELECT s.student_code, s.first_name, s.last_name, sec.section_name, sec.course, sec.room_number
            FROM students s
            JOIN sections sec ON s.section_id = sec.id
            WHERE s.student_id = :student_id
        """)
        
        student_result = db.session.execute(student_query, {'student_id': student_id})
        student_row = student_result.fetchone()
        
        if not student_row:
            return standardize_response(
                success=False,
                error='Student not found',
                status_code=404
            )
        
        student_info = {
            'studentCode': student_row[0],
            'name': student_row[1] + (' ' + student_row[2] if student_row[2] else ''),
            'section': student_row[3],
            'course': student_row[4],
            'room': student_row[5]
        }
        
        # Get timetable for the student's section
        timetable_query = text("""
            SELECT t.day_of_week, t.slot_number, t.start_time, t.end_time, t.subject_code, 
                   t.slot_type, t.room_number, sub.subject_name, sub.short_name, sub.faculty_name
            FROM timetable t
            JOIN sections sec ON t.section_id = sec.id
            LEFT JOIN subjects sub ON t.subject_code = sub.subject_code
            WHERE t.section_id = (SELECT section_id FROM students WHERE student_id = :student_id)
            ORDER BY FIELD(t.day_of_week, 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'), 
                     t.slot_number, t.start_time
        """)
        
        result = db.session.execute(timetable_query, {'student_id': student_id})
        
        # Organize timetable by day
        timetable_schedule = {}
        days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
        
        for day in days:
            timetable_schedule[day] = []
        
        for row in result:
            slot_data = {
                'slotNumber': row[1],
                'startTime': str(row[2])[:-3] if row[2] else None,  # Remove seconds
                'endTime': str(row[3])[:-3] if row[3] else None,   # Remove seconds
                'subjectCode': row[4],
                'subjectName': row[7] if row[7] else (row[4] if row[4] else ''),
                'shortName': row[8] if row[8] else (row[4] if row[4] else ''),
                'facultyName': row[9],
                'room': row[6],
                'slotType': row[5]
            }
            
            timetable_schedule[row[0]].append(slot_data)
        
        return standardize_response(
            success=True,
            data={
                'student': student_info,
                'timetable': timetable_schedule
            },
            message='Student timetable retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error fetching student timetable: {e}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )


@app.route('/api/student/current-session', methods=['GET'])
@jwt_required()
def get_current_session():
    """Get current and next session for the student"""
    try:
        from datetime import datetime, time
        
        # Get current student from JWT token
        claims = get_jwt()
        if claims.get('type') != 'student':
            return standardize_response(
                success=False,
                error='Student access required',
                status_code=403
            )
        
        student_id = claims.get('student_id')
        
        # Get current day and time
        now = datetime.now()
        current_day = now.strftime('%A').upper()
        current_time = now.time()
        
        # Get student's section
        section_query = text("SELECT section_id FROM students WHERE student_id = :student_id")
        section_result = db.session.execute(section_query, {'student_id': student_id})
        section_row = section_result.fetchone()
        
        if not section_row:
            return standardize_response(
                success=False,
                error='Student not found',
                status_code=404
            )
        
        section_id = section_row[0]
        
        # Get current session
        current_session_query = text("""
            SELECT t.id, t.start_time, t.end_time, t.subject_code, t.slot_type, t.room_number,
                   sub.subject_name, sub.short_name, sub.faculty_name
            FROM timetable t
            LEFT JOIN subjects sub ON t.subject_code = sub.subject_code
            WHERE t.section_id = :section_id 
            AND t.day_of_week = :day_of_week
            AND t.start_time <= :current_time 
            AND t.end_time > :current_time
            ORDER BY t.start_time
            LIMIT 1
        """)
        
        current_result = db.session.execute(current_session_query, {
            'section_id': section_id,
            'day_of_week': current_day,
            'current_time': current_time
        })
        
        current_row = current_result.fetchone()
        
        current_session = None
        if current_row:
            start_time_obj = current_row[1]
            end_time_obj = current_row[2]
            
            # Calculate elapsed and remaining time
            elapsed_minutes = int((now - datetime.combine(now.date(), start_time_obj)).total_seconds() / 60)
            remaining_minutes = int((datetime.combine(now.date(), end_time_obj) - now).total_seconds() / 60)
            
            current_session = {
                'isActive': True,
                'subjectCode': current_row[3],
                'subjectName': current_row[6] if current_row[6] else (current_row[3] if current_row[3] else ''),
                'shortName': current_row[7] if current_row[7] else (current_row[3] if current_row[3] else ''),
                'facultyName': current_row[8],
                'startTime': str(start_time_obj)[:-3] if start_time_obj else None,
                'endTime': str(end_time_obj)[:-3] if end_time_obj else None,
                'room': current_row[5],
                'minutesElapsed': max(0, elapsed_minutes),
                'minutesRemaining': max(0, remaining_minutes)
            }
        
        # Get next session
        next_session_query = text("""
            SELECT t.id, t.start_time, t.end_time, t.subject_code, t.slot_type, t.room_number,
                   sub.subject_name, sub.short_name, sub.faculty_name
            FROM timetable t
            LEFT JOIN subjects sub ON t.subject_code = sub.subject_code
            WHERE t.section_id = :section_id 
            AND t.day_of_week = :day_of_week
            AND t.start_time > :current_time
            ORDER BY t.start_time
            LIMIT 1
        """)
        
        next_result = db.session.execute(next_session_query, {
            'section_id': section_id,
            'day_of_week': current_day,
            'current_time': current_time
        })
        
        next_row = next_result.fetchone()
        
        next_session = None
        if next_row:
            start_time_obj = next_row[1]
            end_time_obj = next_row[2]
            
            # Calculate minutes until start
            minutes_until_start = int((datetime.combine(now.date(), start_time_obj) - now).total_seconds() / 60)
            
            next_session = {
                'subjectCode': next_row[3],
                'subjectName': next_row[6] if next_row[6] else (next_row[3] if next_row[3] else ''),
                'shortName': next_row[7] if next_row[7] else (next_row[3] if next_row[3] else ''),
                'facultyName': next_row[8],
                'startTime': str(start_time_obj)[:-3] if start_time_obj else None,
                'endTime': str(end_time_obj)[:-3] if end_time_obj else None,
                'room': next_row[5],
                'minutesUntilStart': max(0, minutes_until_start)
            }
        
        # Check if warm window is active (3 minutes before next session)
        warm_window_active = False
        warm_window_starts_in = None
        
        if next_session:
            if next_session['minutesUntilStart'] <= 3 and next_session['minutesUntilStart'] >= 0:
                warm_window_active = True
                warm_window_starts_in = 0
            elif next_session['minutesUntilStart'] > 3:
                warm_window_starts_in = next_session['minutesUntilStart'] - 3
        
        return standardize_response(
            success=True,
            data={
                'currentSession': current_session,
                'nextSession': next_session,
                'warmWindowActive': warm_window_active,
                'warmWindowStartsIn': warm_window_starts_in
            },
            message='Current session information retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error fetching current session: {e}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )
'''
    
    print("API endpoints created successfully!")
    print("Please add the following code to your app.py file:")
    print("=" * 50)
    print(timetable_endpoint)
    print("=" * 50)

if __name__ == '__main__':
    create_api_endpoints()