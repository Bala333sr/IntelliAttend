package com.intelliattend.student.network.model

/**
 * Models for warm-scan attendance submission to /api/attendance/scan
 */

/**
 * Bluetooth device sample - matches backend BluetoothDevice model
 */
data class WarmBleSample(
    val mac: String,
    val name: String? = null,
    val rssi: Int? = null,
    val smoothedRssi: Double? = null,
    val adv_hex: String? = null,
    val service_uuid: String? = null
)

/**
 * WiFi network data - matches backend WiFiData model
 */
data class WarmWifiData(
    val ssid: String,
    val bssid: String,
    val signal_strength: Int? = null,  // Backend expects this field name
    // Legacy fields for backward compatibility
    val rssi: Int? = null,
    val ipAddress: String? = null,
    val frequency: Int? = null
)

/**
 * GPS location data - matches backend GPSData model
 */
data class WarmGpsData(
    val latitude: Double,
    val longitude: Double,
    val accuracy: Float? = null,
    val timestamp: Long? = null,  // Backend expects this
    // Legacy fields for backward compatibility
    val altitude: Double? = null,
    val speed: Float? = null
)

data class WarmSensorSample(
    val ts: Long,
    val ble: List<WarmBleSample>,
    val wifi: WarmWifiData?,
    val gps: WarmGpsData?
)

/**
 * NEW: Simplified request model matching backend /api/attendance/mark
 */
data class AttendanceMarkRequest(
    val student_id: Int,
    val qr_token: String,
    val gps: WarmGpsData,
    val wifi: WarmWifiData?,
    val bluetooth: List<WarmBleSample>,
    val timestamp: Long
)

/**
 * NEW: Response model matching backend /api/attendance/mark
 */
data class AttendanceMarkResponse(
    val success: Boolean,
    val message: String,
    val verification_score: Double? = null,
    val score_breakdown: Map<String, Double>? = null,
    val verifications: Map<String, Any>? = null,
    val error: String? = null,
    val attendance_id: Int? = null
)

/**
 * LEGACY: Old warm attendance request (keeping for backward compatibility)
 */
data class WarmAttendanceRequest(
    val qr_data: String,
    val biometric_verified: Boolean,
    val location: WarmGpsData?,
    val bluetooth: Map<String, Any>? = null,
    val device_info: DeviceInfo,
    val samples: List<WarmSensorSample>,
    val final_sample: WarmSensorSample
)

/**
 * LEGACY: Old warm attendance response (keeping for backward compatibility)
 */
data class WarmAttendanceResponse(
    val success: Boolean,
    val status: String? = null,
    val verification_score: Double? = null,
    val message: String? = null,
    val error: String? = null
)
