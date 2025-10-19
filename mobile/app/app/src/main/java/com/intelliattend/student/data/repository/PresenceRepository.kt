package com.intelliattend.student.data.repository

import com.intelliattend.student.data.model.PresenceStatus
import com.intelliattend.student.network.ApiClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Repository for presence-related operations
 */
class PresenceRepository(
    private val apiClient: ApiClient
) {
    
    /**
     * Get presence status for a student
     */
    suspend fun getPresenceStatus(studentId: String): Result<PresenceStatus> = withContext(Dispatchers.IO) {
        try {
            val response = apiClient.presenceApiService.getPresenceStatus(studentId)
            
            if (response.isSuccessful) {
                val presenceStatus = response.body()
                if (presenceStatus != null) {
                    Result.success(presenceStatus)
                } else {
                    Result.failure(Exception("Empty response from server"))
                }
            } else {
                Result.failure(Exception("Network error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}