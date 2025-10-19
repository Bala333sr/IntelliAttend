package com.intelliattend.student.ui.connectivity

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.intelliattend.student.connectivity.ConnectivityMonitor
import com.intelliattend.student.connectivity.ConnectivityStatus
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

/**
 * ViewModel for managing connectivity status across the app
 * Provides a single source of truth for Bluetooth, GPS, and Wi-Fi states
 */
class ConnectivityViewModel(application: Application) : AndroidViewModel(application) {
    
    private val connectivityMonitor = ConnectivityMonitor(application.applicationContext)
    
    /**
     * Current connectivity status as a StateFlow
     * Can be collected by any composable to display real-time status
     */
    val connectivityStatus: StateFlow<ConnectivityStatus> = connectivityMonitor.connectivityStatus
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = ConnectivityStatus()
        )
    
    init {
        startMonitoring()
    }
    
    /**
     * Start monitoring connectivity services
     */
    fun startMonitoring() {
        viewModelScope.launch {
            connectivityMonitor.startMonitoring()
        }
    }
    
    /**
     * Stop monitoring connectivity services
     */
    fun stopMonitoring() {
        connectivityMonitor.stopMonitoring()
    }
    
    /**
     * Refresh connectivity status immediately
     */
    fun refreshStatus() {
        stopMonitoring()
        startMonitoring()
    }
    
    override fun onCleared() {
        super.onCleared()
        stopMonitoring()
    }
}
