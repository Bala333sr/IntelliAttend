package com.intelliattend.mobilemodule.collector

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.ConnectivityManager
import android.net.wifi.ScanResult
import android.net.wifi.WifiInfo
import android.net.wifi.WifiManager
import androidx.core.app.ActivityCompat
import com.intelliattend.mobilemodule.model.WiFiData
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.InetAddress
import java.net.NetworkInterface

/**
 * WiFi data collector for network information
 */
class WiFiDataCollector(private val context: Context) {
    
    private val wifiManager: WifiManager = 
        context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
    
    private val connectivityManager: ConnectivityManager =
        context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    
    /**
     * Get current WiFi connection information
     */
    suspend fun getCurrentWiFiData(): Result<WiFiData> = withContext(Dispatchers.IO) {
        try {
            if (!hasLocationPermission()) {
                return@withContext Result.failure(Exception("Location permission required for WiFi scanning"))
            }
            
            if (!wifiManager.isWifiEnabled) {
                return@withContext Result.failure(Exception("WiFi is disabled"))
            }
            
            val wifiInfo = wifiManager.connectionInfo
            
            if (wifiInfo.networkId == -1) {
                return@withContext Result.failure(Exception("Not connected to WiFi"))
            }
            
            val ssid = wifiInfo.ssid?.replace("\"", "") ?: "Unknown"
            val bssid = wifiInfo.bssid ?: ""
            val rssi = wifiInfo.rssi
            val frequency = wifiInfo.frequency
            val ipAddress = getLocalIpAddress()
            
            val wifiData = WiFiData(
                ssid = ssid,
                bssid = bssid,
                rssi = rssi,
                ipAddress = ipAddress,
                frequency = frequency
            )
            
            Result.success(wifiData)
            
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Scan for available WiFi networks
     */
    suspend fun scanAvailableNetworks(): Result<List<WiFiData>> = withContext(Dispatchers.IO) {
        try {
            if (!hasLocationPermission()) {
                return@withContext Result.failure(Exception("Location permission required for WiFi scanning"))
            }
            
            if (!wifiManager.isWifiEnabled) {
                return@withContext Result.failure(Exception("WiFi is disabled"))
            }
            
            val scanResults = wifiManager.scanResults
            val wifiNetworks = scanResults.map { scanResult ->
                WiFiData(
                    ssid = scanResult.SSID,
                    bssid = scanResult.BSSID,
                    rssi = scanResult.level,
                    ipAddress = "", // Not connected, so no IP
                    frequency = scanResult.frequency
                )
            }
            
            Result.success(wifiNetworks)
            
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get local IP address of the device
     */
    private fun getLocalIpAddress(): String {
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            for (networkInterface in interfaces) {
                val addresses = networkInterface.inetAddresses
                for (address in addresses) {
                    if (!address.isLoopbackAddress && address is InetAddress) {
                        val hostAddress = address.hostAddress
                        if (hostAddress != null && !hostAddress.contains(":")) {
                            return hostAddress
                        }
                    }
                }
            }
        } catch (e: Exception) {
            // Fallback to alternative method
            try {
                val wifiInfo = wifiManager.connectionInfo
                val ipInt = wifiInfo.ipAddress
                return String.format(
                    "%d.%d.%d.%d",
                    ipInt and 0xff,
                    ipInt shr 8 and 0xff,
                    ipInt shr 16 and 0xff,
                    ipInt shr 24 and 0xff
                )
            } catch (ex: Exception) {
                return "0.0.0.0"
            }
        }
        return "0.0.0.0"
    }
    
    /**
     * Check if device is connected to internet
     */
    fun isConnectedToInternet(): Boolean {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
               capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
    }
    
    /**
     * Check if connected to WiFi (vs mobile data)
     */
    fun isConnectedToWiFi(): Boolean {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        
        return capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
    }
    
    /**
     * Get signal strength description
     */
    fun getSignalStrengthDescription(rssi: Int): String {
        return when {
            rssi >= -50 -> "Excellent"
            rssi >= -60 -> "Good"
            rssi >= -70 -> "Fair"
            rssi >= -80 -> "Weak"
            else -> "Very Weak"
        }
    }
    
    /**
     * Check location permission for WiFi scanning
     */
    private fun hasLocationPermission(): Boolean {
        return ActivityCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED ||
        ActivityCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    /**
     * Check if specific SSID is in range
     */
    suspend fun isSSIDInRange(targetSSID: String): Result<Boolean> {
        return try {
            val scanResult = scanAvailableNetworks()
            if (scanResult.isSuccess) {
                val networks = scanResult.getOrThrow()
                val found = networks.any { it.ssid == targetSSID }
                Result.success(found)
            } else {
                scanResult.map { false }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}