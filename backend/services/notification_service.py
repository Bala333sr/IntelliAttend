#!/usr/bin/env python3
"""
Notification Service
Manages notification scheduling and delivery
Runs as background job (cron or worker)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app import db, scheduler
from sqlalchemy import text

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Manages notification scheduling and delivery
    Runs as background job (cron or worker)
    """
    
    @staticmethod
    def schedule_daily_reminders():
        """
        Schedule notifications for next day's classes
        This method would typically be called by a scheduled task
        """
        try:
            logger.info("Scheduling daily class reminders")
            
            # Get all students with class reminders enabled
            query = text("""
                SELECT DISTINCT s.student_id, s.email, s.first_name, s.last_name
                FROM students s
                JOIN notification_preferences np ON s.student_id = np.student_id
                WHERE np.class_reminder_enabled = TRUE AND s.is_active = TRUE
            """)
            
            result = db.session.execute(query)
            students = result.fetchall()
            
            logger.info(f"Found {len(students)} students with class reminders enabled")
            
            # For each student, check their timetable for tomorrow's classes
            for student in students:
                # Get tomorrow's classes for this student
                tomorrow_classes = NotificationService._get_tomorrow_classes(student.student_id)
                
                # Schedule reminders for each class
                for class_info in tomorrow_classes:
                    # Schedule the reminder based on student's preference
                    reminder_minutes = NotificationService._get_reminder_minutes(student.student_id)
                    reminder_time = class_info['start_time'] - timedelta(minutes=reminder_minutes)
                    
                    # Check if within quiet hours
                    if not NotificationService._is_within_quiet_hours(student.student_id, reminder_time):
                        # Schedule the notification
                        NotificationService._schedule_notification(
                            student_id=student.student_id,
                            notification_type='class_reminder',
                            title=f"Upcoming Class: {class_info['subject_name']}",
                            message=f"Your {class_info['subject_name']} class starts at {class_info['start_time'].strftime('%I:%M %p')}",
                            scheduled_time=reminder_time
                        )
            
            logger.info("Daily class reminders scheduled successfully")
            
        except Exception as e:
            logger.error(f"Error scheduling daily reminders: {str(e)}")
    
    @staticmethod
    def send_class_reminder(student_id: int, session_info: Dict):
        """
        Send class starting soon notification
        
        Args:
            student_id (int): The student ID
            session_info (Dict): Information about the session
        """
        try:
            # Check if notifications are enabled for this student
            if not NotificationService._is_notification_enabled(student_id, 'class_reminder'):
                return
            
            # Create notification message
            title = f"Upcoming Class: {session_info.get('subject_name', 'Class')}"
            message = f"Your class starts at {session_info.get('start_time', 'soon')}"
            
            # Log the notification
            NotificationService._log_notification(
                student_id=student_id,
                notification_type='class_reminder',
                title=title,
                message=message
            )
            
            logger.info(f"Class reminder sent to student {student_id}")
            
        except Exception as e:
            logger.error(f"Error sending class reminder to student {student_id}: {str(e)}")
    
    @staticmethod
    def send_warm_scan_reminder(student_id: int, session_info: Dict):
        """
        Notify warm scan window is open
        
        Args:
            student_id (int): The student ID
            session_info (Dict): Information about the session
        """
        try:
            # Check if notifications are enabled for this student
            if not NotificationService._is_notification_enabled(student_id, 'warm_scan'):
                return
            
            # Create notification message
            title = f"Warm Scan Window Open: {session_info.get('subject_name', 'Class')}"
            message = f"Warm scan window is now open for your class. You can mark attendance now."
            
            # Log the notification
            NotificationService._log_notification(
                student_id=student_id,
                notification_type='warm_scan',
                title=title,
                message=message
            )
            
            logger.info(f"Warm scan reminder sent to student {student_id}")
            
        except Exception as e:
            logger.error(f"Error sending warm scan reminder to student {student_id}: {str(e)}")
    
    @staticmethod
    def check_attendance_warnings():
        """
        Check for students below 75% and notify
        This method would typically be called by a scheduled task (daily/weekly)
        """
        try:
            logger.info("Checking for attendance warnings")
            
            # Get all students with attendance warnings enabled
            query = text("""
                SELECT DISTINCT s.student_id
                FROM students s
                JOIN notification_preferences np ON s.student_id = np.student_id
                WHERE np.attendance_warning_enabled = TRUE AND s.is_active = TRUE
            """)
            
            result = db.session.execute(query)
            students = result.fetchall()
            
            # For each student, check attendance statistics
            for student_row in students:
                student_id = student_row.student_id
                
                # Get overall attendance percentage (simplified)
                attendance_query = text("""
                    SELECT 
                        COUNT(*) as total_sessions,
                        SUM(CASE WHEN attendance_status = 'present' THEN 1 ELSE 0 END) as attended_sessions
                    FROM attendance_history 
                    WHERE student_id = :student_id
                """)
                
                attendance_result = db.session.execute(attendance_query, {'student_id': student_id})
                attendance_row = attendance_result.fetchone()
                
                if attendance_row and attendance_row.total_sessions > 0:
                    attendance_percentage = (attendance_row.attended_sessions / attendance_row.total_sessions) * 100
                    
                    # If below 75%, send warning
                    if attendance_percentage < 75:
                        NotificationService._send_attendance_warning(student_id, attendance_percentage)
            
            logger.info("Attendance warnings check completed")
            
        except Exception as e:
            logger.error(f"Error checking attendance warnings: {str(e)}")
    
    @staticmethod
    def send_weekly_summary(student_id: int):
        """
        Send weekly attendance summary
        
        Args:
            student_id (int): The student ID
        """
        try:
            # Check if notifications are enabled for this student
            if not NotificationService._is_notification_enabled(student_id, 'weekly_summary'):
                return
            
            # Get weekly attendance statistics (simplified)
            stats_query = text("""
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(CASE WHEN attendance_status = 'present' THEN 1 ELSE 0 END) as attended_sessions,
                    SUM(CASE WHEN attendance_status = 'absent' THEN 1 ELSE 0 END) as absent_sessions
                FROM attendance_history 
                WHERE student_id = :student_id 
                AND marked_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)
            
            stats_result = db.session.execute(stats_query, {'student_id': student_id})
            stats_row = stats_result.fetchone()
            
            if stats_row:
                total = stats_row.total_sessions or 0
                attended = stats_row.attended_sessions or 0
                absent = stats_row.absent_sessions or 0
                
                if total > 0:
                    percentage = (attended / total) * 100
                    
                    # Create notification message
                    title = "Weekly Attendance Summary"
                    message = f"This week: {attended} present, {absent} absent. Overall: {percentage:.1f}%"
                    
                    # Log the notification
                    NotificationService._log_notification(
                        student_id=student_id,
                        notification_type='weekly_summary',
                        title=title,
                        message=message
                    )
                    
                    logger.info(f"Weekly summary sent to student {student_id}")
            
        except Exception as e:
            logger.error(f"Error sending weekly summary to student {student_id}: {str(e)}")
    
    @staticmethod
    def _get_tomorrow_classes(student_id: int) -> List[Dict]:
        """
        Get tomorrow's classes for a student
        
        Args:
            student_id (int): The student ID
            
        Returns:
            List[Dict]: List of class information
        """
        try:
            # This is a simplified implementation
            # In a real system, you would query the timetable table
            # and join with subjects, etc.
            query = text("""
                SELECT 
                    t.id as session_id,
                    s.name as subject_name,
                    t.start_time,
                    t.end_time
                FROM timetable t
                JOIN prd_subjects s ON t.subject_id = s.id
                WHERE t.section_id = (
                    SELECT section_id FROM students WHERE student_id = :student_id
                )
                AND DAYOFWEEK(t.start_time) = DAYOFWEEK(DATE_ADD(CURDATE(), INTERVAL 1 DAY))
                ORDER BY t.start_time
            """)
            
            result = db.session.execute(query, {'student_id': student_id})
            classes = []
            
            for row in result:
                class_info = {
                    'session_id': row.session_id,
                    'subject_name': row.subject_name,
                    'start_time': row.start_time,
                    'end_time': row.end_time
                }
                classes.append(class_info)
            
            return classes
            
        except Exception as e:
            logger.error(f"Error getting tomorrow's classes for student {student_id}: {str(e)}")
            return []
    
    @staticmethod
    def _get_reminder_minutes(student_id: int) -> int:
        """
        Get reminder minutes preference for a student
        
        Args:
            student_id (int): The student ID
            
        Returns:
            int: Reminder minutes before class
        """
        try:
            query = text("""
                SELECT reminder_minutes_before
                FROM notification_preferences
                WHERE student_id = :student_id
            """)
            
            result = db.session.execute(query, {'student_id': student_id})
            row = result.fetchone()
            
            return row.reminder_minutes_before if row else 10
            
        except Exception as e:
            logger.error(f"Error getting reminder minutes for student {student_id}: {str(e)}")
            return 10
    
    @staticmethod
    def _is_within_quiet_hours(student_id: int, notification_time: datetime) -> bool:
        """
        Check if notification time is within quiet hours
        
        Args:
            student_id (int): The student ID
            notification_time (datetime): Time when notification would be sent
            
        Returns:
            bool: True if within quiet hours, False otherwise
        """
        try:
            query = text("""
                SELECT quiet_hours_start, quiet_hours_end
                FROM notification_preferences
                WHERE student_id = :student_id
            """)
            
            result = db.session.execute(query, {'student_id': student_id})
            row = result.fetchone()
            
            if not row or not row.quiet_hours_start or not row.quiet_hours_end:
                return False  # No quiet hours set
            
            # Extract time part from notification_time
            notification_hour = notification_time.hour
            notification_minute = notification_time.minute
            
            # Convert to minutes for comparison
            notification_minutes = notification_hour * 60 + notification_minute
            quiet_start_minutes = row.quiet_hours_start.hour * 60 + row.quiet_hours_start.minute
            quiet_end_minutes = row.quiet_hours_end.hour * 60 + row.quiet_hours_end.minute
            
            # Handle case where quiet hours cross midnight
            if quiet_start_minutes <= quiet_end_minutes:
                # Normal case: quiet hours don't cross midnight
                return quiet_start_minutes <= notification_minutes <= quiet_end_minutes
            else:
                # Quiet hours cross midnight (e.g., 22:00 to 06:00)
                return notification_minutes >= quiet_start_minutes or notification_minutes <= quiet_end_minutes
            
        except Exception as e:
            logger.error(f"Error checking quiet hours for student {student_id}: {str(e)}")
            return False
    
    @staticmethod
    def _is_notification_enabled(student_id: int, notification_type: str) -> bool:
        """
        Check if a specific notification type is enabled for a student
        
        Args:
            student_id (int): The student ID
            notification_type (str): Type of notification
            
        Returns:
            bool: True if enabled, False otherwise
        """
        try:
            column_map = {
                'class_reminder': 'class_reminder_enabled',
                'warm_scan': 'warm_scan_reminder_enabled',
                'attendance_warning': 'attendance_warning_enabled',
                'weekly_summary': 'weekly_summary_enabled'
            }
            
            if notification_type not in column_map:
                return True  # Default to enabled for unknown types
            
            column_name = column_map[notification_type]
            
            query = text(f"""
                SELECT {column_name}
                FROM notification_preferences
                WHERE student_id = :student_id
            """)
            
            result = db.session.execute(query, {'student_id': student_id})
            row = result.fetchone()
            
            return bool(row and row[0]) if row else True  # Default to enabled if no preferences
            
        except Exception as e:
            logger.error(f"Error checking if {notification_type} is enabled for student {student_id}: {str(e)}")
            return True  # Default to enabled on error
    
    @staticmethod
    def _schedule_notification(student_id: int, notification_type: str, title: str, message: str, scheduled_time: datetime):
        """
        Schedule a notification to be sent at a specific time
        
        Args:
            student_id (int): The student ID
            notification_type (str): Type of notification
            title (str): Notification title
            message (str): Notification message
            scheduled_time (datetime): When to send the notification
        """
        try:
            # In a real implementation, you would use a task queue like Celery
            # or a scheduler like APScheduler to actually schedule the notification
            # For now, we'll just log that it would be scheduled
            
            logger.info(f"Scheduled {notification_type} for student {student_id} at {scheduled_time}")
            
            # Log the scheduled notification
            insert_query = text("""
                INSERT INTO notification_log 
                (student_id, notification_type, title, message, sent_at)
                VALUES 
                (:student_id, :notification_type, :title, :message, :scheduled_time)
            """)
            
            db.session.execute(insert_query, {
                'student_id': student_id,
                'notification_type': notification_type,
                'title': title,
                'message': message,
                'scheduled_time': scheduled_time
            })
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error scheduling notification for student {student_id}: {str(e)}")
            db.session.rollback()
    
    @staticmethod
    def _log_notification(student_id: int, notification_type: str, title: str, message: str):
        """
        Log a notification that has been sent
        
        Args:
            student_id (int): The student ID
            notification_type (str): Type of notification
            title (str): Notification title
            message (str): Notification message
        """
        try:
            insert_query = text("""
                INSERT INTO notification_log 
                (student_id, notification_type, title, message)
                VALUES 
                (:student_id, :notification_type, :title, :message)
            """)
            
            db.session.execute(insert_query, {
                'student_id': student_id,
                'notification_type': notification_type,
                'title': title,
                'message': message
            })
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error logging notification for student {student_id}: {str(e)}")
            db.session.rollback()
    
    @staticmethod
    def _send_attendance_warning(student_id: int, percentage: float):
        """
        Send attendance warning notification
        
        Args:
            student_id (int): The student ID
            percentage (float): Current attendance percentage
        """
        try:
            # Create notification message
            title = "Attendance Warning"
            message = f"Your attendance is currently at {percentage:.1f}%, which is below the required 75%."
            
            # Log the notification
            NotificationService._log_notification(
                student_id=student_id,
                notification_type='attendance_warning',
                title=title,
                message=message
            )
            
            logger.info(f"Attendance warning sent to student {student_id} ({percentage:.1f}%)")
            
        except Exception as e:
            logger.error(f"Error sending attendance warning to student {student_id}: {str(e)}")

# Example of how to schedule the notification service methods
# These would typically be called by a cron job or scheduler

def schedule_notification_jobs():
    """Schedule notification-related background jobs"""
    try:
        # Schedule daily reminders every day at 9 PM
        scheduler.add_job(
            NotificationService.schedule_daily_reminders,
            'cron',
            hour=21,
            minute=0,
            id='daily_reminders'
        )
        
        # Schedule attendance warnings check every day at 8 PM
        scheduler.add_job(
            NotificationService.check_attendance_warnings,
            'cron',
            hour=20,
            minute=0,
            id='attendance_warnings'
        )
        
        logger.info("Notification jobs scheduled successfully")
        
    except Exception as e:
        logger.error(f"Error scheduling notification jobs: {str(e)}")

# Example usage (for testing purposes)
if __name__ == "__main__":
    # This would typically be run as part of the application
    # notification_service = NotificationService()
    # notification_service.schedule_daily_reminders()
    pass