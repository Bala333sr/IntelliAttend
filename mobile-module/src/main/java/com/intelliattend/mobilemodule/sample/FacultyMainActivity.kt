package com.intelliattend.faculty

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.intelliattend.mobilemodule.IntelliAttendMobileModule
import com.intelliattend.mobilemodule.collector.EnvironmentalDataCollector

/**
 * Example Faculty App that uses the IntelliAttend Mobile Module
 */
class FacultyMainActivity : AppCompatActivity() {
    
    private lateinit var mobileModule: IntelliAttendMobileModule
    private lateinit var environmentalDataCollector: EnvironmentalDataCollector
    
    // Permission request launcher
    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.all { it.value }
        if (allGranted) {
            initializeModule()
        } else {
            Toast.makeText(this, "Permissions required for faculty features", Toast.LENGTH_LONG).show()
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_faculty_main)
        
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
            initializeModule()
        }
    }
    
    private fun initializeModule() {
        // The module is now ready to use
        Toast.makeText(this, "IntelliAttend Mobile Module initialized", Toast.LENGTH_SHORT).show()
        
        // Example: Check if faculty is in the designated classroom area
        // using GPS geofencing
        checkClassroomProximity()
        
        // Example: Verify faculty device is registered for attendance tracking
        // using Bluetooth proximity
        verifyFacultyDevice()
    }
    
    private fun checkClassroomProximity() {
        // Use GPS data to verify faculty is in the correct classroom
        // This would typically be implemented with the repository pattern
        // and reactive data streams
    }
    
    private fun verifyFacultyDevice() {
        // Use Bluetooth data to verify faculty device is present
        // This would typically use the Bluetooth collector directly
    }
}