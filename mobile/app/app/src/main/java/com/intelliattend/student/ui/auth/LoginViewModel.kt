package com.intelliattend.student.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.data.repository.AuthRepository
import com.intelliattend.student.network.model.DeviceStatusData
import com.intelliattend.student.utils.DeviceEnforcementUtils
import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.intelliattend.student.data.preferences.AppPreferences
import com.intelliattend.student.domain.usecase.LoginUseCase
import com.intelliattend.student.network.model.DeviceStatusData
import com.intelliattend.student.utils.BiometricHelper
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for login screen
 */
@HiltViewModel
class LoginViewModel @Inject constructor(
    private val loginUseCase: LoginUseCase,
    private val appPreferences: AppPreferences
) : ViewModel() {

    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    private val _navigationEvent = MutableSharedFlow<NavigationEvent>()
    val navigationEvent: SharedFlow<NavigationEvent> = _navigationEvent.asSharedFlow()

    fun updateEmail(email: String) {
        _uiState.value = _uiState.value.copy(
            email = email,
            emailError = null,
            errorMessage = null
        )
    }

    fun updatePassword(password: String) {
        _uiState.value = _uiState.value.copy(
            password = password,
            passwordError = null,
            errorMessage = null
        )
    }

    fun togglePasswordVisibility() {
        _uiState.value = _uiState.value.copy(
            isPasswordVisible = !_uiState.value.isPasswordVisible
        )
    }

    fun login(context: Context) {
        val currentState = _uiState.value

        // Validate inputs
        var hasError = false
        val updatedState = currentState.copy(
            emailError = null,
            passwordError = null,
            errorMessage = null
        )

        if (currentState.email.isBlank()) {
            _uiState.value = updatedState.copy(emailError = "Email is required")
            hasError = true
        } else if (!isValidEmail(currentState.email)) {
            _uiState.value = updatedState.copy(emailError = "Invalid email format")
            hasError = true
        }

        if (currentState.password.isBlank()) {
            _uiState.value = _uiState.value.copy(passwordError = "Password is required")
            hasError = true
        } else if (currentState.password.length < 6) {
            _uiState.value = _uiState.value.copy(passwordError = "Password must be at least 6 characters")
            hasError = true
        }

        if (hasError) return

        // Start login process
        _uiState.value = _uiState.value.copy(isLoading = true)

        viewModelScope.launch {
            val result = loginUseCase(context, currentState.email, currentState.password)

            result.fold(
                onSuccess = { (student, deviceStatus) ->
                    println("✅ LoginViewModel - Login success, emitting navigation event")
                    // Store credentials for biometric login
                    appPreferences.lastLoggedInEmail = currentState.email
                    appPreferences.lastLoggedInPassword = currentState.password

                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = null,
                        deviceStatus = deviceStatus
                    )
                    _navigationEvent.emit(NavigationEvent.NavigateToHome)
                },
                onFailure = { error: Throwable ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = error.message ?: "Login failed. Please check your WiFi connection and location settings."
                    )
                }
            )
        }
    }

    fun initiateBiometricLogin(activity: androidx.fragment.app.FragmentActivity) {
        if (BiometricHelper.isBiometricAvailable(activity)) {
            val email = appPreferences.lastLoggedInEmail
            val password = appPreferences.lastLoggedInPassword

            if (email != null && password != null) {
                BiometricHelper.showBiometricPrompt(
                    activity = activity,
                    onSuccess = {
                        updateEmail(email)
                        updatePassword(password)
                        login(activity)
                    },
                    onError = {
                        _uiState.value = _uiState.value.copy(errorMessage = it)
                    }
                )
            } else {
                _uiState.value = _uiState.value.copy(errorMessage = "No stored credentials for biometric login.")
            }
        } else {
            _uiState.value = _uiState.value.copy(errorMessage = "Biometric authentication is not available on this device.")
        }
    }

    private fun isValidEmail(email: String): Boolean {
        return android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
    }
}

data class LoginUiState(
    val email: String = "",
    val password: String = "",
    val isPasswordVisible: Boolean = false,
    val isLoading: Boolean = false,
    val emailError: String? = null,
    val passwordError: String? = null,
    val errorMessage: String? = null,
    val deviceStatus: DeviceStatusData? = null
)

sealed class NavigationEvent {
    object NavigateToHome : NavigationEvent()
}
