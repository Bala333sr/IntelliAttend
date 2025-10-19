package com.intelliattend.student.data.model

import java.time.LocalDateTime
import java.time.LocalTime

/**
 * Data models for notifications feature
 */

data class NotificationPreferences(
    val classReminderEnabled: Boolean = true,
    val warmScanReminderEnabled: Boolean = true,
    val attendanceWarningEnabled: Boolean = true,
    val weeklySummaryEnabled: Boolean = true,
    val reminderMinutesBefore: Int = 10,
    val quietHoursStart: LocalTime? = null,
    val quietHoursEnd: LocalTime? = null,
    val notificationSound: Boolean = true,
    val vibration: Boolean = true
)

data class NotificationRecord(
    val id: String,
    val type: NotificationType,
    val title: String,
    val message: String,
    val sentAt: LocalDateTime,
    val readAt: LocalDateTime? = null,
    val actionTaken: Boolean = false
)

enum class NotificationType {
    CLASS_REMINDER,
    WARM_SCAN,
    ATTENDANCE_WARNING,
    WEEKLY_SUMMARY,
    SESSION_MISSED
}