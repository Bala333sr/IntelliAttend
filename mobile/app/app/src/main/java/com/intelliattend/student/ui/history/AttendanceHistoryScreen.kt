package com.intelliattend.student.ui.history

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.intelliattend.student.ui.theme.IntelliBlue

@Composable
fun AttendanceHistoryScreen(
    onNavigateBack: () -> Unit,
    viewModel: AttendanceHistoryViewModel = viewModel()
) {
    // Delegate to Rork-themed Attendance History Screen
    RorkAttendanceHistoryScreen(
        onNavigateBack = onNavigateBack,
        viewModel = viewModel
    )
}

@Composable
fun OldAttendanceHistoryScreen(
    onNavigateBack: () -> Unit,
    viewModel: AttendanceHistoryViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var selectedTab by remember { mutableStateOf(2) } // Default to Month tab
    
    LaunchedEffect(Unit) {
        viewModel.loadAttendanceData()
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Attendance History") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Time period tabs
            TabRow(
                selectedTabIndex = selectedTab,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp)
            ) {
                Tab(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    text = { Text("Day") }
                )
                Tab(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    text = { Text("Week") }
                )
                Tab(
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 },
                    text = { Text("Month") }
                )
            }
            
            // Attendance percentage card
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp),
                colors = CardDefaults.cardColors(
                    containerColor = IntelliBlue.copy(alpha = 0.1f)
                )
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "You attended ${uiState.attendancePercentage}% of classes this month",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = IntelliBlue
                    )
                }
            }
            
            // Monthly overview header
            Text(
                text = "Monthly Overview",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(top = 8.dp)
            )
            
            // Week indicators
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                for (week in 1..4) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "W$week",
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                        )
                        Box(
                            modifier = Modifier
                                .size(24.dp)
                                .background(
                                    color = when {
                                        week == 1 -> Color(0xFF4CAF50).copy(alpha = 0.2f)
                                        week == 2 -> Color(0xFF4CAF50).copy(alpha = 0.4f)
                                        week == 3 -> Color(0xFF4CAF50).copy(alpha = 0.6f)
                                        else -> Color(0xFF4CAF50).copy(alpha = 0.8f)
                                    },
                                    shape = RoundedCornerShape(4.dp)
                                )
                        )
                    }
                }
            }
            
            // Details header
            Text(
                text = "Details",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(top = 8.dp)
            )
            
            // Attendance details list
            LazyColumn(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(uiState.attendanceRecords) { record ->
                    AttendanceRecordItem(record)
                }
            }
        }
    }
}

@Composable
fun AttendanceRecordItem(record: AttendanceRecord) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Status icon
        Box(
            modifier = Modifier
                .size(32.dp)
                .background(
                    color = when (record.status) {
                        AttendanceStatus.PRESENT -> Color(0xFFE8F5E9)
                        AttendanceStatus.ABSENT -> Color(0xFFFFEBEE)
                        AttendanceStatus.LATE -> Color(0xFFFFF9C4)
                        AttendanceStatus.MANUAL -> Color(0xFFE3F2FD)
                        AttendanceStatus.PENDING_SYNC -> Color(0xFFF3E5F5)
                        AttendanceStatus.SYNC_FAILED -> Color(0xFFFBE9E7)
                        AttendanceStatus.UNKNOWN -> Color(0xFFECEFF1)
                    },
                    shape = RoundedCornerShape(16.dp)
                ),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = when (record.status) {
                    AttendanceStatus.PRESENT -> Icons.Outlined.CheckCircle
                    AttendanceStatus.ABSENT -> Icons.Outlined.Cancel
                    AttendanceStatus.LATE -> Icons.Outlined.WatchLater
                    AttendanceStatus.MANUAL -> Icons.Outlined.Edit
                    AttendanceStatus.PENDING_SYNC -> Icons.Outlined.Sync
                    AttendanceStatus.SYNC_FAILED -> Icons.Outlined.SyncProblem
                    AttendanceStatus.UNKNOWN -> Icons.Outlined.Help
                },
                contentDescription = record.status.name,
                tint = when (record.status) {
                    AttendanceStatus.PRESENT -> Color(0xFF4CAF50)
                    AttendanceStatus.ABSENT -> Color(0xFFF44336)
                    AttendanceStatus.LATE -> Color(0xFFFBC02D)
                    AttendanceStatus.MANUAL -> Color(0xFF2196F3)
                    AttendanceStatus.PENDING_SYNC -> Color(0xFF9C27B0)
                    AttendanceStatus.SYNC_FAILED -> Color(0xFFFF5722)
                    AttendanceStatus.UNKNOWN -> Color(0xFF607D8B)
                },
                modifier = Modifier.size(20.dp)
            )
        }
        
        // Subject name
        Column(
            modifier = Modifier
                .weight(1f)
                .padding(horizontal = 12.dp)
        ) {
            Text(
                text = record.subject,
                fontWeight = FontWeight.Medium,
                fontSize = 16.sp
            )
            Text(
                text = record.date,
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )
        }
        
        // Status text
        Text(
            text = when (record.status) {
                AttendanceStatus.PRESENT -> "Present"
                AttendanceStatus.ABSENT -> "Absent"
                AttendanceStatus.LATE -> "Late"
                AttendanceStatus.MANUAL -> "Manual"
                AttendanceStatus.PENDING_SYNC -> "Pending Sync"
                AttendanceStatus.SYNC_FAILED -> "Sync Failed"
                AttendanceStatus.UNKNOWN -> "Unknown"
            },
            fontSize = 14.sp,
            color = when (record.status) {
                AttendanceStatus.PRESENT -> Color(0xFF4CAF50)
                AttendanceStatus.ABSENT -> Color(0xFFF44336)
                AttendanceStatus.LATE -> Color(0xFFFBC02D)
                AttendanceStatus.MANUAL -> Color(0xFF2196F3)
                AttendanceStatus.PENDING_SYNC -> Color(0xFF9C27B0)
                AttendanceStatus.SYNC_FAILED -> Color(0xFFFF5722)
                AttendanceStatus.UNKNOWN -> Color(0xFF607D8B)
            },
            fontWeight = FontWeight.Medium
        )
    }
}