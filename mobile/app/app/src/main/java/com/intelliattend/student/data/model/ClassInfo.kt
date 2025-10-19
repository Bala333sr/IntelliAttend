package com.intelliattend.student.data.model

/**
 * Data class representing class information
 */
data class ClassInfo(
    val className: String,
    val facultyName: String,
    val startTime: String,
    val endTime: String,
    val timeUntilStart: String = "",
    val room: String = "",
    val isActive: Boolean = false
)