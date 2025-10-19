package com.intelliattend.student.warm

/**
 * Configurable constants for warm-scan behavior.
 */
object WarmScanConfig {
    // Timing
    const val WARM_WINDOW_MS: Long = 180_000L    // 3 minutes
    const val CYCLE_INTERVAL_MS: Long = 30_000L  // 30 seconds

    // Bluetooth scan timeouts
    const val BLE_QUICK_SCAN_MS: Long = 700L     // fast BLE scan
    const val CLASSIC_DISCOVERY_MS: Long = 12_000L // classic fallback

    // RSSI thresholds (informational)
    const val RSSI_STRONG_DBM: Int = -70
    const val RSSI_WEAK_DBM: Int = -85

    // Acceptance threshold (server-side reference)
    const val ACCEPT_THRESHOLD: Double = 0.6
}