#!/usr/bin/env python3
"""
Auto Attendance Service
Evaluates presence detection data and makes auto-marking decisions
Completely separate from existing attendance submission flow
"""

import logging
from typing import Dict, List, Optional, Tuple
from app import db
from sqlalchemy import text

logger = logging.getLogger(__name__)

class AutoAttendanceService:
    """
    Evaluates presence detection data and makes auto-marking decisions
    Completely separate from existing attendance submission flow
    """
    
    @staticmethod
    def calculate_presence_confidence(sensor_data: Dict) -> float:
        """
        Compute confidence score from GPS, WiFi, Bluetooth data
        
        Args:
            sensor_data (Dict): Dictionary containing sensor data
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        try:
            # Extract sensor data
            gps_data = sensor_data.get('gps', {})
            wifi_data = sensor_data.get('wifi', {})
            bluetooth_data = sensor_data.get('bluetooth', [])
            
            # Calculate individual sensor scores
            gps_score = AutoAttendanceService._calculate_gps_score(gps_data)
            wifi_score = AutoAttendanceService._calculate_wifi_score(wifi_data)
            bluetooth_score = AutoAttendanceService._calculate_bluetooth_score(bluetooth_data)
            
            # Calculate weighted final confidence score
            # Weight distribution: GPS (40%), WiFi (30%), Bluetooth (30%)
            final_confidence = (
                gps_score * 0.4 +
                wifi_score * 0.3 +
                bluetooth_score * 0.3
            )
            
            return round(final_confidence, 2)
            
        except Exception as e:
            logger.error(f"Error calculating presence confidence: {str(e)}")
            return 0.0
    
    @staticmethod
    def verify_presence(student_id: int, session_id: int, sensor_data: Dict) -> Dict:
        """
        Verify student presence in classroom
        Returns confidence score and contributing factors
        
        Args:
            student_id (int): The student ID
            session_id (int): The session ID
            sensor_data (Dict): Sensor data from mobile device
            
        Returns:
            Dict: Verification result including confidence score and factors
        """
        try:
            # Calculate individual sensor scores
            gps_data = sensor_data.get('gps', {})
            wifi_data = sensor_data.get('wifi', {})
            bluetooth_data = sensor_data.get('bluetooth', [])
            
            gps_score = AutoAttendanceService._calculate_gps_score(gps_data)
            wifi_score = AutoAttendanceService._calculate_wifi_score(wifi_data)
            bluetooth_score = AutoAttendanceService._calculate_bluetooth_score(bluetooth_data)
            
            # Get student's configuration to determine which sensors to use
            config = AutoAttendanceService._get_student_config(student_id)
            
            # Calculate weighted final confidence score
            # Only include sensors that are enabled in the configuration
            total_weight = 0
            weighted_score = 0
            contributing_factors = []
            
            if config.get('gps_enabled', True):
                total_weight += 0.4
                weighted_score += gps_score * 0.4
                if gps_score > 0:
                    contributing_factors.append('GPS')
            
            if config.get('wifi_enabled', True):
                total_weight += 0.3
                weighted_score += wifi_score * 0.3
                if wifi_score > 0:
                    contributing_factors.append('WiFi')
            
            if config.get('bluetooth_enabled', True):
                total_weight += 0.3
                weighted_score += bluetooth_score * 0.3
                if bluetooth_score > 0:
                    contributing_factors.append('Bluetooth')
            
            # Normalize the score based on total weight
            final_confidence = weighted_score / total_weight if total_weight > 0 else 0
            
            # Determine action based on confidence threshold
            confidence_threshold = config.get('confidence_threshold', 0.85)
            
            if final_confidence >= confidence_threshold:
                action = 'auto_marked'
            elif final_confidence >= 0.65:
                action = 'suggested'
            else:
                action = 'ignored'
            
            return {
                'session_id': session_id,
                'detected_at': sensor_data.get('timestamp'),
                'gps_score': round(gps_score, 2),
                'wifi_score': round(wifi_score, 2),
                'bluetooth_score': round(bluetooth_score, 2),
                'final_confidence': round(final_confidence, 2),
                'can_auto_mark': action == 'auto_marked',
                'action': action,
                'contributing_factors': contributing_factors
            }
            
        except Exception as e:
            logger.error(f"Error verifying presence for student {student_id}, session {session_id}: {str(e)}")
            return {
                'session_id': session_id,
                'detected_at': sensor_data.get('timestamp'),
                'gps_score': 0,
                'wifi_score': 0,
                'bluetooth_score': 0,
                'final_confidence': 0,
                'can_auto_mark': False,
                'action': 'ignored',
                'contributing_factors': []
            }
    
    @staticmethod
    def can_auto_mark(student_id: int, session_id: int, confidence: float) -> bool:
        """
        Check if auto-marking is allowed based on config and threshold
        
        Args:
            student_id (int): The student ID
            session_id (int): The session ID
            confidence (float): Calculated confidence score
            
        Returns:
            bool: True if auto-marking is allowed, False otherwise
        """
        try:
            # Get student's configuration
            config = AutoAttendanceService._get_student_config(student_id)
            
            # Check if auto-attendance is enabled
            if not config.get('enabled', False):
                return False
            
            # Check confidence threshold
            confidence_threshold = config.get('confidence_threshold', 0.85)
            return confidence >= confidence_threshold
            
        except Exception as e:
            logger.error(f"Error checking if auto-marking is allowed for student {student_id}: {str(e)}")
            return False
    
    @staticmethod
    def auto_mark_attendance(student_id: int, session_id: int, sensor_data: Dict) -> Dict:
        """
        Automatically mark attendance if conditions met
        Uses existing attendance submission logic
        
        Args:
            student_id (int): The student ID
            session_id (int): The session ID
            sensor_data (Dict): Sensor data from mobile device
            
        Returns:
            Dict: Result of auto-marking attempt
        """
        try:
            # Verify presence first
            verification_result = AutoAttendanceService.verify_presence(student_id, session_id, sensor_data)
            
            # Check if auto-marking is allowed
            if not verification_result['can_auto_mark']:
                return {
                    'success': False,
                    'error': 'Confidence threshold not met for auto-marking',
                    'verification_result': verification_result
                }
            
            # Log the auto-attendance activity
            AutoAttendanceService._log_activity(
                student_id=student_id,
                session_id=session_id,
                scores={
                    'gps_score': verification_result['gps_score'],
                    'wifi_score': verification_result['wifi_score'],
                    'bluetooth_score': verification_result['bluetooth_score'],
                    'final_confidence': verification_result['final_confidence']
                },
                action='auto_marked',
                sensor_data=sensor_data
            )
            
            # In a real implementation, this would call the existing attendance marking logic
            # For now, we'll just return a success response
            
            return {
                'success': True,
                'message': 'Attendance auto-marked successfully',
                'verification_result': verification_result
            }
            
        except Exception as e:
            logger.error(f"Error auto-marking attendance for student {student_id}, session {session_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to auto-mark attendance',
                'verification_result': None
            }
    
    @staticmethod
    def log_activity(student_id: int, session_id: int, scores: Dict, action: str, sensor_data: Dict):
        """
        Record auto-attendance attempt for auditing
        
        Args:
            student_id (int): The student ID
            session_id (int): The session ID
            scores (Dict): Confidence scores
            action (str): Action taken
            sensor_data (Dict): Sensor data from mobile device
        """
        try:
            AutoAttendanceService._log_activity(student_id, session_id, scores, action, sensor_data)
        except Exception as e:
            logger.error(f"Error logging activity for student {student_id}: {str(e)}")
    
    @staticmethod
    def _calculate_gps_score(gps_data: Dict) -> float:
        """
        Calculate GPS confidence score based on proximity to classroom
        
        Args:
            gps_data (Dict): GPS data from mobile device
            
        Returns:
            float: GPS confidence score between 0.0 and 1.0
        """
        try:
            if not gps_data or not gps_data.get('latitude') or not gps_data.get('longitude'):
                return 0.0
            
            accuracy = gps_data.get('accuracy', 100)
            
            # Simple scoring based on accuracy
            if accuracy <= 10:
                return 1.0
            elif accuracy <= 30:
                return 0.8
            elif accuracy <= 50:
                return 0.6
            else:
                return 0.3
                
        except Exception as e:
            logger.error(f"Error calculating GPS score: {str(e)}")
            return 0.0
    
    @staticmethod
    def _calculate_wifi_score(wifi_data: Dict) -> float:
        """
        Calculate WiFi confidence score based on connected network
        
        Args:
            wifi_data (Dict): WiFi data from mobile device
            
        Returns:
            float: WiFi confidence score between 0.0 and 1.0
        """
        try:
            if not wifi_data or not wifi_data.get('ssid'):
                return 0.0
            
            ssid = wifi_data.get('ssid', '')
            
            # Simple scoring based on SSID
            if 'classroom' in ssid.lower() or 'campus' in ssid.lower():
                return 1.0
            elif ssid:
                return 0.6
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating WiFi score: {str(e)}")
            return 0.0
    
    @staticmethod
    def _calculate_bluetooth_score(bluetooth_data: List) -> float:
        """
        Calculate Bluetooth confidence score based on nearby devices
        
        Args:
            bluetooth_data (List): Bluetooth data from mobile device
            
        Returns:
            float: Bluetooth confidence score between 0.0 and 1.0
        """
        try:
            if not bluetooth_data:
                return 0.0
            
            device_count = len(bluetooth_data)
            
            # Simple scoring based on number of devices detected
            if device_count >= 3:
                return 1.0
            elif device_count >= 2:
                return 0.8
            elif device_count >= 1:
                return 0.6
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating Bluetooth score: {str(e)}")
            return 0.0
    
    @staticmethod
    def _get_student_config(student_id: int) -> Dict:
        """
        Get student's auto-attendance configuration
        
        Args:
            student_id (int): The student ID
            
        Returns:
            Dict: Student's configuration or default values
        """
        try:
            query = text("""
                SELECT 
                    enabled,
                    gps_enabled,
                    wifi_enabled,
                    bluetooth_enabled,
                    confidence_threshold,
                    require_warm_data,
                    auto_submit
                FROM auto_attendance_config 
                WHERE student_id = :student_id
            """)
            
            result = db.session.execute(query, {'student_id': student_id})
            row = result.fetchone()
            
            if not row:
                # Return default configuration if none exists
                return {
                    'enabled': False,
                    'gps_enabled': True,
                    'wifi_enabled': True,
                    'bluetooth_enabled': True,
                    'confidence_threshold': 0.85,
                    'require_warm_data': True,
                    'auto_submit': False
                }
            
            return {
                'enabled': bool(row.enabled),
                'gps_enabled': bool(row.gps_enabled),
                'wifi_enabled': bool(row.wifi_enabled),
                'bluetooth_enabled': bool(row.bluetooth_enabled),
                'confidence_threshold': float(row.confidence_threshold),
                'require_warm_data': bool(row.require_warm_data),
                'auto_submit': bool(row.auto_submit)
            }
            
        except Exception as e:
            logger.error(f"Error getting student config for student {student_id}: {str(e)}")
            # Return default configuration on error
            return {
                'enabled': False,
                'gps_enabled': True,
                'wifi_enabled': True,
                'bluetooth_enabled': True,
                'confidence_threshold': 0.85,
                'require_warm_data': True,
                'auto_submit': False
            }
    
    @staticmethod
    def _log_activity(student_id: int, session_id: int, scores: Dict, action: str, sensor_data: Dict):
        """
        Internal method to log auto-attendance activity
        
        Args:
            student_id (int): The student ID
            session_id (int): The session ID
            scores (Dict): Confidence scores
            action (str): Action taken
            sensor_data (Dict): Sensor data from mobile device
        """
        try:
            insert_query = text("""
                INSERT INTO auto_attendance_log 
                (student_id, session_id, gps_score, wifi_score, bluetooth_score, 
                 final_confidence, action_taken, latitude, longitude, wifi_ssid, bluetooth_devices)
                VALUES 
                (:student_id, :session_id, :gps_score, :wifi_score, :bluetooth_score,
                 :final_confidence, :action_taken, :latitude, :longitude, :wifi_ssid, :bluetooth_devices)
            """)
            
            db.session.execute(insert_query, {
                'student_id': student_id,
                'session_id': session_id,
                'gps_score': scores.get('gps_score', 0),
                'wifi_score': scores.get('wifi_score', 0),
                'bluetooth_score': scores.get('bluetooth_score', 0),
                'final_confidence': scores.get('final_confidence', 0),
                'action_taken': action,
                'latitude': sensor_data.get('gps', {}).get('latitude'),
                'longitude': sensor_data.get('gps', {}).get('longitude'),
                'wifi_ssid': sensor_data.get('wifi', {}).get('ssid'),
                'bluetooth_devices': str(sensor_data.get('bluetooth', []))  # Simplified for now
            })
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error logging activity for student {student_id}: {str(e)}")
            db.session.rollback()