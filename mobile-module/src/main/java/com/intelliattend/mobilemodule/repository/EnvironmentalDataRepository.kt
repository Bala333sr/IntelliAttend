package com.intelliattend.mobilemodule.repository

import android.content.Context
import com.intelliattend.mobilemodule.collector.BluetoothDataCollector
import com.intelliattend.mobilemodule.collector.GPSDataCollector
import com.intelliattend.mobilemodule.collector.WiFiDataCollector
import com.intelliattend.mobilemodule.model.BluetoothData
import com.intelliattend.mobilemodule.model.GPSData
import com.intelliattend.mobilemodule.model.WiFiData
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * Repository for managing environmental data from WiFi, Bluetooth, and GPS
 */
class EnvironmentalDataRepository(context: Context) {
    
    private val wifiCollector = WiFiDataCollector(context)
    private val bluetoothCollector = BluetoothDataCollector(context)
    private val gpsCollector = GPSDataCollector(context)
    
    // State flows for reactive data updates
    private val _wifiData = MutableStateFlow<WiFiData?>(null)
    val wifiData: StateFlow<WiFiData?> = _wifiData
    
    private val _bluetoothDevices = MutableStateFlow<List<BluetoothData>>(emptyList())
    val bluetoothDevices: StateFlow<List<BluetoothData>> = _bluetoothDevices
    
    private val _gpsData = MutableStateFlow<GPSData?>(null)
    val gpsData: StateFlow<GPSData?> = _gpsData
    
    /**
     * Refresh WiFi data
     */
    suspend fun refreshWiFiData() {
        val result = wifiCollector.getCurrentWiFiData()
        if (result.isSuccess) {
            _wifiData.value = result.getOrNull()
        }
    }
    
    /**
     * Refresh Bluetooth devices
     */
    fun refreshBluetoothDevices() {
        bluetoothCollector.startScanning { devices ->
            _bluetoothDevices.value = devices
        }
    }
    
    /**
     * Refresh GPS data
     */
    suspend fun refreshGPSData() {
        val result = gpsCollector.getCurrentLocation()
        if (result.isSuccess) {
            _gpsData.value = result.getOrNull()
        }
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
    fun getPairedBluetoothDevices(): List<BluetoothData> {
        return bluetoothCollector.getPairedDevices()
    }
    
    /**
     * Check if a specific Bluetooth device is in range
     */
    fun isBluetoothDeviceInRange(deviceAddress: String): Boolean {
        return bluetoothCollector.isDeviceInRange(deviceAddress)
    }
    
    /**
     * Get RSSI value for a specific Bluetooth device
     */
    fun getBluetoothDeviceRssi(deviceAddress: String): Int? {
        return bluetoothCollector.getDeviceRssi(deviceAddress)
    }
    
    /**
     * Check if connected to internet
     */
    fun isConnectedToInternet(): Boolean {
        return wifiCollector.isConnectedToInternet()
    }
    
    /**
     * Check if connected to WiFi
     */
    fun isConnectedToWiFi(): Boolean {
        return wifiCollector.isConnectedToWiFi()
    }
    
    /**
     * Check if current location is within geofence
     */
    fun isWithinGeofence(
        targetLatitude: Double,
        targetLongitude: Double,
        radiusMeters: Float
    ): Boolean {
        val currentLocation = _gpsData.value
        return if (currentLocation != null) {
            gpsCollector.isWithinGeofence(
                currentLocation,
                targetLatitude,
                targetLongitude,
                radiusMeters
            )
        } else {
            false
        }
    }
}