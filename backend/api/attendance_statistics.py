#!/usr/bin/env python3
"""
Attendance Statistics API Endpoints
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import text
from app import db, standardize_response, logger

# Create blueprint for attendance statistics
attendance_stats_bp = Blueprint('attendance_stats', __name__, url_prefix='/api/student/attendance')

@attendance_stats_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_attendance_statistics():
    """Get overall and subject-wise attendance statistics"""
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
        
        # Get overall statistics
        overall_stats_query = text("""
            SELECT 
                total_sessions,
                attended_sessions,
                absent_sessions,
                late_sessions,
                attendance_percentage
            FROM attendance_statistics 
            WHERE student_id = :student_id AND subject_id IS NULL
            ORDER BY last_updated DESC
            LIMIT 1
        """)
        
        overall_result = db.session.execute(overall_stats_query, {'student_id': student_id})
        overall_stats = overall_result.fetchone()
        
        # Get subject-wise statistics
        subject_stats_query = text("""
            SELECT 
                s.subject_code,
                s.subject_name,
                s.short_name,
                ast.total_sessions,
                ast.attended_sessions,
                ast.absent_sessions,
                ast.late_sessions,
                ast.attendance_percentage
            FROM attendance_statistics ast
            JOIN subjects s ON ast.subject_id = s.id
            WHERE ast.student_id = :student_id AND ast.subject_id IS NOT NULL
            ORDER BY s.subject_name
        """)
        
        subject_result = db.session.execute(subject_stats_query, {'student_id': student_id})
        subject_stats = subject_result.fetchall()
        
        # Format subject stats
        subject_stats_list = []
        for row in subject_stats:
            # Determine status based on attendance percentage
            percentage = float(row[7]) if row[7] is not None else 0.0
            if percentage >= 75.0:
                status = 'SAFE'
            elif percentage >= 65.0:
                status = 'WARNING'
            else:
                status = 'CRITICAL'
            
            # Check if student can reach 75% with remaining sessions
            total_sessions = row[3] if row[3] is not None else 0
            attended_sessions = row[4] if row[4] is not None else 0
            can_reach_75 = True
            sessions_needed = 0
            
            if total_sessions > 0 and percentage < 75.0:
                # Calculate how many more sessions needed to reach 75%
                needed = (0.75 * total_sessions) - attended_sessions
                if needed > 0:
                    sessions_needed = int(needed)
                    # Check if it's still possible
                    if attended_sessions + sessions_needed > total_sessions:
                        can_reach_75 = False
            
            subject_stats_list.append({
                'subjectCode': row[0],
                'subjectName': row[1],
                'shortName': row[2],
                'totalSessions': row[3] if row[3] is not None else 0,
                'attendedSessions': row[4] if row[4] is not None else 0,
                'absentSessions': row[5] if row[5] is not None else 0,
                'lateSessions': row[6] if row[6] is not None else 0,
                'percentage': percentage,
                'status': status,
                'canReach75': can_reach_75,
                'sessionsNeeded': sessions_needed
            })
        
        # Format overall stats
        overall_data = {
            'totalSessions': overall_stats[0] if overall_stats and overall_stats[0] is not None else 0,
            'attendedSessions': overall_stats[1] if overall_stats and overall_stats[1] is not None else 0,
            'absentSessions': overall_stats[2] if overall_stats and overall_stats[2] is not None else 0,
            'lateSessions': overall_stats[3] if overall_stats and overall_stats[3] is not None else 0,
            'attendancePercentage': float(overall_stats[4]) if overall_stats and overall_stats[4] is not None else 0.0
        }
        
        # Determine overall status
        overall_percentage = overall_data['attendancePercentage']
        if overall_percentage >= 75.0:
            overall_status = 'SAFE'
        elif overall_percentage >= 65.0:
            overall_status = 'WARNING'
        else:
            overall_status = 'CRITICAL'
        
        overall_data['status'] = overall_status
        
        return standardize_response(
            success=True,
            data={
                'overall': overall_data,
                'subjects': subject_stats_list
            },
            message='Attendance statistics retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error fetching attendance statistics: {e}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )


@attendance_stats_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_attendance_summary():
    """Get subject-level attendance summary for the History page according to PRD specifications"""
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
        
        # Get student's section to determine enrolled subjects
        section_query = text("""
            SELECT s.section_id
            FROM students s
            WHERE s.student_id = :student_id
        """)
        
        section_result = db.session.execute(section_query, {'student_id': student_id})
        section_row = section_result.fetchone()
        
        if not section_row:
            return standardize_response(
                success=False,
                error='Student not found',
                status_code=404
            )
        
        section_id = section_row[0]
        
        # Get subjects for the student's section from timetable
        subjects_query = text("""
            SELECT DISTINCT t.subject_code, s.subject_name, s.short_name, s.faculty_name
            FROM timetable t
            JOIN subjects s ON t.subject_code = s.subject_code
            WHERE t.section_id = :section_id
            AND t.slot_type NOT IN ('break', 'lunch', 'free')
            AND t.subject_code IS NOT NULL
            AND t.subject_code != ''
        """)
        
        subjects_result = db.session.execute(subjects_query, {'section_id': section_id})
        subjects = subjects_result.fetchall()
        
        # Calculate attendance statistics for each subject according to PRD
        subject_stats_list = []
        
        for subject in subjects:
            subject_code = subject[0]
            
            # Get total classes conducted for this subject
            total_classes_query = text("""
                SELECT COUNT(*) as total_sessions
                FROM attendance_sessions a_s
                JOIN timetable t ON a_s.class_id = t.id
                WHERE t.subject_code = :subject_code
                AND a_s.status IN ('active', 'completed')
            """)
            
            total_result = db.session.execute(total_classes_query, {'subject_code': subject_code})
            total_row = total_result.fetchone()
            total_classes = total_row[0] if total_row and total_row[0] is not None else 0
            
            # Get attended classes for this subject
            attended_classes_query = text("""
                SELECT COUNT(*) as attended_sessions
                FROM attendance_records a_r
                JOIN attendance_sessions a_s ON a_r.session_id = a_s.session_id
                JOIN timetable t ON a_s.class_id = t.id
                WHERE a_r.student_id = :student_id
                AND t.subject_code = :subject_code
                AND a_r.status IN ('present', 'late')
            """)
            
            attended_result = db.session.execute(attended_classes_query, {
                'student_id': student_id,
                'subject_code': subject_code
            })
            attended_row = attended_result.fetchone()
            attended_count = attended_row[0] if attended_row and attended_row[0] is not None else 0
            
            # Calculate percentage
            if total_classes > 0:
                percentage = round((attended_count / total_classes) * 100, 2)
            else:
                percentage = 0.0
            
            # Get faculty name from subject
            faculty_name = subject[3] if subject[3] else "Unknown Faculty"
            
            subject_stats_list.append({
                'subject_code': subject_code,
                'subject_name': subject[1],
                'short_name': subject[2],
                'faculty_name': faculty_name,
                'total_classes': total_classes,
                'attended_count': attended_count,
                'percentage': percentage
            })
        
        # Sort by total_classes descending, then by subject_name
        subject_stats_list.sort(key=lambda x: (-x['total_classes'], x['subject_name']))
        
        return standardize_response(
            success=True,
            data={
                'subjects': subject_stats_list
            },
            message='Subject attendance summary retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error fetching subject attendance summary: {e}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )


@attendance_stats_bp.route('/history', methods=['GET'])
@jwt_required()
def get_attendance_history():
    """Get detailed attendance history with filters according to PRD specifications"""
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
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        
        # Build query with filters
        query_parts = [
            "SELECT",
            "  ah.record_id,",
            "  ah.session_id,",
            "  s.subject_code,",
            "  s.subject_name,",
            "  f.first_name,",
            "  f.last_name,",
            "  ah.status,",
            "  ah.verification_score,",
            "  ah.scan_timestamp",
            "FROM attendance_records ah",
            "JOIN students st ON ah.student_id = st.student_id",
            "JOIN timetable t ON ah.session_id = t.id",
            "JOIN subjects s ON t.subject_code = s.subject_code",
            "LEFT JOIN faculty f ON s.faculty_id = f.faculty_id",
            "WHERE ah.student_id = :student_id"
        ]
        
        params = {'student_id': student_id}
        
        if from_date:
            query_parts.append("AND DATE(ah.scan_timestamp) >= :from_date")
            params['from_date'] = from_date
        
        if to_date:
            query_parts.append("AND DATE(ah.scan_timestamp) <= :to_date")
            params['to_date'] = to_date
        
        query_parts.append("ORDER BY ah.scan_timestamp DESC")
        query_parts.append("LIMIT :limit")
        params['limit'] = min(limit, 100)  # Cap at 100 records
        
        query = " ".join(query_parts)
        
        result = db.session.execute(text(query), params)
        rows = result.fetchall()
        
        # Format history records
        history_list = []
        for row in rows:
            # Get faculty name
            faculty_name = f"{row[4]} {row[5]}".strip() if row[4] or row[5] else "Unknown Faculty"
            
            history_list.append({
                'record_id': row[0],
                'session_id': row[1],
                'subject_code': row[2],
                'subject_name': row[3],
                'faculty_name': faculty_name,
                'status': row[6].upper() if row[6] else "UNKNOWN",
                'verification_score': float(row[7]) if row[7] is not None else 0.0,
                'scan_timestamp': row[8].isoformat() if row[8] else None
            })
        
        return standardize_response(
            success=True,
            data={
                'records': history_list
            },
            message='Attendance history retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error fetching attendance history: {e}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )


@attendance_stats_bp.route('/trends', methods=['GET'])
@jwt_required()
def get_attendance_trends():
    """Get time-series attendance data for charts"""
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
        
        # Get period parameter (daily, weekly, monthly)
        period = request.args.get('period', 'weekly')
        
        if period == 'daily':
            # Daily trends for the last 30 days
            query = text("""
                SELECT 
                    trend_date,
                    attendance_rate,
                    sessions_count,
                    attended_count
                FROM attendance_trends
                WHERE student_id = :student_id 
                AND subject_id IS NULL
                AND trend_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                ORDER BY trend_date
            """)
        elif period == 'monthly':
            # Monthly trends for the last 12 months
            query = text("""
                SELECT 
                    DATE_FORMAT(trend_date, '%Y-%m') as trend_month,
                    AVG(attendance_rate) as attendance_rate,
                    SUM(sessions_count) as sessions_count,
                    SUM(attended_count) as attended_count
                FROM attendance_trends
                WHERE student_id = :student_id 
                AND subject_id IS NULL
                AND trend_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                GROUP BY DATE_FORMAT(trend_date, '%Y-%m')
                ORDER BY trend_month
            """)
        else:  # weekly (default)
            # Weekly trends for the last 12 weeks
            query = text("""
                SELECT 
                    trend_date,
                    attendance_rate,
                    sessions_count,
                    attended_count
                FROM attendance_trends
                WHERE student_id = :student_id 
                AND subject_id IS NULL
                AND trend_date >= DATE_SUB(CURDATE(), INTERVAL 12 WEEK)
                ORDER BY trend_date
            """)
        
        result = db.session.execute(query, {'student_id': student_id})
        rows = result.fetchall()
        
        # Format trend data
        trend_list = []
        for row in rows:
            trend_list.append({
                'date': row[0].isoformat() if row[0] else None,
                'attendanceRate': float(row[1]) if row[1] is not None else 0.0,
                'sessionsCount': row[2] if row[2] is not None else 0,
                'attendedCount': row[3] if row[3] is not None else 0
            })
        
        return standardize_response(
            success=True,
            data=trend_list,
            message='Attendance trends retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error fetching attendance trends: {e}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )





@attendance_stats_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_subject_attendance_summary():
    """Get subject-level attendance summary for the History page"""
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
        
        # Get subject-wise statistics
        subject_stats_query = text("""
            SELECT 
                s.subject_code,
                s.subject_name,
                s.short_name,
                f.first_name,
                f.last_name,
                ast.total_sessions,
                ast.attended_sessions,
                ast.attendance_percentage
            FROM attendance_statistics ast
            JOIN subjects s ON ast.subject_id = s.id
            LEFT JOIN faculty f ON s.faculty_id = f.faculty_id
            WHERE ast.student_id = :student_id AND ast.subject_id IS NOT NULL
            ORDER BY ast.total_sessions DESC, s.subject_name
        """)
        
        subject_result = db.session.execute(subject_stats_query, {'student_id': student_id})
        subject_stats = subject_result.fetchall()
        
        # Format subject stats for the History page
        subject_stats_list = []
        for row in subject_stats:
            # Calculate percentage
            percentage = float(row[7]) if row[7] is not None else 0.0
            
            # Get faculty name
            faculty_name = f"{row[3]} {row[4]}".strip() if row[3] or row[4] else "Unknown Faculty"
            
            subject_stats_list.append({
                'subject_code': row[0],
                'subject_name': row[1],
                'short_name': row[2],
                'faculty_name': faculty_name,
                'total_classes': row[5] if row[5] is not None else 0,
                'attended_count': row[6] if row[6] is not None else 0,
                'percentage': percentage
            })
        
        return standardize_response(
            success=True,
            data={
                'subjects': subject_stats_list
            },
            message='Subject attendance summary retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error fetching subject attendance summary: {e}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )





@attendance_stats_bp.route('/predictions', methods=['GET'])
@jwt_required()
def get_attendance_predictions():
    """Get predictions based on remaining sessions"""
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
        
        # Get subject-wise statistics with predictions
        query = text("""
            SELECT 
                s.subject_code,
                s.subject_name,
                s.short_name,
                ast.total_sessions,
                ast.attended_sessions,
                ast.attendance_percentage,
                sec.course,
                sec.section_name
            FROM attendance_statistics ast
            JOIN subjects s ON ast.subject_id = s.id
            JOIN students st ON ast.student_id = st.student_id
            JOIN sections sec ON st.section_id = sec.id
            WHERE ast.student_id = :student_id AND ast.subject_id IS NOT NULL
            ORDER BY s.subject_name
        """)
        
        result = db.session.execute(query, {'student_id': student_id})
        subject_stats = result.fetchall()
        
        # Get timetable to estimate remaining sessions
        timetable_query = text("""
            SELECT COUNT(*) as remaining_sessions
            FROM timetable t
            JOIN students st ON t.section_id = st.section_id
            WHERE st.student_id = :student_id
            AND t.day_of_week IN ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY')
            AND t.start_time > CURTIME()
        """)
        
        timetable_result = db.session.execute(timetable_query, {'student_id': student_id})
        timetable_data = timetable_result.fetchone()
        remaining_sessions = timetable_data[0] if timetable_data and timetable_data[0] is not None else 0
        
        # Format predictions
        predictions_list = []
        for row in subject_stats:
            total_sessions = row[3] if row[3] is not None else 0
            attended_sessions = row[4] if row[4] is not None else 0
            percentage = float(row[5]) if row[5] is not None else 0.0
            
            # Calculate what percentage would be if all remaining sessions are attended
            if total_sessions + remaining_sessions > 0:
                max_possible_percentage = ((attended_sessions + remaining_sessions) / 
                                         (total_sessions + remaining_sessions)) * 100
            else:
                max_possible_percentage = 0.0
            
            # Determine if student can reach 75%
            can_reach_75 = max_possible_percentage >= 75.0
            will_reach_75_if_attend_all = percentage >= 75.0 or can_reach_75
            
            # Calculate minimum sessions needed to reach 75%
            sessions_needed = 0
            if percentage < 75.0 and total_sessions > 0:
                # This is a simplified calculation - in reality, this would be more complex
                needed = max(0, int((0.75 * (total_sessions + remaining_sessions)) - attended_sessions))
                sessions_needed = min(needed, remaining_sessions)
            
            predictions_list.append({
                'subjectCode': row[0],
                'subjectName': row[1],
                'shortName': row[2],
                'currentPercentage': percentage,
                'maxPossiblePercentage': max_possible_percentage,
                'canReach75': can_reach_75,
                'willReach75IfAttendAll': will_reach_75_if_attend_all,
                'sessionsNeeded': sessions_needed,
                'remainingSessions': remaining_sessions
            })
        
        return standardize_response(
            success=True,
            data=predictions_list,
            message='Attendance predictions retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error fetching attendance predictions: {e}")
        return standardize_response(
            success=False,
            error=str(e),
            status_code=500
        )