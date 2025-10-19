package com.intelliattend.student.network.model

data class AttendanceRequest(
    val student_id: String,
    val class_id: String,
    val session_token: String,
    val scan_timestamp_utc: String,
    val ble: BleData,
    val wifi: WifiData?,
    val gps: GpsData?,
    val qr_payload: String?,
    val device_info: DeviceInfo,
    val client_signature: String?
)

data class BleData(
    val adv_data_hex: String,
    val rssi: Int,
    val device_address: String,
    val service_uuid: String?
)

data class WifiData(
    val ssid: String,
    val bssid: String
)

data class GpsData(
    val lat: Double,
    val lon: Double,
    val accuracy: Float
)

data class DeviceInfo(
    val os: String,
    val model: String
)

data class AttendanceResponse(
    val success: Boolean,
    val message: String,
    val verification_score: Double
)
