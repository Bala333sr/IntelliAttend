package com.intelliattend.student.network

import com.intelliattend.student.data.model.*
import retrofit2.Response
import retrofit2.http.*

/**
 * Retrofit API interface for IntelliAttend server communication
 */
interface ApiService {
    
    /**
     * Student Authentication Endpoints
     */
    @POST("student/login")
    suspend fun studentLogin(@Body request: LoginRequest): Response<LoginResponse>

    @POST("student/register")
    suspend fun studentRegister(@Body request: StudentRegistrationRequest): Response<ApiResponse>

    @POST("student/logout")
    suspend fun studentLogout(@Header("Authorization") token: String): Response<ApiResponse>
    
    @GET("student/profile")
    suspend fun getStudentProfile(@Header("Authorization") token: String): Response<StudentProfileResponse>
    
    /**
     * Attendance Endpoints
     */
    @POST("attendance/scan")
    suspend fun submitAttendance(
        @Header("Authorization") token: String,
        @Body request: AttendanceRequest
    ): Response<AttendanceResponse>
    
    @GET("attendance/history")
    suspend fun getAttendanceHistory(
        @Header("Authorization") token: String,
        @Query("limit") limit: Int = 50
    ): Response<AttendanceHistoryResponse>
    
    /**
     * Session Management
     */
    @GET("session/current")
    suspend fun getCurrentSessions(@Header("Authorization") token: String): Response<SessionsResponse>
    
    @GET("session/{sessionId}/status")
    suspend fun getSessionStatus(
        @Header("Authorization") token: String,
        @Path("sessionId") sessionId: Int
    ): Response<SessionStatusResponse>
    
    /**
     * Device Management
     */
    @POST("device/register")
    suspend fun registerDevice(
        @Header("Authorization") token: String,
        @Body deviceInfo: DeviceRegistrationRequest
    ): Response<ApiResponse>
    
    @PUT("device/update")
    suspend fun updateDevice(
        @Header("Authorization") token: String,
        @Body deviceInfo: DeviceInfo
    ): Response<ApiResponse>
}

/**
 * Common API response wrapper
 */
data class ApiResponse(
    val success: Boolean,
    val message: String,
    val error: String? = null
)

/**
 * Student profile response
 */
data class StudentProfileResponse(
    val success: Boolean,
    val student: Student?,
    val error: String? = null
)

/**
 * Attendance history response
 */
data class AttendanceHistoryResponse(
    val success: Boolean,
    val records: List<AttendanceHistoryRecord>,
    val error: String? = null
)

/**
 * Sessions response
 */
data class SessionsResponse(
    val success: Boolean,
    val sessions: List<ActiveSession>,
    val error: String? = null
)

/**
 * Session status response
 */
data class SessionStatusResponse(
    val success: Boolean,
    val session: SessionStatus?,
    val error: String? = null
)

/**
 * Student registration request
 */
data class StudentRegistrationRequest(
    val studentCode: String,
    val firstName: String,
    val lastName: String,
    val email: String,
    val phoneNumber: String?,
    val program: String,
    val yearOfStudy: Int?,
    val password: String
)

/**
 * Device registration request
 */
data class DeviceRegistrationRequest(
    val deviceUuid: String,
    val deviceName: String,
    val deviceType: String,
    val deviceModel: String,
    val osVersion: String,
    val appVersion: String
)