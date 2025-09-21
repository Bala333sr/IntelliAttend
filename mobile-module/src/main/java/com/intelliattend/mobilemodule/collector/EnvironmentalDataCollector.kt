package com.intelliattend.mobilemodule.collector

import android.content.Context
import com.intelliattend.mobilemodule.model.BluetoothData
import com.intelliattend.mobilemodule.model.GPSData
import com.intelliattend.mobilemodule.model.WiFiData
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch

/**
 * Unified environmental data collector that combines WiFi, Bluetooth, and GPS data collection
 */
class EnvironmentalDataCollector(context: Context) {
    
    private val wifiCollector = WiFiDataCollector(context)
    private val bluetoothCollector = BluetoothDataCollector(context)
    private val gpsCollector = GPSDataCollector(context)
    private val coroutineScope = CoroutineScope(Dispatchers.Main + Job())
    
    /**
     * Data class to hold all environmental data
     */
    data class EnvironmentalData(
        val wifiData: WiFiData? = null,
        val bluetoothDevices: List<BluetoothData> = emptyList(),
        val gpsData: GPSData? = null
    )
    
    /**
     * Callback interface for environmental data updates
     */
    interface EnvironmentalDataCallback {
        fun onDataUpdated(data: EnvironmentalData)
        fun onError(error: Exception)
    }
    
    /**
     * Start collecting all environmental data
     */
    fun startCollecting(callback: EnvironmentalDataCallback) {
        // Start WiFi data collection
        coroutineScope.launch {
            try {
                val wifiResult = wifiCollector.getCurrentWiFiData()
                if (wifiResult.isSuccess) {
                    callback.onDataUpdated(
                        EnvironmentalData(
                            wifiData = wifiResult.getOrNull()
                        )
                    )
                }
            } catch (e: Exception) {
                callback.onError(e)
            }
        }
        
        // Start Bluetooth scanning
        bluetoothCollector.startScanning { devices ->
            callback.onDataUpdated(
                EnvironmentalData(
                    bluetoothDevices = devices
                )
            )
        }
        
        // Start GPS data collection
        coroutineScope.launch {
            try {
                val gpsResult = gpsCollector.getCurrentLocation()
                if (gpsResult.isSuccess) {
                    callback.onDataUpdated(
                        EnvironmentalData(
                            gpsData = gpsResult.getOrNull()
                        )
                    )
                }
            } catch (e: Exception) {
                callback.onError(e)
            }
        }
    }
    
    /**
     * Stop collecting all environmental data
     */
    fun stopCollecting() {
        bluetoothCollector.stopScanning()
    }
    
    /**
     * Get current WiFi data
     */
    suspend fun getCurrentWiFiData() = wifiCollector.getCurrentWiFiData()
    
    /**
     * Scan for available WiFi networks
     */
    suspend fun scanAvailableNetworks() = wifiCollector.scanAvailableNetworks()
    
    /**
     * Get current GPS location
     */
    suspend fun getCurrentLocation() = gpsCollector.getCurrentLocation()
    
    /**
     * Get last known GPS location
     */
    suspend fun getLastKnownLocation() = gpsCollector.getLastKnownLocation()
    
    /**
     * Start Bluetooth scanning
     */
    fun startBluetoothScanning(onDevicesUpdated: (List<BluetoothData>) -> Unit) {
        bluetoothCollector.startScanning(onDevicesUpdated)
    }
    
    /**
     * Stop Bluetooth scanning
     */
    fun stopBluetoothScanning() {
        bluetoothCollector.stopScanning()
    }
    
    /**
     * Get paired Bluetooth devices
     */
    fun getPairedBluetoothDevices() = bluetoothCollector.getPairedDevices()
    
    /**
     * Check if device is connected to internet
     */
    fun isConnectedToInternet() = wifiCollector.isConnectedToInternet()
    
    /**
     * Check if connected to WiFi
     */
    fun isConnectedToWiFi() = wifiCollector.isConnectedToWiFi()
}