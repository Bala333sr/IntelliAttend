package com.intelliattend.student.ui.permissions

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.google.accompanist.permissions.*
import com.intelliattend.student.ui.theme.IntelliGreen
import com.intelliattend.student.ui.theme.IntelliRed
import com.intelliattend.student.utils.PermissionUtils

/**
 * Composable for handling runtime permissions
 */
@OptIn(ExperimentalPermissionsApi::class, ExperimentalMaterial3Api::class)
@Composable
fun PermissionScreen(
    onPermissionsGranted: () -> Unit,
    onPermissionsDenied: () -> Unit
) {
    val context = LocalContext.current

    val permissionStates = rememberMultiplePermissionsState(
        permissions = PermissionUtils.REQUIRED_PERMISSIONS.toList()
    )

    LaunchedEffect(permissionStates.allPermissionsGranted) {
        if (permissionStates.allPermissionsGranted) {
            onPermissionsGranted()
        }
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("App Permissions", fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            )
        },
        containerColor = MaterialTheme.colorScheme.background
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.Shield,
                contentDescription = "Permissions",
                modifier = Modifier.size(80.dp),
                tint = MaterialTheme.colorScheme.primary
            )

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = "Permissions Required",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "For the app to function correctly, we need you to grant the following permissions.",
                style = MaterialTheme.typography.bodyMedium,
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(24.dp))

            LazyColumn(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(getPermissionGroups()) { group ->
                    PermissionGroupCard(
                        group = group,
                        permissionStates = permissionStates
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = {
                    if (permissionStates.allPermissionsGranted) {
                        onPermissionsGranted()
                    } else {
                        permissionStates.launchMultiplePermissionRequest()
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                shape = MaterialTheme.shapes.medium
            ) {
                Text(
                    text = if (permissionStates.allPermissionsGranted) {
                        "Continue"
                    } else {
                        "Grant All Permissions"
                    }
                )
            }

            if (!permissionStates.allPermissionsGranted &&
                permissionStates.permissions.any { it.status.shouldShowRationale }) {

                Spacer(modifier = Modifier.height(8.dp))

                TextButton(
                    onClick = onPermissionsDenied,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Skip for Now")
                }
            }
        }
    }
}

@OptIn(ExperimentalPermissionsApi::class)
@Composable
private fun PermissionGroupCard(
    group: PermissionGroup,
    permissionStates: MultiplePermissionsState
) {
    val isGranted = group.permissions.all { permission ->
        permissionStates.permissions.find { it.permission == permission }?.status?.isGranted == true
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.medium,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = group.icon,
                contentDescription = group.title,
                modifier = Modifier.size(32.dp),
                tint = if (isGranted) IntelliGreen else MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = group.title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )

                Text(
                    text = group.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Icon(
                imageVector = if (isGranted) Icons.Default.CheckCircle else Icons.Default.RadioButtonUnchecked,
                contentDescription = if (isGranted) "Granted" else "Not Granted",
                tint = if (isGranted) IntelliGreen else IntelliRed
            )
        }
    }
}

private data class PermissionGroup(
    val title: String,
    val description: String,
    val icon: ImageVector,
    val permissions: List<String>,
    val isCritical: Boolean = false
)

private fun getPermissionGroups(): List<PermissionGroup> {
    return listOf(
        PermissionGroup(
            title = "Camera Access",
            description = "To scan QR codes for attendance",
            icon = Icons.Default.CameraAlt,
            permissions = PermissionUtils.getQRScannerPermissions().toList(),
            isCritical = true
        ),
        PermissionGroup(
            title = "Location Services",
            description = "To verify your location for attendance",
            icon = Icons.Default.LocationOn,
            permissions = PermissionUtils.getLocationPermissions().toList(),
            isCritical = true
        ),
        PermissionGroup(
            title = "Biometric Authentication",
            description = "To secure your account and attendance",
            icon = Icons.Default.Fingerprint,
            permissions = PermissionUtils.getBiometricPermissions().toList(),
            isCritical = true
        ),
        PermissionGroup(
            title = "Network Access",
            description = "To connect to the attendance server",
            icon = Icons.Default.Wifi,
            permissions = listOf(
                android.Manifest.permission.ACCESS_WIFI_STATE,
                android.Manifest.permission.ACCESS_NETWORK_STATE
            ),
            isCritical = false
        ),
        PermissionGroup(
            title = "Bluetooth Access",
            description = "For proximity-based attendance marking",
            icon = Icons.Default.Bluetooth,
            permissions = PermissionUtils.getBluetoothPermissions().toList(),
            isCritical = false
        )
    )
}
