package com.intelliattend.student.utils

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.content.ContextCompat

/**
 * Utility class for managing app permissions
 */
object PermissionUtils {
    
    /**
     * All permissions required by the app
     */
    val REQUIRED_PERMISSIONS = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        // Android 12+ permissions
        arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.ACCESS_WIFI_STATE,
            Manifest.permission.CHANGE_WIFI_STATE,
            Manifest.permission.ACCESS_NETWORK_STATE,
            Manifest.permission.USE_BIOMETRIC,
            Manifest.permission.INTERNET,
            Manifest.permission.WAKE_LOCK,
            Manifest.permission.BLUETOOTH_CONNECT,
            Manifest.permission.BLUETOOTH_SCAN
        )
    } else {
        // Pre-Android 12 permissions
        arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.ACCESS_WIFI_STATE,
            Manifest.permission.CHANGE_WIFI_STATE,
            Manifest.permission.ACCESS_NETWORK_STATE,
            Manifest.permission.USE_FINGERPRINT,
            Manifest.permission.USE_BIOMETRIC,
            Manifest.permission.INTERNET,
            Manifest.permission.WAKE_LOCK,
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN
        )
    }
    
    /**
     * Critical permissions that are absolutely required for core functionality
     */
    val CRITICAL_PERMISSIONS = arrayOf(
        Manifest.permission.CAMERA,
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.USE_BIOMETRIC
    )
    
    /**
     * Check if all required permissions are granted
     */
    fun areAllPermissionsGranted(context: Context): Boolean {
        return REQUIRED_PERMISSIONS.all { permission ->
            ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED
        }
    }
    
    /**
     * Check if critical permissions are granted
     */
    fun areCriticalPermissionsGranted(context: Context): Boolean {
        return CRITICAL_PERMISSIONS.all { permission ->
            ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED
        }
    }
    
    /**
     * Get list of missing permissions
     */
    fun getMissingPermissions(context: Context): List<String> {
        return REQUIRED_PERMISSIONS.filter { permission ->
            ContextCompat.checkSelfPermission(context, permission) != PackageManager.PERMISSION_GRANTED
        }
    }
    
    /**
     * Get list of missing critical permissions
     */
    fun getMissingCriticalPermissions(context: Context): List<String> {
        return CRITICAL_PERMISSIONS.filter { permission ->
            ContextCompat.checkSelfPermission(context, permission) != PackageManager.PERMISSION_GRANTED
        }
    }
    
    /**
     * Check specific permission groups
     */
    fun isCameraPermissionGranted(context: Context): Boolean {
        return ContextCompat.checkSelfPermission(
            context, 
            Manifest.permission.CAMERA
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    fun isLocationPermissionGranted(context: Context): Boolean {
        return ContextCompat.checkSelfPermission(
            context, 
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED ||
        ContextCompat.checkSelfPermission(
            context, 
            Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    fun isBiometricPermissionGranted(context: Context): Boolean {
        return ContextCompat.checkSelfPermission(
            context, 
            Manifest.permission.USE_BIOMETRIC
        ) == PackageManager.PERMISSION_GRANTED ||
        ContextCompat.checkSelfPermission(
            context, 
            Manifest.permission.USE_FINGERPRINT
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    fun isBluetoothPermissionGranted(context: Context): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(
                context, 
                Manifest.permission.BLUETOOTH_CONNECT
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            ContextCompat.checkSelfPermission(
                context, 
                Manifest.permission.BLUETOOTH
            ) == PackageManager.PERMISSION_GRANTED
        }
    }
    
    /**
     * Get user-friendly permission descriptions
     */
    fun getPermissionDescription(permission: String): String {
        return when (permission) {
            Manifest.permission.CAMERA -> 
                "Camera access is required to scan QR codes for attendance verification."
            
            Manifest.permission.ACCESS_FINE_LOCATION, 
            Manifest.permission.ACCESS_COARSE_LOCATION -> 
                "Location access is required to verify you are physically present in the classroom."
            
            Manifest.permission.USE_BIOMETRIC,
            Manifest.permission.USE_FINGERPRINT -> 
                "Biometric authentication is required to verify your identity for attendance."
            
            Manifest.permission.ACCESS_WIFI_STATE,
            Manifest.permission.CHANGE_WIFI_STATE,
            Manifest.permission.ACCESS_NETWORK_STATE -> 
                "WiFi access is required to verify network connectivity and location."
            
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN,
            Manifest.permission.BLUETOOTH_CONNECT,
            Manifest.permission.BLUETOOTH_SCAN -> 
                "Bluetooth access is required to detect nearby devices for proximity verification."
            
            else -> "This permission is required for app functionality."
        }
    }
    
    /**
     * Get permission group title
     */
    fun getPermissionGroupTitle(permission: String): String {
        return when (permission) {
            Manifest.permission.CAMERA -> "Camera"
            Manifest.permission.ACCESS_FINE_LOCATION, 
            Manifest.permission.ACCESS_COARSE_LOCATION -> "Location"
            Manifest.permission.USE_BIOMETRIC,
            Manifest.permission.USE_FINGERPRINT -> "Biometric Authentication"
            Manifest.permission.ACCESS_WIFI_STATE,
            Manifest.permission.CHANGE_WIFI_STATE,
            Manifest.permission.ACCESS_NETWORK_STATE -> "Network Access"
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN,
            Manifest.permission.BLUETOOTH_CONNECT,
            Manifest.permission.BLUETOOTH_SCAN -> "Bluetooth Access"
            else -> "App Permission"
        }
    }
    
    /**
     * Check if permission is critical for app functionality
     */
    fun isPermissionCritical(permission: String): Boolean {
        return permission in CRITICAL_PERMISSIONS
    }
    
    /**
     * Get permissions needed for each feature
     */
    fun getQRScannerPermissions(): Array<String> {
        return arrayOf(Manifest.permission.CAMERA)
    }
    
    fun getLocationPermissions(): Array<String> {
        return arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
    }
    
    fun getBiometricPermissions(): Array<String> {
        return arrayOf(
            Manifest.permission.USE_BIOMETRIC,
            Manifest.permission.USE_FINGERPRINT
        )
    }
    
    fun getBluetoothPermissions(): Array<String> {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            arrayOf(
                Manifest.permission.BLUETOOTH_CONNECT,
                Manifest.permission.BLUETOOTH_SCAN
            )
        } else {
            arrayOf(
                Manifest.permission.BLUETOOTH,
                Manifest.permission.BLUETOOTH_ADMIN
            )
        }
    }
}