package com.intelliattend.student.utils

import android.Manifest
import android.app.Application
import android.bluetooth.BluetoothAdapter
import android.content.Context
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.location.LocationManager
import android.net.wifi.WifiManager
import android.os.Build
import android.os.SystemClock
import android.provider.Settings
import androidx.biometric.BiometricManager
import androidx.core.content.ContextCompat
import com.intelliattend.student.BuildConfig
import com.intelliattend.student.IntelliAttendApplication

/**
 * Collects a comprehensive, privacy-respecting device fingerprint for registration and debugging.
 * Mirrors the approach of financial apps: stable device UUID, environment signals, and app context.
 */
data class DeviceFingerprint(
    val deviceUuid: String,
    val androidId: String?,
    val appDeviceId: String?,
    val manufacturer: String,
    val brand: String,
    val model: String,
    val osVersion: String,
    val sdkInt: Int,
    val isEmulator: Boolean,
    val isRooted: Boolean,
    val isDebuggable: Boolean,
    val developerOptionsEnabled: Boolean,
    val biometricCapable: Boolean,
    val bluetoothEnabled: Boolean,
    val wifiEnabled: Boolean,
    val locationEnabled: Boolean,
    val appVersion: String,
    val uptimeSeconds: Long
)

object DeviceFingerprintCollector {
    fun collect(context: Context): DeviceFingerprint {
        val app = IntelliAttendApplication.getInstance()
        val prefs = app.getAppPreferences()

        val androidId = try {
            Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
        } catch (_: Exception) { null }

        val deviceUuid = try {
            DeviceEnforcementUtils.getDeviceUUID(context)
        } catch (_: Exception) {
            DeviceUtils.generateDeviceId()
        }

        val biometricCapable = try {
            val bm = BiometricManager.from(context)
            val canAuth = bm.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            canAuth == BiometricManager.BIOMETRIC_SUCCESS
        } catch (_: Exception) { false }

        val bluetoothEnabled = BluetoothAdapter.getDefaultAdapter()?.isEnabled == true
        val wifiEnabled = try {
            val wm = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as? WifiManager
            wm?.isWifiEnabled == true
        } catch (_: Exception) { false }

        val locationEnabled = try {
            val lm = context.getSystemService(Context.LOCATION_SERVICE) as? LocationManager
            (lm?.isProviderEnabled(LocationManager.GPS_PROVIDER) == true) ||
            (lm?.isProviderEnabled(LocationManager.NETWORK_PROVIDER) == true)
        } catch (_: Exception) { false }

        val isDebuggable = try {
            (context.applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE) != 0
        } catch (_: Exception) { false }

        val developerOptionsEnabled = try {
            Settings.Global.getInt(context.contentResolver, Settings.Global.DEVELOPMENT_SETTINGS_ENABLED, 0) == 1
        } catch (_: Exception) { false }

        val isEmulator = isProbablyEmulator()
        val isRooted = isProbablyRooted()

        val hasFineLocationPerm = ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        val uptimeSeconds = SystemClock.elapsedRealtime() / 1000

        return DeviceFingerprint(
            deviceUuid = deviceUuid,
            androidId = androidId,
            appDeviceId = prefs.deviceId,
            manufacturer = Build.MANUFACTURER ?: "Unknown",
            brand = Build.BRAND ?: "Unknown",
            model = Build.MODEL ?: "Unknown",
            osVersion = Build.VERSION.RELEASE ?: "Unknown",
            sdkInt = Build.VERSION.SDK_INT,
            isEmulator = isEmulator,
            isRooted = isRooted,
            isDebuggable = isDebuggable,
            developerOptionsEnabled = developerOptionsEnabled,
            biometricCapable = biometricCapable,
            bluetoothEnabled = bluetoothEnabled,
            wifiEnabled = wifiEnabled,
            locationEnabled = locationEnabled && hasFineLocationPerm,
            appVersion = BuildConfig.VERSION_NAME,
            uptimeSeconds = uptimeSeconds
        )
    }

    private fun isProbablyEmulator(): Boolean {
        val buildFingerprint = Build.FINGERPRINT?.lowercase() ?: ""
        val buildModel = Build.MODEL?.lowercase() ?: ""
        val product = Build.PRODUCT?.lowercase() ?: ""
        val manufacturer = Build.MANUFACTURER?.lowercase() ?: ""

        return buildFingerprint.contains("generic") ||
                buildFingerprint.contains("unknown") ||
                buildModel.contains("google_sdk") ||
                buildModel.contains("emulator") ||
                buildModel.contains("android sdk built for x86") ||
                manufacturer.contains("genymotion") ||
                product.contains("sdk") ||
                product.contains("emulator") ||
                product.contains("simulator")
    }

    private fun isProbablyRooted(): Boolean {
        val tags = Build.TAGS
        if (tags != null && tags.contains("test-keys")) return true
        val paths = arrayOf(
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su"
        )
        return paths.any { path ->
            try { java.io.File(path).exists() } catch (_: Exception) { false }
        }
    }
}