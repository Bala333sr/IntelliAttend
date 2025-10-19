package com.intelliattend.student.ui

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.intelliattend.student.ui.theme.IntelliAttendTheme
import com.intelliattend.student.utils.ErrorHandler
import kotlinx.coroutines.CoroutineExceptionHandler

import dagger.hilt.android.AndroidEntryPoint

/**
 * Main Activity for IntelliAttend Student App
 */
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    
    private val TAG = "MainActivity"
    
    // Global exception handler for uncaught exceptions
    private val exceptionHandler = CoroutineExceptionHandler { _, throwable ->
        Log.e(TAG, "Uncaught exception: ${throwable.message}", throwable)
        ErrorHandler.showLongToast(this, "An unexpected error occurred. The app will try to recover.")
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Set up global exception handling
        Thread.setDefaultUncaughtExceptionHandler { thread, throwable ->
            Log.e(TAG, "Uncaught exception on thread ${thread.name}: ${throwable.message}", throwable)
            ErrorHandler.showLongToast(this, "An unexpected error occurred. The app will try to recover.")
        }
        
        setContent {
            IntelliAttendTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    IntelliAttendApp()
                }
            }
        }
    }
    
    override fun onResume() {
        super.onResume()
        Log.d(TAG, "MainActivity resumed")
    }
    
    override fun onPause() {
        super.onPause()
        Log.d(TAG, "MainActivity paused")
    }
}