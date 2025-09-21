# IntelliAttend Admin Guide

## Overview

This guide provides comprehensive information on using the IntelliAttend administration panel to manage all aspects of the smart attendance system. The admin panel allows administrators to manage faculty, students, classes, classrooms, devices, attendance records, and system settings.

## Accessing the Admin Panel

1. Navigate to `http://your-server/admin` in your web browser
2. Login with your admin credentials
3. Upon successful authentication, you'll be redirected to the admin dashboard

## Admin Dashboard

The dashboard provides an overview of the system with key metrics and recent activity:

- Total faculty members
- Total student count
- Active attendance sessions
- Pending requests
- Attendance trends visualization
- Recent activity feed

## Faculty Management

### Viewing Faculty
- Navigate to "Faculty Management" in the sidebar
- View all faculty members in a searchable table
- See faculty details including name, email, department, and status

### Adding New Faculty
1. Click "Add New Faculty" button
2. Fill in all required fields:
   - Faculty Code (unique identifier)
   - First Name and Last Name
   - Email (must be unique)
   - Phone Number
   - Department
   - Password (for faculty login)
   - Status (Active/Inactive)
3. Click "Save Faculty"

### Editing Faculty
1. Click the edit icon next to any faculty member
2. Modify the required fields
3. Click "Save Faculty"

### Deleting Faculty
1. Click the delete icon next to any faculty member
2. Confirm the deletion when prompted
3. Note: Faculty members with associated classes cannot be deleted

## Student Management

### Viewing Students
- Navigate to "Student Management" in the sidebar
- View all students in a searchable table
- See student details including name, email, program, year of study, and status

### Adding New Students
1. Click "Add New Student" button
2. Fill in all required fields:
   - Student Code (unique identifier)
   - First Name and Last Name
   - Email (must be unique)
   - Program
   - Year of Study
   - Password (for student login)
   - Status (Active/Inactive)
3. Click "Save Student"

### Editing Students
1. Click the edit icon next to any student
2. Modify the required fields
3. Click "Save Student"

### Deleting Students
1. Click the delete icon next to any student
2. Confirm the deletion when prompted
3. Note: Students with attendance records cannot be deleted

## Class Management

### Viewing Classes
- Navigate to "Class Management" in the sidebar
- View all classes in a searchable table
- See class details including code, name, faculty, classroom, semester, and status

### Adding New Classes
1. Click "Add New Class" button
2. Fill in all required fields:
   - Class Code (unique identifier)
   - Class Name
   - Faculty (select from dropdown)
   - Classroom (optional, select from dropdown)
   - Semester (Fall/Spring/Summer)
   - Academic Year (e.g., 2024-2025)
   - Credits
   - Max Students
   - Schedule (day and time, optional)
   - Status (Active/Inactive)
3. Click "Save Class"

### Editing Classes
1. Click the edit icon next to any class
2. Modify the required fields
3. Click "Save Class"

### Deleting Classes
1. Click the delete icon next to any class
2. Confirm the deletion when prompted
3. Note: Classes with attendance sessions cannot be deleted

## Classroom Management

### Viewing Classrooms
- Navigate to "Classroom Management" in the sidebar
- View all classrooms in a searchable table
- See classroom details including room number, building, floor, capacity, and geofencing settings

### Adding New Classrooms
1. Click "Add New Classroom" button
2. Fill in all required fields:
   - Room Number (unique identifier)
   - Building Name
   - Floor Number (optional)
   - Capacity
   - Geolocation (latitude and longitude for geofencing)
   - Geofence Radius (in meters)
   - Bluetooth Beacon ID (for proximity detection)
   - Status (Active/Inactive)
3. Click "Save Classroom"

### Editing Classrooms
1. Click the edit icon next to any classroom
2. Modify the required fields
3. Click "Save Classroom"

### Deleting Classrooms
1. Click the delete icon next to any classroom
2. Confirm the deletion when prompted
3. Note: Classrooms assigned to classes cannot be deleted

## Device Management

### Viewing Devices
- Navigate to "Device Management" in the sidebar
- View all registered student devices
- See device details including student name, device name, type, UUID, and permissions

### Managing Device Permissions
1. Click the edit icon next to any device
2. Toggle permissions for:
   - Biometric verification
   - Location access
   - Bluetooth connectivity
3. Update device status (Active/Inactive)
4. Click "Save Device"

### Deleting Devices
1. Click the delete icon next to any device
2. Confirm the deletion when prompted

## Attendance Records

### Viewing Attendance
- Navigate to "Attendance Records" in the sidebar
- View all attendance records in a searchable table
- Filter by student, class, status, or date
- See details including verification score and timestamp

### Exporting Attendance Data
1. Use the search and filter options to narrow down records
2. Click "Export Records" to download data in CSV format

## Session Management

### Viewing Sessions
- Navigate to "Session Management" in the sidebar
- View all attendance sessions
- Filter by class, faculty, status, or date
- See session details including start/end times and student counts

### Managing Active Sessions
- View currently active sessions
- Stop sessions manually if needed
- Monitor session statistics

## System Settings

### WiFi Configuration
- Set WiFi network credentials for student devices
- Configure security settings

### Bluetooth Configuration
- Set Bluetooth device parameters
- Configure proximity thresholds

### Geofencing Configuration
- Set default geofence radius
- Configure location accuracy thresholds
- Set GPS update intervals

### System Configuration
- Configure QR refresh intervals
- Set OTP expiry times
- Define maximum session durations

## Substitute Faculty Management

### Assigning Substitute Faculty
1. Navigate to the class or session that needs a substitute
2. Click "Assign Substitute" button
3. Select a qualified faculty member from the dropdown
4. Set the substitution period
5. Save the assignment

### Managing Substitutions
- View all active substitutions
- Modify substitution details
- Cancel substitutions when no longer needed

## Data Management

### Importing Data
- Use the bulk import feature to add multiple faculty, students, or classes
- Upload CSV files with the required data format
- Review import results and resolve any errors

### Exporting Data
- Export faculty, student, class, or attendance data
- Download in various formats (CSV, Excel, PDF)
- Schedule automated exports

### Data Cleanup
- Remove old attendance records
- Archive completed semesters
- Purge unused data while maintaining compliance

## Security Features

### Admin Roles
- **Super Admin**: Full access to all features
- **Admin**: Manage faculty, students, classes, and attendance
- **Operator**: Limited access to view and basic management

### Audit Logs
- Track all admin actions
- Monitor login attempts
- Review data changes

### Password Policies
- Enforce strong password requirements
- Set password expiry periods
- Implement account lockout after failed attempts

## Troubleshooting

### Common Issues
1. **Login Problems**: Verify credentials and check account status
2. **Data Not Loading**: Check network connectivity and database status
3. **Permission Errors**: Ensure admin role has required permissions

### System Monitoring
- Check system health status
- Monitor active sessions
- Review error logs

## Best Practices

1. **Regular Backups**: Schedule automated database backups
2. **Data Validation**: Verify imported data for accuracy
3. **User Training**: Provide adequate training for admin users
4. **Security Updates**: Keep the system updated with latest security patches
5. **Performance Monitoring**: Monitor system performance and optimize as needed

## Support

For technical support, contact the IntelliAttend support team at support@intelliattend.com or call +1-800-ATTEND.

## Version Information

Current Version: 1.0.0
Release Date: September 2024