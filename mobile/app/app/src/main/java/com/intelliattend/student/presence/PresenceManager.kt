package com.intelliattend.student.presence

import android.util.Log
import android.widget.Toast
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.data.model.Student

/**
 * Manager for handling presence tracking lifecycle
 */
class PresenceManager {
    
    private val presenceTrackingService = PresenceTrackingService()
    private var isTracking = false
    private var currentStudent: Student? = null
    
    companion object {
        private const val TAG = "PresenceManager"
        @Volatile
        private var INSTANCE: PresenceManager? = null
        
        fun getInstance(): PresenceManager {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: PresenceManager().also { INSTANCE = it }
            }
        }
    }
    
    init {
        // Set up notification callback
        presenceTrackingService.setNotificationCallback { studentId, status, timestamp ->
            handlePresenceNotification(studentId, status, timestamp)
        }
    }
    
    /**
     * Handle presence notification
     */
    private fun handlePresenceNotification(studentId: String, status: String, timestamp: String) {
        val appContext = IntelliAttendApplication.getContext()
        val currentStudentId = currentStudent?.let { "STU${it.studentId}" }
        
        // Only show notifications for the current student
        if (currentStudentId == studentId) {
            val message = if (status == "online") {
                "You are now online"
            } else {
                "You are now offline"
            }
            
            // Show toast notification on main thread
            android.os.Handler(android.os.Looper.getMainLooper()).post {
                Toast.makeText(appContext, message, Toast.LENGTH_SHORT).show()
            }
            
            Log.d(TAG, "Presence notification: $message")
        }
    }
    
    /**
     * Start presence tracking for the current student
     */
    fun startTracking() {
        if (isTracking) {
            Log.d(TAG, "Presence tracking already started")
            return
        }
        
        try {
            val app = IntelliAttendApplication.getInstance()
            val student = app.getAuthRepository().getCurrentStudent()
            
            if (student != null) {
                currentStudent = student
                presenceTrackingService.connect(student)
                isTracking = true
                Log.d(TAG, "Started presence tracking for student: ${student.studentId}")
            } else {
                Log.w(TAG, "Cannot start tracking - no student data available")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start presence tracking", e)
        }
    }
    
    /**
     * Stop presence tracking
     */
    fun stopTracking() {
        if (!isTracking) {
            Log.d(TAG, "Presence tracking already stopped")
            return
        }
        
        try {
            presenceTrackingService.disconnect()
            isTracking = false
            currentStudent = null
            Log.d(TAG, "Stopped presence tracking")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to stop presence tracking", e)
        }
    }
    
    /**
     * Check if presence tracking is active
     */
    fun isTracking(): Boolean {
        return isTracking && presenceTrackingService.isConnected()
    }
    
    /**
     * Get connection status
     */
    fun isConnected(): Boolean {
        return presenceTrackingService.isConnected()
    }
}