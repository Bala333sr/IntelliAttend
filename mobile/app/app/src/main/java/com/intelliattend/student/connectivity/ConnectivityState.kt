package com.intelliattend.student.connectivity

/**
 * Represents the detailed state of connectivity services
 * Provides granular information about Bluetooth, GPS, and Wi-Fi status
 */

/**
 * Wi-Fi connectivity state with detailed information
 */
sealed class WiFiState {
    object Disabled : WiFiState()
    object Scanning : WiFiState()
    data class Connected(
        val ssid: String,
        val signalStrength: Int, // RSSI value
        val isTransmitting: Boolean = false,
        val dataSpeed: String? = null
    ) : WiFiState()
    data class Hotspot(
        val connectedDevices: Int = 0
    ) : WiFiState()
    data class HighDataUsage(
        val appName: String,
        val dataUsed: String
    ) : WiFiState()
}

/**
 * GPS/Location connectivity state with privacy attribution
 */
sealed class GPSState {
    object Disabled : GPSState()
    object Idle : GPSState() // GPS available but not actively used
    data class ActiveLowPrecision(
        val usingApp: String? = null,
        val timestamp: Long = System.currentTimeMillis()
    ) : GPSState()
    data class ActiveHighPrecision(
        val usingApp: String,
        val accuracy: Float? = null,
        val timestamp: Long = System.currentTimeMillis()
    ) : GPSState()
}

/**
 * Bluetooth connectivity state with device attribution
 */
sealed class BluetoothState {
    object Disabled : BluetoothState()
    object Idle : BluetoothState() // Bluetooth on but no active connections
    data class Connected(
        val deviceName: String,
        val deviceType: BluetoothDeviceType = BluetoothDeviceType.UNKNOWN
    ) : BluetoothState()
    data class Transmitting(
        val deviceName: String,
        val deviceType: BluetoothDeviceType = BluetoothDeviceType.UNKNOWN,
        val dataType: String? = null // e.g., "Audio", "File Transfer"
    ) : BluetoothState()
    data class Scanning(
        val isDiscoverable: Boolean = false
    ) : BluetoothState()
}

/**
 * Bluetooth device types for better UI representation
 */
enum class BluetoothDeviceType {
    HEADPHONES,
    SPEAKER,
    PHONE,
    COMPUTER,
    WEARABLE,
    UNKNOWN
}

/**
 * Signal strength levels for visual representation
 */
enum class SignalStrength {
    EXCELLENT,  // >= -50 dBm
    GOOD,       // >= -60 dBm
    FAIR,       // >= -70 dBm
    WEAK,       // >= -80 dBm
    VERY_WEAK   // < -80 dBm
}

/**
 * Helper function to convert RSSI to signal strength
 */
fun Int.toSignalStrength(): SignalStrength {
    return when {
        this >= -50 -> SignalStrength.EXCELLENT
        this >= -60 -> SignalStrength.GOOD
        this >= -70 -> SignalStrength.FAIR
        this >= -80 -> SignalStrength.WEAK
        else -> SignalStrength.VERY_WEAK
    }
}

/**
 * Combined connectivity state for the entire system
 */
data class ConnectivityStatus(
    val wifiState: WiFiState = WiFiState.Disabled,
    val gpsState: GPSState = GPSState.Disabled,
    val bluetoothState: BluetoothState = BluetoothState.Disabled,
    val timestamp: Long = System.currentTimeMillis()
)
