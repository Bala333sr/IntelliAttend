#!/usr/bin/env python3
"""
Script to add CSE-AIML block coordinates to the classrooms table
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def add_cse_aiml_coordinates():
    """Add CSE-AIML block coordinates to the classrooms table"""
    
    with app.app_context():
        try:
            print("Adding CSE-AIML block coordinates to classrooms...")
            
            # Define the CSE-AIML block points
            cse_aiml_points = [
                {"name": "CSE-AIML Point 1", "latitude": 17.5605259, "longitude": 78.4551113, "room_number": "AIML-01", "building_name": "CSE-AIML Block"},
                {"name": "CSE-AIML Point 2", "latitude": 17.560811, "longitude": 78.4551743, "room_number": "AIML-02", "building_name": "CSE-AIML Block"},
                {"name": "CSE-AIML Point 3", "latitude": 17.5606614, "longitude": 78.4558355, "room_number": "AIML-03", "building_name": "CSE-AIML Block"},
                {"name": "CSE-AIML Point 4", "latitude": 17.5603839, "longitude": 78.4557671, "room_number": "AIML-04", "building_name": "CSE-AIML Block"}
            ]
            
            # Define the CSE-AIML polygon (as a representative point for the building)
            # We'll use the centroid of the polygon as the main building location
            # Centroid calculation: (78.4551113 + 78.4557671 + 78.4558355 + 78.4555525 + 78.4555659 + 78.4554828 + 78.4554626 + 78.4551743) / 8 = 78.4554966
            # Centroid calculation: (17.5605259 + 17.5603839 + 17.5606614 + 17.5607343 + 17.5608084 + 17.5608302 + 17.5607509 + 17.560811) / 8 = 17.5606883
            cse_aiml_building = {
                "name": "CSE-AIML Main Building", 
                "latitude": 17.5606883, 
                "longitude": 78.4554966, 
                "room_number": "AIML-BLDG", 
                "building_name": "CSE-AIML Block",
                "capacity": 200,
                "geofence_radius": 100.00
            }
            
            # Add the polygon data as a separate entry for geofencing purposes
            cse_aiml_polygon = {
                "name": "CSE-AIML Polygon Area",
                "latitude": 17.5606883,  # Centroid of the polygon
                "longitude": 78.4554966,  # Centroid of the polygon
                "room_number": "AIML-POLY",
                "building_name": "CSE-AIML Block",
                "capacity": 300,
                "geofence_radius": 150.00  # Larger radius to cover the polygon area
            }
            
            # Add individual points
            print("1. Adding individual CSE-AIML points...")
            for point in cse_aiml_points:
                # Check if point already exists
                check_point_sql = """
                SELECT classroom_id FROM classrooms 
                WHERE room_number = :room_number AND building_name = :building_name 
                LIMIT 1
                """
                result = db.session.execute(text(check_point_sql), {
                    'room_number': point['room_number'],
                    'building_name': point['building_name']
                }).fetchone()
                
                if not result:
                    insert_point_sql = """
                    INSERT INTO classrooms (room_number, building_name, latitude, longitude, capacity, geofence_radius)
                    VALUES (:room_number, :building_name, :latitude, :longitude, :capacity, :geofence_radius)
                    """
                    db.session.execute(text(insert_point_sql), {
                        'room_number': point['room_number'],
                        'building_name': point['building_name'],
                        'latitude': point['latitude'],
                        'longitude': point['longitude'],
                        'capacity': 30,
                        'geofence_radius': 30.00
                    })
                    print(f"   Added point: {point['name']} ({point['latitude']}, {point['longitude']})")
                else:
                    print(f"   Point already exists: {point['name']}")
            
            # Add main building
            print("2. Adding CSE-AIML main building...")
            check_building_sql = """
            SELECT classroom_id FROM classrooms 
            WHERE room_number = :room_number AND building_name = :building_name 
            LIMIT 1
            """
            result = db.session.execute(text(check_building_sql), {
                'room_number': cse_aiml_building['room_number'],
                'building_name': cse_aiml_building['building_name']
            }).fetchone()
            
            if not result:
                insert_building_sql = """
                INSERT INTO classrooms (room_number, building_name, latitude, longitude, capacity, geofence_radius)
                VALUES (:room_number, :building_name, :latitude, :longitude, :capacity, :geofence_radius)
                """
                db.session.execute(text(insert_building_sql), {
                    'room_number': cse_aiml_building['room_number'],
                    'building_name': cse_aiml_building['building_name'],
                    'latitude': cse_aiml_building['latitude'],
                    'longitude': cse_aiml_building['longitude'],
                    'capacity': cse_aiml_building['capacity'],
                    'geofence_radius': cse_aiml_building['geofence_radius']
                })
                print(f"   Added building: {cse_aiml_building['name']} ({cse_aiml_building['latitude']}, {cse_aiml_building['longitude']})")
            else:
                print(f"   Building already exists: {cse_aiml_building['name']}")
            
            # Add polygon area for geofencing
            print("3. Adding CSE-AIML polygon area...")
            check_polygon_sql = """
            SELECT classroom_id FROM classrooms 
            WHERE room_number = :room_number AND building_name = :building_name 
            LIMIT 1
            """
            result = db.session.execute(text(check_polygon_sql), {
                'room_number': cse_aiml_polygon['room_number'],
                'building_name': cse_aiml_polygon['building_name']
            }).fetchone()
            
            if not result:
                insert_polygon_sql = """
                INSERT INTO classrooms (room_number, building_name, latitude, longitude, capacity, geofence_radius)
                VALUES (:room_number, :building_name, :latitude, :longitude, :capacity, :geofence_radius)
                """
                db.session.execute(text(insert_polygon_sql), {
                    'room_number': cse_aiml_polygon['room_number'],
                    'building_name': cse_aiml_polygon['building_name'],
                    'latitude': cse_aiml_polygon['latitude'],
                    'longitude': cse_aiml_polygon['longitude'],
                    'capacity': cse_aiml_polygon['capacity'],
                    'geofence_radius': cse_aiml_polygon['geofence_radius']
                })
                print(f"   Added polygon area: {cse_aiml_polygon['name']} ({cse_aiml_polygon['latitude']}, {cse_aiml_polygon['longitude']})")
            else:
                print(f"   Polygon area already exists: {cse_aiml_polygon['name']}")
            
            db.session.commit()
            print("✅ CSE-AIML coordinates added successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding CSE-AIML coordinates: {e}")
            raise e

if __name__ == '__main__':
    add_cse_aiml_coordinates()