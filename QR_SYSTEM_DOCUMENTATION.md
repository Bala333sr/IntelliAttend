# QR Code Generation and Decryption System - IntelliAttend

## Overview

The IntelliAttend system uses a sophisticated QR code generation and validation system to ensure secure attendance marking. QR codes are dynamically generated every 5 seconds with encrypted data and multiple security layers.

## QR Code Data Structure

### Generated QR Data Payload
```json
{
  "v": "1.0",                    // Version
  "sid": 123,                   // Session ID
  "tok": "base_token_string",   // Base session token
  "seq": 5,                     // Sequence number
  "ts": 1705123456,             // Unix timestamp
  "sec": "secure_hash",         // Security token (SHA256)
  "exp": 1705123466             // Expiry timestamp (ts + 5s + 2s buffer)
}
```

### Security Features
1. **Version Control**: Ensures compatibility (`v: "1.0"`)
2. **Session ID**: Links QR to specific attendance session
3. **Base Token**: Persistent session identifier
4. **Sequence Number**: Increments with each QR generation
5. **Timestamp**: Current Unix timestamp for freshness validation
6. **Security Token**: SHA256 hash of `session_id:timestamp:sequence:random_hex`
7. **Expiry**: Built-in expiration (5 seconds + 2 second buffer)

## QR Generation Process

### Backend Generation Flow

1. **Session Initialization**
   ```python
   # Create attendance session
   session_token = generate_token()        # 32-byte secure token
   secret_key = generate_token()          # 32-byte secret key
   expires_at = datetime.utcnow() + timedelta(minutes=duration)
   
   # Store in database
   attendance_session = AttendanceSession(
       class_id=class_id,
       faculty_id=faculty_id,
       qr_token=session_token,
       qr_secret_key=secret_key,
       qr_expires_at=expires_at
   )
   ```

2. **Background QR Generation Thread**
   ```python
   def generate_qr_sequence():
       while datetime.utcnow() < end_time:
           # Create QR data payload
           qr_data = {
               'v': '1.0',
               'sid': session_id,
               'tok': base_token,
               'seq': sequence,
               'ts': int(time.time()),
               'sec': generate_secure_token(session_id, timestamp, sequence),
               'exp': timestamp + 5 + 2  # 5s refresh + 2s buffer
           }
           
           # Generate QR image
           qr_image = create_qr_image(json.dumps(qr_data))
           
           # Save QR image and secret key
           save_qr_image(qr_image, session_id, sequence)
           save_secret_key(session_id, sequence, qr_data)
           
           # Wait 5 seconds before next QR
           time.sleep(5)
   ```

3. **File Structure**
   ```
   QR_DATA/
   ├── tokens/                    # QR code images
   │   ├── qr_s123_seq001_1705123456.png
   │   ├── qr_s123_seq002_1705123461.png
   │   └── ...
   ├── keys/                      # Secret validation keys
   │   ├── key_s123_seq001.json
   │   ├── key_s123_seq002.json
   │   └── ...
   └── archive/                   # Archived QR codes
   ```

## QR Decryption and Validation Process

### Mobile App Scanning Flow

1. **Image Capture**
   - Student opens camera in mobile app
   - App captures image containing QR code
   - Image processed using camera API or gallery selection

2. **QR Detection and Decoding**
   ```kotlin
   // In mobile app (Android/Kotlin)
   fun scanQRCode(imageData: String) {
       // Send base64 image data to backend
       val request = ScanRequest(
           qr_image = imageData,
           location = getCurrentLocation(),
           bluetooth = getBluetoothData(),
           biometric = getBiometricVerification(),
           device_info = getDeviceInfo()
       )
       
       // POST to /api/attendance/scan
       apiService.scanAttendance(request)
   }
   ```

3. **Backend Processing Pipeline**
   ```python
   @app.route('/api/attendance/scan', methods=['POST'])
   def scan_attendance():
       # Extract scan data from request
       qr_data_str = data.get('qr_data')
       
       # Decode QR using enhanced decoder
       decoder = QRDecoder(config)
       scan_result = decoder.process_student_scan(image_data, 'base64')
       
       if scan_result['success']:
           qr_data = json.loads(scan_result['qr_data'])
           # Validate session and mark attendance
           validate_and_mark_attendance(qr_data, student_data)
   ```

### QR Validation Steps

1. **Image Processing** (Enhanced Multi-Method Approach)
   ```python
   def enhanced_qr_decode(image_data):
       # Try multiple processing methods:
       methods = [
           ('original', original_image),
           ('grayscale', cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)),
           ('preprocessed', preprocess_image(original))
       ]
       
       for method_name, processed_img in methods:
           qr_codes = pyzbar.decode(processed_img)
           # Calculate confidence score for each detection
   ```

2. **QR Data Validation**
   ```python
   def validate_qr_data(qr_data_str):
       qr_data = json.loads(qr_data_str)
       
       # Check required fields
       session_id = qr_data.get('sid')
       sequence = qr_data.get('seq')
       timestamp = qr_data.get('ts')
       version = qr_data.get('v')
       
       # Validate version compatibility
       if version != '1.0':
           return {'valid': False, 'error': 'Version mismatch'}
       
       # Check timestamp freshness (5 minute tolerance)
       current_time = int(datetime.utcnow().timestamp())
       if abs(current_time - timestamp) > 300:
           return {'valid': False, 'error': 'QR code too old/future'}
       
       # Load secret key for validation
       key_file = f"key_s{session_id}_seq{sequence:03d}.json"
       with open(f"QR_DATA/keys/{key_file}") as f:
           secret_data = json.load(f)
       
       # Validate data integrity
       if hashlib.md5(qr_data_str.encode()).hexdigest() != \
          hashlib.md5(secret_data['qr_data'].encode()).hexdigest():
           return {'valid': False, 'error': 'Data integrity check failed'}
       
       return {'valid': True, 'session_id': session_id, ...}
   ```

3. **Session Validation**
   ```python
   # Verify session exists and is active
   session = AttendanceSession.query.filter_by(
       session_id=session_id,
       qr_token=token,
       status='active'
   ).first()
   
   if not session or datetime.utcnow() > session.qr_expires_at:
       return {'error': 'Invalid or expired session'}
   ```

## Security Measures

### Multi-Layer Security
1. **Time-based Expiration**: QR codes expire every 5-7 seconds
2. **Sequence Validation**: Each QR has unique sequence number
3. **Token Verification**: Base session token must match
4. **Hash Integrity**: SHA256 hash prevents tampering
5. **Secret Key Validation**: Backend validates against stored secret
6. **Session State**: Active session verification in database

### Attack Prevention
- **Replay Attacks**: Timestamp and sequence validation
- **QR Theft**: Short expiration time (5 seconds)
- **Data Tampering**: Hash integrity checks
- **Session Hijacking**: Secure token generation and storage
- **Brute Force**: Complex token generation with cryptographic randomness

## Integration Points

### Frontend (SmartBoard Display)
```javascript
// Fetch current QR code
async function updateQRCode() {
    const response = await fetch(`/api/qr/current/${sessionId}`);
    const data = await response.json();
    
    if (data.success) {
        document.getElementById('qr-image').src = 
            `/static/qr_tokens/${data.qr_filename}`;
    }
}

// Update every 4 seconds (before QR expires)
setInterval(updateQRCode, 4000);
```

### Mobile App (Student Scanning)
```kotlin
// QR Scanner integration
class QRScannerViewModel {
    fun processQRScan(qrData: String) {
        // Validate QR format
        val qrPayload = parseQRData(qrData)
        
        // Collect verification data
        val scanRequest = ScanRequest(
            qr_data = qrData,
            biometric_verified = biometricManager.verify(),
            location = locationManager.getCurrentLocation(),
            bluetooth = bluetoothManager.getNearbyDevices(),
            device_info = deviceManager.getDeviceInfo()
        )
        
        // Submit to backend
        attendanceService.markAttendance(scanRequest)
    }
}
```

### Backend API Endpoints
```python
# QR Generation
POST /api/qr/start          # Start attendance session
GET  /api/qr/current/<id>   # Get current QR image
POST /api/session/stop/<id> # Stop session

# Attendance Scanning
POST /api/attendance/scan   # Process student scan

# Service Status
GET  /api/qr/status        # QR service health
GET  /api/health           # Overall system health
```

## Performance Optimizations

### QR Generation
- **Background Threading**: Non-blocking QR generation
- **File Caching**: Efficient image storage and retrieval
- **Memory Management**: Cleanup of expired QR data
- **Concurrent Access**: Thread-safe session management

### QR Processing
- **Multi-Method Decoding**: Fallback strategies for poor image quality
- **Confidence Scoring**: Best result selection from multiple methods
- **Image Preprocessing**: Gaussian blur, thresholding, morphological operations
- **Parallel Processing**: Multiple QR codes in single image

### Database Optimization
- **Indexed Lookups**: Fast session and student queries
- **Connection Pooling**: Efficient database connections
- **Transaction Management**: Proper commit/rollback handling
- **Cleanup Jobs**: Automated removal of expired data

## Configuration Options

### QR Generation Settings
```python
QR_CODE_SIZE = 10              # QR code box size
QR_CODE_BORDER = 4             # Border size around QR
QR_REFRESH_INTERVAL = 5        # Seconds between QR updates
QR_TOKENS_FOLDER = 'QR_DATA/tokens'
QR_KEYS_FOLDER = 'QR_DATA/keys'
```

### Validation Settings
```python
BLUETOOTH_PROXIMITY_RSSI = -80  # Minimum RSSI for Bluetooth verification
GPS_ACCURACY_THRESHOLD = 20     # Maximum GPS accuracy for location verification
VERIFICATION_SCORE_THRESHOLD = 0.6  # Minimum score for attendance marking
SESSION_TIMEOUT_MINUTES = 10    # Maximum session duration
```

## Error Handling and Logging

### Common Error Scenarios
1. **QR Not Found**: No QR codes detected in image
2. **Invalid Format**: QR data not in expected JSON format
3. **Expired QR**: QR code timestamp too old
4. **Session Invalid**: Session not found or inactive
5. **Already Marked**: Student attendance already recorded
6. **Verification Failed**: Insufficient verification score

### Logging Strategy
```python
# QR Generation Logging
logger.info(f"✅ Generated QR #{sequence} for session {session_id}")
logger.warning(f"❌ Failed to save QR image for session {session_id}")
logger.error(f"🔥 Critical error in QR generation: {error}")

# Validation Logging
logger.info(f"📱 Student {student_id} scanned QR for session {session_id}")
logger.warning(f"⚠️ Invalid QR scan attempt: {error_reason}")
logger.error(f"🚨 Scan processing error: {error}")
```

This QR system provides robust security while maintaining usability for both faculty and students. The dynamic nature of QR codes combined with multi-factor verification ensures accurate attendance tracking while preventing common attack vectors.