# Device Enforcement - Testing Guide

## Prerequisites

1. **Backend running** with device enforcement enabled
2. **Campus WiFi networks configured** in database
3. **Tile38 geofencing** active with campus boundaries
4. **Android device** with:
   - WiFi enabled and connected to campus network
   - Location services enabled
   - GPS accuracy sufficient (< 50m)

## Test Scenarios

### 1. First Device Login (Primary Device)

**Steps:**
1. Open app on a new device
2. Enable WiFi and connect to campus network
3. Enable Location/GPS
4. Navigate to Login screen
5. Enter valid credentials:
   - Email: `alice.williams@student.edu`
   - Password: `student123`
6. Tap "Sign In"

**Expected Result:**
- ✅ Login succeeds
- ✅ Home screen loads
- ✅ No device status banner visible
- ✅ "Scan QR for Attendance" button is **ENABLED**
- ✅ Student profile card shows student info
- ✅ Backend console shows: "Device registered as primary"

**Console Logs to Check:**
```
🔍 Android Enhanced Login Debug - Response code: 200
✅ Android Enhanced Login Debug - Login successful, storing data
```

---

### 2. Device Switch Request (Second Device)

**Steps:**
1. Logout from first device (or use a different phone)
2. Open app on second device
3. Connect to campus WiFi
4. Enable GPS
5. Login with same credentials

**Expected Result:**
- ✅ Login succeeds (doesn't block)
- ✅ **Device Status Banner appears** with:
  - Title: "Device Switch Pending"
  - Countdown timer showing 48:00:00 (or less)
  - Orange warning background
  - Message: "Attendance marking is currently disabled"
  - Message: "Awaiting administrator approval"
- ✅ "Scan QR for Attendance" button changes to "Attendance Disabled"
- ✅ Attendance button is **DISABLED** (grayed out)
- ✅ Warning text: "Device activation required to mark attendance"

**Console Logs:**
```
Device switch detected
Cooldown period: 48 hours
Requires admin approval: true
```

---

### 3. Countdown Timer Verification

**Steps:**
1. Stay on Home screen after device switch login
2. Observe the countdown timer

**Expected Result:**
- ✅ Timer updates every second: `47:59:59`, `47:59:58`, etc.
- ✅ Progress bar gradually fills from left to right
- ✅ Format is `HH:MM:SS`
- ✅ Time accurately reflects remaining cooldown

---

### 4. Device Status Auto-Refresh

**Steps:**
1. Login from second device
2. Navigate to Home screen
3. Wait for 30+ seconds without interacting
4. Observe the device status

**Expected Result:**
- ✅ Every 30 seconds, device status refreshes
- ✅ Countdown timer continues accurately
- ✅ No manual refresh needed
- ✅ UI remains responsive

**Console Logs:**
```
(Every 30 seconds)
Loading device status...
Device status updated: cooldown_remaining = XXXX
```

---

### 5. Admin Approval Flow

**Steps:**
1. Login from second device (device switch)
2. Open admin web dashboard
3. Navigate to "Device Approvals" or "Pending Requests"
4. Find the student's device switch request
5. Click "Approve"
6. Return to mobile app

**Expected Result:**
- ✅ Within 30 seconds, device status banner **disappears**
- ✅ Attendance button becomes **ENABLED**
- ✅ Button text: "Scan QR for Attendance"
- ✅ Student can now mark attendance

**Backend Response:**
```json
{
  "success": true,
  "device_status": {
    "is_active": true,
    "can_mark_attendance": true,
    "cooldown_remaining_seconds": null
  }
}
```

---

### 6. Invalid WiFi Login

**Steps:**
1. Disconnect from campus WiFi
2. Connect to home/mobile WiFi
3. Try to login

**Expected Result:**
- ❌ Login **FAILS**
- ❌ Error message: "Please connect to campus WiFi to login" or "Invalid WiFi network"
- ❌ Login screen shows error card (red background)
- ❌ Student remains on login screen

---

### 7. Out of Campus GPS Login

**Steps:**
1. Connect to campus WiFi (or use WiFi hotspot with campus SSID)
2. Go physically outside campus boundaries
3. Try to login

**Expected Result:**
- ❌ Login **FAILS**
- ❌ Error message: "You must be on campus to login" or "Location validation failed"
- ❌ Red error card appears
- ❌ Login screen does not proceed

---

### 8. Missing Permissions

**Steps:**
1. Disable Location/GPS in device settings
2. Try to login

**Expected Result:**
- ❌ Login **FAILS** or shows warning
- ❌ Error: "WiFi and Location permissions are required"
- ❌ App may prompt for permissions
- ❌ Cannot proceed without permissions

---

### 9. Cooldown Expiry Without Approval

**Steps:**
1. Login from second device
2. Wait 48 hours (or manually update database to expire cooldown)
3. Observe device status

**Expected Result:**
- ✅ Timer reaches `00:00:00`
- ✅ Banner changes to "Approval Required" (purple background)
- ✅ Message: "Awaiting administrator approval"
- ✅ Attendance button **STILL DISABLED**
- ✅ Countdown progress bar at 100%

---

### 10. Multiple Logins Between Devices

**Steps:**
1. Login on Device A (primary)
2. Logout
3. Login on Device B (switch request created)
4. Logout
5. Try to login on Device A again

**Expected Result:**
- ✅ Device A may show cooldown (depending on business logic)
- ✅ OR Device A is allowed (if it's still the registered primary)
- ✅ Backend enforces 48-hour rule correctly
- ✅ Only one device can mark attendance at a time

---

## Testing Checklist

- [ ] First login on new device works correctly
- [ ] Device switch creates cooldown period
- [ ] Countdown timer displays and updates
- [ ] Attendance button is properly disabled
- [ ] Device status banner shows correct information
- [ ] Auto-refresh works every 30 seconds
- [ ] Admin approval enables the device
- [ ] Invalid WiFi prevents login
- [ ] Out of campus GPS prevents login
- [ ] Missing permissions handled gracefully
- [ ] Cooldown expiry shows approval required
- [ ] Multiple device switches handled correctly

---

## API Testing with Postman/cURL

### Enhanced Login
```bash
curl -X POST http://YOUR_BACKEND/api/mobile/v2/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice.williams@student.edu",
    "password": "student123",
    "device_info": {
      "device_uuid": "test-device-123",
      "device_name": "Test Phone",
      "device_type": "android",
      "device_model": "Pixel 6",
      "os_version": "Android 13",
      "app_version": "1.0.0"
    },
    "wifi_info": {
      "ssid": "CampusWiFi",
      "bssid": "AA:BB:CC:DD:EE:FF",
      "signal_strength": 4
    },
    "gps_info": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "accuracy": 10.5,
      "timestamp": 1234567890
    },
    "permissions": {
      "wifi": true,
      "gps": true,
      "bluetooth": true
    }
  }'
```

### Get Device Status
```bash
curl -X GET http://YOUR_BACKEND/api/mobile/v2/device-status \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Debugging Tips

### Check Backend Logs
```
grep "device_enforcement" backend.log
grep "cooldown" backend.log
grep "wifi_validation" backend.log
```

### Check Mobile Logs (Android)
```bash
adb logcat | grep "Enhanced Login"
adb logcat | grep "Device Status"
adb logcat | grep "DeviceEnforcement"
```

### Verify Database
```sql
-- Check student's devices
SELECT * FROM student_devices WHERE student_id = X;

-- Check device switch requests
SELECT * FROM device_switch_requests WHERE student_id = X;

-- Check campus WiFi networks
SELECT * FROM campus_wifi_networks;
```

---

## Common Issues

### Issue: Timer not updating
- **Solution:** Check if device status polling is active
- **Check:** HomeViewModel's `startDeviceStatusPolling()` is called

### Issue: Banner not showing
- **Solution:** Verify `device_status` is not null in HomeUiState
- **Check:** Enhanced login returns `device_status` in response

### Issue: Login fails with "Network error"
- **Solution:** Backend may not be running or endpoint not registered
- **Check:** Backend logs for 404 or 500 errors

### Issue: GPS location null
- **Solution:** Enable location services and grant permissions
- **Check:** `DeviceEnforcementUtils.getCurrentLocation()` returns valid data

### Issue: WiFi info null
- **Solution:** Connect to WiFi network (not mobile data)
- **Check:** WiFi is enabled and connected

---

## Success Indicators

✅ **Full Device Enforcement Working:**
- First login on new device succeeds immediately
- Second device shows cooldown banner
- Countdown timer updates in real-time
- Attendance button is disabled appropriately
- Auto-refresh keeps status current
- Admin approval enables device
- Invalid WiFi/GPS blocks login

✅ **UI/UX Quality:**
- Device status banner is visually clear
- Color coding helps identify status (red, orange, purple)
- Countdown is large and readable
- Progress bar provides visual feedback
- Error messages are helpful and actionable

✅ **Backend Integration:**
- All API endpoints respond correctly
- Device validation works as expected
- Cooldown mechanism enforces 48-hour period
- Admin approval flow updates device status
- Database records device switches accurately
