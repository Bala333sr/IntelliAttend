package com.intelliattend.student.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.data.model.*
import com.intelliattend.student.data.repository.AuthRepository
import com.intelliattend.student.data.repository.AttendanceRepository
import com.intelliattend.student.data.repository.TimetableRepository
import com.intelliattend.student.network.ActiveSession
import com.intelliattend.student.network.AttendanceHistoryRecord
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.time.LocalTime

import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

/**
 * ViewModel for home screen
 */
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val attendanceRepository: AttendanceRepository,
    private val timetableRepository: TimetableRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()
    
    private var countdownJob: Job? = null
    
    init {
        loadStudentData()
        // Auto-login with default user if not logged in
        if (authRepository.shouldAutoLogin()) {
            autoLoginWithDefaultUser()
        }
        
        // Start countdown updates for class statuses
        startCountdownUpdates()
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
        loadTodayClasses()
    }
    
    private fun loadStudentData() {
        // Load from local session first for instant UI
        _uiState.value = _uiState.value.copy(
            student = authRepository.getCurrentStudent()
        )
        
        // Then refresh from server to get authoritative details
        viewModelScope.launch {
            val result = authRepository.refreshProfile()
            result.fold(
                onSuccess = { student ->
                    _uiState.value = _uiState.value.copy(student = student)
                    loadDeviceStatus()
                },
                onFailure = {
                    // Ignore failure silently on home load
                }
            )
        }
    }

    private fun loadDeviceStatus() {
        viewModelScope.launch {
            val result = authRepository.getDeviceStatus()
            result.fold(
                onSuccess = { deviceStatus ->
                    _uiState.value = _uiState.value.copy(deviceStatus = deviceStatus)
                },
                onFailure = {
                    // Ignore failure silently on home load
                }
            )
        }
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
    
    private fun loadTodayClasses() {
        viewModelScope.launch {
            val result = timetableRepository.getTodaySchedule()
            
            result.fold(
                onSuccess = { classes: List<ClassSession> ->
                    _uiState.value = _uiState.value.copy(
                        todayClasses = classes
                    )
                },
                onFailure = { error: Throwable ->
                    // Don't show error for today's classes as it's not critical
                    _uiState.value = _uiState.value.copy(
                        todayClasses = emptyList()
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
    
    /**
     * Start countdown updates for class statuses
     */
    private fun startCountdownUpdates() {
        countdownJob?.cancel()
        countdownJob = viewModelScope.launch {
            while (true) {
                updateClassStatuses()
                delay(30_000) // Update every 30 seconds
            }
        }
    }
    
    /**
     * Update class statuses based on current time
     */
    private fun updateClassStatuses() {
        val currentClasses = _uiState.value.todayClasses
        val currentPage = _uiState.value.currentPage
        if (currentClasses.isEmpty()) return
        
        val updatedClasses = currentClasses.map { classSession ->
            classSession.copy(
                status = calculateStatus(classSession.startTime, classSession.endTime)
            )
        }
        
        // Check if all classes are completed
        val allCompleted = updatedClasses.isNotEmpty() && 
                          updatedClasses.all { it.status is ClassStatus.Completed }
        
        // Check if we should advance to the next page
        var newCurrentPage = currentPage
        if (updatedClasses.isNotEmpty() && !allCompleted) {
            // Group classes into pages of 2
            val pages = updatedClasses.chunked(2)
            
            // Check if the first class on the current page is completed
            val firstClassIndex = currentPage * 2
            if (firstClassIndex < updatedClasses.size) {
                val firstClass = updatedClasses[firstClassIndex]
                if (firstClass.status is ClassStatus.Completed) {
                    // Advance to the next page if there is one
                    if (currentPage < pages.size - 1) {
                        newCurrentPage = currentPage + 1
                    }
                }
            }
        }
        
        _uiState.value = _uiState.value.copy(
            todayClasses = updatedClasses,
            isAllCompleted = allCompleted,
            currentPage = newCurrentPage
        )
    }
    
    /**
     * Calculate class status based on current time
     */
    private fun calculateStatus(startTime: LocalTime, endTime: LocalTime): ClassStatus {
        val now = LocalTime.now()
        
        return when {
            now < startTime -> {
                val minutesUntilStart = java.time.Duration.between(now, startTime).toMinutes()
                when {
                    minutesUntilStart > 60 -> ClassStatus.UpcomingLong("Starts in ${formatTime(minutesUntilStart)}")
                    minutesUntilStart > 15 -> ClassStatus.Upcoming("Starts in $minutesUntilStart minutes")
                    minutesUntilStart > 5 -> ClassStatus.StartingSoon("Starting soon - $minutesUntilStart minutes")
                    else -> ClassStatus.StartingNow("Starting now!")
                }
            }
            now >= startTime && now <= endTime -> {
                ClassStatus.InProgress("In progress")
            }
            else -> ClassStatus.Completed("Completed")
        }
    }
    
    /**
     * Format time duration
     */
    private fun formatTime(minutes: Long): String {
        return when {
            minutes > 60 -> "${minutes / 60}h ${minutes % 60}m"
            else -> "${minutes}m"
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        countdownJob?.cancel()
    }
}

data class HomeUiState(
    val student: Student? = null,
    val attendanceHistory: List<AttendanceHistoryRecord> = emptyList(),
    val activeSessions: List<ActiveSession> = emptyList(),
    val todayClasses: List<ClassSession> = emptyList(),
    val isAllCompleted: Boolean = false,
    val currentPage: Int = 0,
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val deviceStatus: com.intelliattend.student.network.model.DeviceStatusData? = null
)