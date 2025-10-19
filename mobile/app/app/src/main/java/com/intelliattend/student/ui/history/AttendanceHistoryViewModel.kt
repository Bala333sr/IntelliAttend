package com.intelliattend.student.ui.history

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
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*
import kotlin.random.Random

import com.intelliattend.student.data.repository.AttendanceRepository
import com.intelliattend.student.utils.OfflineQueueManager
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class AttendanceHistoryViewModel @Inject constructor(
    private val attendanceRepository: AttendanceRepository,
    private val offlineQueueManager: OfflineQueueManager
) : AndroidViewModel(application) {
    private val _uiState = MutableStateFlow(AttendanceHistoryUiState())
    val uiState: StateFlow<AttendanceHistoryUiState> = _uiState.asStateFlow()
    
    fun loadAttendanceData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            val historyResult = attendanceRepository.getAttendanceHistory()
            val offlineQueue = offlineQueueManager.getQueue()

            val records = mutableListOf<AttendanceRecord>()

            if (historyResult.isSuccess) {
                records.addAll(historyResult.getOrNull()?.map { it.toAttendanceRecord() } ?: emptyList())
            }

            records.addAll(offlineQueue.map { it.toAttendanceRecord() })
            
            val presentCount = records.count { it.status == AttendanceStatus.PRESENT }
            val percentage = if (records.isNotEmpty()) {
                (presentCount * 100) / records.size
            } else {
                0
            }
            
            _uiState.update { currentState ->
                currentState.copy(
                    attendancePercentage = percentage,
                    attendanceRecords = records.sortedByDescending { it.date },
                    isLoading = false
                )
            }
        }
    }
}

data class AttendanceHistoryUiState(
    val attendancePercentage: Int = 0,
    val attendanceRecords: List<AttendanceRecord> = emptyList(),
    val isLoading: Boolean = false
)

data class AttendanceRecord(
    val id: String = UUID.randomUUID().toString(),
    val subject: String,
    val date: String,
    val status: AttendanceStatus,
    val verificationMethods: List<VerificationMethod> = emptyList()
)

enum class AttendanceStatus {
    PRESENT,
    ABSENT,
    LATE,
    MANUAL,
    PENDING_SYNC,
    SYNC_FAILED,
    UNKNOWN
}

enum class VerificationMethod {
    BIOMETRIC,
    BLUETOOTH,
    WIFI,
    GPS
}