package com.intelliattend.student.data.repository

import android.content.Context
import android.util.Log
import com.intelliattend.student.data.collector.GPSDataCollector
import com.intelliattend.student.data.collector.WiFiDataCollector
import com.intelliattend.student.data.model.*
import com.intelliattend.student.network.ActiveSession
import com.intelliattend.student.network.ApiClient
import com.intelliattend.student.network.AttendanceHistoryRecord
import com.intelliattend.student.network.AttendanceService
import com.intelliattend.student.network.model.AttendanceRequest
import com.intelliattend.student.network.model.NetworkAttendanceRequest
import com.intelliattend.student.network.model.NetworkAttendanceResponse
import com.intelliattend.student.utils.DeviceUtils
import com.intelliattend.student.utils.ConnectivityMonitor
import com.intelliattend.student.utils.OfflineQueueManager
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

/**
 * Repository for handling attendance-related operations
 */
class AttendanceRepository(
    private val context: Context,
    private val attendanceService: AttendanceService,
    private val gpsCollector: GPSDataCollector,
    private val wifiCollector: WiFiDataCollector,
    private val connectivityMonitor: ConnectivityMonitor,
    private val offlineQueueManager: OfflineQueueManager
) {
    
    /**
     * Mark attendance with multi-factor verification
     */
    suspend fun markAttendance(
        studentId: Int,
        classId: Int,
        qrToken: String
    ): Result<AttendanceResponse> = coroutineScope {
        try {
            // Collect all required data simultaneously
            val locationDeferred = async { 
                val currentLocationResult = gpsCollector.getCurrentLocation()
                if (currentLocationResult.isSuccess) {
                    currentLocationResult.getOrNull()
                } else {
                    gpsCollector.getLastKnownLocation().getOrNull()
                }
            }
            
            val wifiDataDeferred = async { 
                wifiCollector.getCurrentWiFiData().getOrNull()
            }
            
            val bluetoothDataDeferred = async { 
                // For now, we'll collect paired devices as an example
                // In a real implementation, we would collect nearby devices during scanning
                emptyList<BluetoothData>()
            }
            
            val deviceInfoDeferred = async { 
                DeviceUtils.getDeviceInfo(context)
            }
            
            val biometricDeferred = async { 
                // In testing mode, we simulate biometric verification
                BiometricResult(success = true)
            }
            
            // Wait for all data collection to complete
            val locationResult = locationDeferred.await()
            val wifiResult = wifiDataDeferred.await()
            val bluetoothResult = bluetoothDataDeferred.await()
            val deviceInfo = deviceInfoDeferred.await()
            val biometricResult = biometricDeferred.await()
            
            // Extract data or handle errors
            val locationData = locationResult
                ?: return@coroutineScope Result.failure(Exception("Unable to get location data"))
            
            val wifiData = wifiResult
            
            // Create network request
            val networkRequest = NetworkAttendanceRequest(
                studentId = studentId,
                classId = classId,
                timestamp = System.currentTimeMillis().toString(),
                qrToken = qrToken,
                wifi = wifiData,
                gps = locationData,
                bluetooth = bluetoothResult,
                biometricVerified = biometricResult.success,
                deviceInfo = com.intelliattend.student.network.model.DeviceInfo(
                    os = deviceInfo.osVersion,
                    model = deviceInfo.deviceModel
                )
            )

            if (!connectivityMonitor.isConnected.value) {
                val offlineRequest = OfflineAttendanceRequest(networkRequest, "Pending Sync")
                offlineQueueManager.addToQueue(offlineRequest)
                return@coroutineScope Result.success(AttendanceResponse(success = true, status = "Queued", message = "Attendance recorded offline. Will sync when online."))
            }
            
            // Send attendance request
            val response = attendanceService.markAttendance(networkRequest)
            
            // Convert network response to app model
            val appResponse = AttendanceResponse(
                success = response.success,
                status = response.status,
                verificationScore = response.verificationScore,
                verifications = VerificationStatus(
                    biometric = response.verifications.biometric,
                    location = response.verifications.location,
                    wifi = response.verifications.wifi,
                    bluetooth = response.verifications.bluetooth
                ),
                message = response.message,
                error = response.error
            )
            
            Result.success(appResponse)
            
        } catch (e: Exception) {
            Log.e("AttendanceRepository", "Error marking attendance", e)
            Result.failure(e)
        }
    }

    suspend fun processOfflineQueue() {
        val queue = offlineQueueManager.getQueue()
        if (queue.isNotEmpty()) {
            val updatedQueue = queue.toMutableList()
            try {
                queue.forEach { offlineRequest ->
                    val response = attendanceService.markAttendance(offlineRequest.request)
                    if (response.success) {
                        updatedQueue.remove(offlineRequest)
                    } else {
                        val failedRequest = offlineRequest.copy(status = "Sync Failed")
                        val index = updatedQueue.indexOf(offlineRequest)
                        if (index != -1) {
                            updatedQueue[index] = failedRequest
                        }
                    }
                }
                offlineQueueManager.updateQueue(updatedQueue)
            } catch (e: Exception) {
                Log.e("AttendanceRepository", "Error processing offline queue", e)
            }
        }
    }

    suspend fun submitAttendanceWithBluetooth(request: AttendanceRequest): Result<com.intelliattend.student.network.model.AttendanceResponse> {
        return try {
            val response = attendanceService.submitAttendance(request)
            Result.success(response)
        } catch (e: Exception) {
            Log.e("AttendanceRepository", "Error submitting attendance with bluetooth", e)
            Result.failure(e)
        }
    }
    
    /**
     * Get attendance history
     */
    suspend fun getAttendanceHistory(limit: Int = 50): Result<List<AttendanceHistoryRecord>> {
        return try {
            // In testing mode, return empty list or mock data
            Result.success(emptyList())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get current active sessions
     */
    suspend fun getCurrentSessions(): Result<List<ActiveSession>> {
        return try {
            // In testing mode, return empty list or mock data
            Result.success(emptyList())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Verify attendance data for testing purposes
     */
    suspend fun verifyAttendanceData(
        locationData: GPSData?,
        wifiData: WiFiData?,
        bluetoothData: List<BluetoothData>,
        deviceInfo: com.intelliattend.student.data.model.DeviceInfo
    ): VerificationStatus {
        // Location verification (must be within reasonable accuracy)
        val locationVerified = locationData?.let { location ->
            location.accuracy <= 50.0f // Within 50 meters accuracy
        } ?: false
        
        // WiFi verification (must have valid connection)
        val wifiVerified = wifiData != null
        
        // Bluetooth verification (at least one device detected)
        val bluetoothVerified = bluetoothData.isNotEmpty()
        
        // Device info is always available
        val deviceVerified = true
        
        return VerificationStatus(
            biometric = true, // Simulated in testing mode
            location = locationVerified,
            wifi = wifiVerified,
            bluetooth = bluetoothVerified
        )
    }
}