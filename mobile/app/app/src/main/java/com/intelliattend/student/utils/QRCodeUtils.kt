package com.intelliattend.student.utils

import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import com.intelliattend.student.data.model.QRData

/**
 * Utility class for QR code parsing and validation
 */
object QRCodeUtils {
    
    private val gson = Gson()
    
    /**
     * Parse QR code content into QRData object
     */
    fun parseQRData(qrContent: String): QRData? {
        return try {
            gson.fromJson(qrContent, QRData::class.java)
        } catch (e: JsonSyntaxException) {
            null
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Validate QR data
     */
    fun isValidQRData(qrData: QRData): Boolean {
        return qrData.sessionId > 0 && 
               qrData.token.isNotBlank() && 
               qrData.timestamp > 0 && 
               !isExpired(qrData.timestamp)
    }
    
    /**
     * Check if QR code is expired (older than 2 minutes)
     */
    private fun isExpired(timestamp: Long): Boolean {
        val currentTime = System.currentTimeMillis() / 1000 // Convert to seconds
        val qrTime = timestamp
        val maxAge = 120 // 2 minutes in seconds
        
        return (currentTime - qrTime) > maxAge
    }
}