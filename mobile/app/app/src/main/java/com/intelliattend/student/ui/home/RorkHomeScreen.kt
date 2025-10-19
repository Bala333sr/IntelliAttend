package com.intelliattend.student.ui.home

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.rememberAsyncImagePainter
import com.intelliattend.student.data.model.ClassSession
import com.intelliattend.student.data.model.ClassStatus
import com.intelliattend.student.data.model.Student
import com.intelliattend.student.ui.components.*
import com.intelliattend.student.ui.theme.*

/**
 * Rork-themed Home Screen
 * Modern dark theme with swipeable class cards matching React Native design
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RorkHomeScreen(
    onNavigateToProfile: () -> Unit,
    onNavigateToScanner: () -> Unit,
    onRefresh: () -> Unit,
    viewModel: HomeViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadData()
    }

    Scaffold(
        containerColor = RorkBackground,
        topBar = {
            // No top bar - cleaner design like RN
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(top = 60.dp, bottom = 100.dp),
            verticalArrangement = Arrangement.spacedBy(0.dp)
        ) {
            // Header with greeting and avatar
            item {
                RorkHeader(
                    student = uiState.student,
                    onProfileClick = onNavigateToProfile,
                    onRefreshClick = onRefresh
                )
            }

            // Today's Classes Section
            item {
                Spacer(modifier = Modifier.height(32.dp))
                TodayClassesSection(
                    classes = uiState.todayClasses,
                    currentPage = uiState.currentPage,
                    isLoading = uiState.isLoading
                )
            }

            // Quick Actions (kept from original - for scanner)
            item {
                Spacer(modifier = Modifier.height(24.dp))
                QuickActionsRork(
                    onScanQR = onNavigateToScanner
                )
            }
        }
    }
}

/**
 * Header with greeting and profile avatar
 */
@Composable
private fun RorkHeader(
    student: Student?,
    onProfileClick: () -> Unit,
    onRefreshClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Greeting
        Column {
            Text(
                text = "Hi, ${student?.firstName ?: "Student"} 👋",
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold,
                color = RorkTextPrimary
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Ready for your classes?",
                fontSize = 16.sp,
                color = RorkTextSecondary
            )
        }

        // Avatar with online indicator - clickable to go to profile
        Box(
            modifier = Modifier
                .size(56.dp)
                .clip(CircleShape)
                .background(RorkCardBackground)
                .clickable { onProfileClick() }
        ) {
            // Profile image or initial
            if (student != null) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(RorkPrimary.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = student.firstName?.firstOrNull()?.toString() ?: "?",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = RorkPrimary
                    )
                }
            } else {
                Icon(
                    imageVector = Icons.Default.Person,
                    contentDescription = "Profile",
                    tint = RorkTextSecondary,
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(12.dp)
                )
            }

            // Online indicator
            OnlineIndicator(
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .padding(2.dp)
            )
        }
    }
}

/**
 * Today's Classes Section with swipeable paginated cards
 */
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun TodayClassesSection(
    classes: List<ClassSession>,
    currentPage: Int,
    isLoading: Boolean
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp)
    ) {
        // Section header with page indicators
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Today's Classes",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = RorkTextPrimary
            )

            if (classes.isNotEmpty()) {
                val totalPages = (classes.size + 1) / 2  // 2 cards per page
                PageIndicators(
                    totalPages = totalPages,
                    currentPage = currentPage
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Swipeable class cards
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(400.dp),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = RorkPrimary)
            }
        } else if (classes.isEmpty()) {
            EmptyClassesCard()
        } else {
            ClassCardsPager(classes = classes, currentPage = currentPage)
        }
    }
}

/**
 * Horizontal pager for class cards (2 per page)
 */
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun ClassCardsPager(
    classes: List<ClassSession>,
    currentPage: Int
) {
    val pagerState = rememberPagerState(
        initialPage = currentPage,
        pageCount = { (classes.size + 1) / 2 }
    )

    HorizontalPager(
        state = pagerState,
        modifier = Modifier.fillMaxWidth(),
        pageSpacing = 0.dp
    ) { page ->
        ClassCardsPage(
            classes = classes,
            page = page
        )
    }
}

/**
 * Single page with up to 2 class cards
 */
@Composable
private fun ClassCardsPage(
    classes: List<ClassSession>,
    page: Int
) {
    val startIndex = page * 2
    val pageClasses = classes.subList(
        startIndex,
        minOf(startIndex + 2, classes.size)
    )

    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        pageClasses.forEach { classSession ->
            ClassCard(classSession = classSession)
        }
    }
}

/**
 * Individual class card
 */
@Composable
private fun ClassCard(classSession: ClassSession) {
    val isUpcoming = classSession.status is ClassStatus.StartingSoon ||
                     classSession.status is ClassStatus.StartingNow

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = RorkCardBackground
        ),
        border = if (isUpcoming) {
            androidx.compose.foundation.BorderStroke(2.dp, RorkSuccess)
        } else null
    ) {
        Column {
            // Upcoming badge
            if (isUpcoming) {
                val minutesText = when (val status = classSession.status) {
                    is ClassStatus.StartingSoon -> status.message
                    is ClassStatus.StartingNow -> status.message
                    else -> "Starting soon"
                }
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(RorkSuccess)
                        .padding(vertical = 8.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = minutesText,
                        color = Color.White,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }

            // Card content
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Class info
                Column(
                    modifier = Modifier.weight(1f)
                ) {
                    Text(
                        text = classSession.subjectCode,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = RorkTextPrimary
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = classSession.subjectName,
                        fontSize = 14.sp,
                        color = RorkTextSecondary
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "👨‍🏫 ${classSession.teacherName}",
                        fontSize = 16.sp,
                        color = RorkTextSecondary
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "${classSession.startTime} - ${classSession.endTime}",
                        fontSize = 16.sp,
                        color = RorkTextSecondary
                    )
                }

                // Icon container
                val (icon, color) = getClassIcon(classSession.subjectCode)
                ColoredIconContainer(
                    icon = icon,
                    iconColor = color,
                    backgroundColor = color.copy(alpha = 0.2f),
                    size = 64
                )
            }
        }
    }
}

/**
 * Get icon and color for a class based on subject code
 */
private fun getClassIcon(subjectCode: String): Pair<ImageVector, Color> {
    return when {
        subjectCode.contains("CS", ignoreCase = true) ||
        subjectCode.contains("SE", ignoreCase = true) -> Icons.Default.Code to RorkIconOrange
        subjectCode.contains("DB", ignoreCase = true) ||
        subjectCode.contains("IS", ignoreCase = true) -> Icons.Default.Storage to RorkIconBlue
        subjectCode.contains("OS", ignoreCase = true) -> Icons.Default.Computer to RorkIconPurple
        subjectCode.contains("AI", ignoreCase = true) ||
        subjectCode.contains("ML", ignoreCase = true) -> Icons.Default.SmartToy to RorkIconGreen
        subjectCode.contains("CN", ignoreCase = true) ||
        subjectCode.contains("NET", ignoreCase = true) -> Icons.Default.CloudQueue to RorkIconCyan
        else -> Icons.Default.MenuBook to RorkIconOrange
    }
}

/**
 * Empty state card
 */
@Composable
private fun EmptyClassesCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = RorkCardBackground
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(40.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.EventBusy,
                contentDescription = "No classes",
                tint = RorkTextSecondary,
                modifier = Modifier.size(48.dp)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "No classes today",
                fontSize = 18.sp,
                fontWeight = FontWeight.Medium,
                color = RorkTextPrimary
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Enjoy your free day!",
                fontSize = 14.sp,
                color = RorkTextSecondary
            )
        }
    }
}

/**
 * Quick Actions section
 */
@Composable
private fun QuickActionsRork(
    onScanQR: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp)
    ) {
        Button(
            onClick = onScanQR,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = RorkPrimary
            ),
            shape = RoundedCornerShape(12.dp)
        ) {
            Icon(
                imageVector = Icons.Default.QrCodeScanner,
                contentDescription = "Scan QR",
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Text(
                text = "Scan QR for Attendance",
                fontSize = 17.sp,
                fontWeight = FontWeight.SemiBold
            )
        }
    }
}
