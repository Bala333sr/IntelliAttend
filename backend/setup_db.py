#!/usr/bin/env python3
"""
Database Setup Script for IntelliAttend
Creates all necessary tables and initializes sample data
"""

import os
import sys
from datetime import datetime, time
from werkzeug.security import generate_password_hash

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Classes, Faculty, Student, Classroom, Admin

def create_tables():
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")

def create_sample_data():
    """Create sample data for testing"""
    with app.app_context():
        # Check if sample data already exists
        if Faculty.query.first():
            print("⚠️  Sample data already exists")
            return
        
        # Create sample classrooms
        classroom1 = Classroom(
            room_number="A101",
            building_name="Main Building",
            floor_number=1,
            capacity=50,
            latitude=40.7128,
            longitude=-74.0060,
            geofence_radius=50.00,
            bluetooth_beacon_id="BEACON-A101",
            is_active=True
        )
        
        classroom2 = Classroom(
            room_number="B205",
            building_name="Science Building",
            floor_number=2,
            capacity=30,
            latitude=40.7135,
            longitude=-74.0072,
            geofence_radius=30.00,
            bluetooth_beacon_id="BEACON-B205",
            is_active=True
        )
        
        db.session.add(classroom1)
        db.session.add(classroom2)
        db.session.commit()  # Commit classrooms first
        
        # Create sample faculty
        faculty1 = Faculty(
            faculty_code="FAC001",
            first_name="John",
            last_name="Smith",
            email="john.smith@university.edu",
            phone_number="+1234567890",
            department="Computer Science",
            password_hash=generate_password_hash(os.environ.get('DEFAULT_FACULTY_PASSWORD', 'faculty123')),
            is_active=True
        )
        
        faculty2 = Faculty(
            faculty_code="FAC002",
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@university.edu",
            phone_number="+1234567891",
            department="Mathematics",
            password_hash=generate_password_hash(os.environ.get('DEFAULT_FACULTY_PASSWORD', 'faculty123')),
            is_active=True
        )
        
        db.session.add(faculty1)
        db.session.add(faculty2)
        db.session.commit()  # Commit faculty before classes
        
        # Create sample students
        students = []
        for i in range(1, 21):
            student = Student(
                student_code=f"STU{i:03d}",
                first_name=f"Student{i}",
                last_name=f"Lastname{i}",
                email=f"student{i}@student.edu",
                program="Computer Science",
                password_hash=generate_password_hash(os.environ.get('DEFAULT_STUDENT_PASSWORD', 'student123')),
                phone_number=f"+12345678{i:02d}",
                year_of_study=2,
                is_active=True
            )
            students.append(student)
        
        db.session.add_all(students)
        db.session.commit()  # Commit students before classes
        
        # Create sample classes
        class1 = Classes(
            class_code="CS101",
            class_name="Introduction to Programming",
            faculty_id=1,
            semester="Fall",
            academic_year="2023-2024",
            classroom_id=1,
            credits=3,
            max_students=50,
            schedule_day="Monday",
            start_time=time(10, 30),
            end_time=time(11, 30),
            is_active=True
        )
        
        class2 = Classes(
            class_code="CS201",
            class_name="Data Structures",
            faculty_id=1,
            semester="Fall",
            academic_year="2023-2024",
            classroom_id=2,
            credits=3,
            max_students=30,
            schedule_day="Wednesday",
            start_time=time(14, 0),
            end_time=time(15, 0),
            is_active=True
        )
        
        class3 = Classes(
            class_code="MATH101",
            class_name="Calculus I",
            faculty_id=2,
            semester="Fall",
            academic_year="2023-2024",
            classroom_id=1,
            credits=4,
            max_students=50,
            schedule_day="Tuesday",
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_active=True
        )
        
        db.session.add(class1)
        db.session.add(class2)
        db.session.add(class3)
        
        # Commit all changes
        db.session.commit()
        print("✅ Sample data created successfully")

def create_admin_user():
    """Create default admin user if it doesn't exist"""
    with app.app_context():
        # Check if admin user already exists
        admin = Admin.query.filter_by(username='admin').first()
        if admin:
            print("⚠️  Admin user already exists")
            return
        
        # Create default admin user
        admin = Admin(
            username='admin',
            email='admin@intelliattend.com',
            password_hash=generate_password_hash('admin123'),
            first_name='System',
            last_name='Administrator',
            role='super_admin',
            is_active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin user created successfully")

def main():
    """Main setup function"""
    print("🚀 Setting up IntelliAttend Database...")
    print("=" * 50)
    
    try:
        create_tables()
        create_sample_data()
        create_admin_user()
        print("=" * 50)
        print("🎉 Database setup completed successfully!")
        print("\nSample accounts:")
        print("Faculty: john.smith@university.edu / (DEFAULT_FACULTY_PASSWORD environment variable or 'faculty123' if not set)")
        print("Student: student1@student.edu / (DEFAULT_STUDENT_PASSWORD environment variable or 'student123' if not set)")
        print("SmartBoard Default OTP: 000000")
        print("Admin Portal: http://localhost:5002/admin")
        print("Admin Username: admin")
        print("Admin Password: admin123")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()