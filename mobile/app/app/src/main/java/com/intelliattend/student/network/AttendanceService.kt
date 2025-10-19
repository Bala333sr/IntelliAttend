package com.intelliattend.student.network

import com.intelliattend.student.network.model.AttendanceRequest
import com.intelliattend.student.network.model.AttendanceResponse
import com.intelliattend.student.network.model.NetworkAttendanceRequest
import com.intelliattend.student.network.model.NetworkAttendanceResponse
import com.intelliattend.student.network.model.WarmAttendanceRequest
import com.intelliattend.student.network.model.WarmAttendanceResponse
import com.intelliattend.student.network.model.AttendanceMarkRequest
import com.intelliattend.student.network.model.AttendanceMarkResponse
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.Query

/**
 * Retrofit service for attendance-related API calls
 */
interface AttendanceService {
    
    /**
     * NEW: Mark attendance with multi-factor verification
     * Requires authentication token
     */
    @POST("api/attendance/mark")
    suspend fun markAttendanceWithVerification(
        @Header("Authorization") authToken: String,
        @Body request: AttendanceMarkRequest
    ): AttendanceMarkResponse
    
    /**
     * LEGACY: Old attendance marking endpoint
     */
    @POST("api/attendance/mark")
    suspend fun markAttendance(@Body request: NetworkAttendanceRequest): NetworkAttendanceResponse
    
    @POST("api/attendance/submit")
    suspend fun submitAttendance(@Body request: AttendanceRequest): AttendanceResponse

    @POST("api/attendance/scan")
    suspend fun submitWarmAttendance(@Body request: WarmAttendanceRequest): WarmAttendanceResponse
    
    @GET("api/attendance/history")
    suspend fun getAttendanceHistory(@Query("limit") limit: Int): List<AttendanceHistoryRecord>
    
    @GET("api/sessions/active")
    suspend fun getActiveSessions(): List<ActiveSession>

    // Timetable (today) for auto warm scheduling
    @GET("api/student/timetable/today")
    suspend fun getTodaysTimetable(): List<TimetableItem>
    
}

/**
 * Simple timetable item aligned with backend keys
 */
data class TimetableItem(
    val id: Int,
    val section: String?,
    val day_of_week: String?,
    val slot_number: Int?,
    val slot_type: String?,
    val start_time: String?,
    val end_time: String?,
    val subject_code: String?,
    val subject_name: String?,
    val faculty_name: String?,
    val room_number: String?
)
