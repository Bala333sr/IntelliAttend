package com.intelliattend.mobilemodule.utils

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.content.Context
import android.content.pm.PackageManager
import android.net.wifi.WifiManager
import android.os.Build
import androidx.core.app.ActivityCompat
import com.intelliattend.mobilemodule.model.DeviceInfo
import java.util.*

/**
 * Utility class for device information and permission checking
 */
class DeviceUtils {
    
    /**
     * Get comprehensive device information
     */
    fun getDeviceInfo(context: Context): DeviceInfo {
        return DeviceInfo(
            deviceId = getDeviceId(context),
            deviceName = getDeviceName(),
            osVersion = getOSVersion(),
            appVersion = getAppVersion(context),
            deviceModel = getDeviceModel(),
            manufacturer = getManufacturer()
        )
    }
    
    /**
     * Get unique device ID
     */
    private fun getDeviceId(context: Context): String {
        return try {
            // Use Android ID as device identifier
            android.provider.Settings.Secure.getString(
                context.contentResolver,
                android.provider.Settings.Secure.ANDROID_ID
            ) ?: UUID.randomUUID().toString()
        } catch (e: Exception) {
            UUID.randomUUID().toString()
        }
    }
    
    /**
     * Get device name
     */
    private fun getDeviceName(): String {
        return try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N_MR1) {
                BluetoothAdapter.getDefaultAdapter()?.name ?: Build.MODEL
            } else {
                Build.MODEL
            }
        } catch (e: Exception) {
            Build.MODEL
        }
    }
    
    /**
     * Get OS version
     */
    private fun getOSVersion(): String {
        return "Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})"
    }
    
    /**
     * Get app version
     */
    private fun getAppVersion(context: Context): String {
        return try {
            val packageInfo = context.packageManager.getPackageInfo(context.packageName, 0)
            packageInfo.versionName ?: "1.0"
        } catch (e: Exception) {
            "1.0"
        }
    }
    
    /**
     * Get device model
     */
    private fun getDeviceModel(): String {
        return Build.MODEL
    }
    
    /**
     * Get manufacturer
     */
    private fun getManufacturer(): String {
        return Build.MANUFACTURER
    }
    
    /**
     * Check if all required permissions are granted
     */
    fun checkPermissions(context: Context): Map<String, Boolean> {
        val permissions = arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN
        )
        
        val permissionMap = mutableMapOf<String, Boolean>()
        
        permissions.forEach { permission ->
            permissionMap[permission] = ActivityCompat.checkSelfPermission(
                context,
                permission
            ) == PackageManager.PERMISSION_GRANTED
        }
        
        // Add Bluetooth permissions for Android 12+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val bluetoothPermissions = arrayOf(
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.BLUETOOTH_CONNECT
            )
            
            bluetoothPermissions.forEach { permission ->
                permissionMap[permission] = ActivityCompat.checkSelfPermission(
                    context,
                    permission
                ) == PackageManager.PERMISSION_GRANTED
            }
        }
        
        return permissionMap
    }
    
    /**
     * Check if WiFi is enabled
     */
    fun isWiFiEnabled(context: Context): Boolean {
        val wifiManager = context.getSystemService(Context.WIFI_SERVICE) as WifiManager
        return wifiManager.isWifiEnabled
    }
    
    /**
     * Check if Bluetooth is enabled
     */
    fun isBluetoothEnabled(): Boolean {
        val bluetoothAdapter = BluetoothAdapter.getDefaultAdapter()
        return bluetoothAdapter?.isEnabled == true
    }
}