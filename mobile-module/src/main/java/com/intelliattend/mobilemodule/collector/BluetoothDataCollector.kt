package com.intelliattend.mobilemodule.collector

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.bluetooth.le.BluetoothLeScanner
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanFilter
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.os.Handler
import android.os.Looper
import androidx.core.content.ContextCompat
import androidx.core.content.getSystemService
import com.intelliattend.mobilemodule.model.BluetoothData
import java.util.concurrent.ConcurrentHashMap

/**
 * Bluetooth data collector that behaves like the system Bluetooth settings app
 * Uses BLE scanning with batching, deduplication, and name caching for accurate results
 */
class BluetoothDataCollector(private val context: Context) {
    
    private var bluetoothAdapter: BluetoothAdapter? = null
    private var bleScanner: BluetoothLeScanner? = null
    private val deviceCache = ConcurrentHashMap<String, BluetoothData>()
    private val deviceNameCache = ConcurrentHashMap<String, String>()
    private var scanCallback: ScanCallback? = null
    private var isScanning = false
    private var onDevicesUpdated: ((List<BluetoothData>) -> Unit)? = null
    private val handler = Handler(Looper.getMainLooper())
    private var updateRunnable: Runnable? = null
    private val updateInterval = 1000L // Update UI every 1 second
    
    init {
        val bluetoothManager = context.getSystemService<BluetoothManager>()
        bluetoothAdapter = bluetoothManager?.adapter
        bleScanner = bluetoothAdapter?.bluetoothLeScanner
    }
    
    /**
     * Start Bluetooth scanning with optimal settings
     */
    fun startScanning(onDevicesUpdated: (List<BluetoothData>) -> Unit) {
        this.onDevicesUpdated = onDevicesUpdated
        
        if (!isBluetoothAvailable() || !hasBluetoothPermissions()) {
            onDevicesUpdated(emptyList())
            return
        }
        
        // Clear previous scan data
        deviceCache.clear()
        
        // Set up BLE scan callback
        scanCallback = object : ScanCallback() {
            override fun onScanResult(callbackType: Int, result: ScanResult) {
                processScanResult(result)
            }
            
            override fun onBatchScanResults(results: MutableList<ScanResult>) {
                results.forEach { processScanResult(it) }
            }
            
            override fun onScanFailed(errorCode: Int) {
                // Handle scan failure
                this@BluetoothDataCollector.onDevicesUpdated?.invoke(deviceCache.values.toList())
            }
        }
        
        // Configure scan settings with batching for efficiency
        val scanSettings = ScanSettings.Builder()
            .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
            .setReportDelay(1000) // Batch results every 1 second
            .build()
        
        // Start BLE scanning
        bleScanner?.startScan(emptyList<ScanFilter>(), scanSettings, scanCallback)
        isScanning = true
        
        // Schedule periodic UI updates
        scheduleUIUpdate()
    }
    
    /**
     * Process individual scan results with deduplication and name caching
     */
    private fun processScanResult(result: ScanResult) {
        val device = result.device
        val address = device.address
        
        // Get device name, using cached name if current name is null
        val currentName = device.name
        val cachedName = deviceNameCache[address]
        val displayName = when {
            !currentName.isNullOrEmpty() -> {
                // Update cache with latest name
                deviceNameCache[address] = currentName
                currentName
            }
            !cachedName.isNullOrEmpty() -> cachedName
            else -> "Unknown Device"
        }
        
        // Create BluetoothDevice object with deduplication by MAC address
        val bluetoothDevice = BluetoothData(
            name = displayName,
            address = address,
            rssi = result.rssi
        )
        
        // Store in cache (this automatically deduplicates by address)
        deviceCache[address] = bluetoothDevice
    }
    
    /**
     * Schedule periodic UI updates to avoid excessive refreshes
     */
    private fun scheduleUIUpdate() {
        updateRunnable = object : Runnable {
            override fun run() {
                if (isScanning) {
                    // Update UI with current device list
                    onDevicesUpdated?.invoke(deviceCache.values.toList())
                    
                    // Schedule next update
                    handler.postDelayed(this, updateInterval)
                }
            }
        }
        
        // Start the update cycle
        handler.post(updateRunnable!!)
    }
    
    /**
     * Stop Bluetooth scanning
     */
    fun stopScanning() {
        isScanning = false
        updateRunnable?.let { handler.removeCallbacks(it) }
        scanCallback?.let { bleScanner?.stopScan(it) }
    }
    
    /**
     * Check if Bluetooth is available and enabled
     */
    private fun isBluetoothAvailable(): Boolean {
        return bluetoothAdapter?.isEnabled == true
    }
    
    /**
     * Check if required Bluetooth permissions are granted
     */
    private fun hasBluetoothPermissions(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.BLUETOOTH_SCAN
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.BLUETOOTH_ADMIN
            ) == PackageManager.PERMISSION_GRANTED
        }
    }
    
    /**
     * Get paired devices (classic Bluetooth)
     */
    fun getPairedDevices(): List<BluetoothData> {
        if (!isBluetoothAvailable() || !hasBluetoothPermissions()) return emptyList()
        
        return bluetoothAdapter?.bondedDevices?.map { device ->
            val cachedName = deviceNameCache[device.address]
            val displayName = when {
                !device.name.isNullOrEmpty() -> {
                    deviceNameCache[device.address] = device.name
                    device.name
                }
                !cachedName.isNullOrEmpty() -> cachedName
                else -> "Unknown Device"
            }
            
            BluetoothData(
                name = displayName,
                address = device.address,
                isPaired = true
            )
        } ?: emptyList()
    }
    
    /**
     * Check if a specific device is in range
     */
    fun isDeviceInRange(deviceAddress: String): Boolean {
        return deviceCache.containsKey(deviceAddress)
    }
    
    /**
     * Get RSSI value for a specific device
     */
    fun getDeviceRssi(deviceAddress: String): Int? {
        return deviceCache[deviceAddress]?.rssi
    }
}