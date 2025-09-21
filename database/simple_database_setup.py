#!/usr/bin/env python3
"""
Simple Database Setup for INTELLIATTEND
Creates basic tables needed for the system to work
"""

import pymysql
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration  
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'charset': 'utf8mb4',
    'port': int(os.environ.get('MYSQL_PORT', 3306))
}

DATABASE_NAME = 'IntelliAttend_DataBase'

def create_simple_database():
    """Create database and basic tables"""
    try:
        # Connect and create database
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {DATABASE_NAME}")
        
        # Create faculty table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faculty (
                faculty_id INT AUTO_INCREMENT PRIMARY KEY,
                faculty_code VARCHAR(20) UNIQUE NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone_number VARCHAR(15) UNIQUE NOT NULL,
                department VARCHAR(100) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Create students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                student_code VARCHAR(20) UNIQUE NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone_number VARCHAR(15),
                year_of_study INT,
                program VARCHAR(100) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Create classrooms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classrooms (
                classroom_id INT AUTO_INCREMENT PRIMARY KEY,
                room_number VARCHAR(20) UNIQUE NOT NULL,
                building_name VARCHAR(100) NOT NULL,
                floor_number INT,
                capacity INT DEFAULT 50,
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                geofence_radius DECIMAL(8, 2) DEFAULT 50.00,
                bluetooth_beacon_id VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Create classes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                class_id INT AUTO_INCREMENT PRIMARY KEY,
                class_name VARCHAR(100) NOT NULL,
                class_code VARCHAR(20) UNIQUE NOT NULL,
                faculty_id INT,
                classroom_id INT,
                schedule_day VARCHAR(20),
                start_time TIME,
                end_time TIME,
                semester VARCHAR(20),
                academic_year VARCHAR(9),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id),
                FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id)
            )
        """)
        
        # Create attendance_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_sessions (
                session_id INT AUTO_INCREMENT PRIMARY KEY,
                class_id INT,
                faculty_id INT,
                session_date DATE,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                qr_token VARCHAR(255) UNIQUE,
                qr_secret_key VARCHAR(255),
                qr_expires_at TIMESTAMP,
                otp_used VARCHAR(10),
                status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
                total_students_enrolled INT DEFAULT 0,
                total_students_present INT DEFAULT 0,
                attendance_percentage DECIMAL(5, 2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(class_id),
                FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
            )
        """)
        
        # Create attendance_records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_records (
                record_id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT,
                student_id INT,
                scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                biometric_verified BOOLEAN DEFAULT FALSE,
                location_verified BOOLEAN DEFAULT FALSE,
                bluetooth_verified BOOLEAN DEFAULT FALSE,
                gps_latitude DECIMAL(10, 8),
                gps_longitude DECIMAL(11, 8),
                gps_accuracy DECIMAL(8, 2),
                bluetooth_rssi INT,
                device_info TEXT,
                verification_score DECIMAL(3, 2) DEFAULT 0.00,
                status ENUM('present', 'late', 'absent', 'invalid') DEFAULT 'present',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        """)
        
        # Create otp_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_logs (
                otp_id INT AUTO_INCREMENT PRIMARY KEY,
                faculty_id INT,
                otp_code VARCHAR(10) NOT NULL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                used_at TIMESTAMP,
                session_id INT,
                is_used BOOLEAN DEFAULT FALSE,
                attempts INT DEFAULT 0,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id),
                FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id)
            )
        """)
        
        # Insert sample faculty
        faculty_password = generate_password_hash(os.environ.get('DEFAULT_FACULTY_PASSWORD', 'F@cultY2024!'))
        cursor.execute("""
            INSERT IGNORE INTO faculty (faculty_code, first_name, last_name, email, phone_number, department, password_hash)
            VALUES ('FAC001', 'John', 'Smith', 'john.smith@university.edu', '+1234567890', 'Computer Science', %s)
        """, (faculty_password,))
        
        # Insert sample student  
        student_password = generate_password_hash(os.environ.get('DEFAULT_STUDENT_PASSWORD', 'Stud3nt2024!'))
        cursor.execute("""
            INSERT IGNORE INTO students (student_code, first_name, last_name, email, password_hash, program, year_of_study)
            VALUES ('STU001', 'Alice', 'Williams', 'alice.williams@student.edu', %s, 'Computer Science', 3)
        """, (student_password,))
        
        # Insert sample classroom
        cursor.execute("""
            INSERT IGNORE INTO classrooms (room_number, building_name, floor_number, capacity, latitude, longitude)
            VALUES ('CS101', 'Computer Science Building', 1, 50, 40.7128, -74.0060)
        """)
        
        # Insert sample class
        cursor.execute("""
            INSERT IGNORE INTO classes (class_name, class_code, faculty_id, classroom_id, schedule_day, start_time, end_time, semester, academic_year)
            VALUES ('Advanced Software Engineering', 'CS451', 1, 1, 'Monday', '09:00:00', '11:00:00', 'Fall', '2024-2025')
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Simple database setup completed successfully!")
        print("📧 Faculty Login: john.smith@university.edu /", os.environ.get('DEFAULT_FACULTY_PASSWORD', 'F@cultY2024!'))
        print("📧 Student Login: alice.williams@student.edu /", os.environ.get('DEFAULT_STUDENT_PASSWORD', 'Stud3nt2024!'))
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Simple INTELLIATTEND Database Setup")
    print("=" * 40)
    create_simple_database()