#!/usr/bin/env python3
"""
IntelliAttend Database Seeding Script
======================================
Professional-grade database seeding with realistic test data.
Includes error handling, logging, and transaction management.

Usage:
    python seed_data.py [--reset] [--env production|development]
    
Options:
    --reset     Drop all tables and recreate (DANGEROUS in production)
    --env       Environment (default: development)
"""

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta, time
from decimal import Decimal
import random
import bcrypt

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app import (
    Faculty, Student, Classroom, Classes, StudentDevices,
    AttendanceSession, AttendanceRecord, StudentClassEnrollment,
    SecurityViolation, Admin
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseSeeder:
    """Professional database seeder with transaction management"""
    
    def __init__(self, reset=False):
        self.reset = reset
        self.created_counts = {}
        
    def hash_password(self, password):
        """Securely hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def run(self):
        """Main seeding execution with transaction management"""
        try:
            with app.app_context():
                logger.info("🌱 Starting database seeding...")
                
                if self.reset:
                    logger.warning("⚠️  RESET MODE: Dropping all tables...")
                    self._confirm_reset()
                    db.drop_all()
                    logger.info("✅ All tables dropped")
                
                logger.info("📊 Creating database tables...")
                db.create_all()
                logger.info("✅ Database tables created")
                
                # Seed in order of dependencies
                self._seed_admins()
                self._seed_faculty()
                self._seed_classrooms()
                self._seed_students()
                self._seed_classes()
                self._seed_enrollments()
                self._seed_devices()
                self._seed_attendance_sessions()
                self._seed_attendance_records()
                self._seed_security_violations()
                
                # Commit all changes
                db.session.commit()
                
                self._print_summary()
                logger.info("🎉 Database seeding completed successfully!")
                
        except Exception as e:
            logger.error(f"❌ Seeding failed: {e}")
            db.session.rollback()
            raise
    
    def _confirm_reset(self):
        """Confirm reset in production"""
        if os.environ.get('FLASK_CONFIG') == 'production':
            logger.error("❌ RESET not allowed in production!")
            sys.exit(1)
    
    def _seed_admins(self):
        """Seed administrator accounts"""
        logger.info("👤 Seeding administrators...")
        
        try:
            # Check if Admin table has the required fields
            if not Admin.query.first():
                # Create admin using direct SQL to avoid enum issues
                from sqlalchemy import text
                
                admins_sql = [
                    {
                        'username': 'superadmin',
                        'email': 'superadmin@intelliattend.edu',
                        'password_hash': self.hash_password('Admin@123'),
                        'first_name': 'Super',
                        'last_name': 'Admin',
                        'role': 'super_admin',
                        'is_active': True
                    },
                    {
                        'username': 'admin1',
                        'email': 'admin1@intelliattend.edu',
                        'password_hash': self.hash_password('Admin@123'),
                        'first_name': 'System',
                        'last_name': 'Admin',
                        'role': 'admin',
                        'is_active': True
                    }
                ]
                
                for data in admins_sql:
                    try:
                        sql = text("""
                            INSERT INTO admins (username, email, password_hash, first_name, last_name, role, is_active)
                            VALUES (:username, :email, :password_hash, :first_name, :last_name, :role, :is_active)
                        """)
                        db.session.execute(sql, data)
                        self.created_counts['admins'] = self.created_counts.get('admins', 0) + 1
                    except Exception as e:
                        logger.warning(f"Admin {data['username']} may already exist: {e}")
                
                db.session.flush()
            else:
                logger.info("Admins already exist, skipping...")
                
        except Exception as e:
            logger.warning(f"Could not seed admins: {e}. Skipping...")
            
        logger.info(f"✅ Created {self.created_counts.get('admins', 0)} admins")
    
    def _seed_faculty(self):
        """Seed faculty members with realistic data"""
        logger.info("👨‍🏫 Seeding faculty members...")
        
        departments = ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology']
        faculty_data = [
            ('Dr. John Smith', 'john.smith@university.edu', '+1234567890', 'Computer Science', 'FAC001'),
            ('Dr. Sarah Johnson', 'sarah.johnson@university.edu', '+1234567891', 'Mathematics', 'FAC002'),
            ('Prof. Michael Brown', 'michael.brown@university.edu', '+1234567892', 'Physics', 'FAC003'),
            ('Dr. Emily Davis', 'emily.davis@university.edu', '+1234567893', 'Chemistry', 'FAC004'),
            ('Prof. Robert Wilson', 'robert.wilson@university.edu', '+1234567894', 'Biology', 'FAC005'),
            ('Dr. Jennifer Lee', 'jennifer.lee@university.edu', '+1234567895', 'Computer Science', 'FAC006'),
            ('Dr. David Martinez', 'david.martinez@university.edu', '+1234567896', 'Mathematics', 'FAC007'),
            ('Prof. Lisa Anderson', 'lisa.anderson@university.edu', '+1234567897', 'Physics', 'FAC008'),
        ]
        
        for name, email, phone, dept, code in faculty_data:
            if not Faculty.query.filter_by(email=email).first():
                first_name, last_name = name.split()[-2], name.split()[-1]
                faculty = Faculty(
                    faculty_code=code,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone,
                    department=dept,
                    password_hash=self.hash_password('Faculty@123'),
                    is_active=True
                )
                db.session.add(faculty)
                self.created_counts['faculty'] = self.created_counts.get('faculty', 0) + 1
        
        db.session.flush()
        logger.info(f"✅ Created {self.created_counts.get('faculty', 0)} faculty members")
    
    def _seed_classrooms(self):
        """Seed classrooms with geofencing data"""
        logger.info("🏫 Seeding classrooms...")
        
        # Realistic campus coordinates (San Francisco State University example)
        base_lat, base_lon = Decimal('37.7219'), Decimal('-122.4782')
        
        classrooms_data = [
            ('Room-101', 'Engineering Building', 1, 60, base_lat, base_lon, Decimal('50.00'), 'BLE-ENG-101'),
            ('Room-102', 'Engineering Building', 1, 60, base_lat + Decimal('0.0001'), base_lon, Decimal('50.00'), 'BLE-ENG-102'),
            ('Room-201', 'Engineering Building', 2, 50, base_lat + Decimal('0.0002'), base_lon, Decimal('50.00'), 'BLE-ENG-201'),
            ('Room-202', 'Engineering Building', 2, 50, base_lat + Decimal('0.0003'), base_lon, Decimal('50.00'), 'BLE-ENG-202'),
            ('Room-301', 'Science Building', 3, 40, base_lat, base_lon + Decimal('0.0001'), Decimal('50.00'), 'BLE-SCI-301'),
            ('Room-302', 'Science Building', 3, 40, base_lat, base_lon + Decimal('0.0002'), Decimal('50.00'), 'BLE-SCI-302'),
            ('Lab-A1', 'Computer Lab', 1, 30, base_lat + Decimal('0.0001'), base_lon + Decimal('0.0001'), Decimal('40.00'), 'BLE-LAB-A1'),
            ('Lab-A2', 'Computer Lab', 1, 30, base_lat + Decimal('0.0002'), base_lon + Decimal('0.0001'), Decimal('40.00'), 'BLE-LAB-A2'),
            ('Hall-Main', 'Main Building', 1, 100, base_lat - Decimal('0.0001'), base_lon, Decimal('60.00'), 'BLE-HALL-MAIN'),
            ('Auditorium', 'Main Building', 2, 200, base_lat - Decimal('0.0002'), base_lon, Decimal('70.00'), 'BLE-AUD-01'),
        ]
        
        for room, building, floor, capacity, lat, lon, radius, beacon in classrooms_data:
            if not Classroom.query.filter_by(room_number=room).first():
                classroom = Classroom(
                    room_number=room,
                    building_name=building,
                    floor_number=floor,
                    capacity=capacity,
                    latitude=lat,
                    longitude=lon,
                    geofence_radius=radius,
                    bluetooth_beacon_id=beacon,
                    is_active=True
                )
                db.session.add(classroom)
                self.created_counts['classrooms'] = self.created_counts.get('classrooms', 0) + 1
        
        db.session.flush()
        logger.info(f"✅ Created {self.created_counts.get('classrooms', 0)} classrooms")
    
    def _seed_students(self):
        """Seed students with realistic data"""
        logger.info("👨‍🎓 Seeding students...")
        
        programs = ['Computer Science', 'Data Science', 'Software Engineering', 'Information Systems']
        first_names = ['James', 'Emma', 'Oliver', 'Sophia', 'Noah', 'Ava', 'Liam', 'Isabella', 'Mason', 'Mia',
                      'Ethan', 'Charlotte', 'Alexander', 'Amelia', 'William', 'Harper', 'Benjamin', 'Evelyn']
        last_names = ['Smith', 'Johnson', 'Brown', 'Davis', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas',
                     'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark']
        
        students_created = 0
        for i in range(50):  # Create 50 students
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            student_code = f"STU{2024}{str(i+1).zfill(4)}"
            email = f"{first_name.lower()}.{last_name.lower()}{i}@student.university.edu"
            
            if not Student.query.filter_by(email=email).first():
                student = Student(
                    student_code=student_code,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=f"+1234{str(567890 + i)}",
                    year_of_study=random.randint(1, 4),
                    program=random.choice(programs),
                    password_hash=self.hash_password('Student@123'),
                    is_active=True
                )
                db.session.add(student)
                students_created += 1
        
        self.created_counts['students'] = students_created
        db.session.flush()
        logger.info(f"✅ Created {students_created} students")
    
    def _seed_classes(self):
        """Seed classes with schedule information"""
        logger.info("📚 Seeding classes...")
        
        faculty_list = Faculty.query.all()
        classroom_list = Classroom.query.all()
        
        if not faculty_list or not classroom_list:
            logger.warning("⚠️  No faculty or classrooms found, skipping classes")
            return
        
        classes_data = [
            ('CS101', 'Introduction to Programming', 'Fall', '2024-2025', 3, 60, 'Monday', '09:00', '10:30'),
            ('CS201', 'Data Structures', 'Fall', '2024-2025', 4, 60, 'Tuesday', '10:00', '12:00'),
            ('CS301', 'Algorithms', 'Fall', '2024-2025', 4, 50, 'Wednesday', '14:00', '16:00'),
            ('CS202', 'Database Systems', 'Fall', '2024-2025', 3, 50, 'Thursday', '09:00', '11:00'),
            ('CS302', 'Operating Systems', 'Fall', '2024-2025', 4, 40, 'Friday', '11:00', '13:00'),
            ('MA101', 'Calculus I', 'Fall', '2024-2025', 4, 60, 'Monday', '11:00', '12:30'),
            ('MA201', 'Linear Algebra', 'Fall', '2024-2025', 3, 50, 'Tuesday', '13:00', '14:30'),
            ('PH101', 'Physics I', 'Fall', '2024-2025', 4, 50, 'Wednesday', '09:00', '11:00'),
            ('CH101', 'Chemistry I', 'Fall', '2024-2025', 3, 40, 'Thursday', '14:00', '16:00'),
            ('BI101', 'Biology I', 'Fall', '2024-2025', 3, 40, 'Friday', '09:00', '11:00'),
        ]
        
        for code, name, sem, year, credits, max_stud, day, start, end in classes_data:
            if not Classes.query.filter_by(class_code=code).first():
                class_obj = Classes(
                    class_code=code,
                    class_name=name,
                    faculty_id=random.choice(faculty_list).faculty_id,
                    classroom_id=random.choice(classroom_list).classroom_id,
                    semester=sem,
                    academic_year=year,
                    credits=credits,
                    max_students=max_stud,
                    schedule_day=day,
                    start_time=time(*map(int, start.split(':'))),
                    end_time=time(*map(int, end.split(':'))),
                    is_active=True
                )
                db.session.add(class_obj)
                self.created_counts['classes'] = self.created_counts.get('classes', 0) + 1
        
        db.session.flush()
        logger.info(f"✅ Created {self.created_counts.get('classes', 0)} classes")
    
    def _seed_enrollments(self):
        """Seed student class enrollments"""
        logger.info("📝 Seeding enrollments...")
        
        students = Student.query.all()
        classes = Classes.query.all()
        
        if not students or not classes:
            logger.warning("⚠️  No students or classes found, skipping enrollments")
            return
        
        enrollments_created = 0
        for student in students:
            # Enroll each student in 3-5 random classes
            num_classes = random.randint(3, min(5, len(classes)))
            selected_classes = random.sample(classes, num_classes)
            
            for class_obj in selected_classes:
                if not StudentClassEnrollment.query.filter_by(
                    student_id=student.student_id,
                    class_id=class_obj.class_id
                ).first():
                    enrollment = StudentClassEnrollment(
                        student_id=student.student_id,
                        class_id=class_obj.class_id,
                        status='enrolled',
                        is_active=True
                    )
                    db.session.add(enrollment)
                    enrollments_created += 1
        
        self.created_counts['enrollments'] = enrollments_created
        db.session.flush()
        logger.info(f"✅ Created {enrollments_created} enrollments")
    
    def _seed_devices(self):
        """Seed student devices"""
        logger.info("📱 Seeding devices...")
        
        students = Student.query.limit(20).all()  # First 20 students
        device_types = ['android', 'ios']
        device_models = ['Samsung Galaxy S23', 'iPhone 14 Pro', 'Google Pixel 7', 'OnePlus 11', 'iPhone 13']
        
        devices_created = 0
        for i, student in enumerate(students):
            device_type = random.choice(device_types)
            device = StudentDevices(
                student_id=student.student_id,
                device_uuid=f"device-uuid-{student.student_code}-{i}",
                device_name=f"{student.first_name}'s Phone",
                device_type=device_type,
                device_model=random.choice(device_models),
                os_version='14.0' if device_type == 'ios' else '13.0',
                app_version='1.0.0',
                is_active=True,
                biometric_enabled=random.choice([True, False]),
                location_permission=True,
                bluetooth_permission=True
            )
            db.session.add(device)
            devices_created += 1
        
        self.created_counts['devices'] = devices_created
        db.session.flush()
        logger.info(f"✅ Created {devices_created} devices")
    
    def _seed_attendance_sessions(self):
        """Seed attendance sessions"""
        logger.info("📅 Seeding attendance sessions...")
        
        classes = Classes.query.all()
        if not classes:
            logger.warning("⚠️  No classes found, skipping sessions")
            return
        
        sessions_created = 0
        # Create sessions for past 7 days
        for days_ago in range(7):
            session_date = datetime.utcnow().date() - timedelta(days=days_ago)
            
            for class_obj in classes[:5]:  # First 5 classes
                session = AttendanceSession(
                    class_id=class_obj.class_id,
                    faculty_id=class_obj.faculty_id,
                    session_date=session_date,
                    start_time=datetime.utcnow() - timedelta(days=days_ago, hours=2),
                    end_time=datetime.utcnow() - timedelta(days=days_ago, hours=1) if days_ago > 0 else None,
                    qr_token=f"qr-token-{class_obj.class_id}-{days_ago}",
                    qr_secret_key=f"secret-{class_obj.class_id}-{days_ago}",
                    qr_expires_at=datetime.utcnow() + timedelta(minutes=5) if days_ago == 0 else None,
                    status='active' if days_ago == 0 else 'completed',
                    total_students_enrolled=len(class_obj.enrollments) if hasattr(class_obj, 'enrollments') else 0
                )
                db.session.add(session)
                sessions_created += 1
        
        self.created_counts['sessions'] = sessions_created
        db.session.flush()
        logger.info(f"✅ Created {sessions_created} attendance sessions")
    
    def _seed_attendance_records(self):
        """Seed attendance records"""
        logger.info("✅ Seeding attendance records...")
        
        sessions = AttendanceSession.query.all()
        if not sessions:
            logger.warning("⚠️  No sessions found, skipping records")
            return
        
        records_created = 0
        for session in sessions:
            # Get enrolled students for this class
            enrollments = StudentClassEnrollment.query.filter_by(
                class_id=session.class_id,
                is_active=True
            ).all()
            
            # 80% attendance rate simulation
            for enrollment in enrollments:
                if random.random() < 0.8:  # 80% present
                    record = AttendanceRecord(
                        session_id=session.session_id,
                        student_id=enrollment.student_id,
                        biometric_verified=random.choice([True, False]),
                        location_verified=random.choice([True, True, True, False]),  # 75% location verified
                        bluetooth_verified=random.choice([True, True, False]),  # 66% bluetooth verified
                        gps_latitude=Decimal('37.7219') + Decimal(str(random.uniform(-0.001, 0.001))),
                        gps_longitude=Decimal('-122.4782') + Decimal(str(random.uniform(-0.001, 0.001))),
                        gps_accuracy=Decimal(str(random.uniform(5.0, 20.0))),
                        bluetooth_rssi=random.randint(-70, -30),
                        verification_score=Decimal(str(random.uniform(0.7, 1.0))),
                        status='present'
                    )
                    db.session.add(record)
                    records_created += 1
        
        self.created_counts['records'] = records_created
        db.session.flush()
        logger.info(f"✅ Created {records_created} attendance records")
    
    def _seed_security_violations(self):
        """Seed security violations for testing"""
        logger.info("🔒 Seeding security violations...")
        
        students = Student.query.limit(5).all()
        violation_types = ['screenshot', 'screen_recording', 'root_detected', 'vpn_detected']
        
        violations_created = 0
        for student in students:
            if random.random() < 0.3:  # 30% chance of violation
                violation = SecurityViolation(
                    student_id=student.student_id,
                    violation_type=random.choice(violation_types),
                    details={'screen': 'attendance_marking', 'timestamp': datetime.utcnow().isoformat()},
                    device_info={'model': 'iPhone 14', 'os': 'iOS 16.0'},
                    is_resolved=False
                )
                db.session.add(violation)
                violations_created += 1
        
        self.created_counts['violations'] = violations_created
        db.session.flush()
        logger.info(f"✅ Created {violations_created} security violations")
    
    def _print_summary(self):
        """Print seeding summary"""
        print("\n" + "="*60)
        print("📊 DATABASE SEEDING SUMMARY")
        print("="*60)
        for model, count in self.created_counts.items():
            print(f"  {model.capitalize():.<40} {count:>5}")
        print("="*60)
        print(f"  Total Records Created:.................. {sum(self.created_counts.values()):>5}")
        print("="*60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Seed IntelliAttend database')
    parser.add_argument('--reset', action='store_true', help='Reset database (drop all tables)')
    parser.add_argument('--env', choices=['development', 'production'], default='development',
                       help='Environment')
    
    args = parser.parse_args()
    
    # Set environment
    os.environ['FLASK_CONFIG'] = args.env
    
    # Run seeder
    seeder = DatabaseSeeder(reset=args.reset)
    seeder.run()


if __name__ == '__main__':
    main()
