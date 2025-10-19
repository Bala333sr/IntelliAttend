 package com.intelliattend.student.ui.profile

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class ProfileViewModel(application: Application) : AndroidViewModel(application) {
    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()
    
    // In a real app, this would fetch data from a repository
    fun loadProfileData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            // Simulate network delay
            kotlinx.coroutines.delay(1000)
            
            // Get actual device ID and current timestamp
            val actualDeviceId = android.provider.Settings.Secure.getString(
                getApplication<Application>().contentResolver,
                android.provider.Settings.Secure.ANDROID_ID
            )
            val currentDate = SimpleDateFormat("yyyy-MM-dd HH:mm a", Locale.getDefault()).format(Date())
            
            _uiState.update { 
                ProfileUiState(
                    name = "Rahul Kumar",
                    rollNumber = "2021CS001",
                    department = "Computer Science",
                    year = "3rd",
                    deviceId = actualDeviceId,
                    lastSyncTime = currentDate,
                    notificationsEnabled = true,
                    darkModeEnabled = false,
                    biometricLoginEnabled = true,
                    autoSyncEnabled = true,
                    isLoading = false
                )
            }
        }
    }
    
    fun updateProfilePhoto(uri: Uri) {
        _uiState.update { it.copy(profilePhotoUri = uri.toString()) }
        // In a real app, this would upload the image to the server
    }
    
    fun updateLastSyncTime() {
        val currentDate = SimpleDateFormat("yyyy-MM-dd HH:mm a", Locale.getDefault()).format(Date())
        _uiState.update { it.copy(lastSyncTime = currentDate) }
    }
    
    fun toggleNotifications(enabled: Boolean) {
        _uiState.update { it.copy(notificationsEnabled = enabled) }
        // In a real app, this would update user preferences in a repository
    }
    
    fun toggleDarkMode(enabled: Boolean) {
        _uiState.update { it.copy(darkModeEnabled = enabled) }
        // In a real app, this would update user preferences in a repository
    }
    
    fun toggleBiometricLogin(enabled: Boolean) {
        _uiState.update { it.copy(biometricLoginEnabled = enabled) }
        // In a real app, this would update user preferences in a repository
    }
    
    fun toggleAutoSync(enabled: Boolean) {
        _uiState.update { it.copy(autoSyncEnabled = enabled) }
        // In a real app, this would update user preferences in a repository
    }
    
    companion object {
        val Factory: ViewModelProvider.Factory = viewModelFactory {
            initializer {
                val application = (this[ViewModelProvider.AndroidViewModelFactory.APPLICATION_KEY] as Application)
                ProfileViewModel(application)
            }
        }
    }
}

data class ProfileUiState(
    val name: String = "",
    val rollNumber: String = "",
    val department: String = "",
    val year: String = "",
    val deviceId: String = "",
    val lastSyncTime: String = "",
    val profilePhotoUri: String? = null,
    val notificationsEnabled: Boolean = false,
    val darkModeEnabled: Boolean = false,
    val biometricLoginEnabled: Boolean = false,
    val autoSyncEnabled: Boolean = false,
    val isLoading: Boolean = true
)
