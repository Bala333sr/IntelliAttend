package com.intelliattend.student.ui.navigation

import android.app.Activity
import android.content.Intent
import androidx.activity.result.ActivityResultLauncher
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.outlined.Analytics
import androidx.compose.material.icons.outlined.Dashboard
import androidx.compose.material.icons.outlined.History
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.NavController
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import com.intelliattend.student.bt.BluetoothScreen
import com.intelliattend.student.ui.auth.LoginScreen
import com.intelliattend.student.ui.auth.RegistrationScreen
import com.intelliattend.student.ui.biometric.BiometricActivity
import com.intelliattend.student.ui.history.AttendanceHistoryScreen
import com.intelliattend.student.ui.home.HomeScreen
import com.intelliattend.student.ui.permissions.PermissionScreen
import com.intelliattend.student.ui.profile.ProfileScreen
import com.intelliattend.student.ui.scanner.QRScannerScreen
import com.intelliattend.student.ui.server.ServerConfigScreen
import com.intelliattend.student.ui.settings.SettingsScreen
import com.intelliattend.student.ui.splash.SplashScreen
// import com.intelliattend.student.ui.statistics.AttendanceStatisticsScreen
import com.intelliattend.student.ui.testing.DataTestingScreen
import com.intelliattend.student.ui.testing.TestingScreen
import com.intelliattend.student.ui.testing.WarmScanTestScreen
import com.intelliattend.student.ui.device.DeviceSwitchScreen

/**
 * Main navigation component with bottom navigation bar
 */
@Composable
fun MainNavigation(
    navController: NavController,
    biometricLauncher: ActivityResultLauncher<Intent>,
    context: android.content.Context
) {
    val items = listOf(
        NavigationItem("home", "Home", Icons.Outlined.Dashboard),
        NavigationItem("history", "History", Icons.Outlined.History),
        // NavigationItem("statistics", "Statistics", Icons.Outlined.Analytics),
        NavigationItem("profile", "Profile", Icons.Outlined.Person)
    )
    
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination
    val currentRoute = navBackStackEntry?.destination?.route
    
    // Only show bottom navigation for main screens
    val showBottomBar = currentRoute in items.map { it.route }
    
    Scaffold(
        bottomBar = {
            if (showBottomBar) {
                NavigationBar {
                    items.forEach { item ->
                        val selected = currentDestination?.hierarchy?.any { it.route == item.route } == true
                        
                        NavigationBarItem(
                            icon = { Icon(item.icon, contentDescription = item.title) },
                            label = { Text(item.title) },
                            selected = selected,
                            onClick = {
                                navController.navigate(item.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            }
                        )
                    }
                }
            }
        },
        floatingActionButton = {
            // Center FAB shown on Home only; use to open scanner
            if (currentRoute == "home") {
                androidx.compose.material3.FloatingActionButton(
                    onClick = { navController.navigate("scanner") },
                    containerColor = IntelliBlue,
                    contentColor = androidx.compose.ui.graphics.Color.White
                ) {
androidx.compose.material3.Icon(
                    imageVector = Icons.Filled.CameraAlt,
                    contentDescription = "Scan QR"
                )
                }
            }
        },
        floatingActionButtonPosition = androidx.compose.material3.FabPosition.Center
    ) { innerPadding ->
        NavHost(
            navController = navController as androidx.navigation.NavHostController,
            startDestination = "splash",
            modifier = Modifier.padding(innerPadding)
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
                        navController.navigate("home") {
                            popUpTo("permissions") { inclusive = true }
                        }
                    },
                    onPermissionsDenied = {
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
                        navController.navigate("server_config")
                    },
                    onLogout = {
                        navController.navigate("login") {
                            popUpTo("home") { inclusive = true }
                        }
                    },
                    navController = navController
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
            
            composable("bluetooth_registration") {
                BluetoothScreen(onBack = { navController.popBackStack() })
            }
            
            composable("testing") {
                TestingScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onNavigateToBluetoothRegistration = {
                        navController.navigate("bluetooth_registration")
                    }
                )
            }
            
            composable("data_testing") {
                DataTestingScreen(
                    onBack = {
                        navController.popBackStack()
                    },
                    navController = navController
                )
            }
            
            composable("warm_scan_test") {
                WarmScanTestScreen(
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
            
            // Attendance screen removed per new design (scanner via FAB only)
            
            composable("history") {
                AttendanceHistoryScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }
            
            // composable("statistics") {
            //     AttendanceStatisticsScreen(
            //         onNavigateBack = { navController.popBackStack() }
            //     )
            // }
            
            composable("profile") {
                ProfileScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onLogout = {
                        navController.navigate("login") {
                            popUpTo("home") { inclusive = true }
                        }
                    },
                    onNavigateToTesting = {
                        navController.navigate("testing")
                    }
                )
            }
            
            composable("timetable") {
                com.intelliattend.student.ui.timetable.TimetableScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }

            composable("device_switch") {
                DeviceSwitchScreen()
            }
        }
    }
}

data class NavigationItem(
    val route: String,
    val title: String,
    val icon: ImageVector
)