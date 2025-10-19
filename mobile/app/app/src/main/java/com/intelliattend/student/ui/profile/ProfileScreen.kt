package com.intelliattend.student.ui.profile

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import com.intelliattend.student.ui.theme.IntelliBlue
import com.intelliattend.student.ui.theme.LocalThemeManager
import com.intelliattend.student.ui.connectivity.ConnectivityViewModel
import com.intelliattend.student.ui.components.ConnectivityStatusBar
import com.intelliattend.student.ui.components.PrivacyNoticeBanner

@Composable
fun ProfileScreen(
    onNavigateBack: () -> Unit,
    onLogout: () -> Unit,
    onNavigateToTesting: () -> Unit = {},
    viewModel: ProfileViewModel = viewModel(factory = ProfileViewModel.Factory),
    connectivityViewModel: ConnectivityViewModel = viewModel()
) {
    // Delegate to Rork-themed Profile Screen
    RorkProfileScreen(
        onNavigateBack = onNavigateBack,
        onLogout = onLogout,
        onNavigateToTesting = onNavigateToTesting,
        viewModel = viewModel
    )
}

@Composable
fun OldProfileScreen(
    onNavigateBack: () -> Unit,
    onLogout: () -> Unit,
    onNavigateToTesting: () -> Unit = {},
    viewModel: ProfileViewModel = viewModel(factory = ProfileViewModel.Factory),
    connectivityViewModel: ConnectivityViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val connectivityStatus by connectivityViewModel.connectivityStatus.collectAsState()
    val context = LocalContext.current
    val themeManager = LocalThemeManager.current
    val isDarkMode by themeManager.isDarkMode.collectAsState()
    
    // Image picker launcher
    val imagePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        uri?.let {
            viewModel.updateProfilePhoto(it)
        }
    }
    
    LaunchedEffect(Unit) {
        viewModel.loadProfileData()
        connectivityViewModel.startMonitoring()
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Text(
                        "Profile & Settings",
                        fontWeight = FontWeight.Bold,
                        fontSize = 20.sp
                    ) 
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            Icons.Default.ArrowBack, 
                            contentDescription = "Back",
                            tint = Color.Black
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color(0xFFF5F5F5),
                    titleContentColor = Color.Black
                )
            )
        },
        containerColor = Color(0xFFF5F5F5)
    ) { paddingValues ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = IntelliBlue)
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .verticalScroll(rememberScrollState())
            ) {
                // Privacy Notice Banner - Transparency
                PrivacyNoticeBanner(
                    modifier = Modifier.padding(top = 8.dp)
                )
                
                // Connectivity Status Bar - Real-time sensor monitoring
                ConnectivityStatusBar(
                    connectivityStatus = connectivityStatus,
                    modifier = Modifier.padding(top = 8.dp, bottom = 8.dp)
                )
                
                // Profile Header Section
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color(0xFFF5F5F5))
                        .padding(top = 24.dp, bottom = 32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // Avatar with teal background circle - clickable for photo upload
                    Box(
                        modifier = Modifier
                            .size(140.dp)
                            .clip(CircleShape)
                            .background(Color(0xFF406C6C))
                            .clickable {
                                imagePickerLauncher.launch("image/*")
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        if (uiState.profilePhotoUri != null) {
                            AsyncImage(
                                model = uiState.profilePhotoUri,
                                contentDescription = "Profile Picture",
                                modifier = Modifier
                                    .size(140.dp)
                                    .clip(CircleShape),
                                contentScale = ContentScale.Crop
                            )
                        } else {
                            Icon(
                                Icons.Outlined.Person,
                                contentDescription = "Profile Picture",
                                modifier = Modifier.size(100.dp),
                                tint = Color.White
                            )
                        }
                        
                        // Camera icon overlay
                        Box(
                            modifier = Modifier
                                .align(Alignment.BottomEnd)
                                .size(40.dp)
                                .clip(CircleShape)
                                .background(IntelliBlue),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                Icons.Filled.CameraAlt,
                                contentDescription = "Change Photo",
                                tint = Color.White,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(20.dp))
                    
                    // Student Name
                    Text(
                        text = uiState.name,
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF1A1A1A)
                    )
                    
                    Spacer(modifier = Modifier.height(6.dp))
                    
                    // Roll Number
                    Text(
                        text = "Roll No: ${uiState.rollNumber}",
                        fontSize = 16.sp,
                        color = Color(0xFF666666)
                    )
                    
                    Spacer(modifier = Modifier.height(4.dp))
                    
                    // Department and Year
                    Text(
                        text = "${uiState.department}, ${uiState.year} Year",
                        fontSize = 16.sp,
                        color = Color(0xFF666666)
                    )
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                // Device Info Section
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                ) {
                    Text(
                        text = "Device Info",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF2196F3)
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Device Info Card
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = Color.White
                        ),
                        shape = RoundedCornerShape(12.dp),
                        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(20.dp)
                        ) {
                            // Registered Device ID
                            Text(
                                text = "Registered Device ID",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Medium,
                                color = Color(0xFF1A1A1A)
                            )
                            Spacer(modifier = Modifier.height(6.dp))
                            Text(
                                text = uiState.deviceId,
                                fontSize = 15.sp,
                                color = Color(0xFF666666)
                            )
                            
                            Spacer(modifier = Modifier.height(24.dp))
                            
                            // Last Sync Time
                            Text(
                                text = "Last Sync Time",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Medium,
                                color = Color(0xFF1A1A1A)
                            )
                            Spacer(modifier = Modifier.height(6.dp))
                            Text(
                                text = uiState.lastSyncTime,
                                fontSize = 15.sp,
                                color = Color(0xFF666666)
                            )
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // Preferences Section
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                ) {
                    Text(
                        text = "Preferences",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF2196F3)
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Preferences Card
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = Color.White
                        ),
                        shape = RoundedCornerShape(12.dp),
                        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 8.dp)
                        ) {
                            // Notifications toggle
                            ModernToggleItem(
                                title = "Notifications",
                                checked = uiState.notificationsEnabled,
                                onCheckedChange = { viewModel.toggleNotifications(it) }
                            )
                            
                            HorizontalDivider(
                                modifier = Modifier.padding(horizontal = 20.dp),
                                color = Color(0xFFE0E0E0)
                            )
                            
                            // Dark Mode toggle
                            ModernToggleItem(
                                title = "Dark Mode",
                                checked = isDarkMode,
                                onCheckedChange = { enabled ->
                                    themeManager.setDarkMode(enabled)
                                    viewModel.toggleDarkMode(enabled)
                                }
                            )
                        }
                    }
                }
                
                Spacer(modifier = Modifier.height(32.dp))
                
                // Testing Button
                OutlinedButton(
                    onClick = onNavigateToTesting,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .height(56.dp),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = IntelliBlue
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(
                        Icons.Outlined.BugReport,
                        contentDescription = "Testing",
                        modifier = Modifier.size(22.dp)
                    )
                    Spacer(modifier = Modifier.width(10.dp))
                    Text(
                        "Testing & Debug", 
                        fontSize = 17.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Logout Button
                Button(
                    onClick = onLogout,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFFFFE5E5),
                        contentColor = Color(0xFFE53935)
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(
                        Icons.Filled.Logout,
                        contentDescription = "Logout",
                        modifier = Modifier.size(22.dp)
                    )
                    Spacer(modifier = Modifier.width(10.dp))
                    Text(
                        "Logout", 
                        fontSize = 17.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }
                
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}

/**
 * Modern toggle item matching the design from the image
 */
@Composable
fun ModernToggleItem(
    title: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp, vertical = 16.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = title,
            fontSize = 17.sp,
            fontWeight = FontWeight.Normal,
            color = Color(0xFF1A1A1A)
        )
        
        Switch(
            checked = checked,
            onCheckedChange = onCheckedChange,
            colors = SwitchDefaults.colors(
                checkedThumbColor = Color.White,
                checkedTrackColor = Color(0xFF2196F3),
                uncheckedThumbColor = Color.White,
                uncheckedTrackColor = Color(0xFFBDBDBD)
            )
        )
    }
}
