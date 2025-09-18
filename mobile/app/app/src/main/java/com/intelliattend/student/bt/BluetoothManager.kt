package com.intelliattend.student.bt

import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanFilter
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import com.intelliattend.student.data.model.BeaconInfo
import com.intelliattend.student.data.model.DeviceEntry
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.nio.ByteBuffer

@SuppressLint("MissingPermission")
class BluetoothManager(private val context: Context) {

    private val bluetoothAdapter: BluetoothAdapter? = (context.getSystemService(Context.BLUETOOTH_SERVICE) as android.bluetooth.BluetoothManager).adapter
    private val bleScanner = bluetoothAdapter?.bluetoothLeScanner

    private val _scanResults = MutableStateFlow<Map<String, DeviceEntry>>(emptyMap())
    val scanResults = _scanResults.asStateFlow()

    private val _isBluetoothEnabled = MutableStateFlow(bluetoothAdapter?.isEnabled ?: false)
    val isBluetoothEnabled = _isBluetoothEnabled.asStateFlow()

    private val scanCallback = object : ScanCallback() {
        override fun onBatchScanResults(results: MutableList<ScanResult>?) {
            super.onBatchScanResults(results)
            results?.forEach { result ->
                val deviceAddress = result.device.address
                val beaconInfo = parseAdvertisement(result.scanRecord?.bytes)
                val smoothedRssi = getSmoothedRssi(deviceAddress, result.rssi)
                _scanResults.value = _scanResults.value.toMutableMap().apply {
                    this[deviceAddress] = DeviceEntry(
                        device = result.device,
                        rssi = result.rssi,
                        lastSeen = System.currentTimeMillis(),
                        advPayload = result.scanRecord?.bytes,
                        beaconInfo = beaconInfo,
                        smoothedRssi = smoothedRssi
                    )
                }
            }
        }

        override fun onScanFailed(errorCode: Int) {
            super.onScanFailed(errorCode)
            // Handle scan failure
        }
    }

    private val classicDiscoveryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            if (intent.action == BluetoothDevice.ACTION_FOUND) {
                val device: BluetoothDevice? = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
                device?.let {
                    val deviceAddress = it.address
                    val smoothedRssi = getSmoothedRssi(deviceAddress, intent.getShortExtra(BluetoothDevice.EXTRA_RSSI, Short.MIN_VALUE).toInt())
                    _scanResults.value = _scanResults.value.toMutableMap().apply {
                        this[deviceAddress] = DeviceEntry(
                            device = it,
                            rssi = intent.getShortExtra(BluetoothDevice.EXTRA_RSSI, Short.MIN_VALUE).toInt(),
                            lastSeen = System.currentTimeMillis(),
                            name = it.name,
                            smoothedRssi = smoothedRssi
                        )
                    }
                }
            }
        }
    }

    private val bluetoothStateReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            if (intent.action == BluetoothAdapter.ACTION_STATE_CHANGED) {
                val state = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, BluetoothAdapter.ERROR)
                _isBluetoothEnabled.value = state == BluetoothAdapter.STATE_ON
            }
        }
    }

    init {
        context.registerReceiver(bluetoothStateReceiver, IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED))
    }

    fun startBleScan() {
        val scanFilters = listOf(
            ScanFilter.Builder().build() // Add filters here
        )

        val scanSettings = ScanSettings.Builder()
            .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
            .setReportDelay(1000)
            .build()

        bleScanner?.startScan(scanFilters, scanSettings, scanCallback)
    }

    fun stopBleScan() {
        bleScanner?.stopScan(scanCallback)
    }

    fun startClassicDiscovery() {
        context.registerReceiver(classicDiscoveryReceiver, IntentFilter(BluetoothDevice.ACTION_FOUND))
        bluetoothAdapter?.startDiscovery()
    }

    fun stopClassicDiscovery() {
        try {
            context.unregisterReceiver(classicDiscoveryReceiver)
        } catch (e: IllegalArgumentException) {
            // Receiver was not registered
        }
        bluetoothAdapter?.cancelDiscovery()
    }

    /**
     * Clear cached scan results
     */
    fun clearScanResults() {
        _scanResults.value = emptyMap()
    }

    fun cleanup() {
        context.unregisterReceiver(bluetoothStateReceiver)
    }

    private fun parseAdvertisement(bytes: ByteArray?): BeaconInfo? {
        if (bytes == null) return null

        // This is a simplified parser. A real implementation would be more robust.
        try {
            val buffer = ByteBuffer.wrap(bytes)
            // Find manufacturer data
            while (buffer.remaining() > 2) {
                val length = buffer.get().toInt() and 0xFF
                if (length == 0) break
                val type = buffer.get().toInt() and 0xFF
                if (type == 0xFF) { // Manufacturer Specific Data
                    if (length >= 15) {
                        val protocolVersion = buffer.get()
                        val classId = buffer.short.toInt()
                        val sessionToken = buffer.int
                        val facultyId = buffer.short.toInt()
                        val flags = buffer.get()
                        val signature = ByteArray(6)
                        buffer.get(signature)

                        return BeaconInfo(
                            classId = classId,
                            sessionToken = sessionToken,
                            facultyId = facultyId,
                            flags = flags,
                            signature = signature
                        )
                    }
                }
                buffer.position(buffer.position() + length - 1)
            }
        } catch (e: Exception) {
            // Ignore parsing errors
        }
        return null
    }

    private fun getSmoothedRssi(deviceAddress: String, rssi: Int): Double {
        val alpha = 0.4
        val oldRssi = _scanResults.value[deviceAddress]?.smoothedRssi ?: rssi.toDouble()
        return alpha * rssi + (1 - alpha) * oldRssi
    }
}
