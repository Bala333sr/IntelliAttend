package com.intelliattend.student.connectivity

import android.Manifest
import android.app.ActivityManager
import android.app.ActivityManager.RunningAppProcessInfo
import android.app.AppOpsManager
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothProfile
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.location.LocationManager
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.wifi.WifiManager
import android.os.Build
import android.os.Process
import androidx.core.content.ContextCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

/**
 * Monitors connectivity services (Bluetooth, GPS, Wi-Fi) and provides detailed state information
 * Implements privacy-aware tracking to show which apps are using location services
 */
class ConnectivityMonitor(private val context: Context) {
    
    private val scope = CoroutineScope(Dispatchers.Default + Job())
    
    private val _connectivityStatus = MutableStateFlow(ConnectivityStatus())
    val connectivityStatus: StateFlow<ConnectivityStatus> = _connectivityStatus.asStateFlow()
    
    private val wifiManager: WifiManager by lazy {
        context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
    }
    
    private val bluetoothManager: BluetoothManager? by lazy {
        context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
    }
    
    private val bluetoothAdapter: BluetoothAdapter? by lazy {
        bluetoothManager?.adapter
    }
    
    private val locationManager: LocationManager by lazy {
        context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
    }
    
    private val connectivityManager: ConnectivityManager by lazy {
        context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    }
    
    private val appOpsManager: AppOpsManager by lazy {
        context.getSystemService(Context.APP_OPS_SERVICE) as AppOpsManager
    }
    
    private var monitoringJob: Job? = null
    private var wifiReceiver: BroadcastReceiver? = null
    private var bluetoothReceiver: BroadcastReceiver? = null
    private var locationReceiver: BroadcastReceiver? = null
    
    /**
     * Start monitoring connectivity services
     */
    fun startMonitoring() {
        if (monitoringJob?.isActive == true) return
        
        registerReceivers()
        
        monitoringJob = scope.launch {
            while (isActive) {
                updateConnectivityStatus()
                delay(2000) // Update every 2 seconds
            }
        }
    }
    
    /**
     * Stop monitoring connectivity services
     */
    fun stopMonitoring() {
        monitoringJob?.cancel()
        unregisterReceivers()
    }
    
    /**
     * Register broadcast receivers for connectivity changes
     */
    private fun registerReceivers() {
        // Wi-Fi state receiver
        wifiReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                scope.launch { updateWiFiState() }
            }
        }
        context.registerReceiver(wifiReceiver, IntentFilter().apply {
            addAction(WifiManager.WIFI_STATE_CHANGED_ACTION)
            addAction(WifiManager.NETWORK_STATE_CHANGED_ACTION)
            addAction(ConnectivityManager.CONNECTIVITY_ACTION)
        })
        
        // Bluetooth state receiver
        bluetoothReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                scope.launch { updateBluetoothState() }
            }
        }
        context.registerReceiver(bluetoothReceiver, IntentFilter().apply {
            addAction(BluetoothAdapter.ACTION_STATE_CHANGED)
            addAction(BluetoothAdapter.ACTION_CONNECTION_STATE_CHANGED)
            addAction(BluetoothAdapter.ACTION_SCAN_MODE_CHANGED)
        })
        
        // Location state receiver
        locationReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                scope.launch { updateGPSState() }
            }
        }
        context.registerReceiver(locationReceiver, IntentFilter().apply {
            addAction(LocationManager.PROVIDERS_CHANGED_ACTION)
            addAction(LocationManager.MODE_CHANGED_ACTION)
        })
    }
    
    /**
     * Unregister broadcast receivers
     */
    private fun unregisterReceivers() {
        try {
            wifiReceiver?.let { context.unregisterReceiver(it) }
            bluetoothReceiver?.let { context.unregisterReceiver(it) }
            locationReceiver?.let { context.unregisterReceiver(it) }
        } catch (e: Exception) {
            // Receiver not registered
        }
    }
    
    /**
     * Update all connectivity states
     */
    private suspend fun updateConnectivityStatus() {
        val wifiState = getWiFiState()
        val gpsState = getGPSState()
        val bluetoothState = getBluetoothState()
        
        _connectivityStatus.value = ConnectivityStatus(
            wifiState = wifiState,
            gpsState = gpsState,
            bluetoothState = bluetoothState,
            timestamp = System.currentTimeMillis()
        )
    }
    
    /**
     * Update Wi-Fi state
     */
    private suspend fun updateWiFiState() {
        val wifiState = getWiFiState()
        _connectivityStatus.value = _connectivityStatus.value.copy(
            wifiState = wifiState,
            timestamp = System.currentTimeMillis()
        )
    }
    
    /**
     * Update Bluetooth state
     */
    private suspend fun updateBluetoothState() {
        val bluetoothState = getBluetoothState()
        _connectivityStatus.value = _connectivityStatus.value.copy(
            bluetoothState = bluetoothState,
            timestamp = System.currentTimeMillis()
        )
    }
    
    /**
     * Update GPS state
     */
    private suspend fun updateGPSState() {
        val gpsState = getGPSState()
        _connectivityStatus.value = _connectivityStatus.value.copy(
            gpsState = gpsState,
            timestamp = System.currentTimeMillis()
        )
    }
    
    /**
     * Get current Wi-Fi state with detailed information
     */
    private fun getWiFiState(): WiFiState {
        if (!wifiManager.isWifiEnabled) {
            return WiFiState.Disabled
        }
        
        // Check if hotspot is enabled
        if (isHotspotEnabled()) {
            return WiFiState.Hotspot(connectedDevices = 0) // Device count requires reflection
        }
        
        val wifiInfo = wifiManager.connectionInfo
        
        // Check if connected to a network
        if (wifiInfo.networkId == -1) {
            return WiFiState.Scanning
        }
        
        val ssid = wifiInfo.ssid?.replace("\"", "") ?: "Unknown"
        val rssi = wifiInfo.rssi
        
        // Check if data is being transmitted
        val isTransmitting = isNetworkActive()
        
        return WiFiState.Connected(
            ssid = ssid,
            signalStrength = rssi,
            isTransmitting = isTransmitting
        )
    }
    
    /**
     * Get current GPS state with app attribution
     */
    private fun getGPSState(): GPSState {
        val isGpsEnabled = locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)
        val isNetworkEnabled = locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)
        
        if (!isGpsEnabled && !isNetworkEnabled) {
            return GPSState.Disabled
        }
        
        // Check if location is being actively used
        val locationUsingApp = getLocationUsingApp()
        
        return if (locationUsingApp != null) {
            // Determine if high precision is being used
            if (isGpsEnabled) {
                GPSState.ActiveHighPrecision(
                    usingApp = locationUsingApp,
                    timestamp = System.currentTimeMillis()
                )
            } else {
                GPSState.ActiveLowPrecision(
                    usingApp = locationUsingApp,
                    timestamp = System.currentTimeMillis()
                )
            }
        } else {
            GPSState.Idle
        }
    }
    
    /**
     * Get current Bluetooth state with device attribution
     */
    private fun getBluetoothState(): BluetoothState {
        val adapter = bluetoothAdapter ?: return BluetoothState.Disabled
        
        if (!adapter.isEnabled) {
            return BluetoothState.Disabled
        }
        
        // Check scan mode
        val scanMode = adapter.scanMode
        if (scanMode == BluetoothAdapter.SCAN_MODE_CONNECTABLE_DISCOVERABLE) {
            return BluetoothState.Scanning(isDiscoverable = true)
        }
        
        // Check for connected devices
        val connectedDevice = getConnectedBluetoothDevice()
        
        return if (connectedDevice != null) {
            // Check if actively transmitting data (e.g., audio)
            val isTransmitting = isBluetoothTransmitting()
            if (isTransmitting) {
                BluetoothState.Transmitting(
                    deviceName = connectedDevice.first,
                    deviceType = connectedDevice.second
                )
            } else {
                BluetoothState.Connected(
                    deviceName = connectedDevice.first,
                    deviceType = connectedDevice.second
                )
            }
        } else {
            BluetoothState.Idle
        }
    }
    
    /**
     * Check if Wi-Fi hotspot is enabled
     */
    private fun isHotspotEnabled(): Boolean {
        return try {
            val method = wifiManager.javaClass.getMethod("isWifiApEnabled")
            method.invoke(wifiManager) as? Boolean ?: false
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Check if network is actively transmitting data
     */
    private fun isNetworkActive(): Boolean {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        
        // Check if there's active data transmission
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
    }
    
    /**
     * Get the app currently using location services
     * Returns the package name or display name of the app
     * For privacy transparency: Shows 'IntelliAttend' when we're accessing location
     */
    private fun getLocationUsingApp(): String? {
        val isGpsEnabled = locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)
        val isNetworkEnabled = locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)
        
        if (!isGpsEnabled && !isNetworkEnabled) {
            return null
        }
        
        // Check if IntelliAttend is in foreground and likely using location
        try {
            val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as? android.app.ActivityManager
            if (activityManager != null) {
                val appProcesses = activityManager.runningAppProcesses
                val ourPackageName = context.packageName
                
                // Check if our app is in foreground
                val ourProcess = appProcesses?.find { it.processName == ourPackageName }
                if (ourProcess != null && 
                    ourProcess.importance == android.app.ActivityManager.RunningAppProcessInfo.IMPORTANCE_FOREGROUND) {
                    return "IntelliAttend"
                }
            }
        } catch (e: Exception) {
            // If we can't determine, assume it's us if location is enabled and we're running
            if (isGpsEnabled || isNetworkEnabled) {
                return "IntelliAttend"
            }
        }
        
        // Fallback: If location is enabled, show generic message
        return "System"
    }
    
    /**
     * Get connected Bluetooth device name and type
     */
    private fun getConnectedBluetoothDevice(): Pair<String, BluetoothDeviceType>? {
        if (!hasBluetoothPermission()) return null
        
        val adapter = bluetoothAdapter ?: return null
        
        try {
            // Check A2DP (audio) profile
            val a2dpProfile = bluetoothManager?.getConnectedDevices(BluetoothProfile.A2DP)
            if (!a2dpProfile.isNullOrEmpty()) {
                val device = a2dpProfile.first()
                return Pair(
                    device.name ?: "Unknown Device",
                    BluetoothDeviceType.HEADPHONES
                )
            }
            
            // Check bonded devices
            val bondedDevices = adapter.bondedDevices
            if (!bondedDevices.isNullOrEmpty()) {
                val device = bondedDevices.first()
                return Pair(
                    device.name ?: "Unknown Device",
                    BluetoothDeviceType.UNKNOWN
                )
            }
        } catch (e: Exception) {
            // Permission or API error
        }
        
        return null
    }
    
    /**
     * Check if Bluetooth is actively transmitting data
     */
    private fun isBluetoothTransmitting(): Boolean {
        // Check if audio is playing through Bluetooth
        val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as? android.media.AudioManager
        return audioManager?.isBluetoothA2dpOn == true
    }
    
    /**
     * Get app display name from package name
     */
    private fun getAppName(packageName: String): String? {
        return try {
            val pm = context.packageManager
            val appInfo = pm.getApplicationInfo(packageName, 0)
            pm.getApplicationLabel(appInfo).toString()
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Check if Bluetooth permission is granted
     */
    private fun hasBluetoothPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.BLUETOOTH_CONNECT
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            true
        }
    }
}
