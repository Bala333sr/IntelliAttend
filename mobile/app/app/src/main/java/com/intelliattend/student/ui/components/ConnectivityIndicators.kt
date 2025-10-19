package com.intelliattend.student.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import com.intelliattend.student.connectivity.*
import com.intelliattend.student.ui.theme.*
import kotlinx.coroutines.delay
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.PrivacyTip

/**
 * Enhanced connectivity indicators that show detailed state information
 * for Bluetooth, GPS, and Wi-Fi services with animations and privacy attribution
 */

/**
 * Main connectivity status bar component
 * Displays all three service indicators in a compact row
 */
@Composable
fun ConnectivityStatusBar(
    connectivityStatus: ConnectivityStatus,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(12.dp),
        color = MaterialTheme.colorScheme.surface,
        tonalElevation = 2.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Wi-Fi Indicator
            WiFiIndicator(
                wifiState = connectivityStatus.wifiState,
                modifier = Modifier.weight(1f)
            )
            
            Divider(
                modifier = Modifier
                    .width(1.dp)
                    .height(40.dp),
                color = MaterialTheme.colorScheme.outlineVariant
            )
            
            // GPS Indicator
            GPSIndicator(
                gpsState = connectivityStatus.gpsState,
                modifier = Modifier.weight(1f)
            )
            
            Divider(
                modifier = Modifier
                    .width(1.dp)
                    .height(40.dp),
                color = MaterialTheme.colorScheme.outlineVariant
            )
            
            // Bluetooth Indicator
            BluetoothIndicator(
                bluetoothState = connectivityStatus.bluetoothState,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

/**
 * Wi-Fi indicator with state-specific animations
 */
@Composable
fun WiFiIndicator(
    wifiState: WiFiState,
    modifier: Modifier = Modifier
) {
    var showDetails by remember { mutableStateOf(false) }
    
    Column(
        modifier = modifier
            .clickable { showDetails = true }
            .padding(8.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Icon with animation
        Box(
            contentAlignment = Alignment.Center
        ) {
            when (wifiState) {
                is WiFiState.Disabled -> {
                    Icon(
                        imageVector = Icons.Default.WifiOff,
                        contentDescription = "Wi-Fi Disabled",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f),
                        modifier = Modifier.size(28.dp)
                    )
                }
                is WiFiState.Scanning -> {
                    AnimatedWiFiScanningIcon()
                }
                is WiFiState.Connected -> {
                    AnimatedWiFiConnectedIcon(
                        signalStrength = wifiState.signalStrength,
                        isTransmitting = wifiState.isTransmitting
                    )
                }
                is WiFiState.Hotspot -> {
                    Icon(
                        imageVector = Icons.Default.Wifi,
                        contentDescription = "Hotspot Active",
                        tint = IntelliOrange,
                        modifier = Modifier.size(28.dp)
                    )
                }
                is WiFiState.HighDataUsage -> {
                    Icon(
                        imageVector = Icons.Default.Warning,
                        contentDescription = "High Data Usage",
                        tint = IntelliRed,
                        modifier = Modifier.size(28.dp)
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(4.dp))
        
        // Status text
        Text(
            text = when (wifiState) {
                is WiFiState.Disabled -> "Off"
                is WiFiState.Scanning -> "Scanning"
                is WiFiState.Connected -> wifiState.ssid.take(8)
                is WiFiState.Hotspot -> "Hotspot"
                is WiFiState.HighDataUsage -> "High Usage"
            },
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            maxLines = 1
        )
    }
    
    // Details dialog
    if (showDetails) {
        WiFiDetailsDialog(
            wifiState = wifiState,
            onDismiss = { showDetails = false }
        )
    }
}

/**
 * GPS indicator with privacy attribution
 */
@Composable
fun GPSIndicator(
    gpsState: GPSState,
    modifier: Modifier = Modifier
) {
    var showDetails by remember { mutableStateOf(false) }
    
    Column(
        modifier = modifier
            .clickable { showDetails = true }
            .padding(8.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Icon with animation
        Box(
            contentAlignment = Alignment.Center
        ) {
            when (gpsState) {
                is GPSState.Disabled -> {
                    Icon(
                        imageVector = Icons.Default.LocationOff,
                        contentDescription = "GPS Disabled",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f),
                        modifier = Modifier.size(28.dp)
                    )
                }
                is GPSState.Idle -> {
                    Icon(
                        imageVector = Icons.Default.LocationOn,
                        contentDescription = "GPS Idle",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier
                            .size(28.dp)
                            .alpha(0.6f)
                    )
                }
                is GPSState.ActiveLowPrecision -> {
                    AnimatedGPSActiveIcon(
                        color = IntelliBlue,
                        isPrecise = false
                    )
                }
                is GPSState.ActiveHighPrecision -> {
                    AnimatedGPSActiveIcon(
                        color = IntelliGreen,
                        isPrecise = true
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(4.dp))
        
        // Status text
        Text(
            text = when (gpsState) {
                is GPSState.Disabled -> "Off"
                is GPSState.Idle -> "Idle"
                is GPSState.ActiveLowPrecision -> "Active"
                is GPSState.ActiveHighPrecision -> "Precise"
            },
            style = MaterialTheme.typography.labelSmall,
            color = when (gpsState) {
                is GPSState.ActiveHighPrecision -> IntelliGreen
                is GPSState.ActiveLowPrecision -> IntelliBlue
                else -> MaterialTheme.colorScheme.onSurfaceVariant
            },
            fontWeight = if (gpsState is GPSState.ActiveHighPrecision || gpsState is GPSState.ActiveLowPrecision) {
                FontWeight.Bold
            } else {
                FontWeight.Normal
            },
            maxLines = 1
        )
    }
    
    // Details dialog with privacy attribution
    if (showDetails) {
        GPSDetailsDialog(
            gpsState = gpsState,
            onDismiss = { showDetails = false }
        )
    }
}

/**
 * Bluetooth indicator with device attribution
 */
@Composable
fun BluetoothIndicator(
    bluetoothState: BluetoothState,
    modifier: Modifier = Modifier
) {
    var showDetails by remember { mutableStateOf(false) }
    
    Column(
        modifier = modifier
            .clickable { showDetails = true }
            .padding(8.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Icon with animation
        Box(
            contentAlignment = Alignment.Center
        ) {
            when (bluetoothState) {
                is BluetoothState.Disabled -> {
                    Icon(
                        imageVector = Icons.Default.BluetoothDisabled,
                        contentDescription = "Bluetooth Disabled",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f),
                        modifier = Modifier.size(28.dp)
                    )
                }
                is BluetoothState.Idle -> {
                    Icon(
                        imageVector = Icons.Default.Bluetooth,
                        contentDescription = "Bluetooth Idle",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier
                            .size(28.dp)
                            .alpha(0.6f)
                    )
                }
                is BluetoothState.Connected -> {
                    Icon(
                        imageVector = Icons.Default.BluetoothConnected,
                        contentDescription = "Bluetooth Connected",
                        tint = IntelliBlue,
                        modifier = Modifier.size(28.dp)
                    )
                }
                is BluetoothState.Transmitting -> {
                    AnimatedBluetoothTransmittingIcon()
                }
                is BluetoothState.Scanning -> {
                    AnimatedBluetoothScanningIcon(
                        isDiscoverable = bluetoothState.isDiscoverable
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(4.dp))
        
        // Status text
        Text(
            text = when (bluetoothState) {
                is BluetoothState.Disabled -> "Off"
                is BluetoothState.Idle -> "Idle"
                is BluetoothState.Connected -> "Connected"
                is BluetoothState.Transmitting -> "Active"
                is BluetoothState.Scanning -> if (bluetoothState.isDiscoverable) "Visible" else "Scanning"
            },
            style = MaterialTheme.typography.labelSmall,
            color = when (bluetoothState) {
                is BluetoothState.Transmitting -> IntelliGreen
                is BluetoothState.Connected -> IntelliBlue
                is BluetoothState.Scanning -> IntelliOrange
                else -> MaterialTheme.colorScheme.onSurfaceVariant
            },
            fontWeight = if (bluetoothState is BluetoothState.Transmitting) {
                FontWeight.Bold
            } else {
                FontWeight.Normal
            },
            maxLines = 1
        )
    }
    
    // Details dialog with device attribution
    if (showDetails) {
        BluetoothDetailsDialog(
            bluetoothState = bluetoothState,
            onDismiss = { showDetails = false }
        )
    }
}

/**
 * Animated Wi-Fi scanning icon with pulse effect
 */
@Composable
fun AnimatedWiFiScanningIcon() {
    val infiniteTransition = rememberInfiniteTransition(label = "wifi_scan")
    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "wifi_scan_alpha"
    )
    
    Icon(
        imageVector = Icons.Default.Wifi,
        contentDescription = "Wi-Fi Scanning",
        tint = IntelliBlue.copy(alpha = alpha),
        modifier = Modifier.size(28.dp)
    )
}

/**
 * Animated Wi-Fi connected icon with signal strength and data transmission
 */
@Composable
fun AnimatedWiFiConnectedIcon(
    signalStrength: Int,
    isTransmitting: Boolean
) {
    val strength = signalStrength.toSignalStrength()
    val color = when (strength) {
        SignalStrength.EXCELLENT, SignalStrength.GOOD -> IntelliGreen
        SignalStrength.FAIR -> IntelliBlue
        SignalStrength.WEAK, SignalStrength.VERY_WEAK -> IntelliOrange
    }
    
    Box(contentAlignment = Alignment.Center) {
        Icon(
            imageVector = Icons.Default.Wifi,
            contentDescription = "Wi-Fi Connected",
            tint = color,
            modifier = Modifier.size(28.dp)
        )
        
        // Data transmission indicator
        if (isTransmitting) {
            val infiniteTransition = rememberInfiniteTransition(label = "wifi_transmit")
            val alpha by infiniteTransition.animateFloat(
                initialValue = 0.2f,
                targetValue = 0.8f,
                animationSpec = infiniteRepeatable(
                    animation = tween(500, easing = LinearEasing),
                    repeatMode = RepeatMode.Reverse
                ),
                label = "wifi_transmit_alpha"
            )
            
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .offset(x = 8.dp, y = (-8).dp)
                    .background(IntelliGreen.copy(alpha = alpha), CircleShape)
            )
        }
    }
}

/**
 * Animated GPS active icon with pulse effect
 */
@Composable
fun AnimatedGPSActiveIcon(
    color: Color,
    isPrecise: Boolean
) {
    val infiniteTransition = rememberInfiniteTransition(label = "gps_active")
    val scale by infiniteTransition.animateFloat(
        initialValue = 0.9f,
        targetValue = 1.1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "gps_scale"
    )
    
    Box(contentAlignment = Alignment.Center) {
        Icon(
            imageVector = Icons.Default.LocationOn,
            contentDescription = if (isPrecise) "GPS High Precision" else "GPS Active",
            tint = color,
            modifier = Modifier
                .size(28.dp)
                .scale(scale)
        )
        
        // High precision indicator
        if (isPrecise) {
            Box(
                modifier = Modifier
                    .size(6.dp)
                    .offset(x = 8.dp, y = (-8).dp)
                    .background(IntelliGreen, CircleShape)
            )
        }
    }
}

/**
 * Animated Bluetooth transmitting icon with data flow effect
 */
@Composable
fun AnimatedBluetoothTransmittingIcon() {
    val infiniteTransition = rememberInfiniteTransition(label = "bt_transmit")
    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.5f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "bt_transmit_alpha"
    )
    
    Box(contentAlignment = Alignment.Center) {
        Icon(
            imageVector = Icons.Default.BluetoothConnected,
            contentDescription = "Bluetooth Transmitting",
            tint = IntelliGreen.copy(alpha = alpha),
            modifier = Modifier.size(28.dp)
        )
        
        // Data flow indicator
        Box(
            modifier = Modifier
                .size(8.dp)
                .offset(x = 8.dp, y = (-8).dp)
                .background(IntelliGreen.copy(alpha = alpha), CircleShape)
        )
    }
}

/**
 * Animated Bluetooth scanning icon with radar pulse effect
 */
@Composable
fun AnimatedBluetoothScanningIcon(
    isDiscoverable: Boolean
) {
    val infiniteTransition = rememberInfiniteTransition(label = "bt_scan")
    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "bt_scan_rotation"
    )
    
    Icon(
        imageVector = Icons.Default.BluetoothSearching,
        contentDescription = if (isDiscoverable) "Bluetooth Discoverable" else "Bluetooth Scanning",
        tint = if (isDiscoverable) IntelliOrange else IntelliBlue,
        modifier = Modifier.size(28.dp)
    )
}

/**
 * Wi-Fi details dialog
 */
@Composable
fun WiFiDetailsDialog(
    wifiState: WiFiState,
    onDismiss: () -> Unit
) {
    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 8.dp
        ) {
            Column(
                modifier = Modifier
                    .padding(24.dp)
                    .widthIn(max = 300.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Wifi,
                        contentDescription = null,
                        tint = IntelliBlue,
                        modifier = Modifier.size(32.dp)
                    )
                    Text(
                        text = "Wi-Fi Status",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                when (wifiState) {
                    is WiFiState.Disabled -> {
                        DetailRow("Status", "Disabled")
                        DetailRow("Info", "Wi-Fi is turned off")
                    }
                    is WiFiState.Scanning -> {
                        DetailRow("Status", "Scanning")
                        DetailRow("Info", "Searching for networks")
                    }
                    is WiFiState.Connected -> {
                        DetailRow("Status", "Connected")
                        DetailRow("Network", wifiState.ssid)
                        DetailRow("Signal", "${wifiState.signalStrength} dBm")
                        DetailRow("Quality", wifiState.signalStrength.toSignalStrength().name)
                        if (wifiState.isTransmitting) {
                            DetailRow("Activity", "Transmitting Data", IntelliGreen)
                        }
                    }
                    is WiFiState.Hotspot -> {
                        DetailRow("Status", "Hotspot Active")
                        DetailRow("Devices", "${wifiState.connectedDevices} connected")
                    }
                    is WiFiState.HighDataUsage -> {
                        DetailRow("Status", "High Data Usage", IntelliRed)
                        DetailRow("App", wifiState.appName)
                        DetailRow("Usage", wifiState.dataUsed)
                    }
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Button(
                    onClick = onDismiss,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Close")
                }
            }
        }
    }
}

/**
 * GPS details dialog with privacy attribution
 */
@Composable
fun GPSDetailsDialog(
    gpsState: GPSState,
    onDismiss: () -> Unit
) {
    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 8.dp
        ) {
            Column(
                modifier = Modifier
                    .padding(24.dp)
                    .widthIn(max = 300.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.LocationOn,
                        contentDescription = null,
                        tint = IntelliGreen,
                        modifier = Modifier.size(32.dp)
                    )
                    Text(
                        text = "Location Status",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                when (gpsState) {
                    is GPSState.Disabled -> {
                        DetailRow("Status", "Disabled")
                        DetailRow("Info", "Location services are off")
                    }
                    is GPSState.Idle -> {
                        DetailRow("Status", "Idle")
                        DetailRow("Info", "Location available but not in use")
                    }
                    is GPSState.ActiveLowPrecision -> {
                        DetailRow("Status", "Active", IntelliBlue)
                        DetailRow("Precision", "Low (Network-based)")
                        gpsState.usingApp?.let {
                            DetailRow("Used by", it, IntelliOrange)
                        }
                    }
                    is GPSState.ActiveHighPrecision -> {
                        DetailRow("Status", "Active", IntelliGreen)
                        DetailRow("Precision", "High (GPS)")
                        DetailRow("Used by", gpsState.usingApp, IntelliOrange)
                        gpsState.accuracy?.let {
                            DetailRow("Accuracy", "±${it.toInt()}m")
                        }
                    }
                }
                
                // Privacy notice
                if (gpsState is GPSState.ActiveLowPrecision || gpsState is GPSState.ActiveHighPrecision) {
                    Spacer(modifier = Modifier.height(12.dp))
                    Surface(
                        color = IntelliOrange.copy(alpha = 0.1f),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Security,
                                contentDescription = null,
                                tint = IntelliOrange,
                                modifier = Modifier.size(20.dp)
                            )
                            Text(
                                text = "An app is accessing your location",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Button(
                    onClick = onDismiss,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Close")
                }
            }
        }
    }
}

/**
 * Bluetooth details dialog with device attribution
 */
@Composable
fun BluetoothDetailsDialog(
    bluetoothState: BluetoothState,
    onDismiss: () -> Unit
) {
    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 8.dp
        ) {
            Column(
                modifier = Modifier
                    .padding(24.dp)
                    .widthIn(max = 300.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Bluetooth,
                        contentDescription = null,
                        tint = IntelliBlue,
                        modifier = Modifier.size(32.dp)
                    )
                    Text(
                        text = "Bluetooth Status",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                when (bluetoothState) {
                    is BluetoothState.Disabled -> {
                        DetailRow("Status", "Disabled")
                        DetailRow("Info", "Bluetooth is turned off")
                    }
                    is BluetoothState.Idle -> {
                        DetailRow("Status", "Idle")
                        DetailRow("Info", "No active connections")
                    }
                    is BluetoothState.Connected -> {
                        DetailRow("Status", "Connected", IntelliBlue)
                        DetailRow("Device", bluetoothState.deviceName)
                        DetailRow("Type", bluetoothState.deviceType.name.lowercase().capitalize())
                    }
                    is BluetoothState.Transmitting -> {
                        DetailRow("Status", "Transmitting", IntelliGreen)
                        DetailRow("Device", bluetoothState.deviceName)
                        DetailRow("Type", bluetoothState.deviceType.name.lowercase().capitalize())
                        bluetoothState.dataType?.let {
                            DetailRow("Activity", it)
                        }
                    }
                    is BluetoothState.Scanning -> {
                        DetailRow("Status", if (bluetoothState.isDiscoverable) "Discoverable" else "Scanning", IntelliOrange)
                        DetailRow("Info", if (bluetoothState.isDiscoverable) {
                            "Your device is visible to others"
                        } else {
                            "Searching for devices"
                        })
                    }
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Button(
                    onClick = onDismiss,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Close")
                }
            }
        }
    }
}

/**
 * Helper composable for detail rows
 */
@Composable
fun DetailRow(
    label: String,
    value: String,
    valueColor: Color = MaterialTheme.colorScheme.onSurface
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium,
            color = valueColor
        )
    }
}

/**
 * Privacy Notice Banner - Explains data collection purpose
 * Shows transparency message about WiFi, GPS, and Bluetooth usage
 */
@Composable
fun PrivacyNoticeBanner(
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Icon(
                imageVector = Icons.Filled.PrivacyTip,
                contentDescription = "Privacy Notice",
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp)
            )
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = "Privacy & Data Collection",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "We collect WiFi, GPS, and Bluetooth data only during attendance marking for anti-spoofing verification. Your privacy is our priority.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                    lineHeight = 18.sp
                )
            }
        }
    }
}
