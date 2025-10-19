package com.intelliattend.student.ui.timetable

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.intelliattend.student.data.model.TimetableSlot
import com.intelliattend.student.data.model.StudentTimetable

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TimetableScreen(
    onNavigateBack: () -> Unit,
    viewModel: TimetableViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("My Timetable") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.refreshTimetable() }) {
                        Icon(Icons.Default.Refresh, "Refresh")
                    }
                }
            )
        }
    ) { padding ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else if (uiState.error != null) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text("Error: ${uiState.error}")
            }
        } else if (uiState.timetable != null) {
            Column(modifier = Modifier.padding(padding)) {
                // Day tabs
                ScrollableTabRow(selectedTabIndex = getSelectedDayIndex(uiState.selectedDay, uiState.timetable!!)) {
                    uiState.timetable!!.getDaysInOrder().forEach { day ->
                        Tab(
                            selected = day == uiState.selectedDay,
                            onClick = { viewModel.selectDay(day) },
                            text = { Text(day.take(3)) }
                        )
                    }
                }
                
                // Timetable slots for selected day
                LazyColumn {
                    items(uiState.timetable!!.getScheduleForDay(uiState.selectedDay)) { slot ->
                        TimetableSlotItem(slot)
                    }
                }
            }
        } else {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text("No timetable data available")
            }
        }
    }
}

@Composable
fun TimetableSlotItem(slot: TimetableSlot) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = when (slot.slotType) {
                "regular" -> MaterialTheme.colorScheme.primaryContainer
                "lab" -> MaterialTheme.colorScheme.secondaryContainer
                "break", "lunch" -> MaterialTheme.colorScheme.surfaceVariant
                else -> MaterialTheme.colorScheme.surface
            }
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Column {
                Text(
                    text = slot.shortName,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                if (slot.facultyName != null) {
                    Text(
                        text = slot.facultyName,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = slot.getTimeRange(),
                    style = MaterialTheme.typography.bodySmall
                )
                Text(
                    text = "Room ${slot.room}",
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

private fun getSelectedDayIndex(selectedDay: String, timetable: StudentTimetable): Int {
    val daysOrder = listOf("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY")
    return daysOrder.indexOfFirst { it == selectedDay.uppercase() }
}