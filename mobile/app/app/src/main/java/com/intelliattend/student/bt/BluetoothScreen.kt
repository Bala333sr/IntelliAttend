package com.intelliattend.student.bt

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.intelliattend.student.data.model.DeviceEntry

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BluetoothScreen(onBack: () -> Unit) {
    val viewModel: BluetoothViewModel = viewModel()
    val isScanning by viewModel.isScanning.collectAsState()
    val scanResults by viewModel.scanResults.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Bluetooth Scanner") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Button(onClick = { viewModel.startScan() }, enabled = !isScanning) {
                Text(if (isScanning) "Scanning..." else "Start Scan")
            }
            Spacer(modifier = Modifier.height(16.dp))
            LazyColumn {
                items(scanResults.values.toList()) { deviceEntry ->
                    DeviceItem(deviceEntry = deviceEntry, viewModel = viewModel)
                }
            }
        }
    }
}

@Composable
fun DeviceItem(deviceEntry: DeviceEntry, viewModel: BluetoothViewModel) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = deviceEntry.device.name ?: "Unknown Device",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                val proximity = when {
                    deviceEntry.smoothedRssi ?: 0.0 >= -65 -> "Near"
                    deviceEntry.smoothedRssi ?: 0.0 >= -85 -> "Possible"
                    else -> "Far"
                }
                Icon(
                    imageVector = if (proximity == "Near") Icons.Default.CheckCircle else Icons.Default.Info,
                    contentDescription = "Proximity",
                    tint = if (proximity == "Near") Color.Green else Color.Yellow
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(proximity)
                
                // Add "+" icon to register the device
                Spacer(modifier = Modifier.width(8.dp))
                IconButton(onClick = { viewModel.registerDevice(deviceEntry) }) {
                    Icon(
                        imageVector = Icons.Default.Add,
                        contentDescription = "Register Device",
                        tint = MaterialTheme.colorScheme.primary
                    )
                }
            }
            Text("Address: ${deviceEntry.device.address}")
            Text("RSSI: ${deviceEntry.rssi} dBm (Smoothed: ${String.format("%.2f", deviceEntry.smoothedRssi)})")
            deviceEntry.beaconInfo?.let {
                Text("Class ID: ${it.classId}")
                Text("Session Token: ${it.sessionToken}")
                Text("Faculty ID: ${it.facultyId}")
                Button(onClick = { viewModel.submitAttendance(deviceEntry) }) {
                    Text("Submit Attendance")
                }
            }
        }
    }
}