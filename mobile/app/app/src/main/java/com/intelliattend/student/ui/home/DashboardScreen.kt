package com.intelliattend.student.ui.home

import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.compose.viewModel

/**
 * Dashboard Screen - now delegates to RorkHomeScreen with modern dark theme
 */
@Composable
fun DashboardScreen(
    onNavigateToScanner: () -> Unit,
    onNavigateToHistory: () -> Unit,
    onNavigateToProfile: () -> Unit,
    viewModel: HomeViewModel = viewModel()
) {
    // Delegate to the new Rork-themed home screen
    RorkHomeScreen(
        onNavigateToProfile = onNavigateToProfile,
        onNavigateToScanner = onNavigateToScanner,
        onRefresh = { viewModel.refreshData() },
        viewModel = viewModel
    )
}
