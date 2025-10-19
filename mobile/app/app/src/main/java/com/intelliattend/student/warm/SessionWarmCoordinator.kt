package com.intelliattend.student.warm

import android.app.Application
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.network.ActiveSession
import com.intelliattend.student.data.collector.GPSDataCollector
import com.intelliattend.student.data.collector.WiFiDataCollector
import com.intelliattend.student.bt.BluetoothManager

/**
 * SessionWarmCoordinator
 * - Listens for upcoming sessions and automatically triggers WarmScanScheduler
 *   3 minutes prior to the nearest session start.
 * - Non-intrusive: does not change existing scanning logic.
 */
class SessionWarmCoordinator(
    private val app: Application,
    private val bluetoothManager: BluetoothManager
) {
    private val scope = CoroutineScope(Dispatchers.Default)
    private var pollJob: Job? = null
    private var activeJob: Job? = null

    // Own scheduler instance using mobile-module collectors
    private val wifiCollector by lazy { WiFiDataCollector(app) }
    private val gpsCollector by lazy { GPSDataCollector(app) }
    private val scheduler by lazy { WarmScanScheduler(app, bluetoothManager, wifiCollector, gpsCollector) }

    // Cache of last scheduled start to avoid rescheduling too often
    @Volatile private var scheduledForEpoch: Long? = null

    fun updateSessions(sessions: List<ActiveSession>) {
        val next = sessions
            .mapNotNull { parseIsoToEpochMillis(it.startTime) }
            .filter { it > System.currentTimeMillis() }
            .minOrNull() ?: return
        scheduleFor(next)
    }

    fun startPolling(provider: suspend () -> List<ActiveSession>) {
        if (pollJob != null) return
        pollJob = scope.launch {
            while (true) {
                try {
                    val sessions = provider()
                    updateSessions(sessions)
                } catch (_: Exception) {}
                delay(60_000L) // poll every minute (configurable)
            }
        }
    }

    fun stopPolling() { pollJob?.cancel(); pollJob = null }

    private fun scheduleFor(sessionStartEpochMs: Long) {
        val warmStart = sessionStartEpochMs - 180_000L
        if (scheduledForEpoch == sessionStartEpochMs) return
        scheduledForEpoch = sessionStartEpochMs

        activeJob?.cancel()
        activeJob = scope.launch {
            val now = System.currentTimeMillis()
            val waitMs = (warmStart - now)
            if (waitMs > 0) delay(waitMs)
            scheduler.startWarmWindow(sessionStartEpochMs)
        }
    }

    fun stopWarm() { scheduler.stop(); scheduledForEpoch = null }

    fun currentScheduled(): Long? = scheduledForEpoch
}

// Very simple ISO 8601 parser that tolerates common formats (YYYY-MM-DDThh:mm:ssZ)
private fun parseIsoToEpochMillis(iso: String?): Long? {
    if (iso.isNullOrBlank()) return null
    return try {
        java.time.Instant.parse(iso).toEpochMilli()
    } catch (_: Throwable) {
        // Fallback without nanos or timezone
        runCatching {
            val s = if (iso.endsWith("Z", true)) iso else iso + "Z"
            java.time.Instant.parse(s).toEpochMilli()
        }.getOrNull()
    }
}
