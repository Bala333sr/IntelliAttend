package com.intelliattend.student.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.data.model.Student
import com.intelliattend.student.data.repository.AuthRepository
import com.intelliattend.student.data.repository.AttendanceRepository
import com.intelliattend.student.network.ActiveSession
import com.intelliattend.student.network.AttendanceHistoryRecord
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel for home screen
 */
class HomeViewModel : ViewModel() {
    
    private val authRepository: AuthRepository = IntelliAttendApplication.getInstance().getAuthRepository()
    private val attendanceRepository: AttendanceRepository = IntelliAttendApplication.getInstance().getAttendanceRepository()
    
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()
    
    init {
        loadStudentData()
        // Auto-login with default user if not logged in
        if (authRepository.shouldAutoLogin()) {
            autoLoginWithDefaultUser()
        }
    }
    
    private fun autoLoginWithDefaultUser() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                isLoading = true,
                errorMessage = "Initializing with test user..."
            )
            
            val result = authRepository.autoLoginWithDefaultUser()
            
            result.fold(
                onSuccess = { student: Student ->
                    _uiState.value = _uiState.value.copy(
                        student = student,
                        isLoading = false,
                        errorMessage = null
                    )
                    loadData() // Load additional data after successful login
                },
                onFailure = { error: Throwable ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = "Auto-login failed: ${error.message}. Check network connection."
                    )
                }
            )
        }
    }
    
    fun loadData() {
        loadAttendanceHistory()
        loadActiveSessions()
    }
    
    private fun loadStudentData() {
        _uiState.value = _uiState.value.copy(
            student = authRepository.getCurrentStudent()
        )
    }
    
    private fun loadAttendanceHistory() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            val result = attendanceRepository.getAttendanceHistory(limit = 10)
            
            result.fold(
                onSuccess = { history: List<AttendanceHistoryRecord> ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        attendanceHistory = history,
                        errorMessage = null
                    )
                },
                onFailure = { error: Throwable ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = error.message
                    )
                }
            )
        }
    }
    
    private fun loadActiveSessions() {
        viewModelScope.launch {
            val result = attendanceRepository.getCurrentSessions()
            
            result.fold(
                onSuccess = { sessions: List<ActiveSession> ->
                    _uiState.value = _uiState.value.copy(
                        activeSessions = sessions
                    )
                },
                onFailure = { error: Throwable ->
                    // Don't show error for active sessions as it's not critical
                    _uiState.value = _uiState.value.copy(
                        activeSessions = emptyList()
                    )
                }
            )
        }
    }
    
    fun refreshData() {
        loadData()
        loadStudentData()
        // Re-attempt auto-login if not logged in
        if (authRepository.shouldAutoLogin()) {
            autoLoginWithDefaultUser()
        }
    }
}

data class HomeUiState(
    val student: Student? = null,
    val attendanceHistory: List<AttendanceHistoryRecord> = emptyList(),
    val activeSessions: List<ActiveSession> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)