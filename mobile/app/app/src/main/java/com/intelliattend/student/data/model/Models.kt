package com.intelliattend.student.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

/**
 * Data models for IntelliAttend Student App
 */

@Parcelize
data class Student(
    val studentId: Int,
    val studentCode: String,
    val firstName: String,
    val lastName: String,
    val email: String,
    val program: String,
    val yearOfStudy: Int = 1
) : Parcelable

@Parcelize
data class LoginRequest(
    val email: String,
    val password: String
) : Parcelable

@Parcelize
data class LoginResponse(
    val success: Boolean,
    val accessToken: String?,
    val student: Student?,
    val error: String?
) : Parcelable

@Parcelize
data class QRData(
    val sessionId: Int,
    val token: String,
    val timestamp: Long,
    val sequence: Int
) : Parcelable

@Parcelize
data class WiFiData(
    val ssid: String,
    val bssid: String,
    val rssi: Int,
    val ipAddress: String,
    val frequency: Int = 0
) : Parcelable

@Parcelize
data class GPSData(
    val latitude: Double,
    val longitude: Double,
    val accuracy: Float,
    val altitude: Double = 0.0,
    val speed: Float = 0.0f
) : Parcelable

@Parcelize
data class BluetoothData(
    val name: String,
    val address: String,
    val rssi: Int = 0
) : Parcelable

@Parcelize
data class DeviceInfo(
    val deviceId: String,
    val deviceName: String,
    val osVersion: String,
    val appVersion: String,
    val deviceModel: String,
    val manufacturer: String
) : Parcelable

@Parcelize
data class AttendanceRequest(
    val studentId: Int,
    val classId: Int?,
    val timestamp: String,
    val qrToken: String,
    val wifi: WiFiData?,
    val gps: GPSData,
    val bluetooth: List<BluetoothData> = emptyList(),
    val biometricVerified: Boolean,
    val deviceInfo: DeviceInfo
) : Parcelable

@Parcelize
data class AttendanceResponse(
    val success: Boolean,
    val status: String,
    val verificationScore: Double,
    val verifications: VerificationStatus,
    val message: String,
    val error: String?
) : Parcelable

@Parcelize
data class VerificationStatus(
    val biometric: Boolean,
    val location: Boolean,
    val wifi: Boolean = true,
    val bluetooth: Boolean = false
) : Parcelable

@Parcelize
data class BiometricResult(
    val success: Boolean,
    val errorMessage: String? = null
) : Parcelable

enum class AttendanceStatus {
    PRESENT,
    LATE,
    ABSENT,
    INVALID
}

enum class ScanResult {
    SUCCESS,
    INVALID_QR,
    SESSION_EXPIRED,
    ALREADY_MARKED,
    VERIFICATION_FAILED,
    NETWORK_ERROR,
    UNKNOWN_ERROR
}