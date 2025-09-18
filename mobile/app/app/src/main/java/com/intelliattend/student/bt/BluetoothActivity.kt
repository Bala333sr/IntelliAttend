package com.intelliattend.student.bt

import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.appcompat.app.AppCompatActivity
import com.intelliattend.student.ui.theme.IntelliAttendTheme

class BluetoothActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            IntelliAttendTheme {
                BluetoothScreen(onBack = { finish() })
            }
        }
    }
}
