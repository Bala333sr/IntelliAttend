package com.intelliattend.student.ui.settings

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.selection.toggleable
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Alarm
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.NotificationsActive
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.intelliattend.student.data.model.NotificationPreferences
import java.time.LocalTime
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotificationSettingsScreen(
    modifier: Modifier = Modifier,
    onBack: () -> Unit
) {
    var preferences by remember { mutableStateOf(NotificationPreferences()) }
    
    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Notification Settings", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.Default.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            )
        },
        containerColor = MaterialTheme.colorScheme.background
    ) { paddingValues ->
        LazyColumn(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(vertical = 16.dp)
        ) {
            item {
                NotificationSettingsGroup(
                    title = "Notification Types",
                    preferences = preferences,
                    onPreferencesChanged = { preferences = it }
                )
            }
            
            item {
                ReminderSettingsGroup(
                    preferences = preferences,
                    onPreferencesChanged = { preferences = it }
                )
            }
            
            item {
                QuietHoursSettingsGroup(
                    preferences = preferences,
                    onPreferencesChanged = { preferences = it }
                )
            }
            
            item {
                NotificationTestButton(
                    onTestNotification = {
                        // In a real implementation, this would call the repository to send a test notification
                    }
                )
            }
        }
    }
}

@Composable
private fun NotificationSettingsGroup(
    title: String,
    preferences: NotificationPreferences,
    onPreferencesChanged: (NotificationPreferences) -> Unit
) {
    SettingsGroup(title = title) {
        NotificationToggleItem(
            icon = Icons.Default.NotificationsActive,
            title = "Class Reminders",
            subtitle = "Get notified before your classes start",
            checked = preferences.classReminderEnabled,
            onCheckedChange = { checked ->
                onPreferencesChanged(preferences.copy(classReminderEnabled = checked))
            }
        )
        
        NotificationToggleItem(
            icon = Icons.Default.Schedule,
            title = "Warm Scan Reminders",
            subtitle = "Get notified when warm scan window opens",
            checked = preferences.warmScanReminderEnabled,
            onCheckedChange = { checked ->
                onPreferencesChanged(preferences.copy(warmScanReminderEnabled = checked))
            }
        )
        
        NotificationToggleItem(
            icon = Icons.Default.Alarm,
            title = "Attendance Warnings",
            subtitle = "Get notified when attendance falls below 75%",
            checked = preferences.attendanceWarningEnabled,
            onCheckedChange = { checked ->
                onPreferencesChanged(preferences.copy(attendanceWarningEnabled = checked))
            }
        )
        
        NotificationToggleItem(
            icon = Icons.Default.Notifications,
            title = "Weekly Summary",
            subtitle = "Get weekly attendance summary",
            checked = preferences.weeklySummaryEnabled,
            onCheckedChange = { checked ->
                onPreferencesChanged(preferences.copy(weeklySummaryEnabled = checked))
            }
        )
    }
}

@Composable
private fun ReminderSettingsGroup(
    preferences: NotificationPreferences,
    onPreferencesChanged: (NotificationPreferences) -> Unit
) {
    SettingsGroup(title = "Reminder Settings") {
        SettingsListItem(
            icon = Icons.Default.Alarm,
            title = "Reminder Time",
            subtitle = "${preferences.reminderMinutesBefore} minutes before class"
        ) {
            // In a real implementation, this would open a time picker dialog
            Text(
                text = "${preferences.reminderMinutesBefore} min",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}

@Composable
private fun QuietHoursSettingsGroup(
    preferences: NotificationPreferences,
    onPreferencesChanged: (NotificationPreferences) -> Unit
) {
    SettingsGroup(title = "Quiet Hours") {
        SettingsListItem(
            icon = Icons.Default.Schedule,
            title = "Quiet Hours",
            subtitle = if (preferences.quietHoursStart != null && preferences.quietHoursEnd != null) {
                "From ${preferences.quietHoursStart?.format(DateTimeFormatter.ofPattern("hh:mm a"))} " +
                        "to ${preferences.quietHoursEnd?.format(DateTimeFormatter.ofPattern("hh:mm a"))}"
            } else {
                "Not set"
            }
        ) {
            // In a real implementation, this would open a time range picker dialog
            Text(
                text = if (preferences.quietHoursStart != null && preferences.quietHoursEnd != null) "Set" else "Off",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}

@Composable
private fun NotificationTestButton(
    onTestNotification: () -> Unit
) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Button(
            onClick = onTestNotification,
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer,
                contentColor = MaterialTheme.colorScheme.onPrimaryContainer
            )
        ) {
            Text("Send Test Notification")
        }
    }
}

@Composable
private fun NotificationToggleItem(
    icon: ImageVector,
    title: String,
    subtitle: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    ListItem(
        headlineContent = { Text(title, fontWeight = FontWeight.SemiBold) },
        supportingContent = { Text(subtitle) },
        leadingContent = { Icon(icon, contentDescription = title) },
        trailingContent = {
            Switch(
                checked = checked,
                onCheckedChange = onCheckedChange
            )
        },
        modifier = Modifier.toggleable(
            value = checked,
            onValueChange = onCheckedChange
        )
    )
}

@Composable
private fun SettingsGroup(
    title: String,
    content: @Composable ColumnScope.() -> Unit
) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary,
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
        )
        content()
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SettingsListItem(
    icon: ImageVector,
    title: String,
    subtitle: String,
    action: @Composable (() -> Unit)? = null,
    onClick: (() -> Unit)? = null
) {
    ListItem(
        headlineContent = { Text(title, fontWeight = FontWeight.SemiBold) },
        supportingContent = { Text(subtitle) },
        leadingContent = { Icon(icon, contentDescription = title) },
        trailingContent = action,
        modifier = if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier
    )
}