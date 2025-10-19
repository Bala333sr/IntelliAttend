package com.intelliattend.student.data.model

import com.intelliattend.student.network.model.WarmSensorSample

/**
 * Data class to store the final scan data including QR code and sensor samples
 */
data class FinalScanData(
    val qrData: String,
    val samples: List<WarmSensorSample>,
    val finalSample: WarmSensorSample,
    val timestamp: Long = System.currentTimeMillis()
)

/**
 * Data class to store collected sensor data that can be sent to server
 */
data class CollectedData(
    val id: String = java.util.UUID.randomUUID().toString(),
    val wifiData: com.intelliattend.student.data.model.WiFiData?,
    val gpsData: com.intelliattend.student.data.model.GPSData?,
    val bluetoothData: List<BluetoothDeviceData>,
    val qrToken: String? = null,
    val timestamp: Long = System.currentTimeMillis(),
    val isSent: Boolean = false
)

/**
 * Data class for individual Bluetooth device data
 */
data class BluetoothDeviceData(
    val mac: String,
    val name: String?,
    val rssi: Int,
    val smoothedRssi: Double?
)