package com.intelliattend.student.bt

import android.app.Application
import android.content.Context
import android.content.SharedPreferences
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.data.model.DeviceEntry
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.intelliattend.student.data.model.BluetoothData
import java.util.*

class BluetoothViewModel(application: Application) : AndroidViewModel(application) {

    private val bluetoothManager = BluetoothManager(application)
    private val sharedPreferences: SharedPreferences = application.getSharedPreferences("registered_devices", Context.MODE_PRIVATE)
    private val gson = Gson()

    private val _isScanning = MutableStateFlow(false)
    val isScanning = _isScanning.asStateFlow()

    val scanResults = bluetoothManager.scanResults
    val isBluetoothEnabled = bluetoothManager.isBluetoothEnabled

    fun startScan() {
        viewModelScope.launch {
            _isScanning.value = true
            bluetoothManager.startBleScan()
            delay(700) // BLE scan for 700ms
            if (scanResults.value.isEmpty()) {
                bluetoothManager.stopBleScan()
                bluetoothManager.startClassicDiscovery()
                delay(12000) // Classic discovery for 12 seconds
            }
            stopScan()
        }
    }

    private fun stopScan() {
        viewModelScope.launch {
            _isScanning.value = false
            bluetoothManager.stopBleScan()
            bluetoothManager.stopClassicDiscovery()
        }
    }

    // Add function to register a device
    fun registerDevice(deviceEntry: DeviceEntry) {
        viewModelScope.launch {
            val existingDevicesJson = sharedPreferences.getString("registered_bluetooth_devices", null)
            val type = object : TypeToken<MutableList<BluetoothData>>() {}.type
            val registeredDevices: MutableList<BluetoothData> = existingDevicesJson?.let {
                gson.fromJson(it, type)
            } ?: mutableListOf()

            val newBluetoothData = BluetoothData(
                name = deviceEntry.device.name ?: "Unknown Device",
                address = deviceEntry.device.address,
                rssi = deviceEntry.rssi
            )

            val existingDeviceIndex = registeredDevices.indexOfFirst { it.address == newBluetoothData.address }
            if (existingDeviceIndex != -1) {
                registeredDevices[existingDeviceIndex] = newBluetoothData
            } else {
                registeredDevices.add(newBluetoothData)
            }

            val updatedDevicesJson = gson.toJson(registeredDevices)
            sharedPreferences.edit().putString("registered_bluetooth_devices", updatedDevicesJson).apply()
        }
    }

    fun submitAttendance(deviceEntry: DeviceEntry) {
        // Simplified implementation without server communication
        viewModelScope.launch {
            // In a real implementation, this would submit attendance data
            // For now, we'll just log that the function was called
            println("Attendance submission requested for device: ${deviceEntry.device.address}")
        }
    }

    override fun onCleared() {
        super.onCleared()
        bluetoothManager.cleanup()
    }
}