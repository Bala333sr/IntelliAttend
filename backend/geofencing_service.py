#!/usr/bin/env python3
"""
IntelliAttend Geofencing Service
================================
Professional-grade geofencing using Tile38 for real-time location validation.

Features:
- Sub-second geofence queries
- Classroom boundary management
- Accuracy-weighted distance calculations
- Security event logging
- Performance monitoring

Tile38 Documentation: https://tile38.com/
"""

import os
import logging
import redis
from typing import Tuple, Optional, Dict, Any
from decimal import Decimal
import json
from datetime import datetime
import math

logger = logging.getLogger(__name__)


class GeofencingService:
    """Professional geofencing service with Tile38 integration"""
    
    def __init__(self, host: str = None, port: int = None):
        """
        Initialize Tile38 connection
        
        Args:
            host: Tile38 server host (default: localhost)
            port: Tile38 server port (default: 9851)
        """
        self.host = host or os.environ.get('TILE38_HOST', 'localhost')
        self.port = port or int(os.environ.get('TILE38_PORT', 9851))
        
        try:
            # Connect to Tile38 (uses Redis protocol)
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # Test connection
            self.client.ping()
            logger.info(f"✅ Connected to Tile38 at {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Tile38: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Tile38 is available"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def set_classroom_geofence(
        self,
        classroom_id: int,
        latitude: float,
        longitude: float,
        radius: float = 50.0,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Set or update classroom geofence
        
        Args:
            classroom_id: Unique classroom identifier
            latitude: Classroom latitude (decimal degrees)
            longitude: Classroom longitude (decimal degrees)
            radius: Geofence radius in meters (default: 50m)
            metadata: Additional classroom metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.warning("Tile38 not available, skipping geofence set")
            return False
        
        try:
            # Tile38 SET command with POINT
            # Format: SET key id POINT lat lon
            key = "classrooms"
            object_id = f"classroom_{classroom_id}"
            
            # Build command
            command = ['SET', key, object_id]
            
            # Add metadata as FIELD (optional)
            if metadata:
                for field_key, field_value in metadata.items():
                    command.extend(['FIELD', field_key, str(field_value)])
            
            # Add radius as metadata
            command.extend(['FIELD', 'radius', str(radius)])
            
            # Add POINT coordinates
            command.extend(['POINT', str(latitude), str(longitude)])
            
            # Execute command
            self.client.execute_command(*command)
            
            logger.info(f"✅ Set geofence for classroom {classroom_id}: ({latitude}, {longitude}) r={radius}m")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to set geofence for classroom {classroom_id}: {e}")
            return False
    
    def check_within_geofence(
        self,
        classroom_id: int,
        student_lat: float,
        student_lon: float,
        gps_accuracy: Optional[float] = None
    ) -> Tuple[bool, Optional[float], Dict[str, Any]]:
        """
        Check if student location is within classroom geofence
        
        Args:
            classroom_id: Classroom to check against
            student_lat: Student latitude
            student_lon: Student longitude
            gps_accuracy: GPS accuracy in meters (optional)
            
        Returns:
            Tuple of (is_within, distance_meters, details)
            - is_within: True if within geofence
            - distance_meters: Distance to classroom center
            - details: Additional validation details
        """
        if not self.is_available():
            logger.warning("Tile38 not available, falling back to haversine")
            return self._fallback_geofence_check(classroom_id, student_lat, student_lon, gps_accuracy)
        
        try:
            key = "classrooms"
            object_id = f"classroom_{classroom_id}"
            
            # Get classroom data
            classroom_data = self._get_classroom_data(classroom_id)
            if not classroom_data:
                logger.warning(f"Classroom {classroom_id} not found in Tile38")
                return False, None, {'error': 'classroom_not_found'}
            
            classroom_lat = classroom_data['latitude']
            classroom_lon = classroom_data['longitude']
            radius = classroom_data.get('radius', 50.0)
            
            # Calculate distance using Haversine formula
            distance = self._calculate_haversine_distance(
                student_lat, student_lon,
                classroom_lat, classroom_lon
            )
            
            # Accuracy-weighted validation
            if gps_accuracy:
                # If GPS accuracy is poor, adjust threshold
                effective_radius = radius + (gps_accuracy / 2)
                is_within = distance <= effective_radius
                
                details = {
                    'distance_meters': round(distance, 2),
                    'geofence_radius': radius,
                    'effective_radius': round(effective_radius, 2),
                    'gps_accuracy': gps_accuracy,
                    'accuracy_adjustment': round(gps_accuracy / 2, 2),
                    'confidence': 'high' if gps_accuracy < 20 else 'medium' if gps_accuracy < 50 else 'low'
                }
            else:
                # No accuracy provided, use strict radius
                is_within = distance <= radius
                details = {
                    'distance_meters': round(distance, 2),
                    'geofence_radius': radius,
                    'confidence': 'unknown'
                }
            
            logger.debug(f"Geofence check for classroom {classroom_id}: within={is_within}, distance={distance:.2f}m")
            
            return is_within, distance, details
            
        except Exception as e:
            logger.error(f"❌ Geofence check failed: {e}")
            return False, None, {'error': str(e)}
    
    def get_nearby_classrooms(
        self,
        latitude: float,
        longitude: float,
        radius: float = 100.0,
        limit: int = 10
    ) -> list:
        """
        Find classrooms near a given location
        
        Args:
            latitude: Search center latitude
            longitude: Search center longitude
            radius: Search radius in meters
            limit: Maximum number of results
            
        Returns:
            List of nearby classrooms with distances
        """
        if not self.is_available():
            return []
        
        try:
            # Tile38 NEARBY command
            # FORMAT: NEARBY key POINT lat lon radius [LIMIT count]
            command = [
                'NEARBY', 'classrooms',
                'POINT', str(latitude), str(longitude),
                str(radius),
                'LIMIT', str(limit)
            ]
            
            result = self.client.execute_command(*command)
            
            # Parse result
            classrooms = []
            if result and len(result) > 1:
                items = result[1]  # Skip count
                for item in items:
                    if isinstance(item, list) and len(item) >= 2:
                        classroom_id = item[0].replace('classroom_', '')
                        # Distance might be in item[1] if returned
                        classrooms.append({
                            'classroom_id': int(classroom_id),
                            'object_id': item[0]
                        })
            
            return classrooms
            
        except Exception as e:
            logger.error(f"❌ Failed to find nearby classrooms: {e}")
            return []
    
    def batch_load_classrooms(self, classrooms_data: list) -> int:
        """
        Batch load classroom geofences
        
        Args:
            classrooms_data: List of dicts with classroom data
                [
                    {
                        'classroom_id': 1,
                        'latitude': 37.7749,
                        'longitude': -122.4194,
                        'radius': 50.0,
                        'metadata': {...}
                    },
                    ...
                ]
        
        Returns:
            Number of successfully loaded classrooms
        """
        if not self.is_available():
            logger.error("Tile38 not available for batch load")
            return 0
        
        success_count = 0
        for classroom in classrooms_data:
            if self.set_classroom_geofence(
                classroom_id=classroom['classroom_id'],
                latitude=classroom['latitude'],
                longitude=classroom['longitude'],
                radius=classroom.get('radius', 50.0),
                metadata=classroom.get('metadata')
            ):
                success_count += 1
        
        logger.info(f"✅ Batch loaded {success_count}/{len(classrooms_data)} classrooms")
        return success_count
    
    def delete_classroom_geofence(self, classroom_id: int) -> bool:
        """
        Delete classroom geofence
        
        Args:
            classroom_id: Classroom to delete
            
        Returns:
            True if successful
        """
        if not self.is_available():
            return False
        
        try:
            key = "classrooms"
            object_id = f"classroom_{classroom_id}"
            
            self.client.execute_command('DEL', key, object_id)
            logger.info(f"✅ Deleted geofence for classroom {classroom_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete geofence: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get Tile38 statistics
        
        Returns:
            Dictionary with statistics
        """
        if not self.is_available():
            return {'status': 'unavailable'}
        
        try:
            # Get server info
            info = self.client.info()
            
            # Get classroom count
            count_result = self.client.execute_command('SCAN', 'classrooms', 'COUNT')
            classroom_count = count_result[0] if count_result else 0
            
            return {
                'status': 'online',
                'host': self.host,
                'port': self.port,
                'classroom_count': classroom_count,
                'memory_used': info.get('used_memory_human', 'N/A'),
                'uptime_seconds': info.get('uptime_in_seconds', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get statistics: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _get_classroom_data(self, classroom_id: int) -> Optional[Dict[str, Any]]:
        """Get classroom data from Tile38"""
        try:
            key = "classrooms"
            object_id = f"classroom_{classroom_id}"
            
            # GET command returns object data
            result = self.client.execute_command('GET', key, object_id, 'WITHFIELDS', 'POINT')
            
            if not result or not isinstance(result, dict):
                return None
            
            # Parse coordinates and fields
            coordinates = result.get('coordinates', [])
            fields = result.get('fields', {})
            
            if len(coordinates) >= 2:
                return {
                    'latitude': float(coordinates[1]),
                    'longitude': float(coordinates[0]),
                    'radius': float(fields.get('radius', 50.0)),
                    'fields': fields
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get classroom data: {e}")
            return None
    
    def _calculate_haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two points using Haversine formula
        
        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) *
             math.sin(delta_lambda / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def _fallback_geofence_check(
        self,
        classroom_id: int,
        student_lat: float,
        student_lon: float,
        gps_accuracy: Optional[float]
    ) -> Tuple[bool, Optional[float], Dict[str, Any]]:
        """
        Fallback geofence check when Tile38 is unavailable
        Uses database lookup and Haversine calculation
        """
        try:
            # Import here to avoid circular imports
            from app import Classroom
            
            classroom = Classroom.query.get(classroom_id)
            if not classroom or not classroom.latitude or not classroom.longitude:
                return False, None, {'error': 'classroom_not_found'}
            
            classroom_lat = float(classroom.latitude)
            classroom_lon = float(classroom.longitude)
            radius = float(classroom.geofence_radius) if classroom.geofence_radius else 50.0
            
            distance = self._calculate_haversine_distance(
                student_lat, student_lon,
                classroom_lat, classroom_lon
            )
            
            if gps_accuracy:
                effective_radius = radius + (gps_accuracy / 2)
                is_within = distance <= effective_radius
            else:
                is_within = distance <= radius
            
            return is_within, distance, {
                'distance_meters': round(distance, 2),
                'geofence_radius': radius,
                'fallback_mode': True
            }
            
        except Exception as e:
            logger.error(f"Fallback geofence check failed: {e}")
            return False, None, {'error': str(e)}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def initialize_geofencing_from_database():
    """
    Initialize Tile38 geofences from database classrooms
    Should be called on application startup
    """
    try:
        from app import Classroom, app
        
        with app.app_context():
            geo_service = GeofencingService()
            
            if not geo_service.is_available():
                logger.warning("⚠️  Tile38 not available, skipping geofence initialization")
                return
            
            # Load all active classrooms
            classrooms = Classroom.query.filter_by(is_active=True).all()
            
            classrooms_data = []
            for classroom in classrooms:
                if classroom.latitude and classroom.longitude:
                    classrooms_data.append({
                        'classroom_id': classroom.classroom_id,
                        'latitude': float(classroom.latitude),
                        'longitude': float(classroom.longitude),
                        'radius': float(classroom.geofence_radius) if classroom.geofence_radius else 50.0,
                        'metadata': {
                            'room_number': classroom.room_number,
                            'building': classroom.building_name,
                            'capacity': classroom.capacity
                        }
                    })
            
            if classrooms_data:
                count = geo_service.batch_load_classrooms(classrooms_data)
                logger.info(f"✅ Initialized {count} classroom geofences in Tile38")
            else:
                logger.warning("No classrooms with coordinates found")
                
    except Exception as e:
        logger.error(f"❌ Failed to initialize geofencing: {e}")


def test_geofencing_service():
    """Test geofencing service functionality"""
    print("\n" + "="*60)
    print("🧪 TESTING GEOFENCING SERVICE")
    print("="*60)
    
    # Initialize service
    geo = GeofencingService()
    
    # Check availability
    if not geo.is_available():
        print("❌ Tile38 not available. Please start Tile38 server:")
        print("   brew install tile38")
        print("   tile38-server")
        return
    
    print("✅ Tile38 connection successful")
    
    # Test data
    test_classroom_id = 9999
    classroom_lat, classroom_lon = 37.7749, -122.4194
    radius = 50.0
    
    # Set geofence
    print(f"\n📍 Setting test geofence...")
    success = geo.set_classroom_geofence(
        test_classroom_id,
        classroom_lat,
        classroom_lon,
        radius,
        metadata={'test': True}
    )
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test within geofence
    print(f"\n🎯 Testing location INSIDE geofence...")
    within, dist, details = geo.check_within_geofence(
        test_classroom_id,
        classroom_lat + 0.0001,  # ~11 meters away
        classroom_lon + 0.0001,
        gps_accuracy=10.0
    )
    print(f"   Within: {within}, Distance: {dist:.2f}m")
    print(f"   Details: {details}")
    
    # Test outside geofence
    print(f"\n🎯 Testing location OUTSIDE geofence...")
    within, dist, details = geo.check_within_geofence(
        test_classroom_id,
        classroom_lat + 0.001,  # ~111 meters away
        classroom_lon + 0.001,
        gps_accuracy=10.0
    )
    print(f"   Within: {within}, Distance: {dist:.2f}m")
    print(f"   Details: {details}")
    
    # Get statistics
    print(f"\n📊 Service Statistics:")
    stats = geo.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Cleanup
    print(f"\n🧹 Cleaning up test data...")
    geo.delete_classroom_geofence(test_classroom_id)
    print("✅ Test complete!")
    print("="*60 + "\n")


if __name__ == '__main__':
    # Run tests
    test_geofencing_service()
