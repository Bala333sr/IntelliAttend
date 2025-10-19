package com.intelliattend.student.ui.testing

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Fingerprint
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.CreationExtras
import com.intelliattend.student.ui.theme.*

@Composable
fun TestingScreen(
    onNavigateBack: () -> Unit,
    onNavigateToBluetoothRegistration: () -> Unit = {},
    viewModel: TestingViewModel = viewModel(
        factory = ViewModelProvider.AndroidViewModelFactory(
            LocalContext.current.applicationContext as android.app.Application
        )
    )
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(Unit) {
        viewModel.checkAllServices()
        viewModel.loadRegisteredDevices() // Load registered devices when screen opens
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Testing Page") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = IntelliBlue,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header
            Text(
                text = "Device Services Testing",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(top = 16.dp, bottom = 8.dp)
            )
            
            Text(
                text = "Use this page to test the functionality of your device's services required for attendance verification.",
                fontSize = 16.sp,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )
            
            Divider(modifier = Modifier.padding(vertical = 8.dp))
            
            // Bluetooth Section
            ServiceTestCard(
                title = "Bluetooth",
                description = "Tests if Bluetooth is enabled and can detect nearby devices",
                icon = Icons.Outlined.Bluetooth,
                status = uiState.bluetoothStatus,
                onTest = { viewModel.testBluetooth() },
                detailedContent = {
                    if (uiState.isLoadingBluetooth) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 8.dp),
                            horizontalArrangement = Arrangement.Center,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            CircularProgressIndicator(modifier = Modifier.size(20.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Scanning...", fontSize = 14.sp)
                        }
                    } else if (uiState.bluetoothError != null) {
                        Text(
                            text = "Error: ${uiState.bluetoothError}",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.error,
                            modifier = Modifier.padding(top = 8.dp)
                        )
                    } else if (uiState.bluetoothDevices.isNotEmpty()) {
                        Divider(modifier = Modifier.padding(vertical = 8.dp))
                        Text(
                            text = "Registered Devices:",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(bottom = 4.dp)
                        )
                        uiState.bluetoothDevices.forEach { device ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 4.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = device.name,
                                        fontSize = 14.sp,
                                        fontWeight = FontWeight.Medium
                                    )
                                    Text(
                                        text = device.address,
                                        fontSize = 12.sp,
                                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                                    )
                                }
                                val proximity = when {
                                    device.rssi == 0 -> "Not Found"
                                    device.rssi >= -65 -> "Near (${device.rssi} dBm)"
                                    device.rssi >= -85 -> "Possible (${device.rssi} dBm)"
                                    else -> "Far (${device.rssi} dBm)"
                                }
                                val proximityColor = when {
                                    device.rssi == 0 -> Color.Gray
                                    device.rssi >= -65 -> Color(0xFF4CAF50)
                                    device.rssi >= -85 -> Color(0xFFFF9800)
                                    else -> Color(0xFFF44336)
                                }
                                Text(
                                    text = proximity,
                                    fontSize = 12.sp,
                                    color = proximityColor,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                        val inRangeCount = uiState.bluetoothDevices.count { it.rssi != 0 && it.rssi >= -80 }
                        Text(
                            text = "$inRangeCount of ${uiState.bluetoothDevices.size} devices in range for attendance",
                            fontSize = 12.sp,
                            color = if (inRangeCount > 0) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
                            fontWeight = FontWeight.Medium,
                            modifier = Modifier.padding(top = 8.dp)
                        )
                    }
                }
            )
            
            // GPS Section
            ServiceTestCard(
                title = "GPS",
                description = "Tests if GPS is enabled and can determine your location",
                icon = Icons.Outlined.LocationOn,
                status = uiState.gpsStatus,
                onTest = { viewModel.testGPS() },
                detailedContent = {
                    if (uiState.gpsError != null && uiState.gpsData == null) {
                        Text(
                            text = "Error: ${uiState.gpsError}",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.error,
                            modifier = Modifier.padding(top = 8.dp)
                        )
                    } else if (uiState.gpsData != null) {
                        Divider(modifier = Modifier.padding(vertical = 8.dp))
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            if (uiState.gpsError != null) {
                                Text(
                                    text = uiState.gpsError!!,
                                    fontSize = 12.sp,
                                    color = MaterialTheme.colorScheme.tertiary,
                                    modifier = Modifier.padding(bottom = 4.dp)
                                )
                            }
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text("Latitude:", fontSize = 14.sp, fontWeight = FontWeight.Medium)
                                Text("%.6f".format(uiState.gpsData!!.latitude), fontSize = 14.sp)
                            }
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text("Longitude:", fontSize = 14.sp, fontWeight = FontWeight.Medium)
                                Text("%.6f".format(uiState.gpsData!!.longitude), fontSize = 14.sp)
                            }
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text("Accuracy:", fontSize = 14.sp, fontWeight = FontWeight.Medium)
                                Text("${uiState.gpsData!!.accuracy} meters", fontSize = 14.sp)
                            }
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text("Altitude:", fontSize = 14.sp, fontWeight = FontWeight.Medium)
                                Text("${uiState.gpsData!!.altitude.toInt()} m", fontSize = 14.sp)
                            }
                        }
                    }
                }
            )
            
            // Wi-Fi Section
            ServiceTestCard(
                title = "Wi-Fi",
                description = "Tests if Wi-Fi is enabled and connected to a network",
                icon = Icons.Outlined.Wifi,
                status = uiState.wifiStatus,
                onTest = { viewModel.testWifi() },
                detailedContent = {
                    if (uiState.wifiError != null && uiState.wifiData == null) {
                        Text(
                            text = "Error: ${uiState.wifiError}",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.error,
                            modifier = Modifier.padding(top = 8.dp)
                        )
                    } else if (uiState.wifiData != null) {
                        Divider(modifier = Modifier.padding(vertical = 8.dp))
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text("Network Name:", fontSize = 14.sp, fontWeight = FontWeight.Medium)
                                Text(uiState.wifiData!!.ssid, fontSize = 14.sp)
                            }
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text("Signal Strength:", fontSize = 14.sp, fontWeight = FontWeight.Medium)
                                val signalColor = when {
                                    uiState.wifiData!!.rssi >= -50 -> Color(0xFF4CAF50)
                                    uiState.wifiData!!.rssi >= -70 -> Color(0xFFFF9800)
                                    else -> Color(0xFFF44336)
                                }
                                Text(
                                    text = "${uiState.wifiData!!.rssi} dBm",
                                    fontSize = 14.sp,
                                    color = signalColor,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text("BSSID:", fontSize = 14.sp, fontWeight = FontWeight.Medium)
                                Text(uiState.wifiData!!.bssid, fontSize = 12.sp)
                            }
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text("IP Address:", fontSize = 14.sp, fontWeight = FontWeight.Medium)
                                Text(uiState.wifiData!!.ipAddress, fontSize = 14.sp)
                            }
                        }
                    }
                }
            )
            
            // Biometric Section
            ServiceTestCard(
                title = "Biometric",
                description = "Tests if biometric authentication is available on your device",
                icon = Icons.Default.Fingerprint,
                status = uiState.biometricStatus,
                onTest = { viewModel.testBiometric() }
            )
            
            Divider(modifier = Modifier.padding(vertical = 8.dp))
            
            // Bluetooth Device Registration Section
            Text(
                text = "Bluetooth Device Management",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(top = 8.dp)
            )
            
            // Bluetooth Registration Card
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.Bluetooth,
                            contentDescription = "Bluetooth Registration",
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(32.dp)
                        )
                        Column {
                            Text(
                                text = "Register Bluetooth Devices",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                            Text(
                                text = "Required before proximity testing",
                                fontSize = 14.sp,
                                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                            )
                        }
                    }
                    
                    Text(
                        text = "Register your Bluetooth devices (like headphones, smartwatches) before testing proximity detection. This ensures accurate attendance verification.",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onPrimaryContainer,
                        lineHeight = 20.sp
                    )
                    
                    // Show registered devices list if any
                    if (uiState.bluetoothDevices.isNotEmpty()) {
                        Divider(modifier = Modifier.padding(vertical = 8.dp))
                        Text(
                            text = "Registered Devices (${uiState.bluetoothDevices.size}):",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            uiState.bluetoothDevices.take(3).forEach { device ->
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(vertical = 2.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.CheckCircle,
                                        contentDescription = "Registered",
                                        tint = MaterialTheme.colorScheme.primary,
                                        modifier = Modifier.size(16.dp)
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = device.name,
                                        fontSize = 13.sp,
                                        color = MaterialTheme.colorScheme.onPrimaryContainer
                                    )
                                }
                            }
                            if (uiState.bluetoothDevices.size > 3) {
                                Text(
                                    text = "+${uiState.bluetoothDevices.size - 3} more",
                                    fontSize = 12.sp,
                                    color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f),
                                    modifier = Modifier.padding(start = 24.dp)
                                )
                            }
                        }
                    }
                    
                    Button(
                        onClick = {
                            onNavigateToBluetoothRegistration()
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.primary
                        )
                    ) {
                        Icon(
                            Icons.Outlined.Add,
                            contentDescription = "Register",
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            if (uiState.bluetoothDevices.isEmpty()) "Register Bluetooth Devices" else "Add More Devices",
                            fontSize = 16.sp
                        )
                    }
                }
            }
            
            Divider(modifier = Modifier.padding(vertical = 8.dp))
            
            // Advanced Testing Section
            Text(
                text = "Advanced Testing",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(top = 8.dp)
            )
            
            // Proximity Test
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "Proximity Test",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Text(
                        text = "Tests if your device can detect proximity to a beacon",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )
                    
                    LinearProgressIndicator(
                        progress = uiState.proximityStrength,
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp)
                    )
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "Weak",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                        )
                        Text(
                            text = "Strong",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                        )
                    }
                    
                    Button(
                        onClick = { viewModel.testProximity() },
                        modifier = Modifier.align(Alignment.End)
                    ) {
                        Text("Test Proximity")
                    }
                }
            }
            
            // Geofence Test
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "Geofence Test",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Text(
                        text = "Tests if your device is within the designated geofence area",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )
                    
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "Status:",
                            fontSize = 16.sp
                        )
                        
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Icon(
                                imageVector = if (uiState.isInGeofence) Icons.Outlined.CheckCircle else Icons.Outlined.Cancel,
                                contentDescription = if (uiState.isInGeofence) "Inside Geofence" else "Outside Geofence",
                                tint = if (uiState.isInGeofence) Color(0xFF4CAF50) else Color(0xFFF44336)
                            )
                            Text(
                                text = if (uiState.isInGeofence) "Inside Geofence" else "Outside Geofence",
                                fontSize = 16.sp,
                                color = if (uiState.isInGeofence) Color(0xFF4CAF50) else Color(0xFFF44336)
                            )
                        }
                    }
                    
                    Text(
                        text = "Distance from center: ${uiState.distanceFromCenter} meters",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )
                    
                    Button(
                        onClick = { viewModel.testGeofence() },
                        modifier = Modifier.align(Alignment.End)
                    ) {
                        Text("Test Geofence")
                    }
                }
            }
            
            Divider(modifier = Modifier.padding(vertical = 8.dp))
            
            // Server Configuration Section
            Text(
                text = "Server Configuration",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(top = 8.dp)
            )
            
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.Cloud,
                            contentDescription = "Server",
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(32.dp)
                        )
                        Column {
                            Text(
                                text = "Backend Server",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "Configure server IP address",
                                fontSize = 14.sp,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                            )
                        }
                    }
                    
                    // Current Server IP Display
                    if (uiState.serverUrl.isNotEmpty()) {
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text(
                                text = "Current Server:",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Medium,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                            )
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                color = MaterialTheme.colorScheme.surfaceVariant,
                                shape = RoundedCornerShape(8.dp)
                            ) {
                                Text(
                                    text = uiState.serverUrl,
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    modifier = Modifier.padding(12.dp)
                                )
                            }
                        }
                    }
                    
                    // Server URL Input Field
                    var serverInput by remember { mutableStateOf(uiState.serverUrl) }
                    
                    OutlinedTextField(
                        value = serverInput,
                        onValueChange = { serverInput = it },
                        label = { Text("Server URL") },
                        placeholder = { Text("http://192.168.0.7:5002/api/") },
                        leadingIcon = {
                            Icon(Icons.Outlined.Cloud, contentDescription = "Server URL")
                        },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = Color.Black,
                            unfocusedTextColor = Color.Black,
                            focusedBorderColor = IntelliBlue,
                            focusedLabelColor = IntelliBlue,
                            cursorColor = IntelliBlue
                        )
                    )
                    
                    Text(
                        text = "Enter the IP address of your backend server (e.g., http://192.168.0.7:5002/api/)",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                        lineHeight = 16.sp
                    )
                    
                    // Connection Status
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "Connection Status:",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium
                        )
                        
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            when (uiState.serverConnectionStatus) {
                                ServiceStatus.WORKING -> {
                                    Icon(
                                        imageVector = Icons.Outlined.CheckCircle,
                                        contentDescription = "Connected",
                                        tint = Color(0xFF4CAF50),
                                        modifier = Modifier.size(20.dp)
                                    )
                                    Text(
                                        text = "Connected",
                                        fontSize = 14.sp,
                                        color = Color(0xFF4CAF50),
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                                ServiceStatus.ERROR -> {
                                    Icon(
                                        imageVector = Icons.Outlined.Cancel,
                                        contentDescription = "Disconnected",
                                        tint = Color(0xFFF44336),
                                        modifier = Modifier.size(20.dp)
                                    )
                                    Text(
                                        text = "Disconnected",
                                        fontSize = 14.sp,
                                        color = Color(0xFFF44336),
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                                ServiceStatus.TESTING -> {
                                    CircularProgressIndicator(
                                        modifier = Modifier.size(16.dp),
                                        strokeWidth = 2.dp,
                                        color = Color(0xFFFF9800)
                                    )
                                    Text(
                                        text = "Testing...",
                                        fontSize = 14.sp,
                                        color = Color(0xFFFF9800),
                                        fontWeight = FontWeight.Medium
                                    )
                                }
                                ServiceStatus.UNKNOWN -> {
                                    Icon(
                                        imageVector = Icons.Outlined.Info,
                                        contentDescription = "Unknown",
                                        tint = Color.Gray,
                                        modifier = Modifier.size(20.dp)
                                    )
                                    Text(
                                        text = "Not tested",
                                        fontSize = 14.sp,
                                        color = Color.Gray
                                    )
                                }
                            }
                        }
                    }
                    
                    // Error message if any
                    if (uiState.serverError != null) {
                        Surface(
                            modifier = Modifier.fillMaxWidth(),
                            color = MaterialTheme.colorScheme.errorContainer,
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Row(
                                modifier = Modifier.padding(12.dp),
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Outlined.Warning,
                                    contentDescription = "Error",
                                    tint = MaterialTheme.colorScheme.error,
                                    modifier = Modifier.size(20.dp)
                                )
                                Text(
                                    text = uiState.serverError!!,
                                    fontSize = 13.sp,
                                    color = MaterialTheme.colorScheme.onErrorContainer,
                                    lineHeight = 18.sp
                                )
                            }
                        }
                    }
                    
                    // Action Buttons
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        // Test Connection Button
                        OutlinedButton(
                            onClick = { viewModel.testServerConnection(serverInput) },
                            modifier = Modifier.weight(1f),
                            enabled = serverInput.isNotBlank(),
                            colors = ButtonDefaults.outlinedButtonColors(
                                contentColor = IntelliBlue
                            )
                        ) {
                            Icon(
                                Icons.Outlined.Refresh,
                                contentDescription = "Test",
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("Test", fontSize = 14.sp)
                        }
                        
                        // Save Button
                        Button(
                            onClick = { 
                                viewModel.saveServerUrl(serverInput)
                            },
                            modifier = Modifier.weight(1f),
                            enabled = serverInput.isNotBlank() && serverInput != uiState.serverUrl,
                            colors = ButtonDefaults.buttonColors(
                                containerColor = IntelliBlue
                            )
                        ) {
                            Icon(
                                Icons.Outlined.Done,
                                contentDescription = "Save",
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("Save", fontSize = 14.sp)
                        }
                    }
                    
                    // Success message
                    if (uiState.serverSaveSuccess) {
                        Surface(
                            modifier = Modifier.fillMaxWidth(),
                            color = Color(0xFFE8F5E9),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Row(
                                modifier = Modifier.padding(12.dp),
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Outlined.CheckCircle,
                                    contentDescription = "Success",
                                    tint = Color(0xFF4CAF50),
                                    modifier = Modifier.size(20.dp)
                                )
                                Text(
                                    text = "Server URL saved successfully! App will now use this server.",
                                    fontSize = 13.sp,
                                    color = Color(0xFF2E7D32),
                                    lineHeight = 18.sp
                                )
                            }
                        }
                    }
                }
            }
            
            // Test All Button
            Button(
                onClick = { viewModel.checkAllServices() },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 16.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.primary
                )
            ) {
                Icon(
                    Icons.Outlined.Refresh,
                    contentDescription = "Test All Services",
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("Test All Services", fontSize = 16.sp)
            }
            
            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@Composable
fun ServiceTestCard(
    title: String,
    description: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    status: ServiceStatus,
    onTest: () -> Unit,
    detailedContent: @Composable (() -> Unit)? = null
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = title,
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Text(
                        text = title,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                StatusChip(status = status)
            }
            
            Text(
                text = description,
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )
            
            // Show detailed content if available
            detailedContent?.invoke()
            
            Button(
                onClick = onTest,
                modifier = Modifier.align(Alignment.End)
            ) {
                Text("Test $title")
            }
        }
    }
}

@Composable
fun StatusChip(status: ServiceStatus) {
    val (backgroundColor, textColor, statusText) = when (status) {
        ServiceStatus.WORKING -> Triple(Color(0xFFE8F5E9), Color(0xFF4CAF50), "Working")
        ServiceStatus.ERROR -> Triple(Color(0xFFFFEBEE), Color(0xFFF44336), "Error")
        ServiceStatus.TESTING -> Triple(Color(0xFFFFF3E0), Color(0xFFFF9800), "Testing")
        ServiceStatus.UNKNOWN -> Triple(Color(0xFFF5F5F5), Color(0xFF9E9E9E), "Unknown")
    }
    
    Surface(
        color = backgroundColor,
        shape = MaterialTheme.shapes.small
    ) {
        Text(
            text = statusText,
            color = textColor,
            fontWeight = FontWeight.Medium,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}