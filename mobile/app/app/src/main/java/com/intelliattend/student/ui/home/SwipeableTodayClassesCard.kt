package com.intelliattend.student.ui.home

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.google.accompanist.pager.*
import com.google.accompanist.swiperefresh.SwipeRefresh
import com.google.accompanist.swiperefresh.rememberSwipeRefreshState
import com.intelliattend.student.data.model.ClassPage
import com.intelliattend.student.data.model.ClassSession
import com.intelliattend.student.data.model.ClassStatus
import kotlinx.coroutines.launch

@Composable
fun SwipeableTodayClassesCard(
    classes: List<ClassSession>,
    currentPage: Int = 0,
    onClassClick: (ClassSession) -> Unit,
    onRefresh: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    var isRefreshing by remember { mutableStateOf(false) }
    
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(16.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        SwipeRefresh(
            state = rememberSwipeRefreshState(isRefreshing),
            onRefresh = {
                isRefreshing = true
                onRefresh()
                // Simulate refresh completion
                // In a real app, this would be handled by the ViewModel
                isRefreshing = false
            }
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                // Header
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Today's Classes",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    
                    // Date
                    Text(
                        text = java.time.LocalDate.now().format(
                            java.time.format.DateTimeFormatter.ofPattern("MMM dd, yyyy")
                        ),
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                // Content based on classes
                if (classes.isEmpty()) {
                    EmptyState()
                } else {
                    // Group classes into pages of 2
                    val pages = classes.chunked(2) { pageClasses ->
                        ClassPage(classes = pageClasses.toList())
                    }
                    
                    if (pages.isEmpty()) {
                        EmptyState()
                    } else {
                        // Show swipeable pager
                        SwipeableClassPager(
                            pages = pages,
                            currentPage = currentPage,
                            onClassClick = onClassClick
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SwipeableClassPager(
    pages: List<ClassPage>,
    currentPage: Int = 0,
    onClassClick: (ClassSession) -> Unit
) {
    val pagerState = rememberPagerState(initialPage = currentPage)
    val coroutineScope = rememberCoroutineScope()
    
    Column(
        modifier = Modifier.fillMaxWidth()
    ) {
        // Pager content
        HorizontalPager(
            count = pages.size,
            state = pagerState,
            modifier = Modifier.fillMaxWidth()
        ) { page ->
            ClassPageView(
                page = pages[page],
                onClassClick = onClassClick
            )
        }
        
        // Page indicators
        if (pages.size > 1) {
            Spacer(modifier = Modifier.height(16.dp))
            
            HorizontalPagerIndicator(
                pagerState = pagerState,
                pageCount = pages.size,
                modifier = Modifier
                    .align(Alignment.CenterHorizontally)
                    .padding(8.dp),
                activeColor = MaterialTheme.colorScheme.primary,
                inactiveColor = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
            )
        }
    }
}

@Composable
private fun ClassPageView(
    page: ClassPage,
    onClassClick: (ClassSession) -> Unit
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        page.classes.forEach { classSession ->
            ClassCard(
                classSession = classSession,
                onClick = { onClassClick(classSession) }
            )
        }
    }
}

@Composable
private fun ClassCard(
    classSession: ClassSession,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(8.dp),
        colors = CardDefaults.cardColors(
            containerColor = getStatusBackgroundColor(classSession.status)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            // Status and Icon
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = getStatusText(classSession.status),
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    color = getStatusTextColor(classSession.status)
                )
                
                classSession.icon?.let {
                    Text(
                        text = it,
                        fontSize = 20.sp
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Subject Info
            Text(
                text = classSession.subjectName,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Text(
                text = classSession.subjectCode,
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(4.dp))
            
            // Teacher and Time
            Text(
                text = classSession.teacherName,
                fontSize = 16.sp,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Text(
                text = "${classSession.startTime} - ${classSession.endTime}",
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            classSession.roomNumber?.let {
                Text(
                    text = "Room $it",
                    fontSize = 14.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun EmptyState() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Emoji icon
        Text(
            text = "📅",
            fontSize = 48.sp,
            modifier = Modifier.padding(bottom = 16.dp)
        )
        
        Text(
            text = "No Classes Scheduled Today",
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface,
            modifier = Modifier.padding(bottom = 8.dp)
        )
        
        Text(
            text = "Enjoy your break!",
            fontSize = 16.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun getStatusBackgroundColor(status: ClassStatus): Color {
    return when (status) {
        is ClassStatus.UpcomingLong -> Color(0xFF4CAF50).copy(alpha = 0.1f) // Green
        is ClassStatus.Upcoming -> Color(0xFF4CAF50).copy(alpha = 0.1f) // Green
        is ClassStatus.StartingSoon -> Color(0xFFFFC107).copy(alpha = 0.1f) // Yellow
        is ClassStatus.StartingNow -> Color(0xFFF44336).copy(alpha = 0.1f) // Red
        is ClassStatus.InProgress -> Color(0xFFFF9800).copy(alpha = 0.1f) // Orange
        is ClassStatus.Completed -> Color(0xFF9E9E9E).copy(alpha = 0.1f) // Gray
    }
}

@Composable
private fun getStatusTextColor(status: ClassStatus): Color {
    return when (status) {
        is ClassStatus.UpcomingLong -> Color(0xFF4CAF50) // Green
        is ClassStatus.Upcoming -> Color(0xFF4CAF50) // Green
        is ClassStatus.StartingSoon -> Color(0xFFFFC107) // Yellow
        is ClassStatus.StartingNow -> Color(0xFFF44336) // Red
        is ClassStatus.InProgress -> Color(0xFFFF9800) // Orange
        is ClassStatus.Completed -> Color(0xFF9E9E9E) // Gray
    }
}

@Composable
private fun getStatusText(status: ClassStatus): String {
    return when (status) {
        is ClassStatus.UpcomingLong -> status.message
        is ClassStatus.Upcoming -> status.message
        is ClassStatus.StartingSoon -> status.message
        is ClassStatus.StartingNow -> status.message
        is ClassStatus.InProgress -> status.message
        is ClassStatus.Completed -> status.message
    }
}