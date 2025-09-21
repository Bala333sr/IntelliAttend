package com.intelliattend.student.ui

import android.app.Activity
import android.content.Intent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.bt.BluetoothActivity
import com.intelliattend.student.bt.BluetoothScreen
import com.intelliattend.student.ui.auth.LoginScreen
import com.intelliattend.student.ui.auth.RegistrationScreen
import com.intelliattend.student.ui.biometric.BiometricActivity
import com.intelliattend.student.ui.home.HomeScreen
import com.intelliattend.student.ui.permissions.PermissionScreen
import com.intelliattend.student.ui.scanner.QRScannerScreen
import com.intelliattend.student.ui.server.ServerConfigScreen
import com.intelliattend.student.ui.settings.SettingsScreen
import com.intelliattend.student.ui.splash.SplashScreen
import com.intelliattend.student.ui.testing.DataTestingScreen
import com.intelliattend.student.utils.PermissionUtils

/**
 * Main app composable with navigation
 */
@Composable
fun IntelliAttendApp() {
    val navController = rememberNavController()
    val app = IntelliAttendApplication.getInstance()
    val context = LocalContext.current

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

    NavHost(
        navController = navController,
        startDestination = "splash"
    ) {
        composable("splash") {
            SplashScreen(
                onNavigateToBiometric = {
                    val intent = Intent(context, BiometricActivity::class.java)
                    biometricLauncher.launch(intent)
                },
                onNavigateToPermissions = {
                    navController.navigate("permissions") {
                        popUpTo("splash") { inclusive = true }
                    }
                },
                onNavigateToLogin = {
                    navController.navigate("login") {
                        popUpTo("splash") { inclusive = true }
                    }
                },
                onNavigateToHome = {
                    navController.navigate("home") {
                        popUpTo("splash") { inclusive = true }
                    }
                }
            )
        }

        composable("permissions") {
            PermissionScreen(
                onPermissionsGranted = {
                    // Permissions granted, proceed to home with auto-login
                    navController.navigate("home") {
                        popUpTo("permissions") { inclusive = true }
                    }
                },
                onPermissionsDenied = {
                    // For testing, we'll still allow access but show warning
                    navController.navigate("home") {
                        popUpTo("permissions") { inclusive = true }
                    }
                }
            )
        }

        composable("login") {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate("home") {
                        popUpTo("login") { inclusive = true }
                    }
                },
                onRequestPermissions = {
                    navController.navigate("permissions")
                },
                onNavigateToRegistration = {
                    navController.navigate("registration")
                }
            )
        }

        composable("registration") {
            RegistrationScreen(
                onRegistrationSuccess = {
                    navController.navigate("login") {
                        popUpTo("registration") { inclusive = true }
                    }
                },
                onBackToLogin = {
                    navController.popBackStack()
                }
            )
        }

        composable("home") {
            HomeScreen(
                onNavigateToScanner = {
                    navController.navigate("scanner")
                },
                onNavigateToDataTesting = {
                    navController.navigate("data_testing")
                },
                onNavigateToBluetooth = {
                    navController.navigate("bluetooth")
                },
                onNavigateToServerConfig = {
                    navController.navigate("settings")
                },
                onLogout = {
                    navController.navigate("login") {
                        popUpTo("home") { inclusive = true }
                    }
                }
            )
        }

        composable("scanner") {
            QRScannerScreen(
                onScanComplete = {
                    navController.popBackStack()
                },
                onBack = {
                    navController.popBackStack()
                },
                onNavigateToBluetooth = {
                    navController.navigate("bluetooth")
                }
            )
        }

        composable("bluetooth") {
            BluetoothScreen(onBack = { navController.popBackStack() })
        }

        composable("data_testing") {
            DataTestingScreen(
                onBack = {
                    navController.popBackStack()
                }
            )
        }

        composable("settings") {
            SettingsScreen(
                onNavigateToServerConfig = {
                    navController.navigate("server_config")
                },
                onBack = {
                    navController.popBackStack()
                }
            )
        }

        composable("server_config") {
            ServerConfigScreen(
                onServerConfigured = {
                    navController.popBackStack()
                },
                onBack = {
                    navController.popBackStack()
                }
            )
        }
    }
}