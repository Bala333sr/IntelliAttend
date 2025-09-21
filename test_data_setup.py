#!/usr/bin/env python3
"""
IntelliAttend Test Data Setup Script
Adds comprehensive test data for system testing
"""

import sys
import os
import bcrypt
from datetime import datetime, timedelta

# Add the backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db, Admin, Faculty, Student, Classes, Classroom, StudentClassEnrollment

def create_test_admin():
    """Create test admin user"""
    try:
        # Check if admin already exists
        existing_admin = Admin.query.filter_by(username='testadmin').first()
        if existing_admin:
            print("✓ Test admin already exists")
            return existing_admin
        
        # Create new admin
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin = Admin(
            username='testadmin',
            email='admin@intelliattend.com',
            password_hash=password_hash,
            first_name='Test',
            last_name='Admin',
            role='super_admin',
            is_active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print("✓ Created test admin: testadmin/admin123")
        return admin
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creating admin: {e}")
        return None

def create_test_classrooms():
    """Create test classrooms"""
    classrooms_data = [
        {
            'room_number': 'CS101',
            'building_name': 'Computer Science Building',
            'floor_number': 1,
            'capacity': 30,
            'latitude': 40.7128,
            'longitude': -74.0060,
            'geofence_radius': 50.00,
            'bluetooth_beacon_id': 'CS101_BEACON',
            'is_active': True
        },
        {
            'room_number': 'MATH201',
            'building_name': 'Mathematics Building',
            'floor_number': 2,
            'capacity': 45,
            'latitude': 40.7130,
            'longitude': -74.0062,
            'geofence_radius': 60.00,
            'bluetooth_beacon_id': 'MATH201_BEACON',
            'is_active': True
        },
        {
            'room_number': 'PHYS301',
            'building_name': 'Physics Building',
            'floor_number': 3,
            'capacity': 25,
            'latitude': 40.7132,
            'longitude': -74.0064,
            'geofence_radius': 40.00,
            'bluetooth_beacon_id': 'PHYS301_BEACON',
            'is_active': True
        }
    ]
    
    created_classrooms = []
    for classroom_data in classrooms_data:
        try:
            existing = Classroom.query.filter_by(room_number=classroom_data['room_number']).first()
            if existing:
                print(f"✓ Classroom {classroom_data['room_number']} already exists")
                created_classrooms.append(existing)
                continue
                
            classroom = Classroom(**classroom_data)
            db.session.add(classroom)
            db.session.commit()
            created_classrooms.append(classroom)
            print(f"✓ Created classroom: {classroom_data['room_number']}")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating classroom {classroom_data['room_number']}: {e}")
    
    return created_classrooms

def create_test_faculty():
    """Create test faculty members"""
    faculty_data = [
        {
            'faculty_code': 'FAC001',
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@intelliattend.com',
            'phone_number': '+1234567890',
            'department': 'Computer Science',
            'password': 'faculty123'
        },
        {
            'faculty_code': 'FAC002',
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'email': 'alice.johnson@intelliattend.com',
            'phone_number': '+1234567891',
            'department': 'Mathematics',
            'password': 'faculty123'
        },
        {
            'faculty_code': 'FAC003',
            'first_name': 'Robert',
            'last_name': 'Brown',
            'email': 'robert.brown@intelliattend.com',
            'phone_number': '+1234567892',
            'department': 'Physics',
            'password': 'faculty123'
        }
    ]
    
    created_faculty = []
    for fac_data in faculty_data:
        try:
            existing = Faculty.query.filter_by(faculty_code=fac_data['faculty_code']).first()
            if existing:
                print(f"✓ Faculty {fac_data['faculty_code']} already exists")
                created_faculty.append(existing)
                continue
                
            password_hash = bcrypt.hashpw(fac_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            faculty = Faculty(
                faculty_code=fac_data['faculty_code'],
                first_name=fac_data['first_name'],
                last_name=fac_data['last_name'],
                email=fac_data['email'],
                phone_number=fac_data['phone_number'],
                department=fac_data['department'],
                password_hash=password_hash,
                is_active=True
            )
            
            db.session.add(faculty)
            db.session.commit()
            created_faculty.append(faculty)
            print(f"✓ Created faculty: {fac_data['faculty_code']} - {fac_data['first_name']} {fac_data['last_name']}")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating faculty {fac_data['faculty_code']}: {e}")
    
    return created_faculty

def create_test_students():
    """Create test students"""
    students_data = [
        {
            'student_code': 'STU001',
            'first_name': 'Michael',
            'last_name': 'Davis',
            'email': 'michael.davis@student.intelliattend.com',
            'phone_number': '+1234567900',
            'year_of_study': 2,
            'program': 'Computer Science',
            'password': 'student123'
        },
        {
            'student_code': 'STU002',
            'first_name': 'Sarah',
            'last_name': 'Wilson',
            'email': 'sarah.wilson@student.intelliattend.com',
            'phone_number': '+1234567901',
            'year_of_study': 3,
            'program': 'Mathematics',
            'password': 'student123'
        },
        {
            'student_code': 'STU003',
            'first_name': 'David',
            'last_name': 'Martinez',
            'email': 'david.martinez@student.intelliattend.com',
            'phone_number': '+1234567902',
            'year_of_study': 1,
            'program': 'Physics',
            'password': 'student123'
        },
        {
            'student_code': 'STU004',
            'first_name': 'Emily',
            'last_name': 'Taylor',
            'email': 'emily.taylor@student.intelliattend.com',
            'phone_number': '+1234567903',
            'year_of_study': 4,
            'program': 'Computer Science',
            'password': 'student123'
        },
        {
            'student_code': 'STU005',
            'first_name': 'James',
            'last_name': 'Anderson',
            'email': 'james.anderson@student.intelliattend.com',
            'phone_number': '+1234567904',
            'year_of_study': 2,
            'program': 'Mathematics',
            'password': 'student123'
        }
    ]
    
    created_students = []
    for stu_data in students_data:
        try:
            existing = Student.query.filter_by(student_code=stu_data['student_code']).first()
            if existing:
                print(f"✓ Student {stu_data['student_code']} already exists")
                created_students.append(existing)
                continue
                
            password_hash = bcrypt.hashpw(stu_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            student = Student(
                student_code=stu_data['student_code'],
                first_name=stu_data['first_name'],
                last_name=stu_data['last_name'],
                email=stu_data['email'],
                phone_number=stu_data['phone_number'],
                year_of_study=stu_data['year_of_study'],
                program=stu_data['program'],
                password_hash=password_hash,
                is_active=True
            )
            
            db.session.add(student)
            db.session.commit()
            created_students.append(student)
            print(f"✓ Created student: {stu_data['student_code']} - {stu_data['first_name']} {stu_data['last_name']}")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating student {stu_data['student_code']}: {e}")
    
    return created_students

def create_test_classes(faculty_list, classroom_list):
    """Create test classes"""
    if not faculty_list or not classroom_list:
        print("✗ Cannot create classes without faculty and classrooms")
        return []
    
    classes_data = [
        {
            'class_code': 'CS101',
            'class_name': 'Introduction to Programming',
            'faculty_id': faculty_list[0].faculty_id,
            'classroom_id': classroom_list[0].classroom_id,
            'semester': 'Fall',
            'academic_year': '2024-2025',
            'credits': 3,
            'max_students': 30,
            'schedule_day': 'Monday',
            'start_time': datetime.strptime('09:00', '%H:%M').time(),
            'end_time': datetime.strptime('10:30', '%H:%M').time(),
            'is_active': True
        },
        {
            'class_code': 'MATH201',
            'class_name': 'Calculus II',
            'faculty_id': faculty_list[1].faculty_id if len(faculty_list) > 1 else faculty_list[0].faculty_id,
            'classroom_id': classroom_list[1].classroom_id if len(classroom_list) > 1 else classroom_list[0].classroom_id,
            'semester': 'Fall',
            'academic_year': '2024-2025',
            'credits': 4,
            'max_students': 45,
            'schedule_day': 'Wednesday',
            'start_time': datetime.strptime('11:00', '%H:%M').time(),
            'end_time': datetime.strptime('12:30', '%H:%M').time(),
            'is_active': True
        },
        {
            'class_code': 'PHYS301',
            'class_name': 'Quantum Physics',
            'faculty_id': faculty_list[2].faculty_id if len(faculty_list) > 2 else faculty_list[0].faculty_id,
            'classroom_id': classroom_list[2].classroom_id if len(classroom_list) > 2 else classroom_list[0].classroom_id,
            'semester': 'Fall',
            'academic_year': '2024-2025',
            'credits': 3,
            'max_students': 25,
            'schedule_day': 'Friday',
            'start_time': datetime.strptime('14:00', '%H:%M').time(),
            'end_time': datetime.strptime('15:30', '%H:%M').time(),
            'is_active': True
        }
    ]
    
    created_classes = []
    for class_data in classes_data:
        try:
            existing = Classes.query.filter_by(class_code=class_data['class_code']).first()
            if existing:
                print(f"✓ Class {class_data['class_code']} already exists")
                created_classes.append(existing)
                continue
                
            class_obj = Classes(**class_data)
            db.session.add(class_obj)
            db.session.commit()
            created_classes.append(class_obj)
            print(f"✓ Created class: {class_data['class_code']} - {class_data['class_name']}")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating class {class_data['class_code']}: {e}")
    
    return created_classes

def create_enrollments(student_list, class_list):
    """Create student enrollments in classes"""
    if not student_list or not class_list:
        print("✗ Cannot create enrollments without students and classes")
        return []
    
    enrollments = []
    try:
        # Enroll students in classes
        for i, student in enumerate(student_list[:3]):  # First 3 students
            for j, class_obj in enumerate(class_list):
                if (i + j) % 2 == 0:  # Enroll in alternating pattern
                    existing = StudentClassEnrollment.query.filter_by(
                        student_id=student.student_id,
                        class_id=class_obj.class_id
                    ).first()
                    
                    if not existing:
                        enrollment = StudentClassEnrollment(
                            student_id=student.student_id,
                            class_id=class_obj.class_id,
                            status='enrolled',
                            is_active=True
                        )
                        db.session.add(enrollment)
                        enrollments.append(enrollment)
                        print(f"✓ Enrolled {student.first_name} {student.last_name} in {class_obj.class_name}")
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creating enrollments: {e}")
    
    return enrollments

def main():
    """Main setup function"""
    print("🚀 Setting up IntelliAttend test data...")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Create database tables
            db.create_all()
            print("✓ Database tables created/verified")
            
            # Create test data
            print("\n📝 Creating test admin...")
            admin = create_test_admin()
            
            print("\n🏢 Creating test classrooms...")
            classrooms = create_test_classrooms()
            
            print("\n👨‍🏫 Creating test faculty...")
            faculty = create_test_faculty()
            
            print("\n👨‍🎓 Creating test students...")
            students = create_test_students()
            
            print("\n📚 Creating test classes...")
            classes = create_test_classes(faculty, classrooms)
            
            print("\n📋 Creating student enrollments...")
            enrollments = create_enrollments(students, classes)
            
            print("\n" + "=" * 50)
            print("✅ Test data setup completed!")
            print(f"Created: {len([admin])} admin, {len(classrooms)} classrooms, {len(faculty)} faculty, {len(students)} students, {len(classes)} classes, {len(enrollments)} enrollments")
            
            print("\n🔐 Test Credentials:")
            print("Admin: testadmin / admin123")
            print("Faculty: FAC001, FAC002, FAC003 / faculty123")
            print("Students: STU001-STU005 / student123")
            
        except Exception as e:
            print(f"✗ Setup failed: {e}")
            return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)