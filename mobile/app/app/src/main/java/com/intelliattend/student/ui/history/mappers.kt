
package com.intelliattend.student.ui.history

import com.intelliattend.student.network.AttendanceHistoryRecord
import com.intelliattend.student.network.model.OfflineAttendanceRequest

fun AttendanceHistoryRecord.toAttendanceRecord(): AttendanceRecord {
    return AttendanceRecord(
        id = this.recordId.toString(),
        subject = this.className,
        date = this.scanTimestamp,
        status = when (this.status.lowercase()) {
            "present" -> AttendanceStatus.PRESENT
            "late" -> AttendanceStatus.LATE
            else -> AttendanceStatus.ABSENT
        },
        verificationMethods = mutableListOf<VerificationMethod>().apply {
            if (this@toAttendanceRecord.verificationScore >= 0.4) add(VerificationMethod.BIOMETRIC)
            if (this@toAttendanceRecord.verificationScore >= 0.4) add(VerificationMethod.GPS)
            if (this@toAttendanceRecord.verificationScore >= 0.2) add(VerificationMethod.BLUETOOTH)
            if (this@toAttendanceRecord.verificationScore >= 0.2) add(VerificationMethod.WIFI)
        }
    )
}

fun OfflineAttendanceRequest.toAttendanceRecord(): AttendanceRecord {
    return AttendanceRecord(
        id = this.request.timestamp,
        subject = "Class ID: ${this.request.classId}",
        date = this.request.timestamp,
        status = when (this.status) {
            "Pending Sync" -> AttendanceStatus.PENDING_SYNC
            "Sync Failed" -> AttendanceStatus.SYNC_FAILED
            else -> AttendanceStatus.UNKNOWN
        },
        verificationMethods = emptyList()
    )
}
