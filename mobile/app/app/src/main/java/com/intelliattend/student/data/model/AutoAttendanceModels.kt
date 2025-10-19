package com.intelliattend.student.data.model

import java.time.LocalDateTime

/**
 * Data models for auto-attendance feature
 */

data class AutoAttendanceConfig(
    val enabled: Boolean = false,
    val gpsEnabled: Boolean = true,
    val wifiEnabled: Boolean = true,
    val bluetoothEnabled: Boolean = true,
    val confidenceThreshold: Double = 0.85,
    val requireWarmData: Boolean = true,
    val autoSubmit: Boolean = false,
    val notifyOnAutoMark: Boolean = true
)

data class PresenceDetectionResult(
    val sessionId: String,
    val detectedAt: LocalDateTime,
    val gpsScore: Double,
    val wifiScore: Double,
    val bluetoothScore: Double,
    val finalConfidence: Double,
    val canAutoMark: Boolean,
    val contributingFactors: List<String>
)

data class AutoAttendanceActivity(
    val id: String,
    val sessionInfo: TimetableSession, // Assuming this exists from timetable models
    val detectedAt: LocalDateTime,
    val confidence: Double,
    val actionTaken: AutoAttendanceAction,
    val sensorScores: SensorScores
)

enum class AutoAttendanceAction {
    AUTO_MARKED,
    SUGGESTED,
    IGNORED
}

data class SensorScores(
    val gps: Double,
    val wifi: Double,
    val bluetooth: Double
)

// Sensor data models are imported from Models.kt
// Using unified models to avoid duplicates
