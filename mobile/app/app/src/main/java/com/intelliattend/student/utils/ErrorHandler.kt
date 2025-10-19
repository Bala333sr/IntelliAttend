
package com.intelliattend.student.utils

import androidx.compose.material3.SnackbarHostState
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

object ErrorHandler {

    fun showErrorSnackbar(scope: CoroutineScope, snackbarHostState: SnackbarHostState, message: String) {
        scope.launch {
            snackbarHostState.showSnackbar(message)
        }
    }
}
