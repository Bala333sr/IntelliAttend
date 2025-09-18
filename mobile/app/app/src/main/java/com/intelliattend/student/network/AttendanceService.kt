package com.intelliattend.student.network

import com.intelliattend.student.network.model.AttendanceRequest
import com.intelliattend.student.network.model.AttendanceResponse
import com.intelliattend.student.network.model.NetworkAttendanceRequest
import com.intelliattend.student.network.model.NetworkAttendanceResponse
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

/**
 * Retrofit service for attendance-related API calls
 */
interface AttendanceService {
    
    @POST("api/attendance/mark")
    suspend fun markAttendance(@Body request: NetworkAttendanceRequest): NetworkAttendanceResponse
    
    @POST("api/attendance/submit")
    suspend fun submitAttendance(@Body request: AttendanceRequest): AttendanceResponse
    
    @GET("api/attendance/history")
    suspend fun getAttendanceHistory(@Query("limit") limit: Int): List<AttendanceHistoryRecord>
    
    @GET("api/sessions/active")
    suspend fun getActiveSessions(): List<ActiveSession>
    
}
