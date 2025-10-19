package com.intelliattend.student.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.intelliattend.student.network.model.DeviceStatusData

@Composable
fun DeviceStatusBanner(deviceStatus: DeviceStatusData?, onSwitchDevice: () -> Unit) {
    if (deviceStatus != null && !deviceStatus.can_mark_attendance) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color.Yellow)
                .padding(16.dp)
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(text = deviceStatus.message ?: "Device not authorized")
                Spacer(modifier = Modifier.height(8.dp))
                Button(onClick = onSwitchDevice) {
                    Text(text = "Switch Device")
                }
            }
        }
    }
}