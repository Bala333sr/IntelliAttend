package com.intelliattend.student.network

/**
 * Response models for API calls
 */

/**
 * Attendance history record
 */
data class AttendanceHistoryRecord(
    val recordId: Int,
    val sessionId: Int,
    val scanTimestamp: String,
    val status: String,
    val verificationScore: Double,
    val className: String,
    val facultyName: String
)

/**
 * Active session
 */
data class ActiveSession(
    val sessionId: Int,
    val classId: Int,
    val className: String,
    val facultyName: String,
    val startTime: String,
    val expiresAt: String,
    val status: String
)

/**
 * Session status
 */
data class SessionStatus(
    val sessionId: Int,
    val isActive: Boolean,
    val expiresAt: String,
    val totalStudents: Int,
    val presentStudents: Int
)