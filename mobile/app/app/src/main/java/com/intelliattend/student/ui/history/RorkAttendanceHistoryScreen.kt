package com.intelliattend.student.ui.history

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
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
import com.intelliattend.student.ui.components.PageIndicators
import com.intelliattend.student.ui.components.PercentageCircle
import com.intelliattend.student.ui.components.RorkCard
import com.intelliattend.student.ui.theme.*

/**
 * Rork-themed Attendance History Screen
 * Features: Bar chart trends, swipeable subject cards, attendance percentage
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RorkAttendanceHistoryScreen(
    onNavigateBack: () -> Unit,
    viewModel: AttendanceHistoryViewModel = viewModel(factory = AttendanceHistoryViewModel.Factory)
) {
    val uiState by viewModel.uiState.collectAsState()
    var selectedView by remember { mutableStateOf(1) } // 0=Day, 1=Week, 2=Month

    LaunchedEffect(Unit) {
        viewModel.loadAttendanceData()
    }

    Scaffold(
        containerColor = RorkBackground,
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Attendance Overview",
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
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(horizontal = 20.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // Attendance Trends Chart
            item {
                AttendanceTrendsCard(
                    selectedView = selectedView,
                    onViewChange = { selectedView = it },
                    percentage = uiState.attendancePercentage
                )
            }

            // Subject Attendance Section
            item {
                SubjectAttendanceSection()
            }
        }
    }
}

/**
 * Attendance Trends Chart Card with Day/Week/Month tabs
 */
@Composable
private fun AttendanceTrendsCard(
    selectedView: Int,
    onViewChange: (Int) -> Unit,
    percentage: Int
) {
    RorkCard(
        modifier = Modifier.fillMaxWidth()
    ) {
        // Header
        Text(
            text = "Attendance Trends",
            fontSize = 18.sp,
            fontWeight = FontWeight.SemiBold,
            color = RorkTextPrimary
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Day/Week/Month Tabs
        TabRow(
            selectedTabIndex = selectedView,
            containerColor = Color.Transparent,
            contentColor = RorkPrimary,
            divider = { /* No divider */ }
        ) {
            Tab(
                selected = selectedView == 0,
                onClick = { onViewChange(0) },
                text = {
                    Text(
                        "Day",
                        fontSize = 14.sp,
                        fontWeight = if (selectedView == 0) FontWeight.Bold else FontWeight.Normal
                    )
                },
                selectedContentColor = RorkPrimary,
                unselectedContentColor = RorkTextSecondary
            )
            Tab(
                selected = selectedView == 1,
                onClick = { onViewChange(1) },
                text = {
                    Text(
                        "Week",
                        fontSize = 14.sp,
                        fontWeight = if (selectedView == 1) FontWeight.Bold else FontWeight.Normal
                    )
                },
                selectedContentColor = RorkPrimary,
                unselectedContentColor = RorkTextSecondary
            )
            Tab(
                selected = selectedView == 2,
                onClick = { onViewChange(2) },
                text = {
                    Text(
                        "Month",
                        fontSize = 14.sp,
                        fontWeight = if (selectedView == 2) FontWeight.Bold else FontWeight.Normal
                    )
                },
                selectedContentColor = RorkPrimary,
                unselectedContentColor = RorkTextSecondary
            )
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Bar Chart
        val data = when (selectedView) {
            0 -> listOf( // Day view - hours of the day
                "9AM" to 100,
                "10AM" to 100,
                "11AM" to 100,
                "12PM" to 0,   // Lunch break
                "2PM" to 100,
                "3PM" to 100,
                "4PM" to 100
            )
            1 -> listOf( // Week view - days of week
                "Mon" to 85,
                "Tue" to 90,
                "Wed" to 95,
                "Thu" to 88,
                "Fri" to 92
            )
            else -> listOf( // Month view - months
                "Jan" to 80,
                "Feb" to 85,
                "Mar" to 90,
                "Apr" to 88,
                "May" to 92,
                "Jun" to 95
            )
        }

        BarChart(
            data = data,
            modifier = Modifier
                .fillMaxWidth()
                .height(180.dp)
        )

        Spacer(modifier = Modifier.height(12.dp))

        // Chart label
        Text(
            text = when (selectedView) {
                0 -> "Today's Schedule"
                1 -> "This Week"
                else -> "January - June 2025"
            },
            fontSize = 14.sp,
            color = RorkTextSecondary,
            modifier = Modifier.fillMaxWidth(),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )
    }
}


/**
 * Bar Chart Component
 */
@Composable
private fun BarChart(
    data: List<Pair<String, Int>>,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.padding(horizontal = 8.dp),
        horizontalArrangement = Arrangement.SpaceAround,
        verticalAlignment = Alignment.Bottom
    ) {
        data.forEachIndexed { index, (label, percentage) ->
            val isHighlighted = index == data.size - 1

            Column(
                modifier = Modifier.weight(1f),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Bottom
            ) {
                // Bar
                Box(
                    modifier = Modifier
                        .width(32.dp)
                        .height((percentage * 1.8).dp)
                        .clip(RoundedCornerShape(6.dp))
                        .background(
                            if (isHighlighted) RorkPrimary else RorkBorder
                        )
                )

                Spacer(modifier = Modifier.height(8.dp))

                // Label
                Text(
                    text = label,
                    fontSize = 12.sp,
                    fontWeight = if (isHighlighted) FontWeight.SemiBold else FontWeight.Normal,
                    color = if (isHighlighted) RorkPrimary else RorkTextSecondary
                )
            }
        }
    }
}

/**
 * Subject Attendance Section with swipeable cards
 */
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun SubjectAttendanceSection() {
    // Mock subject data
    val subjects = remember {
        listOf(
            SubjectData("Advanced Algorithms", "CS-401", "Dr. Sharma", 49, 50, 98),
            SubjectData("Database Management", "IS-301", "Prof. Verma", 38, 40, 95),
            SubjectData("Software Engineering", "CS-302", "Dr. Kapoor", 42, 45, 93),
            SubjectData("Operating Systems", "CS-403", "Prof. Singh", 35, 40, 88)
        )
    }

    val pagerState = rememberPagerState(pageCount = { (subjects.size + 1) / 2 })

    Column(
        modifier = Modifier.fillMaxWidth()
    ) {
        // Section header with page indicators
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Subject Attendance",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = RorkTextPrimary
            )

            val totalPages = (subjects.size + 1) / 2
            PageIndicators(
                totalPages = totalPages,
                currentPage = pagerState.currentPage
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Swipeable subject cards
        HorizontalPager(
            state = pagerState,
            modifier = Modifier.fillMaxWidth()
        ) { page ->
            SubjectCardsPage(subjects = subjects, page = page)
        }
    }
}

/**
 * Single page with up to 2 subject cards
 */
@Composable
private fun SubjectCardsPage(
    subjects: List<SubjectData>,
    page: Int
) {
    val startIndex = page * 2
    val pageSubjects = subjects.subList(
        startIndex,
        minOf(startIndex + 2, subjects.size)
    )

    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        pageSubjects.forEach { subject ->
            SubjectCard(subject = subject)
        }
    }
}

/**
 * Individual subject card
 */
@Composable
private fun SubjectCard(subject: SubjectData) {
    RorkCard(
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top
        ) {
            // Subject info
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = subject.name,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = RorkTextPrimary
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = subject.code,
                    fontSize = 13.sp,
                    color = RorkTextSecondary
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = subject.professor,
                    fontSize = 14.sp,
                    color = RorkTextSecondary
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "${subject.attended}/${subject.total} classes",
                    fontSize = 13.sp,
                    color = RorkTextSecondary
                )
            }

            // Percentage circle
            PercentageCircle(
                percentage = subject.percentage,
                size = 60
            )
        }
    }
}

/**
 * Subject data model
 */
private data class SubjectData(
    val name: String,
    val code: String,
    val professor: String,
    val attended: Int,
    val total: Int,
    val percentage: Int
)
