package com.intelliattend.student.network

import com.intelliattend.student.data.model.*
import com.intelliattend.student.network.model.*
import retrofit2.Response
import retrofit2.http.*

/**
 * Retrofit API interface for IntelliAttend server communication
 */
interface ApiService {
    
    /**
     * Student Authentication Endpoints
     */
    @POST("student/mobile-login")
    suspend fun studentLogin(@Body request: LoginRequest): Response<MobileLoginResponse>
    
    /**
     * Enhanced login with device enforcement (WiFi + GPS validation)
     */
    @POST("mobile/v2/login")
    suspend fun enhancedLogin(@Body request: EnhancedLoginRequest): Response<EnhancedLoginResponse>

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
        @Body request: com.intelliattend.student.data.model.AttendanceRequest
    ): Response<com.intelliattend.student.data.model.AttendanceResponse>
    
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
        @Body deviceInfo: com.intelliattend.student.data.model.DeviceInfo
    ): Response<ApiResponse>
    
    /**
     * Device Status and Enforcement
     */
    @GET("mobile/v2/device-status")
    suspend fun getDeviceStatus(@Header("Authorization") token: String): Response<DeviceStatusResponse>
    
    @POST("mobile/v2/device-switch-request")
    suspend fun requestDeviceSwitch(
        @Header("Authorization") token: String,
        @Body request: DeviceSwitchRequest
    ): Response<DeviceSwitchResponse>
    
    /**
     * Timetable Endpoints
     */
    @GET("student/timetable")
    suspend fun getStudentTimetable(
        @Header("Authorization") token: String
    ): Response<WeeklyTimetableEnvelope>
    
    @GET("student/timetable/today")
    suspend fun getTodayTimetable(
        @Header("Authorization") token: String
    ): Response<TodayTimetableResponse>
    
    @GET("student/current-session")
    suspend fun getCurrentSession(
        @Header("Authorization") token: String
    ): Response<SessionInfoResponse>
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
 * Mobile-friendly login response
 */
data class MobileLoginResponse(
    val success: Boolean?,
    val status: String?,
    val message: String?,
    val error: String?,
    val accessToken: String?,
    val token: String?,
    val authToken: String?,
    val jwt: String?,
    val student: Student?,
    val user: Student?,
    val authenticated: Boolean?,
    val login: Boolean?,
    val isLoggedIn: Boolean?
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

/**
 * Today's timetable response
 */
data class TodayTimetableResponse(
    val success: Boolean,
    val data: TodayTimetableData?,
    val message: String?,
    val error: String?
)

data class TodayTimetableData(
    val date: String,
    val day_of_week: String,
    val sessions: List<TodayTimetableSession>,
    val student_info: TodayStudentInfo
)

data class TodayTimetableSession(
    val id: Int,
    val subject_id: Int,
    val subject_name: String,
    val subject_code: String,
    val short_name: String,
    val teacher_name: String?,
    val room_number: String?,
    val start_time: String,  // HH:MM:SS format
    val end_time: String,    // HH:MM:SS format
    val section: String
)

data class TodayStudentInfo(
    val student_id: String,
    val name: String,
    val section: String,
    val program: String
)

/**
 * Weekly timetable envelope (server returns in data{})
 */
data class WeeklyTimetableEnvelope(
    val success: Boolean,
    val data: WeeklyTimetableData?,
    val message: String?,
    val error: String?
)

data class WeeklyTimetableData(
    val student: com.intelliattend.student.data.model.StudentInfo?,
    val timetable: Map<String, List<com.intelliattend.student.data.model.TimetableSlot>>?
)
