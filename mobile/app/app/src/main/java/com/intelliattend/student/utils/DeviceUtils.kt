package com.intelliattend.student.utils

import android.content.Context
import android.os.Build
import com.intelliattend.student.data.model.DeviceInfo
import java.util.*

/**
 * Utility class for device information
 */
object DeviceUtils {
    
    /**
     * Get complete device information
     */
    fun getDeviceInfo(context: Context): DeviceInfo {
        return DeviceInfo(
            deviceId = generateDeviceId(),
            deviceName = getDeviceName(),
            osVersion = getAndroidVersion(),
            appVersion = getAppVersion(),
            deviceModel = getDeviceModel(),
            manufacturer = getManufacturer()
        )
    }
    
    /**
     * Generate unique device identifier
     */
    fun generateDeviceId(): String {
        return UUID.randomUUID().toString()
    }
    
    /**
     * Get device name
     */
    fun getDeviceName(): String {
        return "${Build.MANUFACTURER} ${Build.MODEL}"
    }
    
    /**
     * Get device model
     */
    fun getDeviceModel(): String {
        return Build.MODEL ?: "Unknown"
    }
    
    /**
     * Get Android version
     */
    fun getAndroidVersion(): String {
        return Build.VERSION.RELEASE ?: "Unknown"
    }
    
    /**
     * Get app version (placeholder - should be implemented with BuildConfig)
     */
    fun getAppVersion(): String {
        return "1.0.0" // This should be from BuildConfig.VERSION_NAME
    }
    
    /**
     * Get device manufacturer
     */
    fun getManufacturer(): String {
        return Build.MANUFACTURER ?: "Unknown"
    }
    
    /**
     * Get device brand
     */
    fun getBrand(): String {
        return Build.BRAND ?: "Unknown"
    }
    
    /**
     * Get Android API level
     */
    fun getApiLevel(): Int {
        return Build.VERSION.SDK_INT
    }
    
    /**
     * Check if device supports biometric authentication
     */
    fun isBiometricCapable(): Boolean {
        return Build.VERSION.SDK_INT >= Build.VERSION_CODES.M
    }
}