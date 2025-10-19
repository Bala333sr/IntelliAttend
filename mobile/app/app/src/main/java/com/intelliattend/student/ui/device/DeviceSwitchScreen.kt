
package com.intelliattend.student.ui.device

import androidx.compose.foundation.layout.*
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun DeviceSwitchScreen(
    viewModel: DeviceSwitchViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        if (uiState.isLoading) {
            CircularProgressIndicator()
        } else if (uiState.isRequestSent) {
            Text(text = "Device switch request sent successfully.")
        } else {
            Text(text = "Click the button to switch your device.")
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = { viewModel.switchDevice(context) }) {
                Text(text = "Switch Device")
            }
            uiState.errorMessage?.let {
                Spacer(modifier = Modifier.height(16.dp))
                Text(text = it)
            }
        }
    }
}
