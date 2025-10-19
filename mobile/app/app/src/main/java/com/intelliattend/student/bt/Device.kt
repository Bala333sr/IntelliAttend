package com.intelliattend.student.bt

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class Device(
    val name: String?,
    val address: String,
    val uuid: String? = null,
    var rssi: Int,
    var isRegistered: Boolean = false,
    val manufacturerData: ByteArray? = null,
    val serviceData: Map<String, ByteArray>? = null,
    val classId: String? = null,
    val sessionToken: String? = null,
    val facultyId: String? = null,
    val signature: String? = null
) : Parcelable {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false

        other as Device

        if (name != other.name) return false
        if (address != other.address) return false
        if (uuid != other.uuid) return false
        if (rssi != other.rssi) return false
        if (isRegistered != other.isRegistered) return false
        if (classId != other.classId) return false
        if (sessionToken != other.sessionToken) return false
        if (facultyId != other.facultyId) return false
        if (signature != other.signature) return false

        return true
    }

    override fun hashCode(): Int {
        var result = name?.hashCode() ?: 0
        result = 31 * result + address.hashCode()
        result = 31 * result + (uuid?.hashCode() ?: 0)
        result = 31 * result + rssi
        result = 31 * result + isRegistered.hashCode()
        result = 31 * result + (classId?.hashCode() ?: 0)
        result = 31 * result + (sessionToken?.hashCode() ?: 0)
        result = 31 * result + (facultyId?.hashCode() ?: 0)
        result = 31 * result + (signature?.hashCode() ?: 0)
        return result
    }
}