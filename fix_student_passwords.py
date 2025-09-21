#!/usr/bin/env python3
"""
Student Password Fix Utility
Standardizes student password hashing to ensure login compatibility
"""

import sys
import os
import bcrypt
from werkzeug.security import generate_password_hash

# Add the backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db, Student

def check_password_compatibility(password, password_hash):
    """Test if password check function works with given hash"""
    from app import check_password
    return check_password(password, password_hash)

def fix_student_passwords():
    """Fix student password hashes to ensure compatibility"""
    print("🔧 Student Password Fix Utility")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Get all students
            students = Student.query.all()
            print(f"Found {len(students)} students to check...")
            
            fixed_count = 0
            test_password = 'student123'  # Default test password
            
            for student in students:
                print(f"\n👤 Checking student: {student.email}")
                
                # Test current password hash
                is_working = check_password_compatibility(test_password, student.password_hash)
                print(f"   Current hash format: {'✅ Working' if is_working else '❌ Not working'}")
                
                if not is_working:
                    print(f"   🔧 Fixing password hash...")
                    
                    # Create new bcrypt hash (matching our test setup)
                    new_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                    # Verify new hash works
                    if check_password_compatibility(test_password, new_hash):
                        # Update student record
                        student.password_hash = new_hash
                        db.session.add(student)
                        fixed_count += 1
                        print(f"   ✅ Password hash updated and verified")
                    else:
                        print(f"   ❌ New hash verification failed")
                else:
                    print(f"   ✅ Password already working")
            
            # Commit all changes
            if fixed_count > 0:
                db.session.commit()
                print(f"\n✅ Successfully fixed {fixed_count} student passwords")
            else:
                print(f"\n✅ All student passwords were already working")
                
            # Test login for first few students
            print(f"\n🧪 Testing student logins...")
            test_students = students[:3]  # Test first 3 students
            
            for student in test_students:
                is_working = check_password_compatibility(test_password, student.password_hash)
                status = "✅ PASS" if is_working else "❌ FAIL"
                print(f"   {student.email}: {status}")
                
            print(f"\n🎉 Password fix completed!")
            print(f"📋 Student login credentials:")
            print(f"   Password: {test_password}")
            print(f"   Test with any student email like: {students[0].email if students else 'No students found'}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing passwords: {e}")
            return False

def create_additional_test_students():
    """Create additional test students with proper password hashing"""
    print(f"\n➕ Creating additional test students...")
    
    test_students = [
        {
            'student_code': 'TEST001',
            'first_name': 'Test',
            'last_name': 'Student1',
            'email': 'test1@student.intelliattend.com',
            'program': 'Computer Science',
            'year_of_study': 2
        },
        {
            'student_code': 'TEST002',
            'first_name': 'Demo',
            'last_name': 'Student2',
            'email': 'demo@student.intelliattend.com',
            'program': 'Mathematics',
            'year_of_study': 3
        }
    ]
    
    created_count = 0
    test_password = 'student123'
    
    for student_data in test_students:
        try:
            # Check if student already exists
            existing = Student.query.filter_by(email=student_data['email']).first()
            if existing:
                print(f"   ⚠️ Student {student_data['email']} already exists")
                continue
                
            # Create password hash using bcrypt (matching our working format)
            password_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create student
            student = Student(
                student_code=student_data['student_code'],
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                email=student_data['email'],
                program=student_data['program'],
                password_hash=password_hash,
                year_of_study=student_data['year_of_study'],
                is_active=True
            )
            
            db.session.add(student)
            created_count += 1
            print(f"   ✅ Created: {student_data['email']}")
            
        except Exception as e:
            print(f"   ❌ Error creating {student_data['email']}: {e}")
    
    if created_count > 0:
        db.session.commit()
        print(f"   ✅ Successfully created {created_count} test students")
    
    return created_count

def main():
    """Main execution function"""
    try:
        # Fix existing student passwords
        success = fix_student_passwords()
        
        if success:
            # Create additional test students
            create_additional_test_students()
            
        print(f"\n" + "=" * 50)
        print(f"🎯 SUMMARY:")
        print(f"   ✅ Student password standardization completed")
        print(f"   🔐 All students should now be able to login with: student123")
        print(f"   🧪 Test login with any student email address")
        
    except Exception as e:
        print(f"❌ Utility failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)