package com.intelliattend.student.ui.auth

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.fragment.app.FragmentActivity
import androidx.lifecycle.viewmodel.compose.viewModel
import com.intelliattend.student.utils.BiometricHelper

/**
 * Registration screen for new student accounts
 */
@Composable
fun RegistrationScreen(
    onRegistrationSuccess: () -> Unit,
    onBackToLogin: () -> Unit,
    viewModel: RegistrationViewModel = viewModel()
) {
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsState()
    val biometricHelper = remember { BiometricHelper(context) }

    LaunchedEffect(uiState.isRegistrationSuccessful) {
        if (uiState.isRegistrationSuccessful) {
            onRegistrationSuccess()
        }
    }

    LaunchedEffect(uiState.showBiometricPrompt) {
        if (uiState.showBiometricPrompt) {
            // Check if we're in an activity context
            if (context is FragmentActivity) {
                biometricHelper.authenticate(
                    activity = context,
                    title = "Confirm Registration",
                    subtitle = "Use fingerprint to confirm your registration",
                    description = "This will securely register your account",
                    onSuccess = {
                        viewModel.confirmRegistrationWithBiometric()
                    },
                    onError = { error ->
                        viewModel.hideBiometricPrompt()
                        // Handle biometric error
                    },
                    onCancel = {
                        viewModel.hideBiometricPrompt()
                    }
                )
            }
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Header
            Icon(
                imageVector = Icons.Default.PersonAdd,
                contentDescription = "Register",
                modifier = Modifier
                    .size(64.dp)
                    .padding(16.dp),
                tint = MaterialTheme.colorScheme.primary
            )

            Text(
                text = "Create Account",
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.padding(bottom = 8.dp)
            )

            Text(
                text = "Enter your details to register",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(bottom = 24.dp)
            )

            // Registration form
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Roll Number
                OutlinedTextField(
                    value = uiState.rollNumber,
                    onValueChange = viewModel::updateRollNumber,
                    label = { Text("Roll Number") },
                    leadingIcon = {
                        Icon(Icons.Default.Numbers, contentDescription = "Roll Number")
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !uiState.isLoading,
                    isError = uiState.rollNumberError != null,
                    singleLine = true
                )

                if (uiState.rollNumberError != null) {
                    Text(
                        text = uiState.rollNumberError!!,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(start = 16.dp)
                    )
                }

                // First Name
                OutlinedTextField(
                    value = uiState.firstName,
                    onValueChange = viewModel::updateFirstName,
                    label = { Text("First Name") },
                    leadingIcon = {
                        Icon(Icons.Default.Person, contentDescription = "First Name")
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !uiState.isLoading,
                    isError = uiState.firstNameError != null,
                    singleLine = true
                )

                if (uiState.firstNameError != null) {
                    Text(
                        text = uiState.firstNameError!!,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(start = 16.dp)
                    )
                }

                // Last Name
                OutlinedTextField(
                    value = uiState.lastName,
                    onValueChange = viewModel::updateLastName,
                    label = { Text("Last Name") },
                    leadingIcon = {
                        Icon(Icons.Default.Person, contentDescription = "Last Name")
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !uiState.isLoading,
                    isError = uiState.lastNameError != null,
                    singleLine = true
                )

                if (uiState.lastNameError != null) {
                    Text(
                        text = uiState.lastNameError!!,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(start = 16.dp)
                    )
                }

                // Email
                OutlinedTextField(
                    value = uiState.email,
                    onValueChange = viewModel::updateEmail,
                    label = { Text("Student Email") },
                    leadingIcon = {
                        Icon(Icons.Default.Email, contentDescription = "Email")
                    },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !uiState.isLoading,
                    isError = uiState.emailError != null,
                    singleLine = true
                )

                if (uiState.emailError != null) {
                    Text(
                        text = uiState.emailError!!,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(start = 16.dp)
                    )
                }

                // Phone Number
                OutlinedTextField(
                    value = uiState.phoneNumber,
                    onValueChange = viewModel::updatePhoneNumber,
                    label = { Text("Phone Number") },
                    leadingIcon = {
                        Icon(Icons.Default.Phone, contentDescription = "Phone Number")
                    },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !uiState.isLoading,
                    isError = uiState.phoneNumberError != null,
                    singleLine = true
                )

                if (uiState.phoneNumberError != null) {
                    Text(
                        text = uiState.phoneNumberError!!,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(start = 16.dp)
                    )
                }

                // Program
                OutlinedTextField(
                    value = uiState.program,
                    onValueChange = viewModel::updateProgram,
                    label = { Text("Program") },
                    leadingIcon = {
                        Icon(Icons.Default.School, contentDescription = "Program")
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !uiState.isLoading,
                    isError = uiState.programError != null,
                    singleLine = true
                )

                if (uiState.programError != null) {
                    Text(
                        text = uiState.programError!!,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(start = 16.dp)
                    )
                }

                // Year of Study
                OutlinedTextField(
                    value = uiState.yearOfStudy,
                    onValueChange = viewModel::updateYearOfStudy,
                    label = { Text("Year of Study") },
                    leadingIcon = {
                        Icon(Icons.Default.CalendarToday, contentDescription = "Year")
                    },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !uiState.isLoading,
                    isError = uiState.yearOfStudyError != null,
                    singleLine = true
                )

                if (uiState.yearOfStudyError != null) {
                    Text(
                        text = uiState.yearOfStudyError!!,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(start = 16.dp)
                    )
                }

                // Password
                OutlinedTextField(
                    value = uiState.password,
                    onValueChange = viewModel::updatePassword,
                    label = { Text("Password") },
                    leadingIcon = {
                        Icon(Icons.Default.Lock, contentDescription = "Password")
                    },
                    visualTransformation = if (uiState.isPasswordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !uiState.isLoading,
                    isError = uiState.passwordError != null,
                    singleLine = true
                )

                if (uiState.passwordError != null) {
                    Text(
                        text = uiState.passwordError!!,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(start = 16.dp)
                    )
                }

                // Confirm Password
                OutlinedTextField(
                    value = uiState.confirmPassword,
                    onValueChange = viewModel::updateConfirmPassword,
                    label = { Text("Confirm Password") },
                    leadingIcon = {
                        Icon(Icons.Default.Lock, contentDescription = "Confirm Password")
                    },
                    visualTransformation = if (uiState.isPasswordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !uiState.isLoading,
                    isError = uiState.confirmPasswordError != null,
                    singleLine = true
                )

                if (uiState.confirmPasswordError != null) {
                    Text(
                        text = uiState.confirmPasswordError!!,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.padding(start = 16.dp)
                    )
                }

                // Show password toggle
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Checkbox(
                            checked = uiState.isPasswordVisible,
                            onCheckedChange = viewModel::togglePasswordVisibility
                        )
                        Text(
                            text = "Show Password",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }

                // Error message
                if (uiState.errorMessage != null) {
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.errorContainer
                        ),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = uiState.errorMessage!!,
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.padding(16.dp)
                        )
                    }
                }

                // Success message
                if (uiState.successMessage != null) {
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.primaryContainer
                        ),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = uiState.successMessage!!,
                            color = MaterialTheme.colorScheme.onPrimaryContainer,
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.padding(16.dp)
                        )
                    }
                }

                // Register button
                Button(
                    onClick = viewModel::register,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    enabled = !uiState.isLoading,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.primary,
                        contentColor = Color.White
                    )
                ) {
                    if (uiState.isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            color = Color.White,
                            strokeWidth = 2.dp
                        )
                    } else {
                        Text(
                            "Register",
                            style = MaterialTheme.typography.titleMedium
                        )
                    }
                }

                // Back to login
                TextButton(
                    onClick = onBackToLogin,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Already have an account? Sign In")
                }
            }
        }
    }
}