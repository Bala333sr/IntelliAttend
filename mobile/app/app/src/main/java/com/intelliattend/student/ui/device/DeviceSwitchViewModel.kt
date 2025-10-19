
package com.intelliattend.student.ui.device

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.intelliattend.student.data.repository.AuthRepository
import com.intelliattend.student.utils.DeviceEnforcementUtils
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class DeviceSwitchViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(DeviceSwitchUiState())
    val uiState: StateFlow<DeviceSwitchUiState> = _uiState.asStateFlow()

    fun switchDevice(context: android.content.Context) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)

            val deviceInfo = DeviceEnforcementUtils.getDeviceInfo(context, "1.0.0")
            val wifiInfo = DeviceEnforcementUtils.getWiFiInfo(context)
            val gpsInfo = DeviceEnforcementUtils.getCurrentLocation(context)

            val result = authRepository.requestDeviceSwitch(deviceInfo, wifiInfo, gpsInfo)

            result.fold(
                onSuccess = {
                    _uiState.value = _uiState.value.copy(isLoading = false, isRequestSent = true)
                },
                onFailure = { error ->
                    _uiState.value = _uiState.value.copy(isLoading = false, errorMessage = error.message)
                }
            )
        }
    }
}

data class DeviceSwitchUiState(
    val isLoading: Boolean = false,
    val isRequestSent: Boolean = false,
    val errorMessage: String? = null
)
