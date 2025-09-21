#!/usr/bin/env python3
"""
Student Password Reset Utility for Admins
Allows admins to reset student passwords when needed
"""

import sys
import os
import bcrypt
import argparse
from datetime import datetime

# Add the backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db, Student

def reset_student_password(student_email, new_password):
    """Reset a student's password"""
    with app.app_context():
        try:
            # Find the student
            student = Student.query.filter_by(email=student_email).first()
            
            if not student:
                print(f"❌ Student not found: {student_email}")
                return False
            
            # Generate new password hash
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Update the student's password
            student.password_hash = new_hash
            student.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            print(f"✅ Password reset successful for: {student.first_name} {student.last_name} ({student_email})")
            print(f"   New password: {new_password}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error resetting password: {e}")
            return False

def reset_all_students_password(new_password):
    """Reset all students to the same password"""
    with app.app_context():
        try:
            students = Student.query.filter_by(is_active=True).all()
            
            if not students:
                print("❌ No active students found")
                return False
            
            print(f"Found {len(students)} active students")
            
            # Generate new password hash
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            reset_count = 0
            
            for student in students:
                try:
                    student.password_hash = new_hash
                    student.updated_at = datetime.utcnow()
                    reset_count += 1
                    print(f"   ✅ Reset password for: {student.first_name} {student.last_name} ({student.email})")
                except Exception as e:
                    print(f"   ❌ Failed to reset password for {student.email}: {e}")
            
            db.session.commit()
            
            print(f"\n✅ Successfully reset {reset_count} student passwords")
            print(f"   New password for all students: {new_password}")
            
            return reset_count > 0
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error resetting passwords: {e}")
            return False

def list_students():
    """List all students for reference"""
    with app.app_context():
        try:
            students = Student.query.filter_by(is_active=True).all()
            
            if not students:
                print("❌ No active students found")
                return
            
            print(f"\n👥 Active Students ({len(students)}):")
            print("=" * 70)
            
            for student in students:
                print(f"   • {student.student_code}: {student.first_name} {student.last_name}")
                print(f"     Email: {student.email}")
                print(f"     Program: {student.program} (Year {student.year_of_study})")
                print()
                
        except Exception as e:
            print(f"❌ Error listing students: {e}")

def verify_password(student_email, test_password):
    """Verify a student's password works"""
    with app.app_context():
        try:
            from app import check_password
            
            student = Student.query.filter_by(email=student_email).first()
            
            if not student:
                print(f"❌ Student not found: {student_email}")
                return False
            
            is_correct = check_password(test_password, student.password_hash)
            
            if is_correct:
                print(f"✅ Password verification successful for: {student_email}")
            else:
                print(f"❌ Password verification failed for: {student_email}")
            
            return is_correct
            
        except Exception as e:
            print(f"❌ Error verifying password: {e}")
            return False

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Student Password Reset Utility")
    parser.add_argument('action', choices=['reset', 'reset-all', 'list', 'verify'], 
                       help='Action to perform')
    parser.add_argument('--email', help='Student email address')
    parser.add_argument('--password', default='student123', help='New password (default: student123)')
    
    args = parser.parse_args()
    
    print("🔐 Student Password Reset Utility")
    print("=" * 50)
    
    if args.action == 'list':
        list_students()
        
    elif args.action == 'reset':
        if not args.email:
            print("❌ Email address is required for individual reset")
            print("Usage: python3 student_password_reset.py reset --email student@example.com [--password newpass]")
            return False
            
        return reset_student_password(args.email, args.password)
        
    elif args.action == 'reset-all':
        confirm = input(f"⚠️  This will reset ALL student passwords to: {args.password}\n   Continue? (y/N): ")
        if confirm.lower() == 'y':
            return reset_all_students_password(args.password)
        else:
            print("❌ Operation cancelled")
            return False
            
    elif args.action == 'verify':
        if not args.email:
            print("❌ Email address is required for verification")
            print("Usage: python3 student_password_reset.py verify --email student@example.com [--password testpass]")
            return False
            
        return verify_password(args.email, args.password)
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        print("\n" + "=" * 50)
        if success:
            print("✅ Operation completed successfully")
        else:
            print("❌ Operation failed")
            
        print("\n💡 Usage Examples:")
        print("   List students:     python3 student_password_reset.py list")
        print("   Reset one student: python3 student_password_reset.py reset --email alice@student.edu")
        print("   Reset all students: python3 student_password_reset.py reset-all --password newpass123")
        print("   Verify password:   python3 student_password_reset.py verify --email alice@student.edu")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)