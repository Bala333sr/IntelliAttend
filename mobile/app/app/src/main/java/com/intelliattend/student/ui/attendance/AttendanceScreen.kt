package com.intelliattend.student.ui.attendance

import android.app.Application
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.intelliattend.student.ui.theme.IntelliBlue
import com.intelliattend.student.ui.theme.IntelliGreen
import com.intelliattend.student.ui.theme.IntelliRed
import com.intelliattend.student.utils.ErrorHandler
import com.intelliattend.student.utils.ErrorSnackbar

@Composable
fun AttendanceScreen(
    onNavigateBack: () -> Unit,
    viewModel: AttendanceViewModel = viewModel(factory = AttendanceViewModel.Factory)
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Attendance") },
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
        },
        snackbarHost = { SnackbarHost(hostState = snackbarHostState) }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Current Session Details
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
                        text = "Current Session Details",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text(
                                text = "Subject",
                                fontSize = 14.sp,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                            )
                            Text(
                                text = uiState.currentSubject,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Medium
                            )
                        }
                        
                        Column {
                            Text(
                                text = "Faculty",
                                fontSize = 14.sp,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                            )
                            Text(
                                text = uiState.faculty,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Medium
                            )
                        }
                    }
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text(
                                text = "Room",
                                fontSize = 14.sp,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                            )
                            Text(
                                text = uiState.room,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Medium
                            )
                        }
                    }
                }
            }
            
            // QR Code Scanner Area
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp)
                    .padding(vertical = 8.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.QrCode2,
                            contentDescription = "Scan QR Code",
                            modifier = Modifier.size(64.dp),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Scan the code on SmartBoard",
                            fontSize = 16.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            // Status Box
            Text(
                text = "Status Box",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(top = 8.dp)
            )
            
            // Verification Status Items
            VerificationStatusItem(
                title = "Biometric Verification",
                status = uiState.biometricVerification
            )
            
            VerificationStatusItem(
                title = "Bluetooth Proximity",
                status = uiState.bluetoothProximity
            )
            
            VerificationStatusItem(
                title = "Wi-Fi Verification",
                status = uiState.wifiVerification
            )
            
            VerificationStatusItem(
                title = "GPS Geofence",
                status = uiState.gpsGeofence
            )
            
            // Attendance Status Message
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (uiState.attendanceStatus.contains("Failed")) Color(0xFFFFEBEE) else Color(0xFFE8F5E9)
                )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Icon(
                        imageVector = if (uiState.attendanceStatus.contains("Failed")) 
                            Icons.Outlined.ErrorOutline else Icons.Filled.Check,
                        contentDescription = "Status",
                        tint = if (uiState.attendanceStatus.contains("Failed")) IntelliRed else IntelliGreen,
                        modifier = Modifier.size(32.dp)
                    )
                    
                    Text(
                        text = uiState.attendanceStatus,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (uiState.attendanceStatus.contains("Failed")) IntelliRed else IntelliGreen
                    )
                    
                    if (uiState.attendanceReason.isNotEmpty()) {
                        Text(
                            text = "Reason: ${uiState.attendanceReason}",
                            fontSize = 14.sp,
                            color = if (uiState.attendanceStatus.contains("Failed")) 
                                IntelliRed.copy(alpha = 0.8f) else IntelliGreen.copy(alpha = 0.8f)
                        )
                    }
                    
                    if (uiState.attendanceStatus.contains("Failed")) {
                        Button(
                            onClick = { viewModel.retryAttendance() },
                            modifier = Modifier.padding(top = 8.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = IntelliBlue)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Refresh,
                                contentDescription = "Retry",
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Retry")
                        }
                    }
                }
            }
            
            if (uiState.isLoading) {
                Box(
                    modifier = Modifier.fillMaxWidth(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(color = IntelliBlue)
                }
            }
        }
    }
}

@Composable
fun VerificationStatusItem(
    title: String,
    status: VerificationStatus
) {
    val isVerified = status == VerificationStatus.SUCCESS
    val isPending = status == VerificationStatus.PENDING
    
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = title,
            fontSize = 16.sp
        )
        
        Box(
            modifier = Modifier
                .size(24.dp)
                .background(
                    color = when(status) {
                        VerificationStatus.SUCCESS -> Color(0xFFE8F5E9)
                        VerificationStatus.FAILED -> Color(0xFFFFEBEE)
                        VerificationStatus.PENDING -> Color(0xFFFFF9C4)
                    },
                    shape = RoundedCornerShape(12.dp)
                ),
            contentAlignment = Alignment.Center
        ) {
            when(status) {
                VerificationStatus.SUCCESS -> Icon(
                    imageVector = Icons.Default.Check,
                    contentDescription = "Verified",
                    tint = IntelliGreen,
                    modifier = Modifier.size(16.dp)
                )
                VerificationStatus.FAILED -> Icon(
                    imageVector = Icons.Default.Close,
                    contentDescription = "Failed",
                    tint = IntelliRed,
                    modifier = Modifier.size(16.dp)
                )
                VerificationStatus.PENDING -> CircularProgressIndicator(
                    modifier = Modifier.size(16.dp),
                    strokeWidth = 2.dp,
                    color = Color(0xFFFFB300)
                )
            }
        }
    }
}