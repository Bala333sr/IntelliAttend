package com.intelliattend.student.data.model

data class BeaconInfo(
    val classId: Int,
    val sessionToken: Int,
    val facultyId: Int,
    val flags: Byte,
    val signature: ByteArray
)
