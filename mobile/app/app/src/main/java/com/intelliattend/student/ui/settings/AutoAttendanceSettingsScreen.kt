package com.intelliattend.student.ui.settings

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.intelliattend.student.data.model.AutoAttendanceConfig
import java.text.DecimalFormat

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AutoAttendanceSettingsScreen(
    modifier: Modifier = Modifier,
    onBack: () -> Unit
) {
    var config by remember { mutableStateOf(AutoAttendanceConfig()) }
    
    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Auto Attendance Settings", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
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
                MasterToggleItem(
                    enabled = config.enabled,
                    onCheckedChange = { enabled ->
                        config = config.copy(enabled = enabled)
                    }
                )
            }
            
            if (config.enabled) {
                item {
                    SensorSettingsGroup(
                        config = config,
                        onConfigChanged = { config = it }
                    )
                }
                
                item {
                    ThresholdSettingsGroup(
                        config = config,
                        onConfigChanged = { config = it }
                    )
                }
                
                item {
                    BehaviorSettingsGroup(
                        config = config,
                        onConfigChanged = { config = it }
                    )
                }
                
                item {
                    ActivityLogSection(
                        onViewActivityLog = {
                            // TODO: Navigate to activity log screen
                        }
                    )
                }
                
                item {
                    StatisticsSection(
                        onRefreshStats = {
                            // TODO: Refresh statistics
                        }
                    )
                }
            }
            
            item {
                PrivacyInformationSection()
            }
        }
    }
}

@Composable
private fun MasterToggleItem(
    enabled: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    SettingsGroup(title = "Auto Attendance") {
        ListItem(
            headlineContent = { Text("Enable Auto Attendance", fontWeight = FontWeight.SemiBold) },
            supportingContent = { 
                Text(
                    if (enabled) "Auto attendance is currently enabled" 
                    else "Auto attendance is currently disabled"
                ) 
            },
            leadingContent = { Icon(Icons.Default.AutoAwesome, contentDescription = "Auto Attendance") },
            trailingContent = {
                Switch(
                    checked = enabled,
                    onCheckedChange = onCheckedChange
                )
            }
        )
        
        if (!enabled) {
            Text(
                text = "When enabled, the app will automatically mark your attendance when you're detected in the classroom.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
            )
        }
    }
}

@Composable
private fun SensorSettingsGroup(
    config: AutoAttendanceConfig,
    onConfigChanged: (AutoAttendanceConfig) -> Unit
) {
    SettingsGroup(title = "Sensors") {
        ToggleItem(
            icon = Icons.Default.LocationOn,
            title = "GPS Detection",
            subtitle = "Use GPS to verify your location",
            checked = config.gpsEnabled,
            onCheckedChange = { checked ->
                onConfigChanged(config.copy(gpsEnabled = checked))
            }
        )
        
        ToggleItem(
            icon = Icons.Default.Wifi,
            title = "WiFi Detection",
            subtitle = "Use WiFi networks to verify your location",
            checked = config.wifiEnabled,
            onCheckedChange = { checked ->
                onConfigChanged(config.copy(wifiEnabled = checked))
            }
        )
        
        ToggleItem(
            icon = Icons.Default.Bluetooth,
            title = "Bluetooth Detection",
            subtitle = "Use Bluetooth beacons to verify your location",
            checked = config.bluetoothEnabled,
            onCheckedChange = { checked ->
                onConfigChanged(config.copy(bluetoothEnabled = checked))
            }
        )
    }
}

@Composable
private fun ThresholdSettingsGroup(
    config: AutoAttendanceConfig,
    onConfigChanged: (AutoAttendanceConfig) -> Unit
) {
    SettingsGroup(title = "Detection Settings") {
        ListItem(
            headlineContent = { Text("Confidence Threshold", fontWeight = FontWeight.SemiBold) },
            supportingContent = { 
                Text("Minimum confidence required for auto-marking: ${DecimalFormat("#.##").format(config.confidenceThreshold * 100)}%") 
            },
            leadingContent = { Icon(Icons.Default.Speed, contentDescription = "Threshold") }
        ) {
            // In a real implementation, this would open a slider dialog
            Text(
                text = "${DecimalFormat("#.##").format(config.confidenceThreshold * 100)}%",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.primary
            )
        }
        
        ToggleItem(
            icon = Icons.Default.Thermostat,
            title = "Require Warm Data",
            subtitle = "Only auto-mark when warm scan data is available",
            checked = config.requireWarmData,
            onCheckedChange = { checked ->
                onConfigChanged(config.copy(requireWarmData = checked))
            }
        )
        
        ToggleItem(
            icon = Icons.Default.CheckCircle,
            title = "Auto Submit",
            subtitle = "Automatically submit attendance without confirmation",
            checked = config.autoSubmit,
            onCheckedChange = { checked ->
                onConfigChanged(config.copy(autoSubmit = checked))
            }
        )
    }
}

@Composable
private fun BehaviorSettingsGroup(
    config: AutoAttendanceConfig,
    onConfigChanged: (AutoAttendanceConfig) -> Unit
) {
    SettingsGroup(title = "Notifications") {
        ToggleItem(
            icon = Icons.Default.Notifications,
            title = "Notify on Auto-Mark",
            subtitle = "Show notification when attendance is auto-marked",
            checked = config.notifyOnAutoMark,
            onCheckedChange = { checked ->
                onConfigChanged(config.copy(notifyOnAutoMark = checked))
            }
        )
    }
}

@Composable
private fun ActivityLogSection(
    onViewActivityLog: () -> Unit
) {
    SettingsGroup(title = "Activity") {
        SettingsListItem(
            icon = Icons.Default.History,
            title = "Activity Log",
            subtitle = "View history of auto-attendance attempts",
            onClick = onViewActivityLog
        )
    }
}

@Composable
private fun StatisticsSection(
    onRefreshStats: () -> Unit
) {
    SettingsGroup(title = "Statistics") {
        Column(modifier = Modifier.fillMaxWidth()) {
            // In a real implementation, you would show actual statistics
            ListItem(
                headlineContent = { Text("Success Rate", fontWeight = FontWeight.SemiBold) },
                supportingContent = { Text("85% of auto-attendance attempts successful") },
                leadingContent = { Icon(Icons.Default.BarChart, contentDescription = "Statistics") }
            )
            
            ListItem(
                headlineContent = { Text("Total Auto-Marked", fontWeight = FontWeight.SemiBold) },
                supportingContent = { Text("120 sessions auto-marked") },
                leadingContent = { Icon(Icons.Default.Check, contentDescription = "Total") }
            )
            
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.End
            ) {
                Button(
                    onClick = onRefreshStats,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.secondaryContainer,
                        contentColor = MaterialTheme.colorScheme.onSecondaryContainer
                    )
                ) {
                    Icon(Icons.Default.Refresh, contentDescription = "Refresh", modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Refresh")
                }
            }
        }
    }
}

@Composable
private fun PrivacyInformationSection() {
    SettingsGroup(title = "Privacy") {
        Column(modifier = Modifier.fillMaxWidth()) {
            Text(
                text = "Privacy Information",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
            )
            
            Text(
                text = "• Location data is only used during class hours to verify your presence",
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp)
            )
            
            Text(
                text = "• Sensor data is processed locally on your device when possible",
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp)
            )
            
            Text(
                text = "• You can disable auto-attendance at any time",
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp)
            )
            
            Text(
                text = "• All activity is logged for your transparency",
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp)
            )
        }
    }
}

@Composable
private fun ToggleItem(
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
        }
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