package com.intelliattend.student.auto

import android.content.Context
import android.util.Log
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.bt.BluetoothManager
import com.intelliattend.student.data.collector.GPSDataCollector
import com.intelliattend.student.data.collector.WiFiDataCollector
import com.intelliattend.student.data.model.*
import com.intelliattend.student.data.repository.AttendanceRepository
import com.intelliattend.student.data.repository.TimetableRepository
import com.intelliattend.student.utils.ConnectivityMonitor
import kotlinx.coroutines.*

/**
 * Orchestrates automatic attendance detection and marking.
 * Integrates GPS, Wi-Fi, Bluetooth, timetable, and attendance repositories.
 */
class AutoAttendanceManager(
    private val context: Context,
    private val gpsCollector: GPSDataCollector,
    private val wifiCollector: WiFiDataCollector,
    private val timetableRepository: TimetableRepository,
    private val attendanceRepository: AttendanceRepository,
    private val connectivityMonitor: ConnectivityMonitor
) {

    private val bluetoothManager: BluetoothManager =
        (context.applicationContext as IntelliAttendApplication).getBluetoothManager()

    private val prefs = (context.applicationContext as IntelliAttendApplication).getAppPreferences()

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    suspend fun tryMarkAttendanceForCurrentSession(): Result<com.intelliattend.student.network.model.AttendanceResponse> {
        // Prefer student code if available, otherwise fallback to numeric ID as string
        val studentIdStr = prefs.studentData?.studentCode ?: prefs.studentData?.studentId?.toString()
            ?: return Result.failure(Exception("No student data"))
    
        // Fetch current session info via repository (Result wrapper)
        val sessionInfoResult = timetableRepository.getCurrentSession()
        val sessionInfo = sessionInfoResult.getOrNull()
        if (sessionInfo == null) {
            Log.d("AAM", "No current session")
            return Result.failure(Exception("No current session"))
        }
        if (!sessionInfo.hasActiveClass()) {
            Log.d("AAM", "No active class" )
            return Result.failure(Exception("No active class"))
        }
    
        // Collect sensor data concurrently
        return coroutineScope {
            val locDef = async { gpsCollector.getCurrentLocation() }
            val wifiDef = async { wifiCollector.getCurrentWiFiData() }
    
            // Perform a short BLE scan and choose best candidate (prefer beaconInfo)
            bluetoothManager.startBleScan()
            delay(1_500)
            val bleEntries = bluetoothManager.scanResults.value.values.toList()
            bluetoothManager.stopBleScan()
            val bleCandidate = bleEntries
                .filter { it.beaconInfo != null }
                .maxByOrNull { it.rssi }
                ?: bleEntries.maxByOrNull { it.rssi }
    
            val loc = locDef.await().getOrNull()
            val wifi = wifiDef.await().getOrNull()
    
            if (loc == null) {
                return@coroutineScope Result.failure(Exception("Location unavailable"))
            }
            if (bleCandidate == null) {
                return@coroutineScope Result.failure(Exception("No BLE devices discovered"))
            }
    
            // Map app models to network models
            val wifiNet = wifi?.let {
                com.intelliattend.student.network.model.WifiData(ssid = it.ssid, bssid = it.bssid)
            }
            val gpsNet = com.intelliattend.student.network.model.GpsData(
                lat = loc.latitude,
                lon = loc.longitude,
                accuracy = loc.accuracy
            )
            val advHex = bleCandidate.advPayload?.joinToString("") { b -> "%02X".format(b) } ?: ""
            val bleNet = com.intelliattend.student.network.model.BleData(
                adv_data_hex = advHex,
                rssi = bleCandidate.rssi,
                device_address = bleCandidate.device.address,
                service_uuid = null
            )
            val deviceInfo = com.intelliattend.student.utils.DeviceUtils.getDeviceInfo(context)
            val deviceNet = com.intelliattend.student.network.model.DeviceInfo(
                os = deviceInfo.osVersion,
                model = deviceInfo.deviceModel
            )
    
            // Use beaconInfo to derive class_id and session_token when available
            val classIdStr = bleCandidate.beaconInfo?.classId?.toString() ?: sessionInfo.currentSession?.subjectCode ?: ""
            val sessionTokenStr = bleCandidate.beaconInfo?.sessionToken?.toString() ?: ""
            val timestampUtc = java.time.Instant.now().toString()
    
            // Build network attendance request
            val request = com.intelliattend.student.network.model.AttendanceRequest(
                student_id = studentIdStr,
                class_id = classIdStr,
                session_token = sessionTokenStr,
                scan_timestamp_utc = timestampUtc,
                ble = bleNet,
                wifi = wifiNet,
                gps = gpsNet,
                qr_payload = null,
                device_info = deviceNet,
                client_signature = null
            )
    
            // Submit via repository (handles network call)
            attendanceRepository.submitAttendanceWithBluetooth(request)
        }
    }

    fun startMonitoring() {
        scope.launch {
            while (isActive) {
                delay(60_000) // 1 min polling
                if (connectivityMonitor.isConnected.value) {
                    tryMarkAttendanceForCurrentSession()
                }
            }
        }
    }

    fun stopMonitoring() {
        scope.cancel()
    }
}