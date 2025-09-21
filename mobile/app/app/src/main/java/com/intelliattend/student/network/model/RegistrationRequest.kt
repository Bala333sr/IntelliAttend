package com.intelliattend.student.network.model

/**
 * Registration request model for student self-registration
 */
data class RegistrationRequest(
    val studentCode: String,
    val firstName: String,
    val lastName: String,
    val email: String,
    val phoneNumber: String?,
    val program: String,
    val yearOfStudy: Int?,
    val password: String
)