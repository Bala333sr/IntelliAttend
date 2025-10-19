package com.intelliattend.student.ui.testing

import android.content.Context
import android.content.SharedPreferences
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.bt.BluetoothManager
import com.intelliattend.student.data.collector.GPSDataCollector
import com.intelliattend.student.data.collector.WiFiDataCollector
import com.intelliattend.student.data.model.GPSData
import com.intelliattend.student.data.model.WiFiData
import com.intelliattend.student.data.model.BluetoothData
import com.intelliattend.student.network.ApiClient
import com.intelliattend.student.network.AttendanceService
import com.intelliattend.student.network.model.*
import com.intelliattend.student.utils.DeviceUtils
import com.intelliattend.student.warm.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

data class WarmScanTestUiState(
    val isWarmScanActive: Boolean = false,
    val isSendingData: Boolean = false,
    val warmScanStatus: String = "Stopped",
    val collectedSamples: List<SensorSample> = emptyList(),
    val nextScanIn: Long? = null,
    val errorMessage: String? = null
)

class WarmScanTestViewModel : ViewModel() {
    
    private val context = IntelliAttendApplication.getContext()
    private val bluetoothManager = BluetoothManager(context)
    private val wifiCollector = WiFiDataCollector(context)
    private val gpsCollector = GPSDataCollector(context)
    private val attendanceService: AttendanceService = ApiClient.createAttendanceService()
    private val sharedPreferences: SharedPreferences = context.getSharedPreferences("registered_devices", Context.MODE_PRIVATE)
    private val gson = Gson()
    
    private val _uiState = MutableStateFlow(WarmScanTestUiState())
    val uiState: StateFlow<WarmScanTestUiState> = _uiState.asStateFlow()
    
    // Store registered device UUIDs for filtering
    private val registeredDeviceUuids = mutableSetOf<String>()
    
    private var warmScanJob: Job? = null
    private var timerJob: Job? = null
    private var warmWindowStart: Long = 0
    private var warmWindowEnd: Long = 0
    private val cycleIntervalMs = 30_000L // 30 seconds
    private val warmWindowMs = 180_000L // 3 minutes
    
    private val sampleBuffer = SampleBuffer(8)
    
    init {
        // Initialize with existing warm samples if any
        _uiState.value = _uiState.value.copy(
            collectedSamples = WarmScanHolder.getSamples()
        )
        
        // Load registered devices from SharedPreferences (same as environmental data testing)
        loadRegisteredDevices()
    }
    
    // Load registered devices from SharedPreferences (same approach as environmental data testing)
    private fun loadRegisteredDevices() {
        val existingDevicesJson = sharedPreferences.getString("registered_bluetooth_devices", null)
        val type = object : TypeToken<MutableList<BluetoothData>>() {}.type
        val registeredDevices: MutableList<BluetoothData> = existingDevicesJson?.let {
            gson.fromJson(it, type)
        } ?: mutableListOf()
        
        // Populate the registered device UUIDs set
        registeredDeviceUuids.clear()
        registeredDevices.forEach { device ->
            registeredDeviceUuids.add(device.address)
        }
    }
    
    fun startWarmScanTest() {
        // Set up a mock session start time for testing (3 minutes from now)
        val mockSessionStart = System.currentTimeMillis() + warmWindowMs
        startWarmWindow(mockSessionStart)
    }
    
    fun toggleWarmScan() {
        if (_uiState.value.isWarmScanActive) {
            stopWarmScan()
        } else {
            startWarmScanTest()
        }
    }
    
    private fun startWarmWindow(sessionStartEpochMs: Long) {
        stopWarmScan()
        
        warmWindowStart = sessionStartEpochMs - warmWindowMs
        warmWindowEnd = sessionStartEpochMs
        
        _uiState.value = _uiState.value.copy(
            isWarmScanActive = true,
            warmScanStatus = "Active",
            collectedSamples = emptyList(),
            nextScanIn = warmWindowMs
        )
        
        // Clear previous samples
        sampleBuffer.clear()
        
        warmScanJob = viewModelScope.launch {
            val now = System.currentTimeMillis()
            val waitMs = (warmWindowStart - now).coerceAtLeast(0)
            
            if (waitMs > 0) {
                delay(waitMs)
            }
            
            // Start the warm scan cycles
            runWarmScanCycles()
        }
        
        // Start timer to update UI
        startTimer()
    }
    
    private suspend fun runWarmScanCycles() {
        try {
            while (System.currentTimeMillis() < warmWindowEnd && _uiState.value.isWarmScanActive) {
                val sample = runCycleOnce()
                sampleBuffer.add(sample)
                
                // Update UI state safely
                _uiState.value = _uiState.value.copy(
                    collectedSamples = sampleBuffer.toList()
                )
                
                // Wait for next cycle
                val nextCycleTime = System.currentTimeMillis() + cycleIntervalMs
                val waitTime = (nextCycleTime - System.currentTimeMillis()).coerceAtLeast(0)
                
                if (waitTime > 0 && System.currentTimeMillis() + waitTime < warmWindowEnd) {
                    delay(waitTime)
                } else {
                    break
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("WarmScanTestViewModel", "Error in warm scan cycles", e)
        } finally {
            // Warm scan completed
            _uiState.value = _uiState.value.copy(
                isWarmScanActive = false,
                warmScanStatus = "Completed"
            )
        }
    }
    
    private suspend fun runCycleOnce(): SensorSample {
        try {
            // 1) Quick BLE scan with the same approach as environmental data testing
            bluetoothManager.clearScanResults()
            bluetoothManager.startBleScan()
            delay(WarmScanConfig.BLE_QUICK_SCAN_MS)
            
            // Check if any registered devices were found during BLE scan
            val registeredDevicesFound = bluetoothManager.scanResults.value.values.any { scanResult ->
                registeredDeviceUuids.contains(scanResult.device.address)
            }
            
            // If no registered devices found, run Classic Bluetooth for 12 seconds
            if (!registeredDevicesFound) {
                bluetoothManager.stopBleScan()
                bluetoothManager.startClassicDiscovery()
                delay(WarmScanConfig.CLASSIC_DISCOVERY_MS)
            }
            
            // Stop scanning
            bluetoothManager.stopBleScan()
            bluetoothManager.stopClassicDiscovery()

            val bleEntries = bluetoothManager.scanResults.value.values.toList()
            val wifi = wifiCollector.getCurrentWiFiData().getOrNull()
            val gps = gpsCollector.getLastKnownLocation().getOrNull()

            // Filter BLE devices to only include registered ones
            val filteredBleEntries = bleEntries.filter { deviceEntry ->
                val deviceUuid = deviceEntry.device.address
                registeredDeviceUuids.contains(deviceUuid)
            }

            return SensorSample(
                ts = System.currentTimeMillis(),
                ble = filteredBleEntries.map {
                    WarmBle(
                        mac = it.device.address,
                        name = it.device.name,
                        rssi = it.rssi,
                        smoothedRssi = it.smoothedRssi
                    )
                },
                wifi = wifi,
                gps = gps
            )
        } catch (e: Exception) {
            android.util.Log.e("WarmScanTestViewModel", "Error in runCycleOnce", e)
            // Return empty sample in case of error
            return SensorSample(
                ts = System.currentTimeMillis(),
                ble = emptyList(),
                wifi = null,
                gps = null
            )
        }
    }
    
    private fun startTimer() {
        timerJob?.cancel()
        timerJob = viewModelScope.launch {
            try {
                while (_uiState.value.isWarmScanActive) {
                    val now = System.currentTimeMillis()
                    val timeRemaining = (warmWindowEnd - now).coerceAtLeast(0)
                    
                    _uiState.value = _uiState.value.copy(
                        nextScanIn = timeRemaining
                    )
                    
                    delay(1000) // Update every second
                }
            } catch (e: Exception) {
                android.util.Log.e("WarmScanTestViewModel", "Error in timer job", e)
            }
        }
    }
    
    private fun stopWarmScan() {
        warmScanJob?.cancel()
        timerJob?.cancel()
        bluetoothManager.stopBleScan()
        bluetoothManager.stopClassicDiscovery()
        
        _uiState.value = _uiState.value.copy(
            isWarmScanActive = false,
            warmScanStatus = "Stopped"
        )
    }
    
    fun sendCollectedData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                isSendingData = true,
                errorMessage = null
            )
            
            try {
                // Get the collected samples
                val samples = _uiState.value.collectedSamples
                
                // Convert to enhanced warm scan data model with detailed information
                val warmSamples = samples.map { sample ->
                    WarmSensorSample(
                        ts = sample.ts,
                        ble = sample.ble.map { bleDevice ->
                            WarmBleSample(
                                mac = bleDevice.mac,
                                name = bleDevice.name,
                                rssi = bleDevice.rssi,
                                smoothedRssi = bleDevice.smoothedRssi,
                                // Add detailed information
                                adv_hex = getAdvertisementHex(bleDevice.mac), // Mock advertisement data
                                service_uuid = getServiceUuid(bleDevice.mac) // Mock service UUID
                            )
                        },
                        wifi = sample.wifi?.let { wifi ->
                            WarmWifiData(
                                ssid = wifi.ssid ?: "",
                                bssid = wifi.bssid ?: "",
                                rssi = wifi.rssi,
                                ipAddress = wifi.ipAddress,
                                frequency = wifi.frequency
                            )
                        },
                        gps = sample.gps?.let { gps ->
                            WarmGpsData(
                                latitude = gps.latitude,
                                longitude = gps.longitude,
                                accuracy = gps.accuracy,
                                altitude = gps.altitude,
                                speed = gps.speed
                            )
                        }
                    )
                }
                
                // Get the final sample (most recent)
                val finalSample = warmSamples.lastOrNull()
                
                if (warmSamples.isEmpty() || finalSample == null) {
                    _uiState.value = _uiState.value.copy(
                        isSendingData = false,
                        errorMessage = "No samples collected"
                    )
                    return@launch
                }
                
                // Create device info using the proper DeviceUtils
                val deviceInfoData = DeviceUtils.getDeviceInfo(context)
                val deviceInfo = com.intelliattend.student.network.model.DeviceInfo(
                    os = deviceInfoData.osVersion,
                    model = deviceInfoData.deviceModel
                )
                
                // Create the warm attendance request with detailed information
                val request = WarmAttendanceRequest(
                    qr_data = "", // Empty for testing
                    biometric_verified = false, // Not verified for testing
                    location = finalSample.gps,
                    bluetooth = null, // Not used in this context
                    device_info = deviceInfo,
                    samples = warmSamples,
                    final_sample = finalSample
                )
                
                // Send to server using the correct attendance service
                val response = attendanceService.submitWarmAttendance(request)
                
                if (response.success) {
                    _uiState.value = _uiState.value.copy(
                        isSendingData = false,
                        errorMessage = null
                    )
                } else {
                    _uiState.value = _uiState.value.copy(
                        isSendingData = false,
                        errorMessage = response.error ?: "Failed to send data"
                    )
                }
            } catch (e: Exception) {
                android.util.Log.e("WarmScanTestViewModel", "Error sending warm scan data", e)
                _uiState.value = _uiState.value.copy(
                    isSendingData = false,
                    errorMessage = e.message ?: "Unknown error"
                )
            }
        }
    }
    
    // Helper methods to get device information
    private fun getAdvertisementHex(mac: String): String? {
        // In a real implementation, this would get the actual advertisement data
        // For now, we'll return a mock hex string
        return "0201061AFF4C000215E20A39F473F45C4C9A6E7DB8E0F5F7D1F90C010203"
    }
    
    // Helper method to get service UUID
    private fun getServiceUuid(mac: String): String? {
        // In a real implementation, this would extract service UUID from advertisement data
        // For now, we'll return a mock service UUID
        return "service_001"
    }
    
    override fun onCleared() {
        super.onCleared()
        try {
            stopWarmScan()
            bluetoothManager.cleanup()
        } catch (e: Exception) {
            android.util.Log.e("WarmScanTestViewModel", "Error in onCleared", e)
        }
    }
}