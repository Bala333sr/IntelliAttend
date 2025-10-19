package com.intelliattend.student.data.repository

import android.content.Context
import com.intelliattend.student.data.collector.BluetoothDataCollector
import com.intelliattend.student.data.model.BluetoothData
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

/**
 * Repository for Bluetooth-related operations
 */
class BluetoothRepository(context: Context) {
    
    private val bluetoothCollector = BluetoothDataCollector(context)
    
    /**
     * Get flow of Bluetooth devices discovered during scanning
     */
    fun getBluetoothDevices(): Flow<List<BluetoothData>> = callbackFlow {
        bluetoothCollector.startScanning { devices: List<BluetoothData> ->
            trySend(devices)
        }
        
        awaitClose {
            bluetoothCollector.stopScanning()
        }
    }
    
    /**
     * Get paired Bluetooth devices
     */
    fun getPairedDevices(): List<BluetoothData> {
        return bluetoothCollector.getPairedDevices()
    }
}