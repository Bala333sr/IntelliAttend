package com.intelliattend.student.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize
import java.time.LocalTime

/**
 * Data models for today's swipeable class cards feature
 */

@Parcelize
data class ClassSession(
    val id: Int,
    val subjectName: String,
    val subjectCode: String,
    val teacherName: String,
    val roomNumber: String?,
    val startTime: LocalTime,
    val endTime: LocalTime,
    val status: ClassStatus,
    val icon: String? = null  // Emoji or icon identifier
) : Parcelable

@Parcelize
data class ClassPage(
    val classes: List<ClassSession>  // Max 2 classes per page
) : Parcelable

sealed class ClassStatus : Parcelable {
    @Parcelize
    data class UpcomingLong(val message: String) : ClassStatus()
    
    @Parcelize
    data class Upcoming(val message: String) : ClassStatus()
    
    @Parcelize
    data class StartingSoon(val message: String) : ClassStatus()
    
    @Parcelize
    data class StartingNow(val message: String) : ClassStatus()
    
    @Parcelize
    data class InProgress(val message: String) : ClassStatus()
    
    @Parcelize
    data class Completed(val message: String) : ClassStatus()
}

data class TodayClassesUiState(
    val isLoading: Boolean = false,
    val classes: List<ClassSession> = emptyList(),
    val classPages: List<ClassPage> = emptyList(),
    val currentPage: Int = 0,
    val totalPages: Int = 0,
    val error: String? = null,
    val isAllCompleted: Boolean = false,
    val isEmpty: Boolean = false
)