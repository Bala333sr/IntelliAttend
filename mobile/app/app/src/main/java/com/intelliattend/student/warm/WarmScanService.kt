package com.intelliattend.student.warm

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Binder
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.intelliattend.student.R // Correct import
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.bt.BluetoothManager
import com.intelliattend.mobilemodule.collector.GPSDataCollector
import com.intelliattend.mobilemodule.collector.WiFiDataCollector

/**
 * Foreground service that runs warm-scan cycles in the 3-minute window
 * before session start, collecting BLE/WiFi/GPS samples.
 */
class WarmScanService : Service() {

    companion object {
        const val CHANNEL_ID = "warm_scan_channel"
        const val NOTIFICATION_ID = 42001

        const val EXTRA_SESSION_START_EPOCH_MS = "extra_session_start_epoch_ms"

        fun start(context: Context, sessionStartEpochMs: Long) {
            val intent = Intent(context, WarmScanService::class.java).apply {
                putExtra(EXTRA_SESSION_START_EPOCH_MS, sessionStartEpochMs)
            }
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }
    }

    private val binder = LocalBinder()
    private lateinit var scheduler: WarmScanScheduler

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()

        val app = application as IntelliAttendApplication
        val bluetoothManager = app.getBluetoothManager()
        val wifiCollector = WiFiDataCollector(this)
        val gpsCollector = GPSDataCollector(this)

        scheduler = WarmScanScheduler(
            app = app,
            bluetoothManager = bluetoothManager,
            wifiCollector = wifiCollector,
            gpsCollector = gpsCollector,
            buffer = SampleBuffer(8),
            clock = { System.currentTimeMillis() }
        )
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val sessionStartEpochMs = intent?.getLongExtra(EXTRA_SESSION_START_EPOCH_MS, -1L) ?: -1L
        startForeground(NOTIFICATION_ID, buildNotification())
        if (sessionStartEpochMs > 0) {
            scheduler.startWarmWindow(sessionStartEpochMs)
        }
        // Periodically reflect samples into holder for easy UI access
        WarmScanHolder.startReflecting { scheduler.getSamples() }
        return START_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            scheduler.stop()
            WarmScanHolder.stopReflecting()
        } catch (e: Exception) {
            android.util.Log.e("WarmScanService", "Error in onDestroy", e)
        }
    }

    override fun onBind(intent: Intent?): IBinder = binder

    inner class LocalBinder : Binder() {
        fun getService(): WarmScanService = this@WarmScanService
    }

    fun getSamples(): List<SensorSample> = scheduler.getSamples()

    private fun buildNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(getString(R.string.app_name))
            .setContentText("Warming sensors… preparing for attendance")
            .setSmallIcon(R.mipmap.ic_launcher)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Warm Scan",
                NotificationManager.IMPORTANCE_LOW
            )
            val nm = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            nm.createNotificationChannel(channel)
        }
    }
}

/**
 * Global holder for accessing warm samples without binding to the service.
 * The service updates this holder periodically.
 */
object WarmScanHolder {
    @Volatile
    private var samples: List<SensorSample> = emptyList()
    private var running: Boolean = false
    private var thread: Thread? = null

    fun getSamples(): List<SensorSample> = samples

    fun startReflecting(provider: () -> List<SensorSample>) {
        if (running) return
        running = true
        thread = Thread {
            while (running) {
                try { samples = provider() } catch (_: Exception) {}
                try { Thread.sleep(5_000L) } catch (_: InterruptedException) {}
            }
        }.also { it.start() }
    }

    fun stopReflecting() {
        running = false
        try { thread?.interrupt() } catch (_: Exception) {}
        thread = null
    }
}