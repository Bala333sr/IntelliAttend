package com.intelliattend.student.network

import com.intelliattend.student.data.model.PresenceStatus
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path

/**
 * Retrofit API interface for presence tracking service
 */
interface PresenceApiService {
    
    /**
     * Get presence status for a specific student
     */
    @GET("presence/{studentId}")
    suspend fun getPresenceStatus(@Path("studentId") studentId: String): Response<PresenceStatus>
    
    /**
     * Get presence status for all students
     */
    @GET("presence/all")
    suspend fun getAllPresenceStatus(): Response<Map<String, PresenceStatus>>
}