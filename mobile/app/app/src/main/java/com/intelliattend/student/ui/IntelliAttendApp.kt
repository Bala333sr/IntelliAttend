package com.intelliattend.student.ui

import android.app.Activity
import android.content.Intent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.compose.foundation.layout.Column
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
import com.intelliattend.student.connectivity.ConnectivityViewModel
import com.intelliattend.student.ui.components.ConnectivityStatusBar

/**
 * Main app composable with navigation
 */
@Composable
fun IntelliAttendApp() {
    val navController = rememberNavController()
    val context = LocalContext.current
    val connectivityViewModel: ConnectivityViewModel = hiltViewModel()
    val isConnected by connectivityViewModel.isConnected.collectAsState()

    val biometricLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult(),
        onResult = { result ->
            if (result.resultCode == Activity.RESULT_OK) {
                if (!PermissionUtils.areAllPermissionsGranted(context)) {
                    navController.navigate("permissions")
                } else {
                    navController.navigate("home")
                }
            } else {
                // Handle biometric failure
                navController.navigate("login")
            }
        }
    )

    Column {
        ConnectivityStatusBar(isConnected = isConnected)
        MainNavigation(
            navController = navController,
            biometricLauncher = biometricLauncher,
            context = context
        )
    }
}