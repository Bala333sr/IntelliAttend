package com.intelliattend.student.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class BluetoothDevice(
    val name: String,
    val address: String,
    val rssi: Int = 0,
    val isPaired: Boolean = false
) : Parcelable