package com.intelliattend.student.data.model

import java.time.LocalDate
import java.time.LocalDateTime

/**
 * Data models for attendance statistics feature
 */

data class AttendanceStatistics(
    val studentId: String,
    val overallPercentage: Double,
    val subjectStats: List<SubjectAttendanceStats>,
    val totalSessions: Int,
    val attendedSessions: Int,
    val absentSessions: Int,
    val requiredPercentage: Double = 75.0,
    val status: AttendanceHealthStatus // SAFE, WARNING, CRITICAL
)

data class SubjectAttendanceStats(
    val subjectId: String,
    val subjectName: String,
    val subjectCode: String,
    val totalSessions: Int,
    val attendedSessions: Int,
    val percentage: Double,
    val status: AttendanceHealthStatus,
    val canReach75: Boolean,
    val sessionsNeeded: Int
)

data class AttendanceHistoryRecord(
    val id: String,
    val date: LocalDateTime,
    val subjectName: String,
    val sessionTime: String,
    val status: AttendanceRecordStatus, // PRESENT, ABSENT, LATE
    val attendanceType: AttendanceType, // QR_SCAN, WARM_SCAN, AUTO
    val classroomName: String
)

data class AttendanceTrend(
    val date: LocalDate,
    val attendanceRate: Double,
    val sessionsCount: Int,
    val attendedCount: Int
)

enum class AttendanceHealthStatus {
    SAFE,      // >= 75%
    WARNING,   // 65-75%
    CRITICAL   // < 65%
}

enum class AttendanceRecordStatus {
    PRESENT,
    ABSENT,
    LATE
}

enum class AttendanceType {
    QR_SCAN,
    WARM_SCAN,
    AUTO,
    MANUAL
}

enum class TrendPeriod {
    DAILY,
    WEEKLY,
    MONTHLY
}

enum class ExportFormat {
    PDF,
    CSV
}