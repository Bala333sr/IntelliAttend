package com.intelliattend.student.data.repository

import com.intelliattend.student.data.model.LoginRequest
import com.intelliattend.student.data.model.LoginResponse
import com.intelliattend.student.data.model.Student
import com.intelliattend.student.data.preferences.AppPreferences
import com.intelliattend.student.network.ApiClient
import com.intelliattend.student.network.DeviceRegistrationRequest
import com.intelliattend.student.network.model.EnhancedLoginRequest
import com.intelliattend.student.network.model.DeviceStatusData
import com.intelliattend.student.presence.PresenceManager
import com.intelliattend.student.utils.DeviceUtils
import com.intelliattend.student.utils.DeviceEnforcementUtils
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
        // No default credentials for security
    }
    
    /**
     * Auto-login with default test user credentials
     * Bypasses login screen for testing purposes
     */
    suspend fun autoLoginWithDefaultUser(): Result<Student> = withContext(Dispatchers.IO) {
        // Return failure for security - no default credentials
        return@withContext Result.failure(Exception("Auto-login disabled for security"))
    }
    
    /**
     * Enhanced login with device enforcement (WiFi + GPS validation)
     */
    suspend fun enhancedLogin(
        email: String,
        password: String,
        deviceInfo: com.intelliattend.student.utils.DeviceInfo,
        wifiInfo: com.intelliattend.student.utils.WiFiInfo?,
        gpsInfo: com.intelliattend.student.utils.GPSInfo?,
        permissionStatus: com.intelliattend.student.utils.PermissionStatus
    ): Result<Pair<Student, DeviceStatusData?>> = withContext(Dispatchers.IO) {
        try {
            val request = EnhancedLoginRequest(
                email = email,
                password = password,
                device_info = deviceInfo,
                wifi_info = wifiInfo,
                gps_info = gpsInfo,
                permissions = permissionStatus
            )
            
            val response = apiClient.apiService.enhancedLogin(request)
            
            println("🔍 Android Enhanced Login Debug - Response code: ${response.code()}")
            println("🔍 Android Enhanced Login Debug - Response successful: ${response.isSuccessful}")
            
            if (response.isSuccessful) {
                val loginResponse = response.body()
                println("🔍 Android Enhanced Login Debug - Response body: $loginResponse")
                
                // Extract data from nested structure
                val data = loginResponse?.data
                val accessToken = data?.access_token ?: data?.token
                val student = data?.student ?: data?.user
                val deviceStatus = data?.device_status
                
                println("🔍 Android Enhanced Login Debug - Extracted - token: ${accessToken != null}, student: ${student != null}")
                
                if (loginResponse?.success == true && student != null && accessToken != null) {
                    println("✅ Android Enhanced Login Debug - Login successful, storing data")
                    
                    // Store authentication data
                    appPreferences.accessToken = accessToken
                    appPreferences.studentData = student
                    appPreferences.isFirstLogin = false
                    
                    if (deviceStatus?.can_mark_attendance == false) {
                        return@withContext Result.failure(Exception(deviceStatus.message ?: "Device not authorized"))
                    }

                    // Start presence tracking only if device is active
                    if (deviceStatus?.is_active == true && deviceStatus.can_mark_attendance) {
                        try {
                            PresenceManager.getInstance().startTracking()
                        } catch (e: Exception) {
                            println("⚠️  Android Enhanced Login Debug - Failed to start presence tracking: ${e.message}")
                        }
                    }
                    
                    Result.success(Pair(student, deviceStatus))
                } else {
                    println("❌ Android Enhanced Login Debug - Login failed")
                    val errorMessage = loginResponse?.error ?: loginResponse?.message ?: "Login failed"
                    Result.failure(Exception(errorMessage))
                }
            } else {
                println("❌ Android Enhanced Login Debug - Response not successful: ${response.code()}")
                val errorBody = response.errorBody()?.string()
                println("❌ Android Enhanced Login Debug - Error body: $errorBody")
                Result.failure(Exception("Network error: ${response.code()}"))
            }
        } catch (e: Exception) {
            println("❌ Android Enhanced Login Debug - Exception: ${e.message}")
            e.printStackTrace()
            Result.failure(e)
        }
    }
    
    /**
     * Login student with email and password (legacy method)
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
                
                // Handle multiple response formats from mobile-login endpoint
                val isSuccess = loginResponse?.success == true || 
                               loginResponse?.status == "success" || 
                               loginResponse?.authenticated == true || 
                               loginResponse?.login == true || 
                               loginResponse?.isLoggedIn == true
                
                val token = loginResponse?.accessToken ?: 
                           loginResponse?.token ?: 
                           loginResponse?.authToken ?: 
                           loginResponse?.jwt
                
                val student = loginResponse?.student ?: loginResponse?.user
                
                println("🔍 Android Login Debug - Success field: $isSuccess")
                println("🔍 Android Login Debug - Student field: $student")
                println("🔍 Android Login Debug - AccessToken field: $token")
                
                if (isSuccess && student != null && token != null) {
                    println("✅ Android Login Debug - All conditions met, storing data")
                    // Store authentication data
                    appPreferences.accessToken = token
                    appPreferences.studentData = student
                    appPreferences.isFirstLogin = false
                    
                    // Register device if needed
                    registerDeviceIfNeeded()
                    
                    // Start presence tracking
                    try {
                        PresenceManager.getInstance().startTracking()
                    } catch (e: Exception) {
                        println("⚠️  Android Login Debug - Failed to start presence tracking: ${e.message}")
                    }
                    
                    Result.success(student)
                } else {
                    println("❌ Android Login Debug - Condition failed")
                    val errorMessage = loginResponse?.error ?: 
                                     loginResponse?.message ?: 
                                     "Login failed"
                    Result.failure(Exception(errorMessage))
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
            // Stop presence tracking
            try {
                PresenceManager.getInstance().stopTracking()
            } catch (e: Exception) {
                println("⚠️  Android Logout Debug - Failed to stop presence tracking: ${e.message}")
            }
            
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
     * Get device status from server
     */
    suspend fun getDeviceStatus(): Result<DeviceStatusData> = withContext(Dispatchers.IO) {
        try {
            val token = appPreferences.accessToken
            if (token == null) {
                return@withContext Result.failure(Exception("No access token"))
            }
            
            val response = apiClient.apiService.getDeviceStatus("Bearer $token")
            
            if (response.isSuccessful) {
                val deviceStatusResponse = response.body()
                if (deviceStatusResponse?.success == true && deviceStatusResponse.device_status != null) {
                    Result.success(deviceStatusResponse.device_status)
                } else {
                    Result.failure(Exception(deviceStatusResponse?.error ?: "Failed to get device status"))
                }
            } else {
                Result.failure(Exception("Network error: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun requestDeviceSwitch(
        deviceInfo: com.intelliattend.student.utils.DeviceInfo,
        wifiInfo: com.intelliattend.student.utils.WiFiInfo?,
        gpsInfo: com.intelliattend.student.utils.GPSInfo?
    ): Result<DeviceSwitchResponse> = withContext(Dispatchers.IO) {
        try {
            val token = appPreferences.accessToken
            if (token == null) {
                return@withContext Result.failure(Exception("No access token"))
            }

            val request = DeviceSwitchRequest(
                new_device_info = deviceInfo,
                wifi_info = wifiInfo,
                gps_info = gpsInfo
            )

            val response = apiClient.apiService.requestDeviceSwitch("Bearer $token", request)

            if (response.isSuccessful) {
                val switchResponse = response.body()
                if (switchResponse?.success == true) {
                    Result.success(switchResponse)
                } else {
                    Result.failure(Exception(switchResponse?.error ?: "Failed to switch device"))
                }
            } else {
                Result.failure(Exception("Network error: ${response.code()}"))
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
                val newDeviceId = DeviceEnforcementUtils.getDeviceUUID(IntelliAttendApplication.getContext())
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

    /**
     * Immediately register the device with backend, using current fingerprint info.
     */
    suspend fun registerDeviceNow(): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val token = appPreferences.accessToken
            if (token.isNullOrEmpty()) {
                return@withContext Result.failure(Exception("No access token; login required"))
            }
            val deviceUuid = DeviceEnforcementUtils.getDeviceUUID(IntelliAttendApplication.getContext())
            appPreferences.deviceId = deviceUuid
            val deviceInfo = DeviceRegistrationRequest(
                deviceUuid = deviceUuid,
                deviceName = DeviceUtils.getDeviceName(),
                deviceType = "android",
                deviceModel = DeviceUtils.getDeviceModel(),
                osVersion = DeviceUtils.getAndroidVersion(),
                appVersion = DeviceUtils.getAppVersion()
            )
            val response = apiClient.apiService.registerDevice("Bearer $token", deviceInfo)
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(true)
            } else {
                val msg = response.body()?.error ?: response.body()?.message ?: "Registration failed"
                Result.failure(Exception(msg))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
