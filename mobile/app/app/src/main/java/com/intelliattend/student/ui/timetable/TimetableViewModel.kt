package com.intelliattend.student.ui.timetable

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.intelliattend.student.data.model.StudentTimetable
import com.intelliattend.student.data.model.TimetableSlot
import com.intelliattend.student.data.repository.TimetableRepository
import com.intelliattend.student.network.ApiClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.DayOfWeek

data class TimetableUiState(
    val timetable: StudentTimetable? = null,
    val selectedDay: String = java.time.LocalDate.now().dayOfWeek.name,
    val isLoading: Boolean = false,
    val error: String? = null
)

class TimetableViewModel(application: Application) : AndroidViewModel(application) {
    
    private val repository = TimetableRepository(
        ApiClient.getInstance(application).apiService,
        application
    )
    
    private val _uiState = MutableStateFlow(TimetableUiState())
    val uiState: StateFlow<TimetableUiState> = _uiState.asStateFlow()
    
    init {
        loadTimetable()
    }
    
    fun loadTimetable() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            val result = repository.getTimetable()
            
            if (result.isSuccess) {
                _uiState.value = _uiState.value.copy(
                    timetable = result.getOrNull(),
                    isLoading = false
                )
            } else {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = result.exceptionOrNull()?.message ?: "Failed to load timetable"
                )
            }
        }
    }
    
    fun selectDay(day: String) {
        _uiState.value = _uiState.value.copy(selectedDay = day)
    }
    
    fun refreshTimetable() {
        repository.clearCache()
        loadTimetable()
    }
    
    companion object {
        private fun getCurrentDay(): String {
            return LocalDate.now().dayOfWeek.name
        }
    }
}