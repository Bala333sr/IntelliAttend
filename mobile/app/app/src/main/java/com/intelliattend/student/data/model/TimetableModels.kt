package com.intelliattend.student.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

/**
 * Timetable data models for IntelliAttend Student App
 */

@Parcelize
data class TimetableSlot(
    val slotNumber: Int,
    val startTime: String,          // Format: "09:20"
    val endTime: String,            // Format: "10:30"
    val subjectCode: String?,       // Null for breaks
    val subjectName: String,        // e.g., "COMPUTER NETWORKS" or "BREAK"
    val shortName: String,          // e.g., "CN" or "BREAK"
    val facultyName: String?,       // Null for breaks
    val room: String,               // e.g., "4208"
    val slotType: String            // "regular", "break", "lunch", "lab"
) : Parcelable {
    
    /**
     * Check if this is a regular class (not break/lunch)
     */
    fun isRegularClass(): Boolean {
        return slotType == "regular" || slotType == "lab"
    }
    
    /**
     * Check if this is a break
     */
    fun isBreak(): Boolean {
        return slotType == "break" || slotType == "lunch"
    }
    
    /**
     * Get display time range (e.g., "09:20 - 10:30")
     */
    fun getTimeRange(): String {
        return "$startTime - $endTime"
    }
}

@Parcelize
data class DailySchedule(
    val dayOfWeek: String,          // e.g., "MONDAY"
    val slots: List<TimetableSlot>
) : Parcelable {
    
    /**
     * Get only regular classes (exclude breaks)
     */
    fun getRegularClasses(): List<TimetableSlot> {
        return slots.filter { it.isRegularClass() }
    }
    
    /**
     * Get short day name (e.g., "MON")
     */
    fun getShortDayName(): String {
        return when (dayOfWeek.uppercase()) {
            "MONDAY" -> "MON"
            "TUESDAY" -> "TUE"
            "WEDNESDAY" -> "WED"
            "THURSDAY" -> "THU"
            "FRIDAY" -> "FRI"
            "SATURDAY" -> "SAT"
            "SUNDAY" -> "SUN"
            else -> dayOfWeek.take(3)
        }
    }
}

@Parcelize
data class StudentInfo(
    val studentCode: String,        // e.g., "23N31A6645"
    val name: String,               // e.g., "BALA"
    val section: String,            // e.g., "A"
    val course: String,             // e.g., "III CSE (AIML)"
    val room: String                // e.g., "4208"
) : Parcelable

@Parcelize
data class StudentTimetable(
    val student: StudentInfo,
    val timetable: Map<String, List<TimetableSlot>>
) : Parcelable {
    
    /**
     * Get schedule for a specific day
     */
    fun getScheduleForDay(day: String): List<TimetableSlot> {
        return timetable[day.uppercase()] ?: emptyList()
    }
    
    /**
     * Get all days in order
     */
    fun getDaysInOrder(): List<String> {
        val daysOrder = listOf("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY")
        return daysOrder.filter { timetable.containsKey(it) }
    }
    
    /**
     * Get schedule for today
     */
    fun getTodaySchedule(): List<TimetableSlot> {
        val today = java.time.LocalDate.now().dayOfWeek.name
        return getScheduleForDay(today)
    }
}

@Parcelize
data class CurrentSession(
    val isActive: Boolean,
    val subjectCode: String?,
    val subjectName: String,
    val shortName: String,
    val facultyName: String?,
    val startTime: String,          // Format: "09:20"
    val endTime: String,            // Format: "10:30"
    val room: String,
    val minutesElapsed: Int?,       // Null if not active
    val minutesRemaining: Int?      // Null if not active
) : Parcelable {
    
    /**
     * Get progress percentage (0-100)
     */
    fun getProgressPercentage(): Int {
        if (!isActive || minutesElapsed == null || minutesRemaining == null) return 0
        val total = minutesElapsed + minutesRemaining
        if (total == 0) return 0
        return ((minutesElapsed.toFloat() / total) * 100).toInt()
    }
    
    /**
     * Format time remaining (e.g., "35 minutes left")
     */
    fun getTimeRemainingText(): String {
        if (!isActive || minutesRemaining == null) return ""
        return when {
            minutesRemaining == 1 -> "1 minute left"
            minutesRemaining < 60 -> "$minutesRemaining minutes left"
            else -> "${minutesRemaining / 60}h ${minutesRemaining % 60}m left"
        }
    }
}

@Parcelize
data class NextSession(
    val subjectCode: String?,
    val subjectName: String,
    val shortName: String,
    val facultyName: String?,
    val startTime: String,
    val endTime: String,
    val room: String,
    val minutesUntilStart: Int
) : Parcelable {
    
    /**
     * Format time until start (e.g., "Starts in 25 minutes")
     */
    fun getTimeUntilStartText(): String {
        return when {
            minutesUntilStart == 0 -> "Starting now"
            minutesUntilStart == 1 -> "Starts in 1 minute"
            minutesUntilStart < 60 -> "Starts in $minutesUntilStart minutes"
            else -> "Starts in ${minutesUntilStart / 60}h ${minutesUntilStart % 60}m"
        }
    }
    
    /**
     * Check if warm window should be active (3 minutes before)
     */
    fun shouldShowWarmWindow(): Boolean {
        return minutesUntilStart in 1..3
    }
}

@Parcelize
data class SessionInfo(
    val currentSession: CurrentSession?,
    val nextSession: NextSession?,
    val warmWindowActive: Boolean,
    val warmWindowStartsIn: Int?       // Minutes until warm window starts
) : Parcelable {
    
    /**
     * Check if there's an active class happening now
     */
    fun hasActiveClass(): Boolean {
        return currentSession?.isActive == true
    }
    
    /**
     * Check if there's a next class coming up
     */
    fun hasNextClass(): Boolean {
        return nextSession != null
    }
    
    /**
     * Get warm window message
     */
    fun getWarmWindowMessage(): String? {
        return when {
            warmWindowActive -> "Warm window active - Collecting data for attendance"
            warmWindowStartsIn != null && warmWindowStartsIn in 1..10 -> 
                "Warm window starts in $warmWindowStartsIn minutes"
            else -> null
        }
    }
}

// Response models for API calls

@Parcelize
data class TimetableResponse(
    val success: Boolean,
    val student: StudentInfo?,
    val timetable: Map<String, List<TimetableSlot>>?,
    val error: String?
) : Parcelable {
    
    fun toStudentTimetable(): StudentTimetable? {
        if (!success || student == null || timetable == null) return null
        return StudentTimetable(student, timetable)
    }
}

@Parcelize
data class SessionInfoResponse(
    val success: Boolean,
    val currentSession: CurrentSession?,
    val nextSession: NextSession?,
    val warmWindowActive: Boolean,
    val warmWindowStartsIn: Int?,
    val error: String?
) : Parcelable {
    
    fun toSessionInfo(): SessionInfo? {
        if (!success) return null
        return SessionInfo(currentSession, nextSession, warmWindowActive, warmWindowStartsIn)
    }
}
