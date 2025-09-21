package com.intelliattend.student.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.data.model.LoginRequest
import com.intelliattend.student.data.model.Student
import com.intelliattend.student.data.repository.AuthRepository
import com.intelliattend.student.network.ApiClient
import com.intelliattend.student.network.StudentRegistrationRequest
import com.intelliattend.student.network.model.RegistrationRequest
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel for student registration
 */
class RegistrationViewModel : ViewModel() {
    
    private val authRepository: AuthRepository = IntelliAttendApplication.getInstance().getAuthRepository()
    private val apiClient: ApiClient = IntelliAttendApplication.getInstance().getApiClient()
    
    private val _uiState = MutableStateFlow(RegistrationUiState())
    val uiState: StateFlow<RegistrationUiState> = _uiState.asStateFlow()
    
    fun updateRollNumber(rollNumber: String) {
        _uiState.value = _uiState.value.copy(
            rollNumber = rollNumber,
            rollNumberError = null,
            errorMessage = null
        )
    }
    
    fun updateFirstName(firstName: String) {
        _uiState.value = _uiState.value.copy(
            firstName = firstName,
            firstNameError = null,
            errorMessage = null
        )
    }
    
    fun updateLastName(lastName: String) {
        _uiState.value = _uiState.value.copy(
            lastName = lastName,
            lastNameError = null,
            errorMessage = null
        )
    }
    
    fun updateEmail(email: String) {
        _uiState.value = _uiState.value.copy(
            email = email,
            emailError = null,
            errorMessage = null
        )
    }
    
    fun updatePhoneNumber(phoneNumber: String) {
        _uiState.value = _uiState.value.copy(
            phoneNumber = phoneNumber,
            phoneNumberError = null,
            errorMessage = null
        )
    }
    
    fun updateProgram(program: String) {
        _uiState.value = _uiState.value.copy(
            program = program,
            programError = null,
            errorMessage = null
        )
    }
    
    fun updateYearOfStudy(yearOfStudy: String) {
        _uiState.value = _uiState.value.copy(
            yearOfStudy = yearOfStudy,
            yearOfStudyError = null,
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
    
    fun updateConfirmPassword(confirmPassword: String) {
        _uiState.value = _uiState.value.copy(
            confirmPassword = confirmPassword,
            confirmPasswordError = null,
            errorMessage = null
        )
    }
    
    fun togglePasswordVisibility(checked: Boolean) {
        _uiState.value = _uiState.value.copy(
            isPasswordVisible = checked
        )
    }
    
    fun register() {
        val currentState = _uiState.value
        
        // Validate inputs
        if (!validateInputs()) return
        
        // Start registration process
        _uiState.value = _uiState.value.copy(isLoading = true)
        
        viewModelScope.launch {
            try {
                val request = RegistrationRequest(
                    studentCode = currentState.rollNumber,
                    firstName = currentState.firstName,
                    lastName = currentState.lastName,
                    email = currentState.email,
                    phoneNumber = currentState.phoneNumber.ifEmpty { null },
                    program = currentState.program,
                    yearOfStudy = currentState.yearOfStudy.toIntOrNull(),
                    password = currentState.password
                )
                
                // Perform actual registration
                performRegistration(request)
                
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = e.message ?: "Registration failed. Please try again."
                )
            }
        }
    }
    
    private fun validateInputs(): Boolean {
        var hasError = false
        var updatedState = _uiState.value.copy(
            rollNumberError = null,
            firstNameError = null,
            lastNameError = null,
            emailError = null,
            phoneNumberError = null,
            programError = null,
            yearOfStudyError = null,
            passwordError = null,
            confirmPasswordError = null,
            errorMessage = null
        )
        
        // Roll Number validation
        if (updatedState.rollNumber.isBlank()) {
            updatedState = updatedState.copy(rollNumberError = "Roll number is required")
            hasError = true
        }
        
        // First Name validation
        if (updatedState.firstName.isBlank()) {
            updatedState = updatedState.copy(firstNameError = "First name is required")
            hasError = true
        }
        
        // Last Name validation
        if (updatedState.lastName.isBlank()) {
            updatedState = updatedState.copy(lastNameError = "Last name is required")
            hasError = true
        }
        
        // Email validation
        if (updatedState.email.isBlank()) {
            updatedState = updatedState.copy(emailError = "Email is required")
            hasError = true
        } else if (!isValidEmail(updatedState.email)) {
            updatedState = updatedState.copy(emailError = "Invalid email format")
            hasError = true
        }
        
        // Program validation
        if (updatedState.program.isBlank()) {
            updatedState = updatedState.copy(programError = "Program is required")
            hasError = true
        }
        
        // Year of Study validation
        if (updatedState.yearOfStudy.isBlank()) {
            updatedState = updatedState.copy(yearOfStudyError = "Year of study is required")
            hasError = true
        } else {
            val year = updatedState.yearOfStudy.toIntOrNull()
            if (year == null || year < 1 || year > 5) {
                updatedState = updatedState.copy(yearOfStudyError = "Year must be between 1 and 5")
                hasError = true
            }
        }
        
        // Password validation
        if (updatedState.password.isBlank()) {
            updatedState = updatedState.copy(passwordError = "Password is required")
            hasError = true
        } else if (updatedState.password.length < 6) {
            updatedState = updatedState.copy(passwordError = "Password must be at least 6 characters")
            hasError = true
        }
        
        // Confirm Password validation
        if (updatedState.confirmPassword.isBlank()) {
            updatedState = updatedState.copy(confirmPasswordError = "Please confirm your password")
            hasError = true
        } else if (updatedState.password != updatedState.confirmPassword) {
            updatedState = updatedState.copy(confirmPasswordError = "Passwords do not match")
            hasError = true
        }
        
        _uiState.value = updatedState
        return !hasError
    }
    
    private fun isValidEmail(email: String): Boolean {
        return android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
    }
    
    private suspend fun performRegistration(request: RegistrationRequest) {
        try {
            // Create the registration request for the API
            val apiRequest = com.intelliattend.student.network.StudentRegistrationRequest(
                studentCode = request.studentCode,
                firstName = request.firstName,
                lastName = request.lastName,
                email = request.email,
                phoneNumber = request.phoneNumber,
                program = request.program,
                yearOfStudy = request.yearOfStudy,
                password = request.password
            )
            
            // Call the registration API
            val response = apiClient.apiService.studentRegister(apiRequest)
            
            if (response.isSuccessful) {
                val apiResponse = response.body()
                if (apiResponse?.success == true) {
                    // Registration successful, show biometric prompt for confirmation
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        showBiometricPrompt = true
                    )
                } else {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = apiResponse?.error ?: "Registration failed"
                    )
                }
            } else {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Network error: ${response.code()}"
                )
            }
        } catch (e: Exception) {
            _uiState.value = _uiState.value.copy(
                isLoading = false,
                errorMessage = e.message ?: "Failed to register student"
            )
        }
    }
    
    fun confirmRegistrationWithBiometric() {
        val currentState = _uiState.value
        
        // In a real implementation, this would complete the registration process
        _uiState.value = _uiState.value.copy(
            showBiometricPrompt = false,
            isRegistrationSuccessful = true,
            successMessage = "Successfully registered! Please login with your credentials."
        )
        
        // Verify registration by attempting to login with the new credentials
        viewModelScope.launch {
            verifyRegistration(currentState.email, currentState.password)
        }
    }
    
    private suspend fun verifyRegistration(email: String, password: String) {
        try {
            // Attempt to login with the new credentials to verify registration
            val loginRequest = LoginRequest(email, password)
            val response = apiClient.apiService.studentLogin(loginRequest)
            
            if (response.isSuccessful) {
                val loginResponse = response.body()
                if (loginResponse?.success == true) {
                    // Verification successful - registration confirmed in database
                    _uiState.value = _uiState.value.copy(
                        successMessage = "Successfully registered and verified! Please login with your credentials."
                    )
                } else {
                    // Registration may have failed silently
                    _uiState.value = _uiState.value.copy(
                        errorMessage = "Registration verification failed: ${loginResponse?.error ?: "Unknown error"}"
                    )
                }
            } else {
                // Network error during verification
                _uiState.value = _uiState.value.copy(
                    errorMessage = "Verification failed due to network error. Please try logging in manually."
                )
            }
        } catch (e: Exception) {
            // Exception during verification
            _uiState.value = _uiState.value.copy(
                errorMessage = "Verification failed: ${e.message ?: "Unknown error"}"
            )
        }
    }
    
    fun hideBiometricPrompt() {
        _uiState.value = _uiState.value.copy(
            showBiometricPrompt = false
        )
    }
}

data class RegistrationUiState(
    val rollNumber: String = "",
    val firstName: String = "",
    val lastName: String = "",
    val email: String = "",
    val phoneNumber: String = "",
    val program: String = "",
    val yearOfStudy: String = "",
    val password: String = "",
    val confirmPassword: String = "",
    val isPasswordVisible: Boolean = false,
    val isLoading: Boolean = false,
    val isRegistrationSuccessful: Boolean = false,
    val showBiometricPrompt: Boolean = false,
    val rollNumberError: String? = null,
    val firstNameError: String? = null,
    val lastNameError: String? = null,
    val emailError: String? = null,
    val phoneNumberError: String? = null,
    val programError: String? = null,
    val yearOfStudyError: String? = null,
    val passwordError: String? = null,
    val confirmPasswordError: String? = null,
    val errorMessage: String? = null,
    val successMessage: String? = null
)