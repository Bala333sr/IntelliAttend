package com.intelliattend.student.scanner

import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import com.intelliattend.student.data.model.QRData

/**
 * Utility class for QR code validation and parsing
 */
object QRCodeValidator {
    
    private val gson = Gson()
    
    /**
     * Validate and parse QR code content
     */
    fun validateAndParse(qrContent: String): Result<QRData> {
        return try {
            // Parse JSON content
            val qrData = gson.fromJson(qrContent, QRData::class.java)
            
            // Validate required fields
            when {
                qrData.sessionId <= 0 -> {
                    Result.failure(Exception("Invalid session ID"))
                }
                qrData.token.isBlank() -> {
                    Result.failure(Exception("Missing token"))
                }
                qrData.timestamp <= 0 -> {
                    Result.failure(Exception("Invalid timestamp"))
                }
                isExpired(qrData.timestamp) -> {
                    Result.failure(Exception("QR code expired"))
                }
                else -> {
                    Result.success(qrData)
                }
            }
        } catch (e: JsonSyntaxException) {
            Result.failure(Exception("Invalid QR code format"))
        } catch (e: Exception) {
            Result.failure(Exception("QR validation failed: ${e.message}"))
        }
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
    
    /**
     * Get time remaining for QR code validity
     */
    fun getTimeRemaining(timestamp: Long): Long {
        val currentTime = System.currentTimeMillis() / 1000
        val qrTime = timestamp
        val maxAge = 120 // 2 minutes
        val elapsed = currentTime - qrTime
        
        return maxOf(0, maxAge - elapsed)
    }
    
    /**
     * Check if QR code content looks like IntelliAttend format
     */
    fun isIntelliAttendQR(content: String): Boolean {
        return try {
            content.contains("session_id") && 
            content.contains("token") && 
            content.contains("timestamp") &&
            content.startsWith("{") && 
            content.endsWith("}")
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * Format QR data for display
     */
    fun formatQRDataForDisplay(qrData: QRData): String {
        return buildString {
            appendLine("Session ID: ${qrData.sessionId}")
            appendLine("Token: ${qrData.token.take(8)}...")
            appendLine("Sequence: ${qrData.sequence}")
            appendLine("Time Remaining: ${getTimeRemaining(qrData.timestamp)}s")
        }
    }
}