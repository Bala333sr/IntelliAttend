package com.intelliattend.student.ui.testing

import android.Manifest
import android.app.Application
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.content.Context
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.location.LocationManager
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build
import androidx.core.content.ContextCompat
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.intelliattend.student.bt.BluetoothManager as CustomBluetoothManager
import com.intelliattend.student.data.collector.GPSDataCollector
import com.intelliattend.student.data.collector.WiFiDataCollector
import com.intelliattend.student.data.model.BluetoothData
import com.intelliattend.student.data.model.GPSData
import com.intelliattend.student.data.model.WiFiData
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.Dispatchers

enum class ServiceStatus {
    UNKNOWN, WORKING, ERROR, TESTING
}

data class TestingUiState(
    val bluetoothStatus: ServiceStatus = ServiceStatus.UNKNOWN,
    val gpsStatus: ServiceStatus = ServiceStatus.UNKNOWN,
    val wifiStatus: ServiceStatus = ServiceStatus.UNKNOWN,
    val proximityStrength: Float = 0f,
    val geofenceStatus: ServiceStatus = ServiceStatus.UNKNOWN,
    val biometricStatus: ServiceStatus = ServiceStatus.UNKNOWN,
    val isInGeofence: Boolean = false,
    val distanceFromCenter: Int = 0,
    // Detailed data
    val gpsData: GPSData? = null,
    val gpsError: String? = null,
    val wifiData: WiFiData? = null,
    val wifiError: String? = null,
    val bluetoothDevices: List<BluetoothData> = emptyList(),
    val bluetoothError: String? = null,
    val isLoadingBluetooth: Boolean = false,
    // Server configuration
    val serverUrl: String = "",
    val serverConnectionStatus: ServiceStatus = ServiceStatus.UNKNOWN,
    val serverError: String? = null,
    val serverSaveSuccess: Boolean = false
)

class TestingViewModel(application: Application) : AndroidViewModel(application) {
    private val _uiState = MutableStateFlow(TestingUiState())
    val uiState: StateFlow<TestingUiState> = _uiState.asStateFlow()
    
    private val context: Context
        get() = getApplication<Application>().applicationContext
    
    // Real data collectors (same as used in attendance)
    private val gpsCollector = GPSDataCollector(context)
    private val wifiCollector = WiFiDataCollector(context)
    private val bluetoothManager = CustomBluetoothManager(context)
    private val sharedPreferences: SharedPreferences = context.getSharedPreferences("registered_devices", Context.MODE_PRIVATE)
    private val appPreferences: SharedPreferences = context.getSharedPreferences("app_preferences", Context.MODE_PRIVATE)
    private val gson = Gson()
    
    init {
        loadRegisteredDevices()
        loadServerUrl()
    }
    
    fun loadRegisteredDevices() {
        val existingDevicesJson = sharedPreferences.getString("registered_bluetooth_devices", null)
        val type = object : TypeToken<MutableList<BluetoothData>>() {}.type
        val registeredDevices: MutableList<BluetoothData> = existingDevicesJson?.let {
            gson.fromJson(it, type)
        } ?: mutableListOf()
        android.util.Log.d("TestingViewModel", "Loaded ${registeredDevices.size} registered devices")
        _uiState.value = _uiState.value.copy(bluetoothDevices = registeredDevices)
    }
    
    fun checkAllServices() {
        testBluetooth()
        testGPS()
        testWifi()
        testProximity()
        testGeofence()
        testBiometric()
    }
    
    fun testBluetooth() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                bluetoothStatus = ServiceStatus.TESTING,
                isLoadingBluetooth = true,
                bluetoothError = null
            )
            
            try {
                android.util.Log.d("TestingViewModel", "=== Starting Bluetooth Test ===")
                
                // Check if Bluetooth permissions are granted
                if (!hasBluetoothPermissions()) {
                    android.util.Log.e("TestingViewModel", "Bluetooth permissions not granted")
                    _uiState.value = _uiState.value.copy(
                        bluetoothStatus = ServiceStatus.ERROR,
                        isLoadingBluetooth = false,
                        bluetoothError = "Bluetooth permissions not granted"
                    )
                    return@launch
                }
                
                // Check if Bluetooth is enabled
                if (!bluetoothManager.isBluetoothEnabled.value) {
                    android.util.Log.e("TestingViewModel", "Bluetooth is disabled")
                    _uiState.value = _uiState.value.copy(
                        bluetoothStatus = ServiceStatus.ERROR,
                        isLoadingBluetooth = false,
                        bluetoothError = "Bluetooth is disabled"
                    )
                    return@launch
                }
                
                // Log registered devices
                val registeredDevices = _uiState.value.bluetoothDevices
                android.util.Log.d("TestingViewModel", "Registered devices count: ${registeredDevices.size}")
                registeredDevices.forEach { device ->
                    android.util.Log.d("TestingViewModel", "  - ${device.name} (${device.address})")
                }
                
                if (registeredDevices.isEmpty()) {
                    android.util.Log.w("TestingViewModel", "No registered devices to scan for")
                    _uiState.value = _uiState.value.copy(
                        bluetoothStatus = ServiceStatus.ERROR,
                        isLoadingBluetooth = false,
                        bluetoothError = "No devices registered. Please register devices first."
                    )
                    return@launch
                }
                
                // Clear previous scan results and reset devices
                bluetoothManager.stopBleScan()
                bluetoothManager.stopClassicDiscovery()
                bluetoothManager.clearScanResults()
                
                val resetDevices = registeredDevices.map { it.copy(rssi = 0) }
                _uiState.value = _uiState.value.copy(bluetoothDevices = resetDevices)
                
                android.util.Log.d("TestingViewModel", "Starting BLE scan for 700ms...")
                // Start BLE scan (same as in attendance verification)
                bluetoothManager.startBleScan()
                delay(700) // BLE scan for 700ms
                
                // Log scan results after BLE
                val bleScanResults = bluetoothManager.scanResults.value
                android.util.Log.d("TestingViewModel", "BLE scan found ${bleScanResults.size} devices")
                bleScanResults.forEach { (address, deviceEntry) ->
                    android.util.Log.d("TestingViewModel", "  BLE: ${deviceEntry.device.name ?: "Unknown"} ($address) RSSI: ${deviceEntry.rssi}")
                }
                
                // Check if registered devices were found
                val registeredDevicesFound = bleScanResults.values.any { scanResult ->
                    registeredDevices.any { registeredDevice ->
                        val match = registeredDevice.address.equals(scanResult.device.address, ignoreCase = true)
                        if (match) {
                            android.util.Log.d("TestingViewModel", "Found registered device via BLE: ${registeredDevice.name} (${registeredDevice.address})")
                        }
                        match
                    }
                }
                
                android.util.Log.d("TestingViewModel", "Registered devices found via BLE: $registeredDevicesFound")
                
                // If no registered devices found, run Classic Bluetooth
                if (!registeredDevicesFound) {
                    android.util.Log.d("TestingViewModel", "Starting Classic Bluetooth discovery for 12 seconds...")
                    bluetoothManager.stopBleScan()
                    bluetoothManager.startClassicDiscovery()
                    delay(12000) // Classic discovery for 12 seconds
                    
                    val classicScanResults = bluetoothManager.scanResults.value
                    android.util.Log.d("TestingViewModel", "Classic scan found ${classicScanResults.size} devices")
                    classicScanResults.forEach { (address, deviceEntry) ->
                        android.util.Log.d("TestingViewModel", "  Classic: ${deviceEntry.device.name ?: deviceEntry.name ?: "Unknown"} ($address) RSSI: ${deviceEntry.rssi}")
                    }
                }
                
                // Stop scanning
                bluetoothManager.stopBleScan()
                bluetoothManager.stopClassicDiscovery()
                
                // Update RSSI values for registered devices
                val finalResults = bluetoothManager.scanResults.value
                android.util.Log.d("TestingViewModel", "Final scan results: ${finalResults.size} devices")
                
                val updatedDevices = registeredDevices.map { device ->
                    // Match by address (case-insensitive)
                    val scanResult = finalResults.values.find { 
                        it.device.address.equals(device.address, ignoreCase = true)
                    }
                    
                    if (scanResult != null) {
                        android.util.Log.d("TestingViewModel", "MATCH: ${device.name} (${device.address}) -> RSSI: ${scanResult.rssi}")
                        device.copy(rssi = scanResult.rssi) // Found with RSSI
                    } else {
                        android.util.Log.d("TestingViewModel", "NOT FOUND: ${device.name} (${device.address})")
                        device.copy(rssi = 0) // Not detected
                    }
                }
                
                val devicesInRange = updatedDevices.filter { it.rssi != 0 }
                android.util.Log.d("TestingViewModel", "Devices in range: ${devicesInRange.size} / ${updatedDevices.size}")
                
                val status = if (devicesInRange.isNotEmpty()) {
                    ServiceStatus.WORKING
                } else {
                    ServiceStatus.ERROR
                }
                
                _uiState.value = _uiState.value.copy(
                    bluetoothStatus = status,
                    bluetoothDevices = updatedDevices,
                    isLoadingBluetooth = false,
                    bluetoothError = if (status == ServiceStatus.ERROR) "No registered devices found in range" else null
                )
                
                android.util.Log.d("TestingViewModel", "=== Bluetooth Test Complete ===")
                
            } catch (e: Exception) {
                android.util.Log.e("TestingViewModel", "Bluetooth test error", e)
                bluetoothManager.stopBleScan()
                bluetoothManager.stopClassicDiscovery()
                _uiState.value = _uiState.value.copy(
                    bluetoothStatus = ServiceStatus.ERROR,
                    isLoadingBluetooth = false,
                    bluetoothError = e.message ?: "Bluetooth scan failed"
                )
            }
        }
    }
    
    fun testGPS() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                gpsStatus = ServiceStatus.TESTING,
                gpsError = null
            )
            
            try {
                // Try current location first (same as used in attendance)
                val currentLocationResult = gpsCollector.getCurrentLocation()
                
                if (currentLocationResult.isSuccess) {
                    _uiState.value = _uiState.value.copy(
                        gpsStatus = ServiceStatus.WORKING,
                        gpsData = currentLocationResult.getOrThrow(),
                        gpsError = null
                    )
                } else {
                    // Fallback to last known location
                    val lastLocationResult = gpsCollector.getLastKnownLocation()
                    
                    if (lastLocationResult.isSuccess) {
                        _uiState.value = _uiState.value.copy(
                            gpsStatus = ServiceStatus.WORKING,
                            gpsData = lastLocationResult.getOrThrow(),
                            gpsError = "Using last known location"
                        )
                    } else {
                        _uiState.value = _uiState.value.copy(
                            gpsStatus = ServiceStatus.ERROR,
                            gpsData = null,
                            gpsError = currentLocationResult.exceptionOrNull()?.message ?: "GPS unavailable"
                        )
                    }
                }
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    gpsStatus = ServiceStatus.ERROR,
                    gpsData = null,
                    gpsError = e.message ?: "GPS error"
                )
            }
        }
    }
    
    fun testWifi() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                wifiStatus = ServiceStatus.TESTING,
                wifiError = null
            )
            
            try {
                // Get WiFi data (same as used in attendance)
                val wifiResult = wifiCollector.getCurrentWiFiData()
                
                if (wifiResult.isSuccess) {
                    _uiState.value = _uiState.value.copy(
                        wifiStatus = ServiceStatus.WORKING,
                        wifiData = wifiResult.getOrThrow(),
                        wifiError = null
                    )
                } else {
                    _uiState.value = _uiState.value.copy(
                        wifiStatus = ServiceStatus.ERROR,
                        wifiData = null,
                        wifiError = wifiResult.exceptionOrNull()?.message ?: "WiFi unavailable"
                    )
                }
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    wifiStatus = ServiceStatus.ERROR,
                    wifiData = null,
                    wifiError = e.message ?: "WiFi error"
                )
            }
        }
    }
    
    fun testProximity() {
        viewModelScope.launch {
            // Simulate testing proximity sensor
            _uiState.value = _uiState.value.copy(proximityStrength = 0f)
            
            delay(500)
            _uiState.value = _uiState.value.copy(proximityStrength = 0.2f)
            
            delay(500)
            _uiState.value = _uiState.value.copy(proximityStrength = 0.5f)
            
            delay(500)
            _uiState.value = _uiState.value.copy(proximityStrength = 0.85f)
        }
    }
    
    fun testGeofence() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(geofenceStatus = ServiceStatus.TESTING)
            
            delay(1500) // Simulate geofence testing
            
            // In a real app, this would check if geofencing is available and working
            _uiState.value = _uiState.value.copy(geofenceStatus = ServiceStatus.WORKING)
        }
    }
    
    fun testBiometric() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(biometricStatus = ServiceStatus.TESTING)
            
            delay(1500) // Simulate biometric testing
            
            // In a real app, this would check if biometric authentication is available
            _uiState.value = _uiState.value.copy(
                biometricStatus = ServiceStatus.WORKING,
                isInGeofence = true,
                distanceFromCenter = 15
            )
        }
    }
    
    /**
     * Check if Bluetooth permissions are granted
     */
    private fun hasBluetoothPermissions(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.BLUETOOTH_SCAN
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.BLUETOOTH_ADMIN
            ) == PackageManager.PERMISSION_GRANTED
        }
    }
    
    // ========== Server Configuration Functions ==========
    
    /**
     * Load saved server URL from preferences
     */
    private fun loadServerUrl() {
        val savedUrl = appPreferences.getString("base_url", "") ?: ""
        _uiState.value = _uiState.value.copy(serverUrl = savedUrl)
        android.util.Log.d("TestingViewModel", "Loaded server URL: $savedUrl")
    }
    
    /**
     * Test connection to the server
     */
    fun testServerConnection(url: String) {
        if (url.isBlank()) {
            _uiState.value = _uiState.value.copy(
                serverConnectionStatus = ServiceStatus.ERROR,
                serverError = "Please enter a server URL",
                serverSaveSuccess = false
            )
            return
        }
        
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                serverConnectionStatus = ServiceStatus.TESTING,
                serverError = null,
                serverSaveSuccess = false
            )
            
            try {
                android.util.Log.d("TestingViewModel", "Testing connection to: $url")
                
                // Validate URL format
                if (!url.startsWith("http://") && !url.startsWith("https://")) {
                    throw Exception("URL must start with http:// or https://")
                }
                
                // Ensure URL ends with /api/ or /
                val testUrl = when {
                    url.endsWith("/api/") -> url + "discover"
                    url.endsWith("/") -> url + "api/discover"
                    else -> "$url/api/discover"
                }
                
                android.util.Log.d("TestingViewModel", "Testing endpoint: $testUrl")
                
                // Test connection using OkHttp
                val client = okhttp3.OkHttpClient.Builder()
                    .connectTimeout(5, java.util.concurrent.TimeUnit.SECONDS)
                    .readTimeout(5, java.util.concurrent.TimeUnit.SECONDS)
                    .build()
                
                val request = okhttp3.Request.Builder()
                    .url(testUrl)
                    .get()
                    .build()
                
                withContext(kotlinx.coroutines.Dispatchers.IO) {
                    val response = client.newCall(request).execute()
                    response.use {
                        if (it.isSuccessful) {
                            android.util.Log.d("TestingViewModel", "Server connection successful! Code: ${it.code}")
                            _uiState.value = _uiState.value.copy(
                                serverConnectionStatus = ServiceStatus.WORKING,
                                serverError = null
                            )
                        } else {
                            throw Exception("Server returned error code: ${it.code}")
                        }
                    }
                }
                
            } catch (e: java.net.UnknownHostException) {
                android.util.Log.e("TestingViewModel", "Cannot reach server", e)
                _uiState.value = _uiState.value.copy(
                    serverConnectionStatus = ServiceStatus.ERROR,
                    serverError = "Cannot reach server. Check IP address and network connection."
                )
            } catch (e: java.net.SocketTimeoutException) {
                android.util.Log.e("TestingViewModel", "Connection timeout", e)
                _uiState.value = _uiState.value.copy(
                    serverConnectionStatus = ServiceStatus.ERROR,
                    serverError = "Connection timeout. Make sure server is running and reachable."
                )
            } catch (e: java.net.ConnectException) {
                android.util.Log.e("TestingViewModel", "Connection refused", e)
                _uiState.value = _uiState.value.copy(
                    serverConnectionStatus = ServiceStatus.ERROR,
                    serverError = "Connection refused. Verify server is running on this IP:PORT."
                )
            } catch (e: Exception) {
                android.util.Log.e("TestingViewModel", "Server connection failed", e)
                _uiState.value = _uiState.value.copy(
                    serverConnectionStatus = ServiceStatus.ERROR,
                    serverError = e.message ?: "Connection failed"
                )
            }
        }
    }
    
    /**
     * Save server URL to preferences
     */
    fun saveServerUrl(url: String) {
        if (url.isBlank()) {
            _uiState.value = _uiState.value.copy(
                serverError = "Please enter a server URL",
                serverSaveSuccess = false
            )
            return
        }
        
        viewModelScope.launch {
            try {
                // Ensure URL has proper format
                var formattedUrl = url.trim()
                
                // Remove trailing slash if present
                if (formattedUrl.endsWith("/")) {
                    formattedUrl = formattedUrl.dropLast(1)
                }
                
                // Add /api/ if not already present
                if (!formattedUrl.endsWith("/api")) {
                    formattedUrl += "/api"
                }
                
                // Add trailing slash
                formattedUrl += "/"
                
                // Save to preferences
                appPreferences.edit().putString("base_url", formattedUrl).apply()
                
                android.util.Log.d("TestingViewModel", "Server URL saved: $formattedUrl")
                
                // Recreate ApiClient to use new URL
                try {
                    com.intelliattend.student.network.ApiClient.recreateInstance(context)
                    android.util.Log.d("TestingViewModel", "ApiClient recreated with new URL")
                } catch (e: Exception) {
                    android.util.Log.e("TestingViewModel", "Failed to recreate ApiClient", e)
                }
                
                _uiState.value = _uiState.value.copy(
                    serverUrl = formattedUrl,
                    serverSaveSuccess = true,
                    serverError = null
                )
                
                // Hide success message after 3 seconds
                delay(3000)
                _uiState.value = _uiState.value.copy(serverSaveSuccess = false)
                
            } catch (e: Exception) {
                android.util.Log.e("TestingViewModel", "Failed to save server URL", e)
                _uiState.value = _uiState.value.copy(
                    serverError = "Failed to save: ${e.message}",
                    serverSaveSuccess = false
                )
            }
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        bluetoothManager.cleanup()
    }
}
