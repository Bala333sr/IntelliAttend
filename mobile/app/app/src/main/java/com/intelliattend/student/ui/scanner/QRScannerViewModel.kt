package com.intelliattend.student.ui.scanner

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.lifecycle.LifecycleOwner
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.data.model.QRData
import com.intelliattend.student.data.repository.AuthRepository
import com.intelliattend.student.network.AttendanceService
import com.intelliattend.student.network.ApiClient
import com.intelliattend.student.scanner.QRCodeScanner
import com.intelliattend.student.utils.QRCodeUtils
import com.intelliattend.student.bt.BluetoothManager
import com.intelliattend.student.data.collector.GPSDataCollector
import com.intelliattend.student.data.collector.WiFiDataCollector
import com.intelliattend.student.data.model.FinalScanData
import com.intelliattend.student.network.model.WarmAttendanceRequest
import com.intelliattend.student.network.model.WarmAttendanceResponse
import com.intelliattend.student.network.model.WarmBleSample
import com.intelliattend.student.network.model.WarmGpsData
import com.intelliattend.student.network.model.WarmSensorSample
import com.intelliattend.student.network.model.WarmWifiData
import com.intelliattend.student.network.model.AttendanceMarkRequest
import com.intelliattend.student.network.model.AttendanceMarkResponse
import com.intelliattend.student.utils.DeviceUtils
import com.google.gson.Gson
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import android.content.Context
import android.content.SharedPreferences
import com.google.gson.reflect.TypeToken
import com.intelliattend.student.data.model.BluetoothData
import com.intelliattend.student.data.model.CollectedData
import com.intelliattend.student.data.model.BluetoothDeviceData
import com.intelliattend.student.data.repository.CollectedDataRepository

class QRScannerViewModel : ViewModel() {
    
    private val context = IntelliAttendApplication.getContext()
    private val apiClient = ApiClient.getInstance(context)
    private val authRepository = AuthRepository(apiClient, IntelliAttendApplication.getInstance().getAppPreferences())
    private val attendanceService: AttendanceService = ApiClient.createAttendanceService()
    private val sharedPreferences: SharedPreferences = context.getSharedPreferences("registered_devices", Context.MODE_PRIVATE)
    private val gson = Gson()
    private val collectedDataRepository = CollectedDataRepository(context)
    
    private var qrCodeScanner: QRCodeScanner? = null
    private val bluetoothManager = BluetoothManager(context)
    private val wifiCollector = WiFiDataCollector(context)
    private val gpsCollector = GPSDataCollector(context)
    
    // Store registered device UUIDs for filtering
    private val registeredDeviceUuids = mutableSetOf<String>()
    
    var onScanComplete: ((Boolean, String?) -> Unit)? = null
    
    init {
        // Load registered devices from SharedPreferences
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
    
    /**
     * Start the camera for QR scanning
     */
    fun startCamera(previewView: PreviewView, lifecycleOwner: LifecycleOwner) {
        qrCodeScanner = QRCodeScanner(
            context = context,
            previewView = previewView,
            lifecycleOwner = lifecycleOwner,
            onQRCodeDetected = { qrContent ->
                processQRCode(qrContent)
            },
            onError = { error ->
                Log.e("QRScannerViewModel", "Camera error: $error")
                onScanComplete?.invoke(false, error)
            }
        )
        qrCodeScanner?.startScanning()
    }
    
    /**
     * Stop the camera
     */
    fun stopCamera() {
        qrCodeScanner?.stopScanning()
        qrCodeScanner?.release()
        qrCodeScanner = null
        bluetoothManager.stopBleScan()
        bluetoothManager.stopClassicDiscovery()
    }
    
    /**
     * Process scanned QR code and perform final scan
     */
    fun processQRCode(qrContent: String) {
        // Notify UI that QR code is detected (for success animation)
        onScanComplete?.invoke(true, qrContent)
        
        viewModelScope.launch {
            try {
                // Validate and parse QR data
                val qrData = QRCodeUtils.parseQRData(qrContent)
                
                if (qrData != null) {
                    // Validate QR data
                    if (QRCodeUtils.isValidQRData(qrData)) {
                        // Add a small delay to allow the success animation to be visible
                        delay(2000)
                        
                        // Perform final scan when QR code is detected
                        performFinalScan(qrContent, qrData)
                    } else {
                        onScanComplete?.invoke(false, "Invalid QR code data")
                    }
                } else {
                    onScanComplete?.invoke(false, "Unable to parse QR code")
                }
                
            } catch (e: Exception) {
                Log.e("QRScannerViewModel", "Error processing QR code", e)
                onScanComplete?.invoke(false, "Error processing QR code: ${e.message}")
            }
        }
    }
    
    /**
     * Perform a final quick scan for Bluetooth, WiFi, and GPS when QR code is detected
     */
    private suspend fun performFinalScan(qrContent: String, qrData: QRData) {
        try {
            // Collect sensor data
            val collectedData = collectSensorData(qrData.token)
            
            // Save collected data locally as backup
            collectedDataRepository.saveCollectedData(collectedData)
            
            // Submit to server immediately
            submitToServer(qrData.token, collectedData)
            
        } catch (e: Exception) {
            Log.e("QRScannerViewModel", "Error performing final scan", e)
            onScanComplete?.invoke(false, "Error performing final scan: ${e.message}")
        }
    }
    
    /**
     * Collect sensor data
     */
    private suspend fun collectSensorData(qrToken: String): CollectedData {
        try {
            // 1) Quick BLE scan
            bluetoothManager.clearScanResults()
            bluetoothManager.startBleScan()
            delay(700) // Quick BLE scan
            
            // Check if any registered devices were found during BLE scan
            val registeredDevicesFound = bluetoothManager.scanResults.value.values.any { scanResult ->
                registeredDeviceUuids.contains(scanResult.device.address)
            }
            
            // If no registered devices found, run Classic Bluetooth for 12 seconds
            if (!registeredDevicesFound) {
                bluetoothManager.stopBleScan()
                bluetoothManager.startClassicDiscovery()
                delay(1000) // Short classic discovery for final scan
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

            // Convert to BluetoothDeviceData list
            val bluetoothDeviceData = filteredBleEntries.map { deviceEntry ->
                BluetoothDeviceData(
                    mac = deviceEntry.device.address,
                    name = deviceEntry.device.name,
                    rssi = deviceEntry.rssi,
                    smoothedRssi = deviceEntry.smoothedRssi
                )
            }

            return CollectedData(
                wifiData = wifi,
                gpsData = gps,
                bluetoothData = bluetoothDeviceData,
                qrToken = qrToken,
                timestamp = System.currentTimeMillis()
            )
        } catch (e: Exception) {
            Log.e("QRScannerViewModel", "Error collecting sensor data", e)
            // Return empty collected data in case of error
            return CollectedData(
                wifiData = null,
                gpsData = null,
                bluetoothData = emptyList(),
                qrToken = null,
                timestamp = System.currentTimeMillis()
            )
        }
    }
    
    /**
     * Submit collected data to server for attendance marking
     */
    private suspend fun submitToServer(qrToken: String, data: CollectedData) {
        try {
            // Get student ID from auth repository
            val student = authRepository.getCurrentStudent()
            if (student == null) {
                onScanComplete?.invoke(false, "Not logged in")
                return
            }
            
            // Get auth token
            val authToken = authRepository.getAccessToken()
            if (authToken == null) {
                onScanComplete?.invoke(false, "No authentication token")
                return
            }
            
            // Prepare request
            val request = AttendanceMarkRequest(
                student_id = student.student_id,
                qr_token = qrToken,
                gps = WarmGpsData(
                    latitude = data.gpsData?.latitude ?: 0.0,
                    longitude = data.gpsData?.longitude ?: 0.0,
                    accuracy = data.gpsData?.accuracy,
                    timestamp = System.currentTimeMillis(),
                    altitude = data.gpsData?.altitude,
                    speed = data.gpsData?.speed
                ),
                wifi = data.wifiData?.let {
                    WarmWifiData(
                        ssid = it.ssid,
                        bssid = it.bssid,
                        signal_strength = it.rssi,
                        rssi = it.rssi,
                        ipAddress = it.ipAddress,
                        frequency = it.frequency
                    )
                },
                bluetooth = data.bluetoothData.map { device ->
                    WarmBleSample(
                        mac = device.mac,
                        name = device.name,
                        rssi = device.rssi,
                        smoothedRssi = device.smoothedRssi
                    )
                },
                timestamp = System.currentTimeMillis()
            )
            
            Log.i("QRScannerViewModel", "Submitting attendance to server...")
            Log.i("QRScannerViewModel", "Student ID: ${student.student_id}")
            Log.i("QRScannerViewModel", "QR Token: $qrToken")
            Log.i("QRScannerViewModel", "GPS: ${data.gpsData?.latitude}, ${data.gpsData?.longitude}")
            Log.i("QRScannerViewModel", "WiFi: ${data.wifiData?.ssid}")
            Log.i("QRScannerViewModel", "Bluetooth devices: ${data.bluetoothData.size}")
            
            // Call API
            val response = attendanceService.markAttendanceWithVerification(
                authToken = "Bearer $authToken",
                request = request
            )
            
            // Handle response
            if (response.success) {
                val score = response.verification_score ?: 0.0
                val message = "✅ Attendance Marked!\n" +
                        "Score: ${String.format("%.1f", score)}/100\n" +
                        response.message
                
                Log.i("QRScannerViewModel", "Attendance marked successfully: $message")
                Log.i("QRScannerViewModel", "Score breakdown: ${response.score_breakdown}")
                
                onScanComplete?.invoke(true, message)
            } else {
                val errorMsg = response.error ?: "Unknown error"
                val score = response.verification_score ?: 0.0
                val message = "❌ Verification Failed\n" +
                        "Score: ${String.format("%.1f", score)}/100\n" +
                        errorMsg
                
                Log.w("QRScannerViewModel", "Attendance verification failed: $errorMsg")
                Log.w("QRScannerViewModel", "Score: $score")
                Log.w("QRScannerViewModel", "Verifications: ${response.verifications}")
                
                onScanComplete?.invoke(false, message)
            }
            
        } catch (e: Exception) {
            Log.e("QRScannerViewModel", "Error submitting to server", e)
            val errorMessage = "Server submission failed: ${e.message}\nData saved locally for retry."
            onScanComplete?.invoke(false, errorMessage)
        }
    }
    
    /**
     * Send stored data to server (for manual sending if needed)
     */
    fun sendStoredDataToServer() {
        viewModelScope.launch {
            try {
                // Retrieve stored data
                val storedData = collectedDataRepository.getCollectedData()
                
                if (storedData.isEmpty()) {
                    onScanComplete?.invoke(false, "No stored data to send")
                    return@launch
                }
                
                // Send first stored entry
                val data = storedData.first()
                val qrToken = data.qrToken ?: ""
                
                if (qrToken.isEmpty()) {
                    onScanComplete?.invoke(false, "Invalid stored data: No QR token")
                    return@launch
                }
                
                // Submit to server
                submitToServer(qrToken, data)
                
            } catch (e: Exception) {
                Log.e("QRScannerViewModel", "Error sending stored data", e)
                onScanComplete?.invoke(false, "Error sending stored data: ${e.message}")
            }
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        stopCamera()
        bluetoothManager.cleanup()
    }
}