package com.intelliattend.mobilemodule.sample

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.intelliattend.mobilemodule.IntelliAttendMobileModule
import com.intelliattend.mobilemodule.collector.EnvironmentalDataCollector
import kotlinx.coroutines.launch

/**
 * Sample activity demonstrating how to use the IntelliAttend Mobile Module
 */
class SampleActivity : AppCompatActivity() {
    
    private lateinit var mobileModule: IntelliAttendMobileModule
    private lateinit var environmentalDataCollector: EnvironmentalDataCollector
    
    // Permission request launcher
    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.all { it.value }
        if (allGranted) {
            startDataCollection()
        } else {
            Toast.makeText(this, "Permissions required for environmental data collection", Toast.LENGTH_LONG).show()
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_sample)
        
        // Initialize the mobile module
        mobileModule = IntelliAttendMobileModule.create(this)
        environmentalDataCollector = mobileModule.getEnvironmentalDataCollector()
        
        // Check and request permissions
        checkAndRequestPermissions()
    }
    
    private fun checkAndRequestPermissions() {
        val requiredPermissions = arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN
        )
        
        // Add Bluetooth permissions for Android 12+
        val allPermissions = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.S) {
            requiredPermissions + arrayOf(
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.BLUETOOTH_CONNECT
            )
        } else {
            requiredPermissions
        }
        
        val permissionsToRequest = allPermissions.filter { permission ->
            ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED
        }.toTypedArray()
        
        if (permissionsToRequest.isNotEmpty()) {
            permissionLauncher.launch(permissionsToRequest)
        } else {
            startDataCollection()
        }
    }
    
    private fun startDataCollection() {
        // Start collecting environmental data
        environmentalDataCollector.startCollecting(object : EnvironmentalDataCollector.EnvironmentalDataCallback {
            override fun onDataUpdated(data: EnvironmentalDataCollector.EnvironmentalData) {
                // Update UI with the collected data
                runOnUiThread {
                    updateUI(data)
                }
            }
            
            override fun onError(error: Exception) {
                runOnUiThread {
                    Toast.makeText(this@SampleActivity, "Error: ${error.message}", Toast.LENGTH_SHORT).show()
                }
            }
        })
    }
    
    private fun updateUI(data: EnvironmentalDataCollector.EnvironmentalData) {
        // Update UI components with the collected data
        data.wifiData?.let { wifi ->
            // Update WiFi information in UI
            // e.g., wifiSSIDTextView.text = wifi.ssid
        }
        
        // Update Bluetooth devices list
        // bluetoothDevicesAdapter.updateDevices(data.bluetoothDevices)
        
        data.gpsData?.let { gps ->
            // Update GPS information in UI
            // e.g., locationTextView.text = "${gps.latitude}, ${gps.longitude}"
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // Stop data collection to free resources
        environmentalDataCollector.stopCollecting()
    }
}