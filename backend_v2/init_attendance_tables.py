#!/usr/bin/env python3
"""
IntelliAttend - Attendance System Database Initialization
Creates attendance-related tables and inserts test data
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, time as dt_time, date as dt_date
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import Base, Classroom, ClassroomWiFi, ClassroomBeacon, AttendanceSession, Student, Faculty, Section, Timetable
from main import DATABASE_URL

def init_attendance_tables():
    """Initialize attendance system tables and add test data"""
    
    print("=" * 70)
    print("IntelliAttend - Attendance System Initialization")
    print("=" * 70)
    
    # Create engine and session
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    print("\n[1/5] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    
    db = SessionLocal()
    
    try:
        # Check if test data already exists
        existing_classroom = db.query(Classroom).filter(Classroom.room_number == "R301").first()
        if existing_classroom:
            print("\n⚠️  Test data already exists. Skipping insertion.")
            print("\nExisting test classroom:")
            print(f"  Room: {existing_classroom.room_number}")
            print(f"  Location: ({existing_classroom.latitude}, {existing_classroom.longitude})")
            return
        
        print("\n[2/5] Creating test classroom...")
        # Test Classroom - R301 (Main Building)
        # Using coordinates near a typical educational institution
        classroom = Classroom(
            room_number="R301",
            building_name="Main Academic Block",
            latitude=17.4435,  # Example: Near Hyderabad area
            longitude=78.3489,
            geofence_radius=50,  # 50 meters
            floor_number="3",
            capacity=60,
            is_active=True
        )
        db.add(classroom)
        db.flush()  # Get classroom_id
        
        print(f"✅ Classroom created: {classroom.room_number}")
        print(f"   GPS: ({classroom.latitude}, {classroom.longitude})")
        print(f"   Geofence radius: {classroom.geofence_radius}m")
        
        print("\n[3/5] Registering WiFi networks...")
        # Test WiFi Network
        wifi1 = ClassroomWiFi(
            classroom_id=classroom.classroom_id,
            ssid="CampusWiFi-R301",
            bssid="AA:BB:CC:DD:EE:FF",
            signal_strength_threshold=-70,
            is_active=True
        )
        wifi2 = ClassroomWiFi(
            classroom_id=classroom.classroom_id,
            ssid="CampusSecure",
            bssid="11:22:33:44:55:66",
            signal_strength_threshold=-75,
            is_active=True
        )
        db.add(wifi1)
        db.add(wifi2)
        
        print(f"✅ WiFi registered: {wifi1.ssid} ({wifi1.bssid})")
        print(f"✅ WiFi registered: {wifi2.ssid} ({wifi2.bssid})")
        
        print("\n[4/5] Registering Bluetooth beacons...")
        # Test Bluetooth Beacons
        beacon1 = ClassroomBeacon(
            classroom_id=classroom.classroom_id,
            mac_address="A1:B2:C3:D4:E5:F6",
            uuid="FDA50693-A4E2-4FB1-AFCF-C6EB07647825",
            major=1,
            minor=301,
            rssi_threshold=-70,
            is_active=True
        )
        beacon2 = ClassroomBeacon(
            classroom_id=classroom.classroom_id,
            mac_address="B1:C2:D3:E4:F5:A6",
            uuid="FDA50693-A4E2-4FB1-AFCF-C6EB07647826",
            major=1,
            minor=302,
            rssi_threshold=-75,
            is_active=True
        )
        db.add(beacon1)
        db.add(beacon2)
        
        print(f"✅ Beacon registered: {beacon1.mac_address} (UUID: {beacon1.uuid})")
        print(f"✅ Beacon registered: {beacon2.mac_address} (UUID: {beacon2.uuid})")
        
        print("\n[5/5] Creating test attendance session...")
        
        # Find a faculty member (use first available or create demo)
        faculty = db.query(Faculty).first()
        if not faculty:
            print("⚠️  No faculty found. Creating demo faculty...")
            from main import hash_password
            faculty = Faculty(
                faculty_code="FAC001",
                first_name="Demo",
                last_name="Professor",
                email="demo.prof@intelliattend.com",
                phone_number="1234567890",
                department="Computer Science",
                password_hash=hash_password("password123"),
                is_active=True
            )
            db.add(faculty)
            db.flush()
            print(f"✅ Demo faculty created: {faculty.first_name} {faculty.last_name}")
        
        # Find a timetable entry (use first available or create demo)
        timetable_entry = db.query(Timetable).first()
        if not timetable_entry:
            print("⚠️  No timetable found. Creating demo timetable entry...")
            
            # Check if section exists
            section = db.query(Section).first()
            if not section:
                section = Section(
                    section_name="CSE-A",
                    course="Computer Science",
                    room_number="R301"
                )
                db.add(section)
                db.flush()
                print(f"✅ Demo section created: {section.section_name}")
            
            timetable_entry = Timetable(
                section_id=section.id,
                day_of_week="MONDAY",
                slot_number=1,
                slot_type="lecture",
                start_time=dt_time(9, 0),
                end_time=dt_time(10, 0),
                subject_code="CS101",
                subject_name="Data Structures",
                faculty_name=f"{faculty.first_name} {faculty.last_name}",
                room_number="R301"
            )
            db.add(timetable_entry)
            db.flush()
            print(f"✅ Demo timetable created: {timetable_entry.subject_name}")
        
        # Create test attendance session
        # Valid for next 2 hours
        now = datetime.utcnow()
        session_start = now + timedelta(minutes=5)
        session_end = session_start + timedelta(hours=1)
        
        session = AttendanceSession(
            class_id=timetable_entry.id,
            classroom_id=classroom.classroom_id,
            faculty_id=faculty.faculty_id,
            qr_token="TEST_QR_TOKEN_2024",
            qr_expires_at=now + timedelta(hours=2),
            status='active',
            session_date=dt_date.today(),
            start_time=session_start.time(),
            end_time=session_end.time(),
            attendance_window_start=session_start - timedelta(minutes=3),
            attendance_window_end=session_end + timedelta(minutes=5),
        )
        db.add(session)
        
        print(f"✅ Attendance session created!")
        print(f"   QR Token: {session.qr_token}")
        print(f"   Expires: {session.qr_expires_at}")
        print(f"   Status: {session.status}")
        print(f"   Window: {session.attendance_window_start} to {session.attendance_window_end}")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "=" * 70)
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("=" * 70)
        
        print("\n📋 TEST DATA SUMMARY:")
        print("-" * 70)
        print(f"Classroom:      {classroom.room_number} ({classroom.building_name})")
        print(f"GPS Location:   {classroom.latitude}, {classroom.longitude}")
        print(f"Geofence:       {classroom.geofence_radius} meters")
        print(f"WiFi Networks:  2 registered")
        print(f"BT Beacons:     2 registered")
        print(f"QR Token:       {session.qr_token}")
        print(f"Token Valid:    {session.qr_expires_at}")
        print("-" * 70)
        
        print("\n🧪 TESTING INSTRUCTIONS:")
        print("-" * 70)
        print("1. Start the backend server:")
        print("   cd /Users/anji/Desktop/IntelliAttend/backend_v2")
        print("   python main.py")
        print()
        print("2. Use the following test data:")
        print(f"   QR Token:     {session.qr_token}")
        print(f"   GPS Location: {classroom.latitude}, {classroom.longitude}")
        print(f"   WiFi SSID:    {wifi1.ssid}")
        print(f"   WiFi BSSID:   {wifi1.bssid}")
        print(f"   BT MAC:       {beacon1.mac_address}")
        print()
        print("3. Test the attendance marking endpoint:")
        print("   POST http://localhost:8080/api/attendance/mark")
        print()
        print("4. Install mobile APK and test end-to-end:")
        print("   - Login with demo account")
        print("   - View today's timetable")
        print("   - Scan QR code (use token above)")
        print("   - Verify attendance marked")
        print("-" * 70)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    init_attendance_tables()
