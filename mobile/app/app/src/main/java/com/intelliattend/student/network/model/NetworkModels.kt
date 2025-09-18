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
 * Network verification status
 */
data class NetworkVerificationStatus(
    val biometric: Boolean,
    val location: Boolean,
    val wifi: Boolean,
    val bluetooth: Boolean = false
)