package com.intelliattend.student.notification

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.intelliattend.student.R
import com.intelliattend.student.data.model.NotificationType
import com.intelliattend.student.data.model.TimetableSession
import com.intelliattend.student.ui.MainActivity

/**
 * Manages local device notifications
 * Integrates with Android NotificationManager
 * Does not affect existing system components
 */
class IntelliAttendNotificationManager(
    private val context: Context
) {

    companion object {
        private const val CHANNEL_ID = "intelliattend_notifications"
        private const val CHANNEL_NAME = "IntelliAttend Notifications"
        private const val CHANNEL_DESCRIPTION = "Notifications for class reminders and attendance alerts"
    }

    init {
        createNotificationChannels()
    }

    /**
     * Create notification channels for Android O and above
     */
    fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = CHANNEL_DESCRIPTION
                enableLights(true)
                enableVibration(true)
            }

            val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    /**
     * Show a simple notification
     */
    fun showNotification(
        id: Int,
        title: String,
        message: String,
        type: NotificationType,
        priority: Int = NotificationCompat.PRIORITY_DEFAULT
    ) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val builder = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(message)
            .setPriority(priority)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)

        with(NotificationManagerCompat.from(context)) {
            notify(id, builder.build())
        }
    }

    /**
     * Show class reminder notification using TimetableSession
     */
    fun showClassReminder(session: TimetableSession) {
        val startTimeText = java.text.SimpleDateFormat("hh:mm a", java.util.Locale.getDefault())
            .format(java.util.Date(session.startTime))
        showNotification(
            id = session.classId,
            title = "Upcoming: ${session.subject}",
            message = "Class at $startTimeText in ${session.room}",
            type = NotificationType.CLASS_REMINDER,
            priority = NotificationCompat.PRIORITY_HIGH
        )
    }

    /**
     * Show warm scan reminder notification
     */
    fun showWarmScanReminder(subject: String) {
        showNotification(
            id = System.currentTimeMillis().toInt(),
            title = "Warm Scan Open",
            message = "Scanning window is open for $subject",
            type = NotificationType.WARM_SCAN,
            priority = NotificationCompat.PRIORITY_HIGH
        )
    }

    /**
     * Show attendance warning notification
     */
    fun showAttendanceWarning(subject: String, percentage: Double) {
        showNotification(
            id = System.currentTimeMillis().toInt(),
            title = "Attendance Warning",
            message = "Your attendance in $subject is ${"%.1f".format(percentage)}% (below 75%)",
            type = NotificationType.ATTENDANCE_WARNING,
            priority = NotificationCompat.PRIORITY_HIGH
        )
    }

    /**
     * Show weekly summary notification
     */
    fun showWeeklySummary(total: Int, attended: Int, percentage: Double) {
        showNotification(
            id = System.currentTimeMillis().toInt(),
            title = "Weekly Summary",
            message = "$attended/$total sessions attended (${"%.1f".format(percentage)}%)",
            type = NotificationType.WEEKLY_SUMMARY
        )
    }

    /**
     * Cancel a specific notification
     */
    fun cancelNotification(notificationId: Int) {
        with(NotificationManagerCompat.from(context)) {
            cancel(notificationId)
        }
    }

    /**
     * Cancel all notifications
     */
    fun cancelAllNotifications() {
        with(NotificationManagerCompat.from(context)) {
            cancelAll()
        }
    }
}