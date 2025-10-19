# IntelliAttend API Testing Guide

This document provides comprehensive testing examples for all IntelliAttend APIs using curl commands.

## Table of Contents
1. [Authentication](#authentication)
2. [Admin - Classroom Management](#admin---classroom-management)
3. [Admin - Student Management](#admin---student-management)
4. [Admin - Faculty Management](#admin---faculty-management)
5. [Admin - Device Management](#admin---device-management)
6. [Mobile - Device Enforcement & Login](#mobile---device-enforcement--login)

---

## Base Configuration

```bash
# Set base URL
BASE_URL="http://localhost:5002"

# Get admin JWT token (replace with actual admin credentials)
ADMIN_TOKEN=$(curl -s -X POST "$BASE_URL/api/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@intelliattend.com","password":"admin123"}' \
  | jq -r '.access_token')

echo "Admin Token: $ADMIN_TOKEN"
```

---

## Authentication

### Admin Login
```bash
curl -X POST "$BASE_URL/api/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@intelliattend.com",
    "password": "admin123"
  }'
```

### Student Login (Mobile)
```bash
curl -X POST "$BASE_URL/api/mobile/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "student123",
    "device_info": {
      "device_uuid": "abc123-device-uuid",
      "device_name": "Samsung Galaxy S21",
      "device_type": "android",
      "device_model": "SM-G991B",
      "os_version": "Android 13",
      "app_version": "1.0.0"
    },
    "wifi_info": {
      "ssid": "Campus-WiFi",
      "bssid": "AA:BB:CC:DD:EE:FF"
    }
  }'
```

---

## Admin - Classroom Management

### 1. Create Classroom
```bash
curl -X POST "$BASE_URL/api/admin/classrooms" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "classroom_code": "BLOCK-A-101",
    "classroom_name": "Computer Science Lab 1",
    "building": "Block A",
    "floor": "1",
    "room_number": "101",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "radius_meters": 50,
    "capacity": 60,
    "classroom_type": "lab",
    "equipment": ["Projector", "AC", "Computers"]
  }'
```

### 2. Get All Classrooms
```bash
curl -X GET "$BASE_URL/api/admin/classrooms?page=1&per_page=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 3. Get Classroom by Code
```bash
curl -X GET "$BASE_URL/api/admin/classrooms/BLOCK-A-101" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 4. Update Classroom
```bash
curl -X PUT "$BASE_URL/api/admin/classrooms/BLOCK-A-101" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "classroom_name": "Advanced Computer Lab 1",
    "capacity": 70,
    "equipment": ["Projector", "AC", "Computers", "Smartboard"]
  }'
```

### 5. Delete Classroom (Soft Delete)
```bash
curl -X DELETE "$BASE_URL/api/admin/classrooms/BLOCK-A-101" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 6. Permanently Delete Classroom
```bash
curl -X DELETE "$BASE_URL/api/admin/classrooms/BLOCK-A-101?permanent=true" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 7. Search Classrooms by Proximity
```bash
curl -X GET "$BASE_URL/api/admin/classrooms/nearby?latitude=12.9716&longitude=77.5946&radius_meters=100" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Admin - Student Management

### 1. Create Student
```bash
curl -X POST "$BASE_URL/api/admin/students" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_code": "CSE2021001",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "student123",
    "program": "B.Tech Computer Science",
    "year_of_study": 3,
    "phone": "9876543210"
  }'
```

### 2. Get All Students
```bash
curl -X GET "$BASE_URL/api/admin/students?page=1&per_page=20&program=Computer%20Science" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 3. Get Student by Code
```bash
curl -X GET "$BASE_URL/api/admin/students/CSE2021001" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 4. Update Student
```bash
curl -X PUT "$BASE_URL/api/admin/students/CSE2021001" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "year_of_study": 4,
    "phone": "9876543211"
  }'
```

### 5. Delete Student (Soft Delete)
```bash
curl -X DELETE "$BASE_URL/api/admin/students/CSE2021001" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 6. Bulk Import Students via CSV
```bash
# Create sample CSV file
cat > students.csv << EOF
student_code,email,first_name,last_name,password,program,year_of_study,phone
CSE2021001,john.doe@example.com,John,Doe,pass123,B.Tech CSE,3,9876543210
CSE2021002,jane.smith@example.com,Jane,Smith,pass123,B.Tech CSE,3,9876543211
CSE2021003,bob.wilson@example.com,Bob,Wilson,pass123,B.Tech CSE,2,9876543212
EOF

# Upload CSV
curl -X POST "$BASE_URL/api/admin/students/bulk-import" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@students.csv"
```

### 7. Bulk Activate Students
```bash
curl -X POST "$BASE_URL/api/admin/students/bulk/activate" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_codes": ["CSE2021001", "CSE2021002", "CSE2021003"]
  }'
```

### 8. Bulk Deactivate Students
```bash
curl -X POST "$BASE_URL/api/admin/students/bulk/deactivate" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_codes": ["CSE2021001", "CSE2021002"]
  }'
```

---

## Admin - Faculty Management

### 1. Create Faculty
```bash
curl -X POST "$BASE_URL/api/admin/faculty" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "faculty_code": "FAC001",
    "email": "dr.smith@example.com",
    "first_name": "Robert",
    "last_name": "Smith",
    "password": "faculty123",
    "department": "Computer Science",
    "designation": "Professor",
    "phone": "9876543220"
  }'
```

### 2. Get All Faculty
```bash
curl -X GET "$BASE_URL/api/admin/faculty?page=1&per_page=20&department=Computer%20Science" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 3. Get Faculty by Code
```bash
curl -X GET "$BASE_URL/api/admin/faculty/FAC001" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 4. Update Faculty
```bash
curl -X PUT "$BASE_URL/api/admin/faculty/FAC001" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "designation": "Associate Professor",
    "phone": "9876543221"
  }'
```

### 5. Delete Faculty (Soft Delete)
```bash
curl -X DELETE "$BASE_URL/api/admin/faculty/FAC001" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 6. Bulk Activate Faculty
```bash
curl -X POST "$BASE_URL/api/admin/faculty/bulk/activate" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "faculty_codes": ["FAC001", "FAC002"]
  }'
```

---

## Admin - Device Management

### 1. Get All Device Switch Requests
```bash
# Get pending requests
curl -X GET "$BASE_URL/api/admin/devices/switch-requests?status=pending&page=1&per_page=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Get requests with cooldown complete
curl -X GET "$BASE_URL/api/admin/devices/switch-requests?cooldown_complete=true" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Search by student
curl -X GET "$BASE_URL/api/admin/devices/switch-requests?student_code=CSE2021001" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 2. Get Device Switch Request Detail
```bash
curl -X GET "$BASE_URL/api/admin/devices/switch-requests/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 3. Approve Device Switch Request
```bash
curl -X POST "$BASE_URL/api/admin/devices/switch-requests/1/approve" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Approved after verification. Student confirmed device change."
  }'
```

### 4. Reject Device Switch Request
```bash
curl -X POST "$BASE_URL/api/admin/devices/switch-requests/1/reject" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Suspicious activity detected. Multiple device changes in short period."
  }'
```

### 5. Get Student Devices
```bash
curl -X GET "$BASE_URL/api/admin/devices/students/CSE2021001/devices" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 6. Deactivate Device (Admin Override)
```bash
curl -X POST "$BASE_URL/api/admin/devices/students/CSE2021001/devices/abc123-device-uuid/deactivate" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Device reported as compromised"
  }'
```

### 7. Emergency Device Activation (Bypass 48-hour Cooldown)
```bash
curl -X POST "$BASE_URL/api/admin/devices/students/CSE2021001/devices/new-device-uuid/emergency-activate" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Student phone was stolen. New device required immediately.",
    "admin_notes": "Verified with student ID and emergency contact. Police report filed."
  }'
```

### 8. Get Device Activity Logs
```bash
# All logs
curl -X GET "$BASE_URL/api/admin/devices/activity-logs?page=1&per_page=50" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Filter by student
curl -X GET "$BASE_URL/api/admin/devices/activity-logs?student_code=CSE2021001" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Filter by device
curl -X GET "$BASE_URL/api/admin/devices/activity-logs?device_uuid=abc123-device-uuid" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Filter by activity type
curl -X GET "$BASE_URL/api/admin/devices/activity-logs?activity_type=device_activated" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Filter by date range
curl -X GET "$BASE_URL/api/admin/devices/activity-logs?start_date=2024-01-01T00:00:00Z&end_date=2024-12-31T23:59:59Z" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Mobile - Device Enforcement & Login

### 1. Student Login - First Time (New Device)
```bash
curl -X POST "$BASE_URL/api/mobile/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "student123",
    "device_info": {
      "device_uuid": "abc123-first-device",
      "device_name": "iPhone 13",
      "device_type": "ios",
      "device_model": "iPhone14,2",
      "os_version": "iOS 16.4",
      "app_version": "1.0.0"
    },
    "wifi_info": {
      "ssid": "Campus-WiFi",
      "bssid": "AA:BB:CC:DD:EE:FF"
    }
  }'
```

**Response:** Device will be activated immediately (first device)

### 2. Student Login - Device Switch (Within 48 Hours)
```bash
curl -X POST "$BASE_URL/api/mobile/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "student123",
    "device_info": {
      "device_uuid": "xyz789-new-device",
      "device_name": "Samsung Galaxy S23",
      "device_type": "android",
      "device_model": "SM-S911B",
      "os_version": "Android 13",
      "app_version": "1.0.0"
    },
    "wifi_info": {
      "ssid": "Campus-WiFi",
      "bssid": "AA:BB:CC:DD:EE:FF"
    }
  }'
```

**Response:** Login succeeds but `limited_access: true`, cannot mark attendance

### 3. Student Login - During Cooldown (Not Admin Approved)
When 48 hours have passed but admin hasn't approved yet:

**Response:**
```json
{
  "success": true,
  "message": "Login successful (Awaiting Admin Approval)",
  "device_status": "awaiting_admin_approval",
  "limited_access": true,
  "can_mark_attendance": false,
  "approval_info": {
    "cooldown_completed": true,
    "cooldown_hours": 48.5,
    "admin_approval_pending": true,
    "status": "pending_admin_approval",
    "message": "The 48-hour cooldown is complete. Your device activation request is now pending admin approval...",
    "restrictions": {
      "can_view_history": true,
      "can_view_classes": true,
      "can_view_profile": true,
      "can_mark_attendance": false,
      "reason": "Dual approval required: 48-hour cooldown complete ✓ | Admin approval pending ⏳"
    }
  }
}
```

### 4. Student Login - After Approval (Full Access)
After admin approves AND 48 hours passed:

**Response:**
```json
{
  "success": true,
  "message": "Device fully activated! You can now mark attendance.",
  "device_status": "active",
  "device_switch_completed": true,
  "dual_approval_complete": {
    "cooldown_completed": true,
    "admin_approved": true,
    "cooldown_hours": 50.2
  }
}
```

### 5. Check Device Status
```bash
curl -X GET "$BASE_URL/api/mobile/device-status" \
  -H "Authorization: Bearer $STUDENT_TOKEN"
```

### 6. Get Device Switch Request Status
```bash
curl -X GET "$BASE_URL/api/mobile/switch-request-status" \
  -H "Authorization: Bearer $STUDENT_TOKEN"
```

---

## Testing Scenarios

### Scenario 1: Complete Device Switch Workflow

```bash
# 1. Student logs in with new device (creates switch request)
STUDENT_TOKEN=$(curl -s -X POST "$BASE_URL/api/mobile/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "student123",
    "device_info": {
      "device_uuid": "new-device-2024",
      "device_name": "New Phone",
      "device_type": "android",
      "os_version": "Android 14",
      "app_version": "1.0.0"
    },
    "wifi_info": {
      "ssid": "Campus-WiFi",
      "bssid": "AA:BB:CC:DD:EE:FF"
    }
  }' | jq -r '.access_token')

# 2. Admin views pending requests
curl -X GET "$BASE_URL/api/admin/devices/switch-requests?status=pending" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 3. Wait for cooldown to complete (or skip in testing)
# In production: wait 48 hours
# In testing: you can modify the requested_at timestamp in DB

# 4. Admin approves the request
curl -X POST "$BASE_URL/api/admin/devices/switch-requests/1/approve" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Approved after verification"
  }'

# 5. Student logs in again (device now fully activated)
curl -X POST "$BASE_URL/api/mobile/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "student123",
    "device_info": {
      "device_uuid": "new-device-2024",
      "device_name": "New Phone",
      "device_type": "android"
    },
    "wifi_info": {
      "ssid": "Campus-WiFi",
      "bssid": "AA:BB:CC:DD:EE:FF"
    }
  }'
```

### Scenario 2: Emergency Device Activation

```bash
# Student reports phone stolen, needs immediate access

# 1. Admin performs emergency activation
curl -X POST "$BASE_URL/api/admin/devices/students/CSE2021001/devices/emergency-device-uuid/emergency-activate" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Student phone was stolen. Emergency replacement required.",
    "admin_notes": "Verified with student ID. Police report on file."
  }'

# 2. Student can immediately login with new device
curl -X POST "$BASE_URL/api/mobile/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "student123",
    "device_info": {
      "device_uuid": "emergency-device-uuid",
      "device_name": "Emergency Phone",
      "device_type": "android"
    },
    "wifi_info": {
      "ssid": "Campus-WiFi",
      "bssid": "AA:BB:CC:DD:EE:FF"
    }
  }'
```

### Scenario 3: Bulk Student Import and Device Management

```bash
# 1. Create CSV with student data
cat > students_batch1.csv << EOF
student_code,email,first_name,last_name,password,program,year_of_study,phone
CSE2024001,alice@example.com,Alice,Johnson,pass123,B.Tech CSE,1,9876540001
CSE2024002,bob@example.com,Bob,Williams,pass123,B.Tech CSE,1,9876540002
CSE2024003,charlie@example.com,Charlie,Brown,pass123,B.Tech CSE,1,9876540003
EOF

# 2. Bulk import students
curl -X POST "$BASE_URL/api/admin/students/bulk-import" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@students_batch1.csv"

# 3. Each student registers their device via mobile app
# (Students install app, login for first time with campus WiFi)

# 4. Admin monitors device registrations
curl -X GET "$BASE_URL/api/admin/devices/activity-logs?activity_type=device_registered&start_date=2024-01-01T00:00:00Z" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Error Handling Examples

### Invalid Campus WiFi
```bash
curl -X POST "$BASE_URL/api/mobile/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "student123",
    "device_info": {"device_uuid": "test-device"},
    "wifi_info": {
      "ssid": "Home-WiFi",
      "bssid": "11:22:33:44:55:66"
    }
  }'
```

**Response:** 403 Forbidden - "Campus WiFi required for device registration"

### Attendance Marking with Inactive Device
```bash
curl -X POST "$BASE_URL/api/mobile/mark-attendance" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": 123,
    "location": {"latitude": 12.9716, "longitude": 77.5946}
  }'
```

**Response:** 403 Forbidden - "Device not activated. Cannot mark attendance until [date]"

---

## Notes

1. **JWT Token Expiration:** Tokens expire after a configured period (default: 24 hours). Renew as needed.
2. **WiFi Validation:** Campus WiFi must be configured in the system before students can register.
3. **Device UUIDs:** Must be unique per device. Use device-specific identifiers (Android ID, iOS identifierForVendor).
4. **Cooldown Period:** Default is 48 hours. Can be configured via `DEVICE_SWITCH_COOLDOWN_HOURS` constant.
5. **Dual Approval:** Device switches require BOTH 48-hour cooldown AND admin approval.
6. **Emergency Activation:** Use sparingly and only for genuine emergencies with proper documentation.

---

## Postman Collection

Import this curl commands collection into Postman for easier testing:

1. Create a new Postman Collection
2. Add an environment variable `BASE_URL` = `http://localhost:5002`
3. Add an environment variable `ADMIN_TOKEN` (set after login)
4. Import each curl command as a new request

Alternatively, use the Postman collection JSON (create separate file).

---

## Database Migration

Before testing, ensure you've run the device enforcement migration:

```bash
psql -U your_username -d intelliattend -f backend/migrations/add_device_switch_and_activity_tables.sql
```

---

## Production Considerations

1. **HTTPS Only:** All APIs should use HTTPS in production
2. **Rate Limiting:** Implement rate limiting on sensitive endpoints
3. **Audit Logging:** All admin actions are logged for compliance
4. **Backup:** Regular database backups before testing bulk operations
5. **Monitoring:** Set up alerts for suspicious device activities

---

**Last Updated:** 2024-01-15
**Version:** 1.0.0
