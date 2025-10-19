package com.intelliattend.student.network.model

import com.intelliattend.student.data.model.*

/**
 * Network models for API communication
 */

/**
 * Network attendance request (matches server API)
 */
data class NetworkAttendanceRequest(
    val studentId: Int,
    val classId: Int,
    val timestamp: String,
    val qrToken: String,
    val wifi: WiFiData?,
    val gps: GPSData,
    val bluetooth: List<BluetoothData> = emptyList(),
    val biometricVerified: Boolean,
    val deviceInfo: DeviceInfo
)

/**
 * Network attendance response (from server)
 */
data class NetworkAttendanceResponse(
    val success: Boolean,
    val status: String,
    val verificationScore: Double,
    val verifications: NetworkVerificationStatus,
    val message: String,
    val error: String?
)

/**
 * Offline attendance request
 */
data class OfflineAttendanceRequest(
    val request: NetworkAttendanceRequest,
    val status: String
)

/**
 * Network verification status
 */
data class NetworkVerificationStatus(
    val biometric: Boolean,
    val location: Boolean,
    val wifi: Boolean,
    val bluetooth: Boolean = false
)

/**
 * Enhanced login request with device enforcement data
 */
data class EnhancedLoginRequest(
    val email: String,
    val password: String,
    val device_info: com.intelliattend.student.utils.DeviceInfo,
    val wifi_info: com.intelliattend.student.utils.WiFiInfo?,
    val gps_info: com.intelliattend.student.utils.GPSInfo?,
    val permissions: com.intelliattend.student.utils.PermissionStatus
)

/**
 * Enhanced login response with device status
 */
data class EnhancedLoginResponse(
    val success: Boolean,
    val message: String?,
    val error: String?,
    val data: EnhancedLoginData?
)

/**
 * Enhanced login data nested object
 */
data class EnhancedLoginData(
    val access_token: String?,
    val refresh_token: String?,
    val token: String?,
    val student: Student?,
    val user: Student?,
    val device_status: DeviceStatusData?
)

/**
 * Device status response
 */
data class DeviceStatusResponse(
    val success: Boolean,
    val device_status: DeviceStatusData?,
    val error: String?
)

/**
 * Device status data
 */
data class DeviceStatusData(
    val is_active: Boolean,
    val is_primary: Boolean,
    val activation_status: String,
    val can_mark_attendance: Boolean,
    val cooldown_remaining_seconds: Int?,
    val cooldown_end_time: String?,
    val device_switch_pending: Boolean,
    val requires_admin_approval: Boolean,
    val message: String?
)

/**
 * Device switch request
 */
data class DeviceSwitchRequest(
    val new_device_info: com.intelliattend.student.utils.DeviceInfo,
    val wifi_info: com.intelliattend.student.utils.WiFiInfo?,
    val gps_info: com.intelliattend.student.utils.GPSInfo?
)

/**
 * Device switch response
 */
data class DeviceSwitchResponse(
    val success: Boolean,
    val message: String?,
    val error: String?,
    val device_status: DeviceStatusData?
)
