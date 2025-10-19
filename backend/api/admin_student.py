#!/usr/bin/env python3
"""
IntelliAttend - Admin Student Management API
Endpoints for student registration, bulk CSV import, and management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
import csv
import io
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db
from app import Student, RegistrationAuditLog, Admin
from validators import (
    validate_student_code,
    validate_email,
    validate_phone_number,
    validate_year_of_study,
    sanitize_string
)
from utils.audit_helpers import (
    log_registration_action,
    create_audit_details,
    sanitize_audit_data
)

# Create Blueprint
admin_student_bp = Blueprint('admin_student', __name__, url_prefix='/api/admin/students')


@admin_student_bp.route('', methods=['POST'])
@jwt_required()
def register_student():
    """
    Register a single student
    
    Request Body:
    {
        "student_code": "STU20240001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@university.edu",
        "phone_number": "+1234567890",
        "program": "Computer Science",
        "year_of_study": 2,
        "password": "SecurePassword123"
    }
    
    Returns:
        JSON response with student details or error message
    """
    try:
        # Get admin ID from JWT
        admin_id = get_jwt_identity()
        
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['student_code', 'first_name', 'last_name', 'email', 'program', 'password']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Validate fields
        errors = []
        
        valid, error = validate_student_code(data['student_code'])
        if not valid:
            errors.append(error)
        
        valid, error = validate_email(data['email'])
        if not valid:
            errors.append(error)
        
        if 'phone_number' in data and data['phone_number']:
            valid, error = validate_phone_number(data['phone_number'])
            if not valid:
                errors.append(error)
        
        if 'year_of_study' in data and data['year_of_study']:
            valid, error = validate_year_of_study(data['year_of_study'])
            if not valid:
                errors.append(error)
        
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'validation_errors': errors
            }), 400
        
        # Check for duplicate student code
        existing_student = Student.query.filter_by(
            student_code=sanitize_string(data['student_code'])
        ).first()
        
        if existing_student:
            return jsonify({
                'success': False,
                'error': f"Student with code '{data['student_code']}' already exists"
            }), 409
        
        # Check for duplicate email
        existing_email = Student.query.filter_by(email=data['email'].lower()).first()
        
        if existing_email:
            return jsonify({
                'success': False,
                'error': f"Student with email '{data['email']}' already exists"
            }), 409
        
        # Hash password
        password_hash = generate_password_hash(data['password'])
        
        # Create student
        try:
            student = Student(
                student_code=sanitize_string(data['student_code']),
                first_name=sanitize_string(data['first_name']),
                last_name=sanitize_string(data['last_name']),
                email=data['email'].lower(),
                phone_number=data.get('phone_number'),
                program=sanitize_string(data['program']),
                year_of_study=data.get('year_of_study'),
                password_hash=password_hash,
                is_active=True
            )
            
            db.session.add(student)
            db.session.flush()
            
            student_id = student.student_id
            
            # Log to audit trail
            audit_details = create_audit_details(
                operation='student_registration',
                new_values=sanitize_audit_data({
                    'student_id': student_id,
                    'student_code': data['student_code'],
                    'email': data['email'],
                    'program': data['program']
                })
            )
            
            log_registration_action(
                db=db,
                RegistrationAuditLog=RegistrationAuditLog,
                Admin=Admin,
                action='create',
                resource_type='student',
                resource_id=student_id,
                admin_id=admin_id,
                details=audit_details
            )
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Student registered successfully',
                'data': {
                    'student_id': student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'program': student.program,
                    'year_of_study': student.year_of_study
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Database error: {e}")
            return jsonify({
                'success': False,
                'error': 'Database error occurred during registration',
                'details': str(e)
            }), 500
            
    except Exception as e:
        print(f"❌ Server error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error occurred',
            'details': str(e)
        }), 500


@admin_student_bp.route('/bulk-import', methods=['POST'])
@jwt_required()
def bulk_import_students():
    """
    Bulk import students from CSV file
    
    CSV Format:
    student_code,first_name,last_name,email,phone_number,program,year_of_study,password
    
    Returns:
        JSON response with import results including successful imports and errors
    """
    try:
        # Get admin ID from JWT
        admin_id = get_jwt_identity()
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided. Please upload a CSV file.'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check if file is CSV
        if not file.filename.endswith('.csv'):
            return jsonify({
                'success': False,
                'error': 'Invalid file format. Please upload a CSV file.'
            }), 400
        
        # Read CSV file
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            # Validate CSV headers
            required_headers = ['student_code', 'first_name', 'last_name', 'email', 'program']
            optional_headers = ['phone_number', 'year_of_study', 'password']
            
            if not csv_reader.fieldnames:
                return jsonify({
                    'success': False,
                    'error': 'CSV file is empty or has no headers'
                }), 400
            
            missing_headers = [h for h in required_headers if h not in csv_reader.fieldnames]
            
            if missing_headers:
                return jsonify({
                    'success': False,
                    'error': f'Missing required CSV columns: {", ".join(missing_headers)}',
                    'expected_headers': required_headers + optional_headers
                }), 400
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to parse CSV file: {str(e)}'
            }), 400
        
        # Process CSV rows
        total_rows = 0
        successful_imports = []
        errors = []
        existing_codes = set()
        existing_emails = set()
        
        # Get all existing student codes and emails for quick lookup
        existing_students = Student.query.with_entities(
            Student.student_code, Student.email
        ).all()
        
        for student in existing_students:
            existing_codes.add(student.student_code.lower())
            existing_emails.add(student.email.lower())
        
        # Process each row
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (row 1 is header)
            total_rows += 1
            row_errors = []
            
            # Validate student code
            student_code = row.get('student_code', '').strip()
            if not student_code:
                row_errors.append('Student code is required')
            else:
                valid, error = validate_student_code(student_code)
                if not valid:
                    row_errors.append(error)
                elif student_code.lower() in existing_codes:
                    row_errors.append(f'Student code already exists: {student_code}')
            
            # Validate email
            email = row.get('email', '').strip().lower()
            if not email:
                row_errors.append('Email is required')
            else:
                valid, error = validate_email(email)
                if not valid:
                    row_errors.append(error)
                elif email in existing_emails:
                    row_errors.append(f'Email already exists: {email}')
            
            # Validate phone number (optional)
            phone_number = row.get('phone_number', '').strip()
            if phone_number:
                valid, error = validate_phone_number(phone_number)
                if not valid:
                    row_errors.append(error)
            
            # Validate year of study (optional)
            year_of_study = row.get('year_of_study', '').strip()
            if year_of_study:
                try:
                    year_of_study = int(year_of_study)
                    valid, error = validate_year_of_study(year_of_study)
                    if not valid:
                        row_errors.append(error)
                except ValueError:
                    row_errors.append(f'Invalid year of study: {year_of_study}')
                    year_of_study = None
            else:
                year_of_study = None
            
            # Check required fields
            first_name = row.get('first_name', '').strip()
            last_name = row.get('last_name', '').strip()
            program = row.get('program', '').strip()
            
            if not first_name:
                row_errors.append('First name is required')
            if not last_name:
                row_errors.append('Last name is required')
            if not program:
                row_errors.append('Program is required')
            
            # Get password or generate default
            password = row.get('password', '').strip()
            if not password:
                # Generate default password: StudentCode@123
                password = f"{student_code}@123"
            
            # If there are errors, add to error list and skip
            if row_errors:
                errors.append({
                    'row': row_num,
                    'student_code': student_code if student_code else 'N/A',
                    'errors': row_errors
                })
                continue
            
            # Create student
            try:
                password_hash = generate_password_hash(password)
                
                student = Student(
                    student_code=sanitize_string(student_code),
                    first_name=sanitize_string(first_name),
                    last_name=sanitize_string(last_name),
                    email=email,
                    phone_number=phone_number if phone_number else None,
                    program=sanitize_string(program),
                    year_of_study=year_of_study,
                    password_hash=password_hash,
                    is_active=True
                )
                
                db.session.add(student)
                db.session.flush()
                
                # Add to existing sets to prevent duplicates within the same CSV
                existing_codes.add(student_code.lower())
                existing_emails.add(email)
                
                successful_imports.append({
                    'row': row_num,
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'email': student.email
                })
                
            except Exception as e:
                db.session.rollback()
                errors.append({
                    'row': row_num,
                    'student_code': student_code,
                    'errors': [f'Database error: {str(e)}']
                })
        
        # Commit all successful imports
        if successful_imports:
            try:
                # Log bulk import to audit trail
                audit_details = create_audit_details(
                    operation='student_bulk_import',
                    metadata={
                        'total_rows': total_rows,
                        'successful_imports': len(successful_imports),
                        'failed_imports': len(errors),
                        'filename': file.filename
                    }
                )
                
                log_registration_action(
                    db=db,
                    RegistrationAuditLog=RegistrationAuditLog,
                    Admin=Admin,
                    action='create',
                    resource_type='student',
                    resource_id=0,  # Bulk operation, no single resource ID
                    admin_id=admin_id,
                    details=audit_details
                )
                
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Failed to commit bulk import: {e}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to commit bulk import',
                    'details': str(e)
                }), 500
        
        # Prepare response
        return jsonify({
            'success': True,
            'message': f'Bulk import completed. {len(successful_imports)} students imported successfully.',
            'data': {
                'total_rows': total_rows,
                'successful_imports': len(successful_imports),
                'failed_imports': len(errors),
                'success_rate': round((len(successful_imports) / total_rows * 100) if total_rows > 0 else 0, 2),
                'imported_students': successful_imports[:10],  # Show first 10
                'errors': errors[:20]  # Show first 20 errors
            }
        }), 200 if not errors else 207  # 207 Multi-Status if partial success
        
    except Exception as e:
        print(f"❌ Server error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error occurred during bulk import',
            'details': str(e)
        }), 500


@admin_student_bp.route('/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    """
    Update student information
    
    Request Body (all fields optional):
    {
        "first_name": "Jane",
        "last_name": "Smith",
        "phone_number": "+1987654321",
        "program": "Data Science",
        "year_of_study": 3,
        "is_active": true
    }
    
    Returns:
        JSON response with updated student details
    """
    try:
        # Get admin ID from JWT
        admin_id = get_jwt_identity()
        
        # Get student
        student = Student.query.get(student_id)
        
        if not student:
            return jsonify({
                'success': False,
                'error': f'Student with ID {student_id} not found'
            }), 404
        
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Store old values for audit
        old_values = {
            'first_name': student.first_name,
            'last_name': student.last_name,
            'phone_number': student.phone_number,
            'program': student.program,
            'year_of_study': student.year_of_study,
            'is_active': student.is_active
        }
        
        # Update fields
        updated_fields = []
        
        if 'first_name' in data:
            student.first_name = sanitize_string(data['first_name'])
            updated_fields.append('first_name')
        
        if 'last_name' in data:
            student.last_name = sanitize_string(data['last_name'])
            updated_fields.append('last_name')
        
        if 'phone_number' in data:
            if data['phone_number']:
                valid, error = validate_phone_number(data['phone_number'])
                if not valid:
                    return jsonify({
                        'success': False,
                        'error': error
                    }), 400
            student.phone_number = data['phone_number']
            updated_fields.append('phone_number')
        
        if 'program' in data:
            student.program = sanitize_string(data['program'])
            updated_fields.append('program')
        
        if 'year_of_study' in data:
            if data['year_of_study']:
                valid, error = validate_year_of_study(data['year_of_study'])
                if not valid:
                    return jsonify({
                        'success': False,
                        'error': error
                    }), 400
            student.year_of_study = data['year_of_study']
            updated_fields.append('year_of_study')
        
        if 'is_active' in data:
            student.is_active = data['is_active']
            updated_fields.append('is_active')
        
        # Commit changes
        try:
            # Log to audit trail
            audit_details = create_audit_details(
                operation='student_update',
                old_values=old_values,
                new_values={field: getattr(student, field) for field in updated_fields},
                metadata={'updated_fields': updated_fields}
            )
            
            log_registration_action(
                db=db,
                RegistrationAuditLog=RegistrationAuditLog,
                Admin=Admin,
                action='update',
                resource_type='student',
                resource_id=student_id,
                admin_id=admin_id,
                details=audit_details
            )
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Student updated successfully',
                'data': {
                    'student_id': student.student_id,
                    'student_code': student.student_code,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'phone_number': student.phone_number,
                    'program': student.program,
                    'year_of_study': student.year_of_study,
                    'is_active': student.is_active,
                    'updated_fields': updated_fields
                }
            }), 200
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Database error: {e}")
            return jsonify({
                'success': False,
                'error': 'Database error occurred during update',
                'details': str(e)
            }), 500
            
    except Exception as e:
        print(f"❌ Server error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error occurred',
            'details': str(e)
        }), 500


@admin_student_bp.route('', methods=['GET'])
@jwt_required()
def get_students():
    """
    Get all students with optional filters
    
    Query Parameters:
        - program: Filter by program
        - year: Filter by year of study
        - is_active: Filter by active status (true/false)
        - search: Search by name, email, or student code
    
    Returns:
        JSON response with list of students
    """
    try:
        # Get query parameters
        program = request.args.get('program')
        year = request.args.get('year', type=int)
        is_active = request.args.get('is_active', type=lambda v: v.lower() == 'true')
        search = request.args.get('search')
        
        # Build query
        query = Student.query
        
        if program:
            query = query.filter(Student.program.ilike(f'%{program}%'))
        
        if year is not None:
            query = query.filter_by(year_of_study=year)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    Student.first_name.ilike(search_pattern),
                    Student.last_name.ilike(search_pattern),
                    Student.email.ilike(search_pattern),
                    Student.student_code.ilike(search_pattern)
                )
            )
        
        # Execute query
        students = query.all()
        
        # Format response
        result = [
            {
                'student_id': student.student_id,
                'student_code': student.student_code,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone_number': student.phone_number,
                'program': student.program,
                'year_of_study': student.year_of_study,
                'is_active': student.is_active,
                'created_at': student.created_at.isoformat() if student.created_at else None
            }
            for student in students
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'students': result,
                'total_count': len(result)
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching students: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch students',
            'details': str(e)
        }), 500
