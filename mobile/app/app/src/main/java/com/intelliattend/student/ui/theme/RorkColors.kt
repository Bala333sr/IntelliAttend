package com.intelliattend.student.ui.theme

import androidx.compose.ui.graphics.Color

/**
 * Rork Dark Theme Colors - Matching React Native UI
 * Modern dark theme with iOS-inspired colors
 */

// Primary brand colors
val RorkPrimary = Color(0xFF007AFF) // iOS Blue
val RorkSecondary = Color(0xFF34C759) // iOS Green

// Background colors
val RorkBackground = Color(0xFF000000) // Pure black background
val RorkCardBackground = Color(0xFF1C1C1E) // Dark gray for cards
val RorkSurfaceVariant = Color(0xFF2C2C2E) // Slightly lighter surface

// Text colors
val RorkTextPrimary = Color(0xFFFFFFFF) // White text
val RorkTextSecondary = Color(0xFF8E8E93) // Gray secondary text
val RorkTextTertiary = Color(0xFF636366) // Lighter gray

// Status colors
val RorkSuccess = Color(0xFF34C759) // Green for success/high attendance
val RorkWarning = Color(0xFFFF9500) // Orange for warnings/medium attendance
val RorkDanger = Color(0xFFFF3B30) // Red for errors/low attendance

// Border and divider colors
val RorkBorder = Color(0xFF38383A) // Dark gray borders
val RorkDivider = Color(0xFF38383A)

// Subject/Class icon colors (vibrant colors for visual distinction)
val RorkIconOrange = Color(0xFFFF9500)
val RorkIconPurple = Color(0xFFAF52DE)
val RorkIconGreen = Color(0xFF32D74B)
val RorkIconBlue = Color(0xFF0A84FF)
val RorkIconPink = Color(0xFFFF2D55)
val RorkIconYellow = Color(0xFFFFD60A)
val RorkIconCyan = Color(0xFF64D2FF)

// Functional colors
val RorkOnlineIndicator = RorkSuccess
val RorkOfflineIndicator = RorkDanger
