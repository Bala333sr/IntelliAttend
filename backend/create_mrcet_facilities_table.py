#!/usr/bin/env python3
"""
Script to create MRCET facilities table and insert facilities data
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def create_mrcet_facilities_table():
    """Create MRCET facilities table and insert data"""
    
    with app.app_context():
        try:
            # Create MRCET facilities table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS mrcet_facilities (
                facility_id INT AUTO_INCREMENT PRIMARY KEY,
                facility_name VARCHAR(100) NOT NULL,
                facility_type ENUM('Auditorium', 'Library', 'Laboratory', 'Sports', 'Dining', 'Medical', 'Transport', 'Support', 'Technology') NOT NULL,
                location VARCHAR(100), -- Building/block where facility is located
                capacity INT, -- Capacity if applicable
                description TEXT,
                features JSON, -- JSON formatted list of features
                operating_hours VARCHAR(100), -- e.g., "08:00-20:00"
                contact_info VARCHAR(200),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_facility_name (facility_name),
                INDEX idx_facility_type (facility_type),
                INDEX idx_location (location)
            );
            """
            
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("✅ MRCET facilities table created successfully!")
            
            # Insert MRCET facilities data
            facilities_data = [
                # Auditorium Complex
                {
                    'facility_name': 'Main Auditorium',
                    'facility_type': 'Auditorium',
                    'location': 'Main Academic Block',
                    'capacity': 500,
                    'description': '500-seat capacity with AC, multimedia projector, sound systems, Wi-Fi',
                    'features': '{"ac": true, "multimedia": true, "sound_system": true, "wifi": true}',
                    'operating_hours': '08:00-22:00',
                    'contact_info': 'auditorium@mrcet.edu.in'
                },
                {
                    'facility_name': 'Mini Auditorium',
                    'facility_type': 'Auditorium',
                    'location': 'Main Academic Block',
                    'capacity': 150,
                    'description': '150-seat capacity with AC and AV equipment',
                    'features': '{"ac": true, "av_equipment": true}',
                    'operating_hours': '08:00-22:00',
                    'contact_info': 'auditorium@mrcet.edu.in'
                },
                # Central Library
                {
                    'facility_name': 'Central Library',
                    'facility_type': 'Library',
                    'location': 'Main Academic Block',
                    'capacity': 200,
                    'description': '2-floor facility with books, e-books, international journals, CDs/DVDs, research reports',
                    'features': '{"wifi": true, "computers": true, "printers": true, "scanners": true, "digital_access": true}',
                    'operating_hours': '08:00-22:00',
                    'contact_info': 'library@mrcet.edu.in'
                },
                # Computer Labs
                {
                    'facility_name': 'CSE Computer Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Main Academic Block',
                    'capacity': 60,
                    'description': 'Computer lab for CSE students',
                    'features': '{"computers": 60, "internet": true, "projectors": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'cse-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'Programming Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Main Academic Block',
                    'capacity': 60,
                    'description': 'Programming lab for coding practice',
                    'features': '{"computers": 60, "internet": true, "projectors": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'cse-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'Data Structures Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Main Academic Block',
                    'capacity': 60,
                    'description': 'Lab for data structures implementation',
                    'features': '{"computers": 60, "internet": true, "projectors": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'cse-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'DBMS Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Main Academic Block',
                    'capacity': 60,
                    'description': 'Database Management Systems lab',
                    'features': '{"computers": 60, "internet": true, "projectors": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'cse-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'Software Engineering Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Main Academic Block',
                    'capacity': 60,
                    'description': 'Lab for software engineering projects',
                    'features': '{"computers": 60, "internet": true, "projectors": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'cse-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'AI/ML Lab',
                    'facility_type': 'Laboratory',
                    'location': 'CSE-AIML Block',
                    'capacity': 60,
                    'description': 'Artificial Intelligence and Machine Learning lab',
                    'features': '{"computers": 60, "gpu_servers": 5, "internet": true, "projectors": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'aiml-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'Cyber Security Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Main Academic Block',
                    'capacity': 40,
                    'description': 'Cyber Security lab with specialized equipment',
                    'features': '{"computers": 40, "security_tools": true, "internet": true, "projectors": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'cse-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'IoT Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Main Academic Block',
                    'capacity': 40,
                    'description': 'Internet of Things lab',
                    'features': '{"devices": 100, "sensors": true, "internet": true, "projectors": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'cse-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'Blockchain Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Main Academic Block',
                    'capacity': 40,
                    'description': 'Blockchain technology lab',
                    'features': '{"computers": 40, "blockchain_platforms": true, "internet": true, "projectors": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'cse-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'Big Data Analytics Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Main Academic Block',
                    'capacity': 40,
                    'description': 'Big Data Analytics lab',
                    'features': '{"computers": 40, "big_data_tools": true, "internet": true, "projectors": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'cse-hod@mrcet.edu.in'
                },
                # Electronics Labs
                {
                    'facility_name': 'Analog Digital & Communication Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Electronics & Electrical Block',
                    'capacity': 40,
                    'description': 'Analog and Digital Electronics with Communication lab',
                    'features': '{"workbenches": 20, "equipment": true, "oscilloscopes": 10, "signal_generators": 10}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'ece-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'VLSI Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Electronics & Electrical Block',
                    'capacity': 30,
                    'description': 'Very Large Scale Integration lab',
                    'features': '{"cad_tools": true, "simulation_software": true, "workstations": 30}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'ece-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'Microprocessor Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Electronics & Electrical Block',
                    'capacity': 40,
                    'description': 'Microprocessor and Microcontroller lab',
                    'features': '{"kits": 20, "development_boards": 20, "programmers": 10}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'ece-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'Electronic Devices Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Electronics & Electrical Block',
                    'capacity': 40,
                    'description': 'Electronic Devices and Circuits lab',
                    'features': '{"components": true, "test_equipment": true, "workbenches": 20}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'ece-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'Communication Networks Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Electronics & Electrical Block',
                    'capacity': 30,
                    'description': 'Communication Networks lab',
                    'features': '{"network_equipment": true, "simulation_software": true, "workstations": 30}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'ece-hod@mrcet.edu.in'
                },
                # Mechanical Labs
                {
                    'facility_name': 'Machine Tools Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Mechanical & Aeronautical Block',
                    'capacity': 40,
                    'description': 'Machine Tools and Manufacturing lab',
                    'features': '{"lathes": 5, "milling_machines": 3, "drilling_machines": 5, "grinding_machines": 3}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'mech-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'CAD & Simulation Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Mechanical & Aeronautical Block',
                    'capacity': 50,
                    'description': 'Computer Aided Design and Simulation lab',
                    'features': '{"computers": 50, "cad_software": true, "simulation_software": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'mech-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'Heat Transfer Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Mechanical & Aeronautical Block',
                    'capacity': 30,
                    'description': 'Heat Transfer lab',
                    'features': '{"heat_exchangers": 5, "boilers": 3, "temperature_measurement": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'mech-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'Fluid Mechanics Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Mechanical & Aeronautical Block',
                    'capacity': 30,
                    'description': 'Fluid Mechanics and Hydraulic Machines lab',
                    'features': '{"flow_measurement": true, "pumps": 5, "turbines": 3, "hydraulic_bench": 5}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'mech-hod@mrcet.edu.in'
                },
                {
                    'facility_name': 'Aircraft Production Technology Lab',
                    'facility_type': 'Laboratory',
                    'location': 'Mechanical & Aeronautical Block',
                    'capacity': 25,
                    'description': 'Aircraft Production Technology lab',
                    'features': '{"aircraft_components": true, "assembly_tools": true, "measurement_equipment": true}',
                    'operating_hours': '08:00-20:00',
                    'contact_info': 'aero-hod@mrcet.edu.in'
                },
                # Sports & Recreation
                {
                    'facility_name': 'Cricket Ground',
                    'facility_type': 'Sports',
                    'location': 'Sports Complex',
                    'capacity': 100,
                    'description': 'Full-size cricket ground with flood lights',
                    'features': '{"flood_lights": true, "pavilion": true, "boundary_fencing": true}',
                    'operating_hours': '06:00-20:00',
                    'contact_info': 'sports@mrcet.edu.in'
                },
                {
                    'facility_name': 'Football Ground',
                    'facility_type': 'Sports',
                    'location': 'Sports Complex',
                    'capacity': 100,
                    'description': 'Professional-size football field',
                    'features': '{"goal_posts": true, "changing_rooms": true, "flood_lights": true}',
                    'operating_hours': '06:00-20:00',
                    'contact_info': 'sports@mrcet.edu.in'
                },
                {
                    'facility_name': 'Basketball Courts',
                    'facility_type': 'Sports',
                    'location': 'Sports Complex',
                    'capacity': 50,
                    'description': '2 basketball courts suitable for tournaments',
                    'features': '{"flood_lights": true, "scoreboard": true, "changing_rooms": true}',
                    'operating_hours': '06:00-20:00',
                    'contact_info': 'sports@mrcet.edu.in'
                },
                {
                    'facility_name': 'Sports Hall',
                    'facility_type': 'Sports',
                    'location': 'Sports Complex',
                    'capacity': 100,
                    'description': 'Multi-purpose indoor sports facility',
                    'features': '{"badminton_courts": 3, "volleyball_courts": 2, "table_tennis_tables": 6}',
                    'operating_hours': '06:00-22:00',
                    'contact_info': 'sports@mrcet.edu.in'
                },
                {
                    'facility_name': 'Gymnasium',
                    'facility_type': 'Sports',
                    'location': 'Sports Complex',
                    'capacity': 50,
                    'description': 'Modern gym with equipment and weight training room',
                    'features': '{"cardio_equipment": 15, "weight_machines": 20, "free_weights": true, "changing_rooms": true}',
                    'operating_hours': '06:00-22:00',
                    'contact_info': 'sports@mrcet.edu.in'
                },
                # Dining & Food Services
                {
                    'facility_name': 'Main Cafeteria',
                    'facility_type': 'Dining',
                    'location': 'Administrative Block',
                    'capacity': 200,
                    'description': '200+ student capacity with multiple counters',
                    'features': '{"food_counters": 5, "seating": 200, "hygienic_preparation": true}',
                    'operating_hours': '07:30-21:30',
                    'contact_info': 'cafeteria@mrcet.edu.in'
                },
                {
                    'facility_name': 'Boys Hostel Dining Hall',
                    'facility_type': 'Dining',
                    'location': 'Boys Hostel Block',
                    'capacity': 200,
                    'description': 'Separate dining hall in boys hostel with varied menu',
                    'features': '{"seating": 200, "hygienic_preparation": true}',
                    'operating_hours': '07:00-22:00',
                    'contact_info': 'boys-hostel@mrcet.edu.in'
                },
                {
                    'facility_name': 'Girls Hostel Dining Hall',
                    'facility_type': 'Dining',
                    'location': 'Girls Hostel Block',
                    'capacity': 200,
                    'description': 'Separate dining hall in girls hostel with varied menu',
                    'features': '{"seating": 200, "hygienic_preparation": true}',
                    'operating_hours': '07:00-22:00',
                    'contact_info': 'girls-hostel@mrcet.edu.in'
                },
                # Medical & Health Services
                {
                    'facility_name': 'Health Center',
                    'facility_type': 'Medical',
                    'location': 'Administrative Block',
                    'capacity': 20,
                    'description': '24x7 medical facility with qualified doctor and nursing staff',
                    'features': '{"doctor": 1, "nurses": 3, "first_aid": true, "emergency_care": true, "ambulance": true}',
                    'operating_hours': '24x7',
                    'contact_info': 'healthcenter@mrcet.edu.in'
                },
                # Transport Services
                {
                    'facility_name': 'Transport Office',
                    'facility_type': 'Transport',
                    'location': 'Administrative Block',
                    'capacity': 0,
                    'description': '30+ buses covering 15+ routes across Hyderabad',
                    'features': '{"buses": 30, "ac_buses": true, "gps_tracking": true, "safety_features": true}',
                    'operating_hours': '05:00-22:00',
                    'contact_info': 'transport@mrcet.edu.in'
                },
                # Support Infrastructure
                {
                    'facility_name': 'Banking Services',
                    'facility_type': 'Support',
                    'location': 'Administrative Block',
                    'capacity': 50,
                    'description': 'ATM facilities for 6 different banks',
                    'features': '{"atm_machines": 6, "bank_branches": 2}',
                    'operating_hours': '24x7',
                    'contact_info': 'accounts@mrcet.edu.in'
                },
                {
                    'facility_name': 'Stationery Store',
                    'facility_type': 'Support',
                    'location': 'Administrative Block',
                    'capacity': 30,
                    'description': 'College stationery store and xerox center',
                    'features': '{"stationery": true, "xerox": true, "binding": true}',
                    'operating_hours': '09:00-18:00',
                    'contact_info': 'store@mrcet.edu.in'
                },
                {
                    'facility_name': 'Parking Areas',
                    'facility_type': 'Support',
                    'location': 'Campus Wide',
                    'capacity': 500,
                    'description': 'Vehicle parking areas across campus',
                    'features': '{"car_parking": 200, "bike_parking": 300, "security": true}',
                    'operating_hours': '24x7',
                    'contact_info': 'security@mrcet.edu.in'
                },
                # Technology Infrastructure
                {
                    'facility_name': 'Campus-wide Wi-Fi',
                    'facility_type': 'Technology',
                    'location': 'Campus Wide',
                    'capacity': 5000,
                    'description': 'Complete campus coverage with high-speed broadband',
                    'features': '{"high_speed": true, "coverage": "100%", "redundancy": true}',
                    'operating_hours': '24x7',
                    'contact_info': 'it-support@mrcet.edu.in'
                },
                {
                    'facility_name': 'ERP System',
                    'facility_type': 'Technology',
                    'location': 'IT Department',
                    'capacity': 5000,
                    'description': 'Comprehensive management system for academics and administration',
                    'features': '{"student_management": true, "faculty_management": true, "academics": true, "finance": true}',
                    'operating_hours': '24x7',
                    'contact_info': 'erp-support@mrcet.edu.in'
                },
                {
                    'facility_name': 'E-learning Platforms',
                    'facility_type': 'Technology',
                    'location': 'IT Department',
                    'capacity': 5000,
                    'description': 'Online learning and resource access platforms',
                    'features': '{"lms": true, "video_lectures": true, "online_assessments": true}',
                    'operating_hours': '24x7',
                    'contact_info': 'elearning@mrcet.edu.in'
                }
            ]
            
            # Clear existing data
            db.session.execute(text("DELETE FROM mrcet_facilities"))
            
            # Insert facilities data
            insert_sql = """
            INSERT INTO mrcet_facilities (
                facility_name, facility_type, location, capacity, description, features, operating_hours, contact_info
            ) VALUES (
                :facility_name, :facility_type, :location, :capacity, :description, :features, :operating_hours, :contact_info
            )
            """
            
            for facility in facilities_data:
                db.session.execute(text(insert_sql), facility)
            
            db.session.commit()
            print("✅ MRCET facilities data inserted successfully!")
            
            # Verify the data
            result = db.session.execute(text("SELECT COUNT(*) as count FROM mrcet_facilities"))
            row = result.fetchone()
            if row:
                print(f"✅ Total facilities in database: {row[0]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating MRCET facilities table: {e}")
            raise e

if __name__ == '__main__':
    create_mrcet_facilities_table()