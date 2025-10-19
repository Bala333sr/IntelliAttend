# IntelliAttend Mobile App

A modern Android application for intelligent attendance management using device fingerprinting, location services, and biometric authentication.

## Features

- **Device Fingerprinting**: Unique device identification for secure attendance
- **Location-based Attendance**: GPS and WiFi-based location verification
- **Biometric Authentication**: Fingerprint and face recognition support
- **Real-time Sync**: Instant attendance data synchronization
- **Offline Support**: Works without internet connectivity
- **Modern UI**: Material Design 3 with Jetpack Compose

## Tech Stack

- **Language**: Kotlin
- **UI Framework**: Jetpack Compose
- **Architecture**: MVVM with Clean Architecture
- **Dependency Injection**: Hilt
- **Networking**: Retrofit + OkHttp
- **Database**: Room (SQLite)
- **Authentication**: Biometric API
- **Location**: Google Play Services Location
- **Build System**: Gradle with KSP

## Project Structure

```
mobile/app/
├── app/
│   ├── src/main/java/com/intelliattend/student/
│   │   ├── ui/           # Compose UI screens
│   │   ├── data/         # Repository and data sources
│   │   ├── domain/       # Use cases and business logic
│   │   ├── network/      # API services and models
│   │   ├── utils/        # Utility classes
│   │   └── auto/         # Auto-attendance features
│   └── build.gradle      # App module configuration
├── build.gradle          # Project configuration
└── gradle.properties     # Gradle properties
```

## Getting Started

### Prerequisites

- Android Studio Hedgehog or later
- JDK 17
- Android SDK 34
- Gradle 8.12+

### Setup

1. Clone the repository
2. Open in Android Studio
3. Sync project with Gradle files
4. Configure `local.properties` with your SDK path
5. Build and run on device/emulator

### Configuration

Update the base URL in `app/build.gradle`:

```gradle
buildConfigField "String", "BASE_URL", '"http://your-server:8080/api/"'
```

## Build

```bash
./gradlew assembleDebug      # Debug build
./gradlew assembleRelease    # Release build
./gradlew test              # Run tests
```

## Contributing

1. Follow Kotlin coding conventions
2. Use Jetpack Compose for UI
3. Implement proper error handling
4. Add unit tests for business logic
5. Update documentation

## License

This project is part of the IntelliAttend system for educational institutions.