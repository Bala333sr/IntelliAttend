package com.intelliattend.student.data.model

/**
 * Data class representing student presence status
 */
data class PresenceStatus(
    val studentId: String,
    val status: String, // "online" or "offline"
    val lastSeen: String? // ISO timestamp
)