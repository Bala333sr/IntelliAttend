# Integration Guide

## How to Integrate IntelliAttend Mobile Module into Your App

### Step 1: Add the Module to Your Project

1. Copy the `mobile-module` directory to your project root
2. Add the module to your `settings.gradle` file:

```gradle
include ':mobile-module'
```

3. Add the module as a dependency in your app's `build.gradle`:

```gradle
dependencies {
    implementation project(':mobile-module')
}
```

### Step 2: Update Your AndroidManifest.xml

Add the required permissions to your app's `AndroidManifest.xml`:

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

### Step 3: Initialize the Module in Your Activity

```kotlin
class YourActivity : AppCompatActivity() {
    
    private lateinit var mobileModule: IntelliAttendMobileModule
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Initialize the mobile module
        mobileModule = IntelliAttendMobileModule.create(this)
    }
}
```

### Step 4: Request Required Permissions

Before using any collectors, ensure you have requested the necessary permissions:

```kotlin
private fun checkAndRequestPermissions() {
    val permissions = mobileModule.checkPermissions()
    val permissionsToRequest = permissions.filter { !it.value }.map { it.key }.toTypedArray()
    
    if (permissionsToRequest.isNotEmpty()) {
        // Request permissions using ActivityResultContracts
    } else {
        // All permissions granted, proceed with data collection
    }
}
```

### Step 5: Use the Collectors

#### Environmental Data Collection

```kotlin
val collector = mobileModule.getEnvironmentalDataCollector()

collector.startCollecting(object : EnvironmentalDataCollector.EnvironmentalDataCallback {
    override fun onDataUpdated(data: EnvironmentalDataCollector.EnvironmentalData) {
        // Handle updated data
        data.wifiData?.let { wifi -> /* Process WiFi data */ }
        data.bluetoothDevices.forEach { device -> /* Process Bluetooth devices */ }
        data.gpsData?.let { gps -> /* Process GPS data */ }
    }
    
    override fun onError(error: Exception) {
        // Handle errors
    }
})
```

#### Direct Collector Access

```kotlin
// WiFi data
val wifiCollector = WiFiDataCollector(context)
lifecycleScope.launch {
    val wifiData = wifiCollector.getCurrentWiFiData()
    // Process WiFi data
}

// Bluetooth scanning
val bluetoothCollector = BluetoothDataCollector(context)
bluetoothCollector.startScanning { devices ->
    // Process Bluetooth devices
}

// GPS location
val gpsCollector = GPSDataCollector(context)
lifecycleScope.launch {
    val location = gpsCollector.getCurrentLocation()
    // Process GPS location
}
```

### Step 6: Use the Repository Pattern

```kotlin
val repository = mobileModule.getEnvironmentalDataRepository()

// Observe data changes
lifecycleScope.launch {
    repository.wifiData.collect { wifiData ->
        // Update UI with WiFi data
    }
}

// Refresh data
lifecycleScope.launch {
    repository.refreshWiFiData()
    repository.refreshGPSData()
}
```

## Best Practices

1. Always check permissions before starting data collection
2. Stop collectors when they're no longer needed to conserve battery
3. Handle errors gracefully
4. Use the repository pattern for reactive data updates
5. Follow Android lifecycle best practices

## Example Use Cases

### Faculty App Integration
- Verify faculty location in designated classroom
- Confirm faculty device presence via Bluetooth
- Monitor classroom WiFi network

### Student App Integration
- Collect environmental data for attendance verification
- Scan for registered devices during attendance
- Verify location accuracy for geofencing

### Admin Dashboard Integration
- Monitor device connectivity across campus
- Track Bluetooth beacon deployments
- Analyze WiFi coverage and performance