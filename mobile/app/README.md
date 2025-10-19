# IntelliAttend Mobile App

The IntelliAttend Mobile App is an Android application that allows students to mark their attendance using QR codes and multi-factor verification.

## Features

- **QR Code Scanning**: Scan QR codes displayed on SmartBoard portals
- **Biometric Authentication**: Fingerprint or face recognition for identity verification
- **Location Verification**: GPS-based verification to ensure students are in the classroom
- **Bluetooth Proximity**: Bluetooth beacon detection for additional verification
- **Offline Capability**: Store attendance data locally when offline and sync when connected
- **Real-time Updates**: Receive notifications about attendance sessions

## Prerequisites

- Android Studio Arctic Fox or later
- Android SDK API level 21 (Android 5.0) or higher
- Kotlin 1.5 or later
- Gradle 7.0 or later

## Setup

1. Open Android Studio
2. Clone or download the IntelliAttend repository
3. Open the `Mobile App` directory as a project in Android Studio
4. Sync the project with Gradle files
5. Build and run the application

## Project Structure

```
app/
├── src/
│   ├── main/
│   │   ├── java/com/intelliattend/student/
│   │   │   ├── MainActivity.kt          # Main activity
│   │   │   ├── LoginActivity.kt         # User authentication
│   │   │   ├── ScannerActivity.kt       # QR code scanning
│   │   │   ├── AttendanceActivity.kt    # Attendance processing
│   │   │   ├── network/                 # Network components
│   │   │   ├── database/                # Local database
│   │   │   └── utils/                   # Utility classes
│   │   ├── res/                         # Resources
│   │   └── AndroidManifest.xml         # Application manifest
│   └── test/                           # Unit tests
├── build.gradle                        # Module-level build file
└── proguard-rules.pro                  # ProGuard rules
```

## Key Components

### Authentication
- Secure login with email and password
- JWT token management
- Session handling

### QR Scanning
- Camera integration for QR code capture
- Real-time QR code detection
- QR code validation

### Biometric Verification
- Fingerprint authentication
- Face recognition (on supported devices)
- Fallback authentication methods

### Location Services
- GPS location retrieval
- Geofencing for classroom verification
- Location accuracy checking

### Bluetooth Integration
- Bluetooth beacon scanning
- Proximity detection
- RSSI signal strength measurement

### Data Management
- Local database using Room
- Offline data storage
- Data synchronization with backend

## API Integration

The mobile app communicates with the IntelliAttend backend through RESTful APIs:

- **Authentication**: `/api/student/login`
- **QR Processing**: `/api/attendance/scan`
- **Session Management**: `/api/session/*`

## Permissions

The app requires the following permissions:

- `CAMERA`: For QR code scanning
- `ACCESS_FINE_LOCATION`: For location verification
- `BLUETOOTH_SCAN`: For Bluetooth beacon detection
- `USE_BIOMETRIC`: For biometric authentication
- `INTERNET`: For network communication

## Testing

### Unit Tests
Run unit tests using:
```bash
./gradlew test
```

### Instrumentation Tests
Run instrumentation tests on connected devices:
```bash
./gradlew connectedAndroidTest
```

## Building

### Debug Build
```bash
./gradlew assembleDebug
```

### Release Build
```bash
./gradlew assembleRelease
```

## Deployment

1. Generate a signed APK or App Bundle
2. Upload to Google Play Console
3. Configure app signing
4. Publish to production or beta tracks

## Troubleshooting

### Common Issues

1. **Camera not working**: Ensure camera permissions are granted
2. **Location services not available**: Check if location services are enabled
3. **Bluetooth not detecting beacons**: Ensure Bluetooth is enabled and permissions are granted
4. **Network errors**: Check internet connectivity and backend server status

### Debugging

- Use Android Studio's Logcat to view application logs
- Enable debug mode in the app settings
- Check the backend server logs for API-related issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact the development team or open an issue on the repository.