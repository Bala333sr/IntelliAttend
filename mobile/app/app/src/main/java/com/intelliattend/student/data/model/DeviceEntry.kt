package com.intelliattend.student.data.model

import android.bluetooth.BluetoothDevice

data class DeviceEntry(
    val device: BluetoothDevice,
    var rssi: Int,
    var lastSeen: Long,
    var name: String? = null,
    var advPayload: ByteArray? = null,
    var beaconInfo: BeaconInfo? = null,
    var smoothedRssi: Double? = null
)
