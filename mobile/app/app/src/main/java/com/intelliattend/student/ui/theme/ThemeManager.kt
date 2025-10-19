package com.intelliattend.student.ui.theme

import androidx.compose.runtime.compositionLocalOf
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class ThemeManager {
    private val _isDarkMode = MutableStateFlow(false)
    val isDarkMode: StateFlow<Boolean> = _isDarkMode.asStateFlow()
    
    fun toggleDarkMode() {
        _isDarkMode.value = !_isDarkMode.value
    }
    
    fun setDarkMode(enabled: Boolean) {
        _isDarkMode.value = enabled
    }
}

// Create a composition local for theme management
val LocalThemeManager = compositionLocalOf { ThemeManager() }