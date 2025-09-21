# IntelliAttend Mobile Module

A reusable Android module for WiFi, Bluetooth, and GPS environmental data collection.

## Overview

This module provides a unified interface for collecting environmental data from mobile devices, including:
- WiFi network information
- Bluetooth device detection
- GPS location data

The module is designed to be reusable across different applications, allowing developers to easily integrate environmental data collection capabilities.

## Features

### WiFi Data Collection
- Current WiFi connection information
- Available network scanning
- Internet connectivity status
- Signal strength analysis

### Bluetooth Data Collection
- BLE device scanning with batching
- Classic Bluetooth device detection
- Device proximity monitoring
- RSSI-based distance estimation

### GPS Data Collection
- High-accuracy location services
- Last known location retrieval
- Geofencing capabilities
- Distance calculations

## Installation

### Gradle Dependencies

Add the following dependencies to your app's `build.gradle`:

```gradle
dependencies {
    implementation 'com.google.android.gms:play-services-location:21.0.1'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.4'
    implementation 'androidx.core:core-ktx:1.9.0'
}
```

### Permissions

Add the following permissions to your `AndroidManifest.xml`:

```xml
<!-- Location Permissions -->
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

<!-- WiFi Permissions -->
<uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
<uses-permission android:name="android.permission.CHANGE_WIFI_STATE" />

<!-- Bluetooth Permissions -->
<uses-permission android:name="android.permission.BLUETOOTH" />
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />

<!-- Bluetooth Permissions for Android 12+ -->
<uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />

<!-- Required features -->
<uses-feature android:name="android.hardware.bluetooth_le" android:required="true" />
<uses-feature android:name="android.hardware.location.gps" android:required="true" />
<uses-feature android:name="android.hardware.wifi" android:required="true" />
```

## Usage

### Initialize the Module

```kotlin
val mobileModule = IntelliAttendMobileModule.create(context)
```

### Collect Environmental Data

```kotlin
// Get the environmental data collector
val collector = mobileModule.getEnvironmentalDataCollector()

// Start collecting data
collector.startCollecting(object : EnvironmentalDataCollector.EnvironmentalDataCallback {
    override fun onDataUpdated(data: EnvironmentalDataCollector.EnvironmentalData) {
        // Handle updated data
        data.wifiData?.let { wifi ->
            println("Connected to WiFi: ${wifi.ssid}")
        }
        
        data.bluetoothDevices.forEach { device ->
            println("Bluetooth device: ${device.name} (RSSI: ${device.rssi})")
        }
        
        data.gpsData?.let { gps ->
            println("Location: ${gps.latitude}, ${gps.longitude}")
        }
    }
    
    override fun onError(error: Exception) {
        // Handle errors
        println("Error collecting data: ${error.message}")
    }
})
```

### Use the Repository Pattern

```kotlin
// Get the environmental data repository
val repository = mobileModule.getEnvironmentalDataRepository()

// Observe WiFi data
lifecycleScope.launch {
    repository.wifiData.collect { wifiData ->
        wifiData?.let {
            // Update UI with WiFi data
        }
    }
}

// Refresh data
lifecycleScope.launch {
    repository.refreshWiFiData()
    repository.refreshGPSData()
}
```

## Architecture

The module follows a clean architecture pattern with the following components:

### Collector Layer
- `WiFiDataCollector`: Handles WiFi data collection
- `BluetoothDataCollector`: Handles Bluetooth device scanning
- `GPSDataCollector`: Handles GPS location services
- `EnvironmentalDataCollector`: Unified interface for all collectors

### Repository Layer
- `EnvironmentalDataRepository`: Manages data state and provides reactive data streams

### Model Layer
- `WiFiData`: WiFi network information model
- `BluetoothData`: Bluetooth device information model
- `GPSData`: GPS location data model
- `DeviceInfo`: Device identification model

### Utility Layer
- `DeviceUtils`: Device information and permission utilities

## Best Practices

### Permission Handling
Always check for required permissions before starting data collection:

```kotlin
val permissions = mobileModule.checkPermissions()
if (permissions.all { it.value }) {
    // All permissions granted
    collector.startCollecting(callback)
} else {
    // Request missing permissions
}
```

### Resource Management
Always stop Bluetooth scanning when it's no longer needed:

```kotlin
override fun onDestroy() {
    super.onDestroy()
    collector.stopCollecting()
}
```

### Error Handling
Implement proper error handling for all data collection operations:

```kotlin
try {
    val result = collector.getCurrentWiFiData()
    if (result.isSuccess) {
        // Handle success
    } else {
        // Handle failure
    }
} catch (e: Exception) {
    // Handle exceptions
}
```

## Testing

The module is designed to be easily testable with mock implementations for each collector.

## License

This module is part of the IntelliAttend project and is licensed under the MIT License.