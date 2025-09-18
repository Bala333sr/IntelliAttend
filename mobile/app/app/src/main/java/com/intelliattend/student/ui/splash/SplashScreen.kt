package com.intelliattend.student.ui.splash

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.School
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.ui.theme.IntelliBlue
import com.intelliattend.student.ui.theme.IntelliBlueLight
import com.intelliattend.student.utils.BiometricHelper
import com.intelliattend.student.utils.BiometricStatus
import com.intelliattend.student.utils.PermissionUtils
import kotlinx.coroutines.delay

/**
 * Splash screen with app initialization
 */
@Composable
fun SplashScreen(
    onNavigateToBiometric: () -> Unit,
    onNavigateToPermissions: () -> Unit,
    onNavigateToLogin: () -> Unit,
    onNavigateToHome: () -> Unit
) {
    val context = LocalContext.current
    val app = IntelliAttendApplication.getInstance()
    val biometricHelper = BiometricHelper(context)

    LaunchedEffect(Unit) {
        delay(2500) // Show splash for 2.5 seconds

        val biometricStatus = biometricHelper.getBiometricStatus()
        val isBiometricEnabled = app.getAppPreferences().isBiometricEnabled

        when {
            isBiometricEnabled && biometricStatus == BiometricStatus.AVAILABLE -> {
                onNavigateToBiometric()
            }
            !PermissionUtils.areAllPermissionsGranted(context) -> {
                onNavigateToPermissions()
            }
            app.getAuthRepository().isLoggedIn() -> {
                onNavigateToHome()
            }
            else -> {
                onNavigateToLogin()
            }
        }
    }

    val infiniteTransition = rememberInfiniteTransition()
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        )
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        MaterialTheme.colorScheme.primaryContainer,
                        MaterialTheme.colorScheme.background
                    )
                )
            ),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // App Logo
            Box(
                modifier = Modifier
                    .size(120.dp)
                    .scale(scale)
                    .clip(MaterialTheme.shapes.large)
                    .background(
                        brush = Brush.verticalGradient(
                            colors = listOf(IntelliBlue, IntelliBlueLight)
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.School,
                    contentDescription = "IntelliAttend Logo",
                    modifier = Modifier.size(80.dp),
                    tint = Color.White
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = "IntelliAttend",
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "Smart Attendance System",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(48.dp))

            CircularProgressIndicator(
                modifier = Modifier.size(32.dp),
                strokeWidth = 3.dp
            )

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = "Initializing...",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
