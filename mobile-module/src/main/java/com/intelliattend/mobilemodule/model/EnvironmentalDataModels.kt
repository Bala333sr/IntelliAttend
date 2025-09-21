package com.intelliattend.mobilemodule.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

/**
 * WiFi data model
 */
@Parcelize
data class WiFiData(
    val ssid: String,
    val bssid: String,
    val rssi: Int,
    val ipAddress: String,
    val frequency: Int = 0
) : Parcelable

/**
 * GPS data model
 */
@Parcelize
data class GPSData(
    val latitude: Double,
    val longitude: Double,
    val accuracy: Float,
    val altitude: Double = 0.0,
    val speed: Float = 0.0f
) : Parcelable

/**
 * Bluetooth data model
 */
@Parcelize
data class BluetoothData(
    val name: String,
    val address: String,
    val rssi: Int = 0,
    val isPaired: Boolean = false
) : Parcelable

/**
 * Device information model
 */
@Parcelize
data class DeviceInfo(
    val deviceId: String,
    val deviceName: String,
    val osVersion: String,
    val appVersion: String,
    val deviceModel: String,
    val manufacturer: String
) : Parcelable