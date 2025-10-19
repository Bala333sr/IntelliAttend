package com.intelliattend.student.ui.testing

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.intelliattend.student.warm.SensorSample
import com.intelliattend.student.warm.WarmBle
import com.intelliattend.student.ui.theme.StandardButton
import com.intelliattend.student.ui.theme.StandardCard
import com.intelliattend.student.ui.theme.StandardOutlinedButton
import com.intelliattend.student.ui.theme.DeviceItem
import com.intelliattend.student.ui.theme.DataItem
import com.intelliattend.student.ui.theme.DataDisplayCard
import com.intelliattend.student.ui.theme.SectionHeader
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WarmScanTestScreen(
    modifier: Modifier = Modifier,
    onBack: () -> Unit,
    viewModel: WarmScanTestViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(Unit) {
        // Start the warm scan test when the screen is opened
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Warm Scan Test", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 16.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                DataDisplayCard(
                    title = "3-Minute Warm Scan Test",
                    icon = {
                        Icon(
                            imageVector = Icons.Default.Science,
                            contentDescription = "Warm Scan Test",
                            tint = MaterialTheme.colorScheme.primary
                        )
                    }
                ) {
                    Text(
                        text = "Collects BLE, WiFi, and GPS data every 30 seconds for 3 minutes",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            item {
                WarmScanControlCard(
                    isWarmScanActive = uiState.isWarmScanActive,
                    onToggleWarmScan = { viewModel.toggleWarmScan() },
                    onSendData = { viewModel.sendCollectedData() },
                    isSending = uiState.isSendingData
                )
            }

            item {
                WarmScanStatusCard(
                    warmScanStatus = uiState.warmScanStatus,
                    collectedSamples = uiState.collectedSamples.size,
                    nextScanIn = uiState.nextScanIn
                )
            }

            item {
                SectionHeader(title = "Collected Samples (${uiState.collectedSamples.size})")
            }

            // Display samples without try-catch around composable
            items(uiState.collectedSamples) { sample ->
                SensorSampleCard(sample = sample)
            }
        }
    }
}

@Composable
private fun WarmScanControlCard(
    isWarmScanActive: Boolean,
    onToggleWarmScan: () -> Unit,
    onSendData: () -> Unit,
    isSending: Boolean
) {
    DataDisplayCard(title = "Controls") {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            StandardButton(
                onClick = onToggleWarmScan,
                enabled = !isSending,
                text = if (isWarmScanActive) "Stop Warm Scan" else "Start Warm Scan",
                icon = {
                    Icon(
                        imageVector = if (isWarmScanActive) Icons.Default.Stop else Icons.Default.PlayArrow,
                        contentDescription = if (isWarmScanActive) "Stop" else "Start"
                    )
                },
                modifier = Modifier.weight(1f)
            )

            StandardButton(
                onClick = onSendData,
                enabled = !isSending,
                text = "Send Data",
                icon = {
                    Icon(
                        imageVector = Icons.Default.Send,
                        contentDescription = "Send Data"
                    )
                },
                modifier = Modifier.weight(1f)
            )
        }

        if (isSending) {
            Spacer(modifier = Modifier.height(16.dp))
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = MaterialTheme.colorScheme.secondary
                )
                Spacer(modifier = Modifier.width(16.dp))
                Text("Sending data to server...")
            }
        }
    }
}

@Composable
private fun WarmScanStatusCard(
    warmScanStatus: String,
    collectedSamples: Int,
    nextScanIn: Long?
) {
    DataDisplayCard(
        title = "Status",
        icon = {
            Icon(
                imageVector = Icons.Default.Info,
                contentDescription = "Status",
                tint = MaterialTheme.colorScheme.primary
            )
        }
    ) {
        DataItem(
            label = "Status",
            value = warmScanStatus,
            valueColor = when (warmScanStatus) {
                "Active" -> Color.Green
                "Stopped" -> MaterialTheme.colorScheme.onSurface
                "Completed" -> Color.Blue
                else -> MaterialTheme.colorScheme.error
            }
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        DataItem(
            label = "Samples Collected",
            value = "$collectedSamples"
        )
        
        if (nextScanIn != null && nextScanIn > 0) {
            Spacer(modifier = Modifier.height(8.dp))
            DataItem(
                label = "Next Scan In",
                value = formatTime(nextScanIn)
            )
        }
    }
}

@Composable
private fun SensorSampleCard(sample: SensorSample) {
    DataDisplayCard(
        title = formatTimestamp(sample.ts),
        icon = {
            Icon(
                imageVector = Icons.Default.DataUsage,
                contentDescription = "Sample Data",
                tint = MaterialTheme.colorScheme.primary
            )
        }
    ) {
        // BLE Data - Enhanced with detailed information like environmental data testing
        SectionHeader(title = "Bluetooth Devices (${sample.ble.size})")
        
        if (sample.ble.isEmpty()) {
            Text(
                text = "No Bluetooth devices detected",
                modifier = Modifier.padding(start = 32.dp, top = 8.dp),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        } else {
            sample.ble.forEach { ble ->
                // Handle potential null values safely
                val deviceName = ble.name ?: "Unknown Device"
                val deviceMac = ble.mac ?: "Unknown MAC"
                val deviceRssi = ble.rssi
                
                DeviceItem(
                    name = deviceName,
                    address = deviceMac,
                    rssi = deviceRssi
                )
                
                Spacer(modifier = Modifier.height(4.dp))
            }
        }
        
        Spacer(modifier = Modifier.height(12.dp))
        
        // WiFi Data - Enhanced with detailed information like environmental data testing
        SectionHeader(title = "Wi-Fi Network")
        
        if (sample.wifi != null) {
            // Handle potential null values safely
            val wifiSsid = sample.wifi.ssid ?: "Unknown Network"
            val wifiBssid = sample.wifi.bssid ?: "Unknown BSSID"
            val wifiRssi = sample.wifi.rssi ?: 0
            val wifiIpAddress = sample.wifi.ipAddress ?: "Unknown IP"
            
            DataItem(label = "Network Name", value = wifiSsid)
            DataItem(label = "Signal Strength", value = "${wifiRssi} dBm")
            DataItem(label = "BSSID", value = wifiBssid)
            DataItem(label = "IP Address", value = wifiIpAddress)
        } else {
            Text(
                text = "No Wi-Fi data available",
                modifier = Modifier.padding(start = 32.dp, top = 8.dp),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        
        Spacer(modifier = Modifier.height(12.dp))
        
        // GPS Data - Enhanced with detailed information like environmental data testing
        SectionHeader(title = "GPS Location")
        
        if (sample.gps != null) {
            // Handle potential null values safely
            val gpsLat = sample.gps.latitude
            val gpsLon = sample.gps.longitude
            val gpsAccuracy = sample.gps.accuracy
            val gpsAltitude = sample.gps.altitude
            
            DataItem(label = "Latitude", value = "%.6f".format(gpsLat))
            DataItem(label = "Longitude", value = "%.6f".format(gpsLon))
            DataItem(label = "Accuracy", value = "${gpsAccuracy} meters")
            DataItem(label = "Altitude", value = "${gpsAltitude.toInt()} m")
        } else {
            Text(
                text = "No GPS data available",
                modifier = Modifier.padding(start = 32.dp, top = 8.dp),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

private fun formatTimestamp(timestamp: Long): String {
    val sdf = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
    return sdf.format(Date(timestamp))
}

private fun formatTime(milliseconds: Long): String {
    val seconds = milliseconds / 1000
    val minutes = seconds / 60
    val remainingSeconds = seconds % 60
    return "${minutes}:${String.format("%02d", remainingSeconds)}"
}