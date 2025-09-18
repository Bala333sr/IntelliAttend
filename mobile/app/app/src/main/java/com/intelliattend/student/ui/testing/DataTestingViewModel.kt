package com.intelliattend.student.ui.testing

import android.Manifest
import android.content.Context
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.bt.BluetoothManager
import com.intelliattend.student.data.collector.GPSDataCollector
import com.intelliattend.student.data.collector.WiFiDataCollector
import com.intelliattend.student.data.model.BluetoothData
import com.intelliattend.student.data.model.GPSData
import com.intelliattend.student.data.model.WiFiData
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

/**
 * ViewModel for data testing screen
 */
class DataTestingViewModel : ViewModel() {
    
    private val context = IntelliAttendApplication.getContext()
    private val gpsCollector = GPSDataCollector(context)
    private val wifiCollector = WiFiDataCollector(context)
    private val bluetoothManager = BluetoothManager(context)
    private val sharedPreferences: SharedPreferences = context.getSharedPreferences("registered_devices", Context.MODE_PRIVATE)
    private val gson = Gson()
    
    private val _uiState = MutableStateFlow(DataTestingUiState())
    val uiState: StateFlow<DataTestingUiState> = _uiState.asStateFlow()
    
    private var dataCollectionJob: Job? = null
    
    init {
        loadRegisteredDevices()
        // Removed the race condition causing init block
        // RSSI updates will now happen only after scan completion in refreshBluetoothData()
    }
    
    private fun loadRegisteredDevices() {
        val existingDevicesJson = sharedPreferences.getString("registered_bluetooth_devices", null)
        val type = object : TypeToken<MutableList<BluetoothData>>() {}.type
        val registeredDevices: MutableList<BluetoothData> = existingDevicesJson?.let {
            gson.fromJson(it, type)
        } ?: mutableListOf()
        _uiState.value = _uiState.value.copy(registeredBluetoothDevices = registeredDevices)
    }
    
    /**
     * Start initial data collection (GPS and WiFi only)
     * Bluetooth scanning is now user-triggered only
     */
    fun startDataCollection() {
        // Load initial GPS and WiFi data once on screen open
        refreshGPSData()
        refreshWiFiData()
        
        // Start continuous GPS and WiFi updates (not Bluetooth)
        dataCollectionJob?.cancel()
        dataCollectionJob = viewModelScope.launch {
            while (true) {
                delay(15000) // Wait 15 seconds
                // Only refresh GPS and WiFi automatically
                refreshGPSData()
                refreshWiFiData()
                // Bluetooth is now user-triggered only via refresh button
            }
        }
    }
    
    /**
     * Stop data collection
     */
    fun stopDataCollection() {
        dataCollectionJob?.cancel()
        bluetoothManager.stopBleScan()
        bluetoothManager.stopClassicDiscovery()
    }
    
    /**
     * Refresh all data sources (called by main refresh button)
     */
    fun refreshAllData() {
        refreshGPSData()
        refreshWiFiData()
        refreshBluetoothData() // Only scan Bluetooth when user requests it
    }
    
    /**
     * Refresh GPS data
     */
    fun refreshGPSData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoadingGPS = true, gpsError = null)
            
            try {
                // Try current location first
                val currentLocationResult = gpsCollector.getCurrentLocation()
                
                if (currentLocationResult.isSuccess) {
                    _uiState.value = _uiState.value.copy(
                        gpsData = currentLocationResult.getOrThrow(),
                        isLoadingGPS = false,
                        gpsError = null
                    )
                } else {
                    // Fallback to last known location
                    val lastLocationResult = gpsCollector.getLastKnownLocation()
                    
                    if (lastLocationResult.isSuccess) {
                        _uiState.value = _uiState.value.copy(
                            gpsData = lastLocationResult.getOrThrow(),
                            isLoadingGPS = false,
                            gpsError = "Using last known location"
                        )
                    } else {
                        _uiState.value = _uiState.value.copy(
                            gpsData = null,
                            isLoadingGPS = false,
                            gpsError = currentLocationResult.exceptionOrNull()?.message ?: "GPS unavailable"
                        )
                    }
                }
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    gpsData = null,
                    isLoadingGPS = false,
                    gpsError = e.message ?: "GPS error"
                )
            }
        }
    }
    
    /**
     * Refresh WiFi data
     */
    fun refreshWiFiData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoadingWiFi = true, wifiError = null)
            
            try {
                val wifiResult = wifiCollector.getCurrentWiFiData()
                
                if (wifiResult.isSuccess) {
                    _uiState.value = _uiState.value.copy(
                        wifiData = wifiResult.getOrThrow(),
                        isLoadingWiFi = false,
                        wifiError = null
                    )
                } else {
                    _uiState.value = _uiState.value.copy(
                        wifiData = null,
                        isLoadingWiFi = false,
                        wifiError = wifiResult.exceptionOrNull()?.message ?: "WiFi unavailable"
                    )
                }
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    wifiData = null,
                    isLoadingWiFi = false,
                    wifiError = e.message ?: "WiFi error"
                )
            }
        }
    }
    
    /**
     * Refresh Bluetooth data (USER-TRIGGERED ONLY)
     * Performs complete fresh scan identical to initial scan
     * Called only when user taps refresh button - no automatic scanning
     */
    fun refreshBluetoothData() {
        viewModelScope.launch {
            // Check if Bluetooth permissions are granted
            if (!hasBluetoothPermissions()) {
                _uiState.value = _uiState.value.copy(
                    isLoadingBluetooth = false,
                    bluetoothError = "Bluetooth permissions not granted. Please enable Bluetooth permissions in settings."
                )
                return@launch
            }
            
            // Check if Bluetooth is enabled
            if (!bluetoothManager.isBluetoothEnabled.value) {
                _uiState.value = _uiState.value.copy(
                    isLoadingBluetooth = false,
                    bluetoothError = "Bluetooth is disabled. Please enable Bluetooth on your device."
                )
                return@launch
            }
            
            // FORCE CLEAR: Stop any existing scans and clear all cached results
            bluetoothManager.stopBleScan()
            bluetoothManager.stopClassicDiscovery()
            bluetoothManager.clearScanResults()
            
            // Set loading state immediately
            _uiState.value = _uiState.value.copy(isLoadingBluetooth = true, bluetoothError = null)
            
            try {
                // Log the number of registered devices
                val registeredDeviceCount = _uiState.value.registeredBluetoothDevices.size
                println("Bluetooth Refresh: Starting FRESH scan for $registeredDeviceCount registered devices")
                
                // RESET: Set all devices to "not detected" state (RSSI = 0)
                val resetDevices = _uiState.value.registeredBluetoothDevices.map { 
                    it.copy(rssi = 0) 
                }
                _uiState.value = _uiState.value.copy(registeredBluetoothDevices = resetDevices)
                
                // IDENTICAL TIMING: Start BLE scan exactly like initial scan
                bluetoothManager.startBleScan()
                
                // IDENTICAL TIMING: Wait 700ms for BLE scan results (same as initial scan)
                delay(700)
                
                // Check if any registered devices were found during BLE scan
                val registeredDevicesFound = bluetoothManager.scanResults.value.values.any { scanResult ->
                    _uiState.value.registeredBluetoothDevices.any { registeredDevice ->
                        registeredDevice.address == scanResult.device.address
                    }
                }
                
                println("Bluetooth Refresh: BLE scan complete. Registered devices found: $registeredDevicesFound")
                
                // IDENTICAL TIMING: If no registered devices found, run Classic Bluetooth for 12 seconds
                if (!registeredDevicesFound) {
                    println("Bluetooth Refresh: No registered devices found in BLE scan, starting 12-second Classic discovery")
                    bluetoothManager.stopBleScan()
                    bluetoothManager.startClassicDiscovery()
                    delay(12000) // IDENTICAL TIMING: Classic discovery for full 12 seconds
                }
                
                // Stop scanning
                bluetoothManager.stopBleScan()
                bluetoothManager.stopClassicDiscovery()
                
                // Log final scan results
                val finalResultCount = bluetoothManager.scanResults.value.size
                println("Bluetooth Refresh: COMPLETE scan finished. Total devices found: $finalResultCount")
                
                // WAIT FOR COMPLETION: Update RSSI values only after full scan completion
                val finalResults = bluetoothManager.scanResults.value
                val updatedDevices = _uiState.value.registeredBluetoothDevices.map { device ->
                    val scanResult = finalResults.values.find { it.device.address == device.address }
                    if (scanResult != null) {
                        println("Bluetooth Refresh: Device ${device.name} (${device.address}) found with RSSI: ${scanResult.rssi}")
                        device.copy(rssi = scanResult.rssi) // Found with fresh RSSI
                    } else {
                        println("Bluetooth Refresh: Device ${device.name} (${device.address}) not detected")
                        device.copy(rssi = 0) // Not detected in fresh scan
                    }
                }
                _uiState.value = _uiState.value.copy(registeredBluetoothDevices = updatedDevices)
                
                // LOADING COMPLETE: Clear loading state after scan completion
                _uiState.value = _uiState.value.copy(
                    isLoadingBluetooth = false,
                    bluetoothError = null
                )
                
                println("Bluetooth Refresh: Fresh scan process completed successfully - identical to initial scan!")
                
            } catch (e: Exception) {
                println("Bluetooth Refresh: Error occurred during fresh scan - ${e.message}")
                // Ensure cleanup on error
                bluetoothManager.stopBleScan()
                bluetoothManager.stopClassicDiscovery()
                _uiState.value = _uiState.value.copy(
                    isLoadingBluetooth = false,
                    bluetoothError = "Bluetooth refresh scan failed: ${e.message ?: "Unknown error"}"
                )
            }
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
    
    override fun onCleared() {
        super.onCleared()
        stopDataCollection()
        bluetoothManager.cleanup()
    }
}

/**
 * UI state for data testing screen
 */
data class DataTestingUiState(
    // GPS Data
    val gpsData: GPSData? = null,
    val isLoadingGPS: Boolean = false,
    val gpsError: String? = null,
    
    // WiFi Data
    val wifiData: WiFiData? = null,
    val isLoadingWiFi: Boolean = false,
    val wifiError: String? = null,
    
    // Registered Bluetooth Devices
    val registeredBluetoothDevices: List<BluetoothData> = emptyList(),
    val isLoadingBluetooth: Boolean = false,
    val bluetoothError: String? = null
)