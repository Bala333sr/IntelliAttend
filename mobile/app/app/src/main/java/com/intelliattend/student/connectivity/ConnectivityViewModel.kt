
package com.intelliattend.student.connectivity

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.intelliattend.student.utils.ConnectivityMonitor
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import javax.inject.Inject

@HiltViewModel
class ConnectivityViewModel @Inject constructor(
    private val connectivityMonitor: ConnectivityMonitor
) : ViewModel() {

    val isConnected: StateFlow<Boolean> = connectivityMonitor.isConnected
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), false)

    init {
        connectivityMonitor.start()
    }

    override fun onCleared() {
        super.onCleared()
        connectivityMonitor.stop()
    }
}
