#!/usr/bin/env python3
"""
Attendance Analytics Service
Computes and caches attendance statistics from attendance history
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from app import db
from sqlalchemy import text

logger = logging.getLogger(__name__)

class AttendanceAnalyticsService:
    """
    Service to compute and cache attendance statistics
    Does not modify existing attendance submission flow
    """
    
    @staticmethod
    def calculate_statistics(student_id: int, subject_id: Optional[int] = None) -> Dict:
        """
        Calculate attendance stats from attendance_history
        
        Args:
            student_id (int): The student ID
            subject_id (int, optional): Specific subject ID, if None calculates overall stats
            
        Returns:
            Dict: Statistics including total_sessions, attended_sessions, etc.
        """
        try:
            # Build query based on whether we're calculating for a specific subject or overall
            if subject_id:
                # Subject-specific statistics
                query = text("""
                    SELECT 
                        COUNT(*) as total_sessions,
                        SUM(CASE WHEN attendance_status = 'present' THEN 1 ELSE 0 END) as attended_sessions,
                        SUM(CASE WHEN attendance_status = 'absent' THEN 1 ELSE 0 END) as absent_sessions,
                        SUM(CASE WHEN attendance_status = 'late' THEN 1 ELSE 0 END) as late_sessions,
                        ROUND(
                            (SUM(CASE WHEN attendance_status = 'present' THEN 1 ELSE 0 END) * 100.0) / 
                            COUNT(*), 2
                        ) as attendance_percentage
                    FROM attendance_history 
                    WHERE student_id = :student_id AND subject_id = :subject_id
                """)
                result = db.session.execute(query, {
                    'student_id': student_id,
                    'subject_id': subject_id
                })
            else:
                # Overall statistics
                query = text("""
                    SELECT 
                        COUNT(*) as total_sessions,
                        SUM(CASE WHEN attendance_status = 'present' THEN 1 ELSE 0 END) as attended_sessions,
                        SUM(CASE WHEN attendance_status = 'absent' THEN 1 ELSE 0 END) as absent_sessions,
                        SUM(CASE WHEN attendance_status = 'late' THEN 1 ELSE 0 END) as late_sessions,
                        ROUND(
                            (SUM(CASE WHEN attendance_status = 'present' THEN 1 ELSE 0 END) * 100.0) / 
                            COUNT(*), 2
                        ) as attendance_percentage
                    FROM attendance_history 
                    WHERE student_id = :student_id
                """)
                result = db.session.execute(query, {'student_id': student_id})
            
            row = result.fetchone()
            
            if not row:
                # Return default values if no data found
                return {
                    'total_sessions': 0,
                    'attended_sessions': 0,
                    'absent_sessions': 0,
                    'late_sessions': 0,
                    'attendance_percentage': 0.0
                }
            
            return {
                'total_sessions': row.total_sessions or 0,
                'attended_sessions': row.attended_sessions or 0,
                'absent_sessions': row.absent_sessions or 0,
                'late_sessions': row.late_sessions or 0,
                'attendance_percentage': float(row.attendance_percentage or 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error calculating statistics for student {student_id}, subject {subject_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_subject_wise_statistics(student_id: int) -> List[Dict]:
        """
        Get subject-wise attendance statistics for a student
        
        Args:
            student_id (int): The student ID
            
        Returns:
            List[Dict]: List of subject statistics
        """
        try:
            query = text("""
                SELECT 
                    s.id as subject_id,
                    s.name as subject_name,
                    s.code as subject_code,
                    COUNT(*) as total_sessions,
                    SUM(CASE WHEN ah.attendance_status = 'present' THEN 1 ELSE 0 END) as attended_sessions,
                    SUM(CASE WHEN ah.attendance_status = 'absent' THEN 1 ELSE 0 END) as absent_sessions,
                    SUM(CASE WHEN ah.attendance_status = 'late' THEN 1 ELSE 0 END) as late_sessions,
                    ROUND(
                        (SUM(CASE WHEN ah.attendance_status = 'present' THEN 1 ELSE 0 END) * 100.0) / 
                        COUNT(*), 2
                    ) as attendance_percentage
                FROM attendance_history ah
                JOIN prd_subjects s ON ah.subject_id = s.id
                WHERE ah.student_id = :student_id
                GROUP BY s.id, s.name, s.code
                ORDER BY s.name
            """)
            
            result = db.session.execute(query, {'student_id': student_id})
            subject_stats = []
            
            for row in result:
                stats = {
                    'subject_id': row.subject_id,
                    'subject_name': row.subject_name,
                    'subject_code': row.subject_code,
                    'total_sessions': row.total_sessions,
                    'attended_sessions': row.attended_sessions,
                    'absent_sessions': row.absent_sessions,
                    'late_sessions': row.late_sessions,
                    'attendance_percentage': float(row.attendance_percentage)
                }
                subject_stats.append(stats)
            
            return subject_stats
            
        except Exception as e:
            logger.error(f"Error getting subject-wise statistics for student {student_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_trends(student_id: int, period: str = 'weekly') -> List[Dict]:
        """
        Aggregate attendance data for trend analysis
        
        Args:
            student_id (int): The student ID
            period (str): Period for aggregation ('daily', 'weekly', 'monthly')
            
        Returns:
            List[Dict]: Trend data for charts
        """
        try:
            # Determine the date format based on period
            if period == 'daily':
                date_format = "%Y-%m-%d"
                date_group = "DATE(marked_at)"
            elif period == 'weekly':
                date_format = "%Y-%U"
                date_group = "DATE_FORMAT(marked_at, '%Y-%u')"
            elif period == 'monthly':
                date_format = "%Y-%m"
                date_group = "DATE_FORMAT(marked_at, '%Y-%m')"
            else:
                raise ValueError("Period must be 'daily', 'weekly', or 'monthly'")
            
            query = text(f"""
                SELECT 
                    {date_group} as trend_date,
                    COUNT(*) as sessions_count,
                    SUM(CASE WHEN attendance_status = 'present' THEN 1 ELSE 0 END) as attended_count,
                    ROUND(
                        (SUM(CASE WHEN attendance_status = 'present' THEN 1 ELSE 0 END) * 100.0) / 
                        COUNT(*), 2
                    ) as attendance_rate
                FROM attendance_history 
                WHERE student_id = :student_id
                GROUP BY {date_group}
                ORDER BY trend_date
            """)
            
            result = db.session.execute(query, {'student_id': student_id})
            trends = []
            
            for row in result:
                trend = {
                    'trend_date': str(row.trend_date),
                    'sessions_count': row.sessions_count,
                    'attended_count': row.attended_count,
                    'attendance_rate': float(row.attendance_rate)
                }
                trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting trends for student {student_id}, period {period}: {str(e)}")
            raise
    
    @staticmethod
    def predict_attendance(student_id: int, subject_id: int) -> Dict:
        """
        Predict if student can meet 75% requirement based on remaining sessions
        
        Args:
            student_id (int): The student ID
            subject_id (int): The subject ID
            
        Returns:
            Dict: Prediction data including can_reach_75 and sessions_needed
        """
        try:
            # Get current statistics for the subject
            current_stats = AttendanceAnalyticsService.calculate_statistics(student_id, subject_id)
            
            # Get total expected sessions for this subject (from timetable)
            # This is a simplified approach - in a real system, you'd have a more sophisticated
            # way to determine remaining sessions
            query = text("""
                SELECT COUNT(*) as total_expected_sessions
                FROM timetable 
                WHERE subject_id = :subject_id
            """)
            
            result = db.session.execute(query, {'subject_id': subject_id})
            row = result.fetchone()
            
            if not row:
                total_expected_sessions = 0
            else:
                total_expected_sessions = row.total_expected_sessions or 0
            
            # Calculate how many more sessions are expected
            attended_so_far = current_stats['attended_sessions']
            total_so_far = current_stats['total_sessions']
            remaining_sessions = max(0, total_expected_sessions - total_so_far)
            
            # Calculate minimum sessions needed to reach 75%
            # Formula: (attended_so_far + x) / (total_so_far + remaining_sessions) >= 0.75
            # Solving for x: x >= 0.75 * (total_so_far + remaining_sessions) - attended_so_far
            min_sessions_needed = max(0, 0.75 * (total_so_far + remaining_sessions) - attended_so_far)
            
            # Check if it's possible to reach 75% (if we can attend all remaining sessions)
            max_possible_attendance = (attended_so_far + remaining_sessions) / (total_so_far + remaining_sessions) if (total_so_far + remaining_sessions) > 0 else 0
            can_reach_75 = max_possible_attendance >= 0.75
            
            # Calculate actual sessions needed (rounded up)
            sessions_needed = int(min_sessions_needed) if min_sessions_needed == int(min_sessions_needed) else int(min_sessions_needed) + 1
            
            return {
                'current_percentage': current_stats['attendance_percentage'],
                'total_sessions_so_far': total_so_far,
                'attended_sessions_so_far': attended_so_far,
                'remaining_sessions': remaining_sessions,
                'can_reach_75': can_reach_75,
                'sessions_needed': sessions_needed,
                'required_percentage': 75.0
            }
            
        except Exception as e:
            logger.error(f"Error predicting attendance for student {student_id}, subject {subject_id}: {str(e)}")
            raise
    
    @staticmethod
    def refresh_cache():
        """
        Update attendance_statistics table (can run as cron job)
        This method would typically be called by a scheduled task to keep cached statistics up to date
        """
        try:
            # This is a placeholder implementation
            # In a production environment, this would:
            # 1. Iterate through all students
            # 2. Calculate their statistics
            # 3. Update the attendance_statistics table
            logger.info("Attendance statistics cache refresh initiated")
            
            # Example of how this might work:
            # students_query = text("SELECT student_id FROM students")
            # students_result = db.session.execute(students_query)
            # 
            # for student_row in students_result:
            #     student_id = student_row.student_id
            #     
            #     # Calculate overall stats
            #     overall_stats = AttendanceAnalyticsService.calculate_statistics(student_id)
            #     
            #     # Update overall stats in cache table
            #     upsert_query = text("""
            #         INSERT INTO attendance_statistics 
            #         (student_id, total_sessions, attended_sessions, absent_sessions, 
            #          late_sessions, attendance_percentage, academic_year, semester)
            #         VALUES 
            #         (:student_id, :total_sessions, :attended_sessions, :absent_sessions,
            #          :late_sessions, :attendance_percentage, :academic_year, :semester)
            #         ON DUPLICATE KEY UPDATE
            #         total_sessions = VALUES(total_sessions),
            #         attended_sessions = VALUES(attended_sessions),
            #         absent_sessions = VALUES(absent_sessions),
            #         late_sessions = VALUES(late_sessions),
            #         attendance_percentage = VALUES(attendance_percentage),
            #         last_updated = CURRENT_TIMESTAMP
            #     """)
            #     
            #     db.session.execute(upsert_query, {
            #         'student_id': student_id,
            #         'total_sessions': overall_stats['total_sessions'],
            #         'attended_sessions': overall_stats['attended_sessions'],
            #         'absent_sessions': overall_stats['absent_sessions'],
            #         'late_sessions': overall_stats['late_sessions'],
            #         'attendance_percentage': overall_stats['attendance_percentage'],
            #         'academic_year': '2024-2025',  # Would be dynamic in real implementation
            #         'semester': 1  # Would be dynamic in real implementation
            #     })
            #     
            #     # Calculate and cache subject-wise stats
            #     subject_stats = AttendanceAnalyticsService.get_subject_wise_statistics(student_id)
            #     for stat in subject_stats:
            #         subject_upsert_query = text("""
            #             INSERT INTO attendance_statistics 
            #             (student_id, subject_id, total_sessions, attended_sessions, absent_sessions, 
            #              late_sessions, attendance_percentage, academic_year, semester)
            #             VALUES 
            #             (:student_id, :subject_id, :total_sessions, :attended_sessions, :absent_sessions,
            #              :late_sessions, :attendance_percentage, :academic_year, :semester)
            #             ON DUPLICATE KEY UPDATE
            #             total_sessions = VALUES(total_sessions),
            #             attended_sessions = VALUES(attended_sessions),
            #             absent_sessions = VALUES(absent_sessions),
            #             late_sessions = VALUES(late_sessions),
            #             attendance_percentage = VALUES(attendance_percentage),
            #             last_updated = CURRENT_TIMESTAMP
            #         """)
            #         
            #         db.session.execute(subject_upsert_query, {
            #             'student_id': student_id,
            #             'subject_id': stat['subject_id'],
            #             'total_sessions': stat['total_sessions'],
            #             'attended_sessions': stat['attended_sessions'],
            #             'absent_sessions': stat['absent_sessions'],
            #             'late_sessions': stat['late_sessions'],
            #             'attendance_percentage': stat['attendance_percentage'],
            #             'academic_year': '2024-2025',  # Would be dynamic in real implementation
            #             'semester': 1  # Would be dynamic in real implementation
            #         })
            # 
            # db.session.commit()
            # logger.info("Attendance statistics cache refresh completed")
            
        except Exception as e:
            logger.error(f"Error refreshing attendance statistics cache: {str(e)}")
            db.session.rollback()
            raise

# Example usage (for testing purposes)
if __name__ == "__main__":
    # This would typically be run as part of the application
    # analytics_service = AttendanceAnalyticsService()
    # stats = analytics_service.calculate_statistics(student_id=1)
    # print(stats)
    pass