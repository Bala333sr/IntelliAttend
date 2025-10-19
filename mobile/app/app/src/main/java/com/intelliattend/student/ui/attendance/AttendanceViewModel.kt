package com.intelliattend.student.ui.attendance

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

enum class VerificationStatus {
    PENDING, SUCCESS, FAILED
}

data class AttendanceUiState(
    val currentSubject: String = "Calculus II",
    val faculty: String = "Dr. Ethan Yates",
    val room: String = "Room 203",
    val biometricVerification: VerificationStatus = VerificationStatus.SUCCESS,
    val bluetoothProximity: VerificationStatus = VerificationStatus.SUCCESS,
    val wifiVerification: VerificationStatus = VerificationStatus.SUCCESS,
    val gpsGeofence: VerificationStatus = VerificationStatus.FAILED,
    val attendanceStatus: String = "Attendance Failed",
    val attendanceReason: String = "Out of range",
    val isLoading: Boolean = false
)

class AttendanceViewModel(application: Application) : AndroidViewModel(application) {
    private val _uiState = MutableStateFlow(AttendanceUiState())
    val uiState: StateFlow<AttendanceUiState> = _uiState.asStateFlow()
    
    init {
        checkAttendanceStatus()
    }
    
    private fun checkAttendanceStatus() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            // Simulate API call delay
            delay(1500)
            
            // Update with verification statuses
            _uiState.value = _uiState.value.copy(
                biometricVerification = VerificationStatus.SUCCESS,
                bluetoothProximity = VerificationStatus.SUCCESS,
                wifiVerification = VerificationStatus.SUCCESS,
                gpsGeofence = VerificationStatus.FAILED,
                attendanceStatus = "Attendance Failed",
                attendanceReason = "Out of range",
                isLoading = false
            )
        }
    }
    
    fun retryAttendance() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            // Simulate retry delay
            delay(2000)
            
            // For demo purposes, let's assume retry still fails
            _uiState.value = _uiState.value.copy(
                gpsGeofence = VerificationStatus.FAILED,
                attendanceStatus = "Attendance Failed",
                attendanceReason = "Out of range",
                isLoading = false
            )
        }
    }
    
    companion object {
        val Factory: ViewModelProvider.Factory = viewModelFactory {
            initializer {
                val application = (this[ViewModelProvider.AndroidViewModelFactory.APPLICATION_KEY] as Application)
                AttendanceViewModel(application)
            }
        }
    }
}