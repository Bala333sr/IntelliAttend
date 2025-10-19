package com.intelliattend.student.data.repository

import android.content.Context
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.data.model.*
import com.intelliattend.student.network.ApiService
import com.intelliattend.student.network.TodayTimetableResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.time.LocalTime

/**
 * Repository for managing timetable data
 */
class TimetableRepository(
    private val apiService: ApiService,
    private val context: Context
) {
    
    // Cache preferences for timetable data
    private val cachePrefs = context.getSharedPreferences("timetable_cache", Context.MODE_PRIVATE)
    
    // Use centralized, secure preferences for auth token
    private val appPreferences = IntelliAttendApplication.getInstance().getAppPreferences()
    
    /**
     * Get student's complete timetable
     */
    suspend fun getTimetable(): Result<StudentTimetable> = withContext(Dispatchers.IO) {
        return@withContext try {
            val token = getAuthToken()
            if (token == null) {
                Result.failure(Exception("Not authenticated"))
            } else {
                val response = apiService.getStudentTimetable("Bearer $token")
                
                if (response.isSuccessful && response.body() != null) {
                    val envelope = response.body()!!
                    
                    if (envelope.success && envelope.data != null) {
                        val studentInfo = envelope.data.student
                        val timetableMap = envelope.data.timetable
                        if (studentInfo != null && timetableMap != null) {
                            val ttResponse = com.intelliattend.student.data.model.TimetableResponse(
                                success = true,
                                student = studentInfo,
                                timetable = timetableMap,
                                error = null
                            )
                            // Cache timetable locally
                            cacheTimetable(ttResponse)
                            Result.success(ttResponse.toStudentTimetable()!!)
                        } else {
                            Result.failure(Exception("Invalid timetable data"))
                        }
                    } else {
                        Result.failure(Exception(envelope.error ?: "Failed to fetch timetable"))
                    }
                } else {
                    // Try to load from cache
                    val cachedTimetable = getCachedTimetable()
                    if (cachedTimetable != null) {
                        Result.success(cachedTimetable)
                    } else {
                        Result.failure(Exception("Failed to fetch timetable: ${response.message()}"))
                    }
                }
            }
        } catch (e: Exception) {
            // Try to load from cache on error
            val cachedTimetable = getCachedTimetable()
            if (cachedTimetable != null) {
                Result.success(cachedTimetable)
            } else {
                Result.failure(e)
            }
        }
    }
    
    /**
     * Get today's schedule for the current student
     */
    suspend fun getTodaySchedule(): Result<List<ClassSession>> = withContext(Dispatchers.IO) {
        return@withContext try {
            val token = getAuthToken()
            if (token == null) {
                Result.failure(Exception("Not authenticated"))
            } else {
                val response = apiService.getTodayTimetable("Bearer $token")
                
                if (response.isSuccessful && response.body() != null) {
                    val todayResponse = response.body()!!
                    
                    if (todayResponse.success && todayResponse.data != null) {
                        val sessions = todayResponse.data.sessions.map { session ->
                            // Parse time strings to LocalTime
                            val startTime = try {
                                LocalTime.parse(session.start_time)
                            } catch (e: Exception) {
                                LocalTime.MIN
                            }
                            
                            val endTime = try {
                                LocalTime.parse(session.end_time)
                            } catch (e: Exception) {
                                LocalTime.MAX
                            }
                            
                            ClassSession(
                                id = session.id,
                                subjectName = session.subject_name,
                                subjectCode = session.subject_code,
                                teacherName = session.teacher_name ?: "TBA",
                                roomNumber = session.room_number,
                                startTime = startTime,
                                endTime = endTime,
                                status = calculateStatus(startTime, endTime),
                                icon = getSubjectIcon(session.subject_code)
                            )
                        }
                        
                        Result.success(sessions)
                    } else {
                        Result.failure(Exception(todayResponse.error ?: "Failed to fetch today's schedule"))
                    }
                } else {
                    Result.failure(Exception("Failed to fetch today's schedule: ${response.message()}"))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get current and next session information
     */
    suspend fun getCurrentSession(): Result<SessionInfo> = withContext(Dispatchers.IO) {
        return@withContext try {
            val token = getAuthToken()
            if (token == null) {
                Result.failure(Exception("Not authenticated"))
            } else {
                val response = apiService.getCurrentSession("Bearer $token")
                
                if (response.isSuccessful && response.body() != null) {
                    val sessionResponse = response.body()!!
                    
                    if (sessionResponse.success) {
                        val sessionInfo = sessionResponse.toSessionInfo()
                        if (sessionInfo != null) {
                            Result.success(sessionInfo)
                        } else {
                            Result.failure(Exception("Invalid session data"))
                        }
                    } else {
                        Result.failure(Exception(sessionResponse.error ?: "Failed to fetch session"))
                    }
                } else {
                    Result.failure(Exception("Failed to fetch session: ${response.message()}"))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get auth token from SharedPreferences
     */
    private fun getAuthToken(): String? {
        return appPreferences.accessToken
    }
    
    /**
     * Cache timetable data locally using Gson
     */
    private fun cacheTimetable(timetableResponse: com.intelliattend.student.data.model.TimetableResponse) {
        try {
            val gson = com.google.gson.Gson()
            val json = gson.toJson(timetableResponse)
            cachePrefs.edit().putString("cached_timetable", json).apply()
            cachePrefs.edit().putLong("timetable_cache_time", System.currentTimeMillis()).apply()
        } catch (e: Exception) {
            android.util.Log.e("TimetableRepository", "Error caching timetable", e)
        }
    }
    
    /**
     * Get cached timetable if available
     */
    private fun getCachedTimetable(): StudentTimetable? {
        return try {
            val json = cachePrefs.getString("cached_timetable", null)
            if (json != null) {
                val gson = com.google.gson.Gson()
                val timetableResponse = gson.fromJson(
                    json, 
                    com.intelliattend.student.data.model.TimetableResponse::class.java
                )
                timetableResponse.toStudentTimetable()
            } else {
                null
            }
        } catch (e: Exception) {
            android.util.Log.e("TimetableRepository", "Error loading cached timetable", e)
            null
        }
    }
    
    /**
     * Check if cached timetable is still valid (cached within last 24 hours)
     */
    fun isCacheValid(): Boolean {
        val cacheTime = cachePrefs.getLong("timetable_cache_time", 0)
        val currentTime = System.currentTimeMillis()
        val dayInMillis = 24 * 60 * 60 * 1000
        return (currentTime - cacheTime) < dayInMillis
    }
    
    /**
     * Clear cached timetable
     */
    fun clearCache() {
        cachePrefs.edit().remove("cached_timetable").apply()
        cachePrefs.edit().remove("timetable_cache_time").apply()
    }
    
    /**
     * Calculate class status based on current time
     */
    private fun calculateStatus(startTime: LocalTime, endTime: LocalTime): ClassStatus {
        val now = LocalTime.now()
        
        return when {
            now < startTime -> {
                val minutesUntilStart = java.time.Duration.between(now, startTime).toMinutes()
                when {
                    minutesUntilStart > 60 -> ClassStatus.UpcomingLong("Starts in ${formatTime(minutesUntilStart)}")
                    minutesUntilStart > 15 -> ClassStatus.Upcoming("Starts in $minutesUntilStart minutes")
                    minutesUntilStart > 5 -> ClassStatus.StartingSoon("Starting soon - $minutesUntilStart minutes")
                    else -> ClassStatus.StartingNow("Starting now!")
                }
            }
            now >= startTime && now <= endTime -> {
                ClassStatus.InProgress("In progress")
            }
            else -> ClassStatus.Completed("Completed")
        }
    }
    
    /**
     * Format time duration
     */
    private fun formatTime(minutes: Long): String {
        return when {
            minutes > 60 -> "${minutes / 60}h ${minutes % 60}m"
            else -> "${minutes}m"
        }
    }
    
    /**
     * Get subject icon based on subject code
     */
    private fun getSubjectIcon(subjectCode: String): String {
        return when {
            subjectCode.contains("CS", ignoreCase = true) || 
            subjectCode.contains("Algorithm", ignoreCase = true) -> "💻"
            subjectCode.contains("DB", ignoreCase = true) || 
            subjectCode.contains("Database", ignoreCase = true) -> "🗄️"
            subjectCode.contains("ML", ignoreCase = true) || 
            subjectCode.contains("Machine", ignoreCase = true) -> "🤖"
            subjectCode.contains("Network", ignoreCase = true) -> "🌐"
            else -> "📚"
        }
    }
}