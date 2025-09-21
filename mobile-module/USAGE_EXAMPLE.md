# Example: Creating a New App Using IntelliAttend Mobile Module

This example shows how to create a new Android application that uses the IntelliAttend Mobile Module.

## Step 1: Create a New Android Project

Create a new Android project in Android Studio with Kotlin support.

## Step 2: Add the Module

1. Copy the `mobile-module` directory to your new project root
2. Add the following to your `settings.gradle`:

```gradle
include ':mobile-module'
```

3. Add the dependency to your app's `build.gradle`:

```gradle
dependencies {
    implementation project(':mobile-module')
}
```

## Step 3: Implement in Your MainActivity

```kotlin
class MainActivity : AppCompatActivity() {
    
    private lateinit var mobileModule: IntelliAttendMobileModule
    private lateinit var environmentalDataCollector: EnvironmentalDataCollector
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Initialize the mobile module
        mobileModule = IntelliAttendMobileModule.create(this)
        environmentalDataCollector = mobileModule.getEnvironmentalDataCollector()
        
        // Start collecting environmental data
        startEnvironmentalDataCollection()
    }
    
    private fun startEnvironmentalDataCollection() {
        environmentalDataCollector.startCollecting(object : EnvironmentalDataCollector.EnvironmentalDataCallback {
            override fun onDataUpdated(data: EnvironmentalDataCollector.EnvironmentalData) {
                runOnUiThread {
                    // Update UI with collected data
                    updateUI(data)
                }
            }
            
            override fun onError(error: Exception) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Error: ${error.message}", Toast.LENGTH_SHORT).show()
                }
            }
        })
    }
    
    private fun updateUI(data: EnvironmentalDataCollector.EnvironmentalData) {
        // Example UI updates
        data.wifiData?.let { wifi ->
            // Update WiFi information display
        }
        
        // Update Bluetooth devices list
        // bluetoothAdapter.updateDevices(data.bluetoothDevices)
        
        data.gpsData?.let { gps ->
            // Update GPS information display
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // Stop data collection to free resources
        environmentalDataCollector.stopCollecting()
    }
}
```

## Step 4: Add Required Permissions

Add these permissions to your `AndroidManifest.xml`:

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

## Step 5: Request Permissions at Runtime

Implement proper permission handling:

```kotlin
private fun checkAndRequestPermissions() {
    val permissions = mobileModule.checkPermissions()
    val permissionsToRequest = permissions.filter { !it.value }.map { it.key }.toTypedArray()
    
    if (permissionsToRequest.isNotEmpty()) {
        // Request missing permissions
        permissionLauncher.launch(permissionsToRequest)
    } else {
        // All permissions granted
        startEnvironmentalDataCollection()
    }
}
```

This example demonstrates how easy it is to integrate the IntelliAttend Mobile Module into any new Android application for environmental data collection.