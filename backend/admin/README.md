# Admin Module Structure

This directory contains all the admin-related functionality for the IntelliAttend system, organized in a modular structure.

## Directory Structure

```
admin/
├── api/                 # API route handlers
│   ├── auth_routes.py    # Authentication endpoints
│   ├── faculty_routes.py # Faculty management endpoints
│   ├── student_routes.py # Student management endpoints
│   ├── classroom_routes.py # Classroom management endpoints
│   ├── class_routes.py   # Class management endpoints
│   ├── device_routes.py  # Device management endpoints
│   └── enrollment_routes.py # Enrollment management endpoints
├── models/              # Admin-specific data models (if any)
├── utils/               # Admin-specific utility functions
└── README.md           # This file
```

## API Endpoints

All admin endpoints are prefixed with `/api/admin`:

### Authentication
- `POST /api/admin/auth/login` - Admin login
- `POST /api/admin/auth/logout` - Admin logout

### Faculty Management
- `GET /api/admin/faculty` - List all faculty members
- `POST /api/admin/faculty` - Create new faculty member
- `GET /api/admin/faculty/<id>` - Get specific faculty member
- `PUT /api/admin/faculty/<id>` - Update faculty member
- `DELETE /api/admin/faculty/<id>` - Delete faculty member

### Student Management
- `GET /api/admin/students` - List all students
- `POST /api/admin/students` - Create new student
- `GET /api/admin/students/<id>` - Get specific student
- `PUT /api/admin/students/<id>` - Update student
- `DELETE /api/admin/students/<id>` - Delete student

### Classroom Management
- `GET /api/admin/classrooms` - List all classrooms
- `POST /api/admin/classrooms` - Create new classroom
- `GET /api/admin/classrooms/<id>` - Get specific classroom
- `PUT /api/admin/classrooms/<id>` - Update classroom
- `DELETE /api/admin/classrooms/<id>` - Delete classroom

### Class Management
- `GET /api/admin/classes` - List all classes
- `POST /api/admin/classes` - Create new class
- `GET /api/admin/classes/<id>` - Get specific class
- `PUT /api/admin/classes/<id>` - Update class
- `DELETE /api/admin/classes/<id>` - Delete class

### Device Management
- `GET /api/admin/devices` - List all student devices
- `GET /api/admin/devices/<id>` - Get specific device
- `DELETE /api/admin/devices/<id>` - Delete device

### Enrollment Management
- `GET /api/admin/enrollments` - List all enrollments
- `POST /api/admin/enrollments` - Create new enrollment
- `GET /api/admin/enrollments/<id>` - Get specific enrollment
- `PUT /api/admin/enrollments/<id>` - Update enrollment
- `DELETE /api/admin/enrollments/<id>` - Delete enrollment
- `GET /api/admin/students/<id>/enrollments` - Get student's enrollments
- `GET /api/admin/classes/<id>/enrollments` - Get class's enrollments