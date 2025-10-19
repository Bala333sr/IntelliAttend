package com.intelliattend.student.utils

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.net.wifi.WifiManager
import android.os.Build
import android.provider.Settings
import androidx.core.content.ContextCompat
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import kotlinx.coroutines.suspendCancellableCoroutine
import java.util.UUID
import kotlin.coroutines.resume

/**
 * Utilities for device enforcement - WiFi and GPS validation
 */
object DeviceEnforcementUtils {
    
    /**
     * Get device UUID (persistent across app reinstalls)
     */
    fun getDeviceUUID(context: Context): String {
        val androidId = Settings.Secure.getString(
            context.contentResolver,
            Settings.Secure.ANDROID_ID
        )
        return UUID.nameUUIDFromBytes(androidId.toByteArray()).toString()
    }
    
    /**
     * Get device information
     */
    fun getDeviceInfo(context: Context, appVersion: String): DeviceInfo {
        return DeviceInfo(
            device_uuid = getDeviceUUID(context),
            device_name = "${Build.MANUFACTURER} ${Build.MODEL}",
            device_type = "android",
            device_model = Build.MODEL,
            os_version = "Android ${Build.VERSION.RELEASE}",
            app_version = appVersion
        )
    }
    
    /**
     * Get WiFi information (SSID and BSSID)
     */
    fun getWiFiInfo(context: Context): WiFiInfo? {
        try {
            val wifiManager = context.applicationContext
                .getSystemService(Context.WIFI_SERVICE) as? WifiManager
                ?: return null
            
            if (!wifiManager.isWifiEnabled) {
                return null
            }
            
            val wifiInfo = wifiManager.connectionInfo ?: return null
            
            // Remove quotes from SSID
            val ssid = wifiInfo.ssid?.replace("\"", "") ?: return null
            
            // Check if actually connected
            if (ssid == "<unknown ssid>" || ssid.isBlank()) {
                return null
            }
            
            val bssid = wifiInfo.bssid ?: return null
            
            val signalStrength = WifiManager.calculateSignalLevel(wifiInfo.rssi, 5)
            
            return WiFiInfo(
                ssid = ssid,
                bssid = bssid,
                signal_strength = signalStrength
            )
        } catch (e: Exception) {
            e.printStackTrace()
            return null
        }
    }
    
    /**
     * Get current GPS location
     */
    suspend fun getCurrentLocation(context: Context): GPSInfo? {
        return suspendCancellableCoroutine { continuation ->
            if (ContextCompat.checkSelfPermission(
                    context,
                    Manifest.permission.ACCESS_FINE_LOCATION
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                continuation.resume(null)
                return@suspendCancellableCoroutine
            }
            
            val fusedLocationClient: FusedLocationProviderClient =
                LocationServices.getFusedLocationProviderClient(context)
            
            fusedLocationClient.lastLocation
                .addOnSuccessListener { location: Location? ->
                    if (location != null) {
                        continuation.resume(
                            GPSInfo(
                                latitude = location.latitude,
                                longitude = location.longitude,
                                accuracy = location.accuracy,
                                timestamp = location.time
                            )
                        )
                    } else {
                        // Try to get fresh location
                        requestFreshLocation(context, fusedLocationClient) { gpsInfo ->
                            continuation.resume(gpsInfo)
                        }
                    }
                }
                .addOnFailureListener {
                    continuation.resume(null)
                }
        }
    }
    
    /**
     * Request fresh GPS location (if last location is null or stale)
     */
    private fun requestFreshLocation(
        context: Context,
        fusedLocationClient: FusedLocationProviderClient,
        callback: (GPSInfo?) -> Unit
    ) {
        try {
            if (ContextCompat.checkSelfPermission(
                    context,
                    Manifest.permission.ACCESS_FINE_LOCATION
                ) == PackageManager.PERMISSION_GRANTED
            ) {
                fusedLocationClient.getCurrentLocation(
                    com.google.android.gms.location.LocationRequest.PRIORITY_HIGH_ACCURACY,
                    null
                ).addOnSuccessListener { location ->
                    if (location != null) {
                        callback(
                            GPSInfo(
                                latitude = location.latitude,
                                longitude = location.longitude,
                                accuracy = location.accuracy,
                                timestamp = location.time
                            )
                        )
                    } else {
                        callback(null)
                    }
                }.addOnFailureListener {
                    callback(null)
                }
            } else {
                callback(null)
            }
        } catch (e: Exception) {
            e.printStackTrace()
            callback(null)
        }
    }
    
    /**
     * Check permission status
     */
    fun getPermissionStatus(context: Context): PermissionStatus {
        return PermissionStatus(
            wifi = ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.ACCESS_WIFI_STATE
            ) == PackageManager.PERMISSION_GRANTED,
            gps = ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) == PackageManager.PERMISSION_GRANTED,
            bluetooth = ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.BLUETOOTH
            ) == PackageManager.PERMISSION_GRANTED
        )
    }
}

/**
 * Data classes for device enforcement
 */
data class DeviceInfo(
    val device_uuid: String,
    val device_name: String,
    val device_type: String,
    val device_model: String,
    val os_version: String,
    val app_version: String
)

data class WiFiInfo(
    val ssid: String,
    val bssid: String,
    val signal_strength: Int
)

data class GPSInfo(
    val latitude: Double,
    val longitude: Double,
    val accuracy: Float,
    val timestamp: Long
)

data class PermissionStatus(
    val wifi: Boolean,
    val gps: Boolean,
    val bluetooth: Boolean
)
