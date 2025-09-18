package com.intelliattend.student.ui.settings

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Dns
import androidx.compose.material.icons.filled.Fingerprint
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Policy
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.utils.BiometricHelper
import com.intelliattend.student.utils.BiometricStatus

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    modifier: Modifier = Modifier,
    onNavigateToServerConfig: () -> Unit,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    val app = IntelliAttendApplication.getInstance()
    val biometricHelper = BiometricHelper(context)

    var isBiometricEnabled by remember { mutableStateOf(app.getAppPreferences().isBiometricEnabled) }
    val biometricStatus = biometricHelper.getBiometricStatus()

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Settings", fontWeight = FontWeight.Bold) },
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
                SettingsGroup(title = "Security") {
                    SettingsListItem(
                        icon = Icons.Default.Fingerprint,
                        title = "Biometric Authentication",
                        subtitle = "Require biometric authentication to access the app",
                        action = {
                            Switch(
                                checked = isBiometricEnabled,
                                onCheckedChange = { checked ->
                                    isBiometricEnabled = checked
                                    app.getAppPreferences().isBiometricEnabled = checked
                                },
                                enabled = biometricStatus == BiometricStatus.AVAILABLE
                            )
                        }
                    )
                    if (biometricStatus != BiometricStatus.AVAILABLE) {
                        Text(
                            text = when (biometricStatus) {
                                BiometricStatus.NOT_ENROLLED -> "No biometric credentials enrolled. Please set up fingerprint or face unlock in device settings"
                                BiometricStatus.UNSUPPORTED -> "Biometric authentication is not supported on this device"
                                else -> "Biometric authentication is currently unavailable"
                            },
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.error,
                            modifier = Modifier.padding(horizontal = 16.dp)
                        )
                    }
                }
            }

            item {
                SettingsGroup(title = "Server") {
                    SettingsListItem(
                        icon = Icons.Default.Dns,
                        title = "Server Configuration",
                        subtitle = "Current: ${app.getAppPreferences().baseUrl}",
                        onClick = onNavigateToServerConfig
                    )
                }
            }

            item {
                SettingsGroup(title = "About") {
                    SettingsListItem(
                        icon = Icons.Default.Info,
                        title = "App Version",
                        subtitle = "1.0.0 (Testing Mode)"
                    )
                    SettingsListItem(
                        icon = Icons.Default.Policy,
                        title = "Privacy Policy",
                        subtitle = "View our privacy policy and data handling practices"
                    )
                }
            }
        }
    }
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