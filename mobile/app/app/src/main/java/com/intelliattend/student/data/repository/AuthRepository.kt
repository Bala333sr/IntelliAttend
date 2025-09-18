package com.intelliattend.student.data.repository

import com.intelliattend.student.data.model.LoginRequest
import com.intelliattend.student.data.model.LoginResponse
import com.intelliattend.student.data.model.Student
import com.intelliattend.student.data.preferences.AppPreferences
import com.intelliattend.student.network.ApiClient
import com.intelliattend.student.network.DeviceRegistrationRequest
import com.intelliattend.student.utils.DeviceUtils
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Repository for authentication-related operations
 */
class AuthRepository(
    private val apiClient: ApiClient,
    private val appPreferences: AppPreferences
) {
    
    companion object {
        // Default test user credentials
        private const val DEFAULT_EMAIL = "alice.williams@student.edu"
        private const val DEFAULT_PASSWORD = "student123"
    }
    
    /**
     * Auto-login with default test user credentials
     * Bypasses login screen for testing purposes
     */
    suspend fun autoLoginWithDefaultUser(): Result<Student> = withContext(Dispatchers.IO) {
        return@withContext login(DEFAULT_EMAIL, DEFAULT_PASSWORD)
    }
    
    /**
     * Login student with email and password
     */
    suspend fun login(email: String, password: String): Result<Student> = withContext(Dispatchers.IO) {
        try {
            val request = LoginRequest(email, password)
            val response = apiClient.apiService.studentLogin(request)
            
            println("🔍 Android Login Debug - Response code: ${response.code()}")
            println("🔍 Android Login Debug - Response successful: ${response.isSuccessful}")
            
            if (response.isSuccessful) {
                val loginResponse = response.body()
                println("🔍 Android Login Debug - Response body: $loginResponse")
                println("🔍 Android Login Debug - Success field: ${loginResponse?.success}")
                println("🔍 Android Login Debug - Student field: ${loginResponse?.student}")
                println("🔍 Android Login Debug - AccessToken field: ${loginResponse?.accessToken}")
                
                if (loginResponse?.success == true && loginResponse.student != null && loginResponse.accessToken != null) {
                    println("✅ Android Login Debug - All conditions met, storing data")
                    // Store authentication data
                    appPreferences.accessToken = loginResponse.accessToken
                    appPreferences.studentData = loginResponse.student
                    appPreferences.isFirstLogin = false
                    
                    // Register device if needed
                    registerDeviceIfNeeded()
                    
                    Result.success(loginResponse.student)
                } else {
                    println("❌ Android Login Debug - Condition failed, error: ${loginResponse?.error}")
                    Result.failure(Exception(loginResponse?.error ?: "Login failed"))
                }
            } else {
                println("❌ Android Login Debug - Response not successful: ${response.code()}")
                Result.failure(Exception("Network error: ${response.code()}"))
            }
        } catch (e: Exception) {
            println("❌ Android Login Debug - Exception: ${e.message}")
            e.printStackTrace()
            Result.failure(e)
        }
    }
    
    /**
     * Logout current user
     */
    suspend fun logout(): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            val token = appPreferences.accessToken
            if (token != null) {
                val response = apiClient.apiService.studentLogout("Bearer $token")
                // Clear local data regardless of server response
                appPreferences.clearSession()
                
                if (response.isSuccessful) {
                    Result.success(Unit)
                } else {
                    // Still success locally even if server call failed
                    Result.success(Unit)
                }
            } else {
                appPreferences.clearSession()
                Result.success(Unit)
            }
        } catch (e: Exception) {
            // Clear local data even on error
            appPreferences.clearSession()
            Result.success(Unit)
        }
    }
    
    /**
     * Check if user is currently logged in or can auto-login with default user
     */
    fun isLoggedIn(): Boolean {
        return appPreferences.isLoggedIn()
    }
    
    /**
     * Check if we should use auto-login for testing
     */
    fun shouldAutoLogin(): Boolean {
        return !appPreferences.isLoggedIn()
    }
    
    /**
     * Get current student data
     */
    fun getCurrentStudent(): Student? {
        return appPreferences.studentData
    }
    
    /**
     * Get current access token
     */
    fun getAccessToken(): String? {
        return appPreferences.accessToken
    }
    
    /**
     * Refresh user profile from server
     */
    suspend fun refreshProfile(): Result<Student> = withContext(Dispatchers.IO) {
        try {
            val token = appPreferences.accessToken
            if (token == null) {
                return@withContext Result.failure(Exception("No access token"))
            }
            
            val response = apiClient.apiService.getStudentProfile("Bearer $token")
            
            if (response.isSuccessful) {
                val profileResponse = response.body()
                if (profileResponse?.success == true && profileResponse.student != null) {
                    appPreferences.studentData = profileResponse.student
                    Result.success(profileResponse.student)
                } else {
                    Result.failure(Exception(profileResponse?.error ?: "Failed to get profile"))
                }
            } else {
                if (response.code() == 401) {
                    // Token expired, logout
                    appPreferences.clearSession()
                    Result.failure(Exception("Session expired"))
                } else {
                    Result.failure(Exception("Network error: ${response.code()}"))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Register device with server if not already registered
     */
    private suspend fun registerDeviceIfNeeded() {
        try {
            val token = appPreferences.accessToken ?: return
            val deviceId = appPreferences.deviceId
            
            if (deviceId == null) {
                // Generate and store device ID
                val newDeviceId = DeviceUtils.generateDeviceId()
                appPreferences.deviceId = newDeviceId
                
                // Register with server
                val deviceInfo = DeviceRegistrationRequest(
                    deviceUuid = newDeviceId,
                    deviceName = DeviceUtils.getDeviceName(),
                    deviceType = "android",
                    deviceModel = DeviceUtils.getDeviceModel(),
                    osVersion = DeviceUtils.getAndroidVersion(),
                    appVersion = DeviceUtils.getAppVersion()
                )
                
                apiClient.apiService.registerDevice("Bearer $token", deviceInfo)
            }
        } catch (e: Exception) {
            // Device registration is not critical, continue silently
        }
    }
}