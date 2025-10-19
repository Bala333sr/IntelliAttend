package com.intelliattend.student.data.preferences

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.google.gson.Gson
import com.intelliattend.student.data.model.Student

/**
 * Secure preferences manager for storing sensitive data
 * Uses EncryptedSharedPreferences for enhanced security
 */
class AppPreferences(context: Context) {
    
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()
    
    private val sharedPreferences: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        PREFS_NAME,
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    
    private val gson = Gson()
    
    companion object {
        private const val PREFS_NAME = "intelliattend_secure_prefs"
        
        // Keys
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_STUDENT_DATA = "student_data"
        private const val KEY_DEVICE_ID = "device_id"
        private const val KEY_BIOMETRIC_ENABLED = "biometric_enabled"
        private const val KEY_FIRST_LOGIN = "first_login"
        private const val KEY_LAST_ATTENDANCE = "last_attendance"
        private const val KEY_BASE_URL = "base_url"
        private const val KEY_LAST_LOGGED_IN_EMAIL = "last_logged_in_email"
        private const val KEY_LAST_LOGGED_IN_PASSWORD = "last_logged_in_password"
    }
    
    // Access Token Management
    var accessToken: String?
        get() = sharedPreferences.getString(KEY_ACCESS_TOKEN, null)
        set(value) = sharedPreferences.edit().putString(KEY_ACCESS_TOKEN, value).apply()
    
    // Student Data
    var studentData: Student?
        get() {
            val json = sharedPreferences.getString(KEY_STUDENT_DATA, null)
            return json?.let { gson.fromJson(it, Student::class.java) }
        }
        set(value) {
            val json = value?.let { gson.toJson(it) }
            sharedPreferences.edit().putString(KEY_STUDENT_DATA, json).apply()
        }
    
    // Last Logged In Credentials
    var lastLoggedInEmail: String?
        get() = sharedPreferences.getString(KEY_LAST_LOGGED_IN_EMAIL, null)
        set(value) = sharedPreferences.edit().putString(KEY_LAST_LOGGED_IN_EMAIL, value).apply()

    var lastLoggedInPassword: String?
        get() = sharedPreferences.getString(KEY_LAST_LOGGED_IN_PASSWORD, null)
        set(value) = sharedPreferences.edit().putString(KEY_LAST_LOGGED_IN_PASSWORD, value).apply()
    
    // Device ID
    var deviceId: String?
        get() = sharedPreferences.getString(KEY_DEVICE_ID, null)
        set(value) = sharedPreferences.edit().putString(KEY_DEVICE_ID, value).apply()
    
    // Biometric Settings
    var isBiometricEnabled: Boolean
        get() = sharedPreferences.getBoolean(KEY_BIOMETRIC_ENABLED, true) // Default to true for security
        set(value) = sharedPreferences.edit().putBoolean(KEY_BIOMETRIC_ENABLED, value).apply()
    
    // First Login Flag
    var isFirstLogin: Boolean
        get() = sharedPreferences.getBoolean(KEY_FIRST_LOGIN, true)
        set(value) = sharedPreferences.edit().putBoolean(KEY_FIRST_LOGIN, value).apply()
    
    // Last Attendance Timestamp
    var lastAttendanceTime: Long
        get() = sharedPreferences.getLong(KEY_LAST_ATTENDANCE, 0L)
        set(value) = sharedPreferences.edit().putLong(KEY_LAST_ATTENDANCE, value).apply()
    
    // Base URL for API
    var baseUrl: String
        get() = sharedPreferences.getString(KEY_BASE_URL, "") ?: ""
        set(value) = sharedPreferences.edit().putString(KEY_BASE_URL, value).apply()
    
    // Check if user is logged in
    fun isLoggedIn(): Boolean {
        return !accessToken.isNullOrEmpty() && studentData != null
    }
    
    // Clear all data (logout)
    fun clearAll() {
        sharedPreferences.edit().clear().apply()
    }
    
    // Clear only session data (keep settings)
    fun clearSession() {
        sharedPreferences.edit()
            .remove(KEY_ACCESS_TOKEN)
            .remove(KEY_STUDENT_DATA)
            .apply()
    }
}