package com.intelliattend.student.ui.scanner

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.data.collector.GPSDataCollector
import com.intelliattend.student.data.collector.WiFiDataCollector
import com.intelliattend.student.data.model.QRData
import com.intelliattend.student.data.repository.AttendanceRepository
import com.intelliattend.student.data.repository.AuthRepository
import com.intelliattend.student.network.AttendanceService
import com.intelliattend.student.network.ApiClient
import com.intelliattend.student.utils.QRCodeUtils
import kotlinx.coroutines.launch

class QRScannerViewModel : ViewModel() {
    
    private val context = IntelliAttendApplication.getContext()
    private val apiClient = ApiClient.getInstance(context)
    private val authRepository = AuthRepository(apiClient, IntelliAttendApplication.getInstance().getAppPreferences())
    private val gpsCollector = GPSDataCollector(context)
    private val wifiCollector = WiFiDataCollector(context)
    
    private val attendanceService: AttendanceService = ApiClient.createAttendanceService()
    private val attendanceRepository = AttendanceRepository(
        context = context,
        attendanceService = attendanceService,
        gpsCollector = gpsCollector,
        wifiCollector = wifiCollector
    )
    
    var onScanComplete: ((Boolean, String?) -> Unit)? = null
    
    /**
     * Process scanned QR code
     */
    fun processQRCode(qrContent: String) {
        viewModelScope.launch {
            try {
                // Validate and parse QR data
                val qrData = QRCodeUtils.parseQRData(qrContent)
                
                if (qrData != null) {
                    // Validate QR data
                    if (QRCodeUtils.isValidQRData(qrData)) {
                        // Proceed with attendance marking
                        markAttendance(qrData)
                    } else {
                        onScanComplete?.invoke(false, "Invalid QR code data")
                    }
                } else {
                    onScanComplete?.invoke(false, "Unable to parse QR code")
                }
                
            } catch (e: Exception) {
                Log.e("QRScannerViewModel", "Error processing QR code", e)
                onScanComplete?.invoke(false, "Error processing QR code: ${e.message}")
            }
        }
    }
    
    /**
     * Mark attendance using the QR data
     */
    private suspend fun markAttendance(qrData: QRData) {
        try {
            val student = authRepository.getCurrentStudent()
            
            if (student != null) {
                val result = attendanceRepository.markAttendance(
                    studentId = student.studentId,
                    classId = qrData.sessionId,
                    qrToken = qrData.token
                )
                
                if (result.isSuccess) {
                    val response = result.getOrThrow()
                    onScanComplete?.invoke(response.success, response.message)
                } else {
                    onScanComplete?.invoke(false, result.exceptionOrNull()?.message ?: "Failed to mark attendance")
                }
            } else {
                onScanComplete?.invoke(false, "User not logged in")
            }
            
        } catch (e: Exception) {
            Log.e("QRScannerViewModel", "Error marking attendance", e)
            onScanComplete?.invoke(false, "Error marking attendance: ${e.message}")
        }
    }
}