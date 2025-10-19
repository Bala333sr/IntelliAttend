package com.intelliattend.student.network.model

import com.intelliattend.student.network.DeviceRegistrationRequest

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
    val password: String,
    val deviceInfo: DeviceRegistrationRequest? = null
)