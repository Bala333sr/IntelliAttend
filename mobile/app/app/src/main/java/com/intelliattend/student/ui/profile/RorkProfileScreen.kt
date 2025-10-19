package com.intelliattend.student.ui.profile

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.BugReport
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.intelliattend.student.ui.components.RorkCard
import com.intelliattend.student.ui.theme.*

/**
 * Rork-themed Profile Screen
 * Minimalist design with centered avatar, device info, and preferences
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RorkProfileScreen(
    onNavigateBack: () -> Unit,
    onLogout: () -> Unit,
    onNavigateToTesting: () -> Unit = {},
    viewModel: ProfileViewModel = viewModel(factory = ProfileViewModel.Factory)
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadProfileData()
    }

    Scaffold(
        containerColor = RorkBackground,
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Profile",
                        fontWeight = FontWeight.Bold,
                        color = RorkTextPrimary
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            Icons.Default.ArrowBack,
                            contentDescription = "Back",
                            tint = RorkTextPrimary
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = RorkBackground
                )
            )
        }
    ) { paddingValues ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = RorkPrimary)
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Spacer(modifier = Modifier.height(24.dp))

                // Profile Header
                ProfileHeader(
                    name = uiState.name,
                    rollNumber = uiState.rollNumber,
                    department = uiState.department,
                    year = uiState.year,
                    profilePhotoUri = uiState.profilePhotoUri
                )

                Spacer(modifier = Modifier.height(32.dp))

                // Device Information Section
                DeviceInformationSection(
                    deviceId = uiState.deviceId,
                    lastSyncTime = uiState.lastSyncTime
                )

                Spacer(modifier = Modifier.height(24.dp))

                // Preferences Section
                PreferencesSection(
                    notificationsEnabled = uiState.notificationsEnabled,
                    darkModeEnabled = uiState.darkModeEnabled,
                    onNotificationsChange = { viewModel.toggleNotifications(it) },
                    onDarkModeChange = { viewModel.toggleDarkMode(it) }
                )

                Spacer(modifier = Modifier.height(24.dp))

                // Testing & Debug Button
                TestingDebugButton(onNavigateToTesting = onNavigateToTesting)

                Spacer(modifier = Modifier.height(16.dp))

                // Logout Button
                LogoutButton(onLogout = onLogout)

                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}

/**
 * Profile Header with avatar and info
 */
@Composable
private fun ProfileHeader(
    name: String,
    rollNumber: String,
    department: String,
    year: String,
    profilePhotoUri: String?
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Avatar with camera button
        Box(
            modifier = Modifier.size(80.dp)
        ) {
            // Avatar circle
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .clip(CircleShape)
                    .background(RorkPrimary.copy(alpha = 0.2f)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = name.firstOrNull()?.toString() ?: "?",
                    fontSize = 32.sp,
                    fontWeight = FontWeight.Bold,
                    color = RorkPrimary
                )
            }

            // Camera button overlay
            Box(
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .offset(x = (-2).dp, y = (-2).dp)
                    .size(32.dp)
                    .clip(CircleShape)
                    .background(RorkPrimary),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.CameraAlt,
                    contentDescription = "Change Photo",
                    tint = Color.White,
                    modifier = Modifier.size(16.dp)
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Name
        Text(
            text = name,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            color = RorkTextPrimary
        )

        Spacer(modifier = Modifier.height(4.dp))

        // Roll Number
        Text(
            text = "Roll No: $rollNumber",
            fontSize = 16.sp,
            color = RorkTextSecondary
        )

        Spacer(modifier = Modifier.height(4.dp))

        // Department and Year
        Text(
            text = "$department, $year Year",
            fontSize = 16.sp,
            color = RorkTextSecondary
        )
    }
}

/**
 * Device Information Section
 */
@Composable
private fun DeviceInformationSection(
    deviceId: String,
    lastSyncTime: String
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp)
    ) {
        Text(
            text = "Device Information",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            color = RorkTextPrimary
        )

        Spacer(modifier = Modifier.height(12.dp))

        // Device ID Card
        RorkCard(modifier = Modifier.fillMaxWidth()) {
            Column {
                Text(
                    text = "Device ID",
                    fontSize = 14.sp,
                    color = RorkTextSecondary
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = deviceId,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    color = RorkTextPrimary
                )
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Last Sync Card
        RorkCard(modifier = Modifier.fillMaxWidth()) {
            Column {
                Text(
                    text = "Last Sync",
                    fontSize = 14.sp,
                    color = RorkTextSecondary
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = lastSyncTime,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    color = RorkTextPrimary
                )
            }
        }
    }
}

/**
 * Preferences Section
 */
@Composable
private fun PreferencesSection(
    notificationsEnabled: Boolean,
    darkModeEnabled: Boolean,
    onNotificationsChange: (Boolean) -> Unit,
    onDarkModeChange: (Boolean) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp)
    ) {
        Text(
            text = "Preferences",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            color = RorkTextPrimary
        )

        Spacer(modifier = Modifier.height(12.dp))

        // Preferences Card with both toggles
        RorkCard(modifier = Modifier.fillMaxWidth()) {
            Column {
                // Notifications Toggle
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "Notifications",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Medium,
                            color = RorkTextPrimary
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = "Receive attendance reminders",
                            fontSize = 14.sp,
                            color = RorkTextSecondary
                        )
                    }

                    Switch(
                        checked = notificationsEnabled,
                        onCheckedChange = onNotificationsChange,
                        colors = SwitchDefaults.colors(
                            checkedThumbColor = Color.White,
                            checkedTrackColor = RorkPrimary,
                            uncheckedThumbColor = Color.White,
                            uncheckedTrackColor = RorkBorder
                        )
                    )
                }

                // Divider
                Spacer(modifier = Modifier.height(16.dp))
                HorizontalDivider(
                    modifier = Modifier.fillMaxWidth(),
                    color = RorkBorder
                )
                Spacer(modifier = Modifier.height(16.dp))

                // Dark Mode Toggle
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "Dark Mode",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Medium,
                            color = RorkTextPrimary
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = "Switch between light and dark theme",
                            fontSize = 14.sp,
                            color = RorkTextSecondary
                        )
                    }

                    Switch(
                        checked = darkModeEnabled,
                        onCheckedChange = onDarkModeChange,
                        colors = SwitchDefaults.colors(
                            checkedThumbColor = Color.White,
                            checkedTrackColor = RorkPrimary,
                            uncheckedThumbColor = Color.White,
                            uncheckedTrackColor = RorkBorder
                        )
                    )
                }
            }
        }
    }
}

/**
 * Testing & Debug Button
 */
@Composable
private fun TestingDebugButton(
    onNavigateToTesting: () -> Unit
) {
    OutlinedButton(
        onClick = onNavigateToTesting,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp)
            .height(56.dp),
        colors = ButtonDefaults.outlinedButtonColors(
            contentColor = RorkPrimary
        ),
        border = androidx.compose.foundation.BorderStroke(1.dp, RorkPrimary),
        shape = RoundedCornerShape(12.dp)
    ) {
        Icon(
            imageVector = Icons.Default.BugReport,
            contentDescription = "Testing",
            modifier = Modifier.size(22.dp)
        )
        Spacer(modifier = Modifier.width(10.dp))
        Text(
            text = "Testing & Debug",
            fontSize = 17.sp,
            fontWeight = FontWeight.SemiBold
        )
    }
}

/**
 * Logout Button
 */
@Composable
private fun LogoutButton(
    onLogout: () -> Unit
) {
    Button(
        onClick = onLogout,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp)
            .height(56.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = RorkDanger.copy(alpha = 0.2f),
            contentColor = RorkDanger
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Icon(
            imageVector = Icons.Default.Logout,
            contentDescription = "Logout",
            modifier = Modifier.size(22.dp)
        )
        Spacer(modifier = Modifier.width(10.dp))
        Text(
            text = "Logout",
            fontSize = 17.sp,
            fontWeight = FontWeight.SemiBold
        )
    }
}
