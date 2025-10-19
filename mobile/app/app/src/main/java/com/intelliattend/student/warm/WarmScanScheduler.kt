package com.intelliattend.student.warm

import android.app.Application
import com.intelliattend.student.bt.BluetoothManager
import com.intelliattend.student.data.collector.GPSDataCollector
import com.intelliattend.student.data.collector.WiFiDataCollector
import com.intelliattend.student.data.model.BluetoothData
import com.intelliattend.student.data.model.GPSData
import com.intelliattend.student.data.model.WiFiData
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

/**
 * Non-intrusive warm scan scheduler. Uses existing BluetoothManager and
 * the mobile-module WiFi/GPS collectors. Designed to run only during a small
 * warm window before session start.
 */
class WarmScanScheduler(
    private val app: Application,
    private val bluetoothManager: BluetoothManager,
    private val wifiCollector: WiFiDataCollector,
    private val gpsCollector: GPSDataCollector,
    private val buffer: SampleBuffer = SampleBuffer(8),
    private val clock: () -> Long = { System.currentTimeMillis() }
) {
    private val scope = CoroutineScope(Dispatchers.Default)
    private var job: Job? = null

    // Tunables
    private val warmWindowMs = 180_000L // 3 minutes
    private val cycleIntervalMs = 30_000L
    private val bleQuickMs = 700L
    private val classicDiscoveryMs = 12_000L

    fun startWarmWindow(sessionStartEpochMs: Long) {
        stop()
        job = scope.launch {
            val windowStart = sessionStartEpochMs - warmWindowMs
            // Wait until warm window begins
            while (clock() < windowStart) {
                val d = windowStart - clock()
                if (d > 0) delay(d.coerceAtMost(5_000L)) else break
            }
            // Run cycles until session start
            while (clock() < sessionStartEpochMs) {
                val sample = runCycleOnce()
                buffer.add(sample)
                val next = clock() + cycleIntervalMs
                val d = next - clock()
                if (d > 0) delay(d)
            }
        }
    }

    suspend fun runCycleOnce(): SensorSample {
        // 1) quick BLE
        bluetoothManager.clearScanResults()
        bluetoothManager.startBleScan()
        delay(bleQuickMs)
        bluetoothManager.stopBleScan()

        var bleEntries = bluetoothManager.scanResults.first().values.toList()
        if (bleEntries.isEmpty()) {
            // 2) classic fallback up to 12s
            bluetoothManager.startClassicDiscovery()
            delay(classicDiscoveryMs)
            bluetoothManager.stopClassicDiscovery()
            bleEntries = bluetoothManager.scanResults.first().values.toList()
        }

        val wifi = wifiCollector.getCurrentWiFiData().getOrNull()
        val gps = gpsCollector.getLastKnownLocation().getOrNull()

        return SensorSample(
            ts = clock(),
            ble = bleEntries.map {
                WarmBle(
                    mac = it.device.address,
                    name = it.device.name,
                    rssi = it.rssi,
                    smoothedRssi = it.smoothedRssi
                )
            },
            wifi = wifi,
            gps = gps
        )
    }

    fun stop() {
        job?.cancel()
        job = null
    }

    fun getSamples(): List<SensorSample> = buffer.toList()
}

// Simple ring buffer
class SampleBuffer(private val capacity: Int) {
    private val deque: ArrayDeque<SensorSample> = ArrayDeque()
    fun add(s: SensorSample) {
        if (deque.size >= capacity) deque.removeFirst()
        deque.addLast(s)
    }
    fun clear() {
        deque.clear()
    }
    fun toList(): List<SensorSample> = deque.toList()
}

// Data models used for JSON serialization when submitting
data class SensorSample(
    val ts: Long,
    val ble: List<WarmBle>,
    val wifi: WiFiData?,
    val gps: GPSData?
)

data class WarmBle(
    val mac: String,
    val name: String?,
    val rssi: Int,
    val smoothedRssi: Double?
)
