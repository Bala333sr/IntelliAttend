package com.intelliattend.student.presence

import android.util.Log
import com.intelliattend.student.IntelliAttendApplication
import com.intelliattend.student.data.model.Student
import kotlinx.coroutines.*
import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import java.net.URI

/**
 * Service for tracking student presence via WebSocket connection
 */
class PresenceTrackingService {
    
    private var webSocketClient: WebSocketClient? = null
    private var isConnected = false
    private var isConnecting = false
    private var heartbeatJob: Job? = null
    private var notificationCallback: ((String, String, String) -> Unit)? = null
    private var coroutineScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    companion object {
        private const val TAG = "PresenceTracking"
        private const val HEARTBEAT_INTERVAL = 15000L // 15 seconds
        private const val RECONNECT_DELAY = 5000L // 5 seconds
    }
    
    /**
     * Set callback for presence notifications
     */
    fun setNotificationCallback(callback: (studentId: String, status: String, timestamp: String) -> Unit) {
        this.notificationCallback = callback
    }
    
    /**
     * Connect to presence tracking WebSocket server
     */
    fun connect(student: Student) {
        if (isConnecting || isConnected) {
            Log.d(TAG, "Already connecting or connected")
            return
        }
        
        isConnecting = true
        
        try {
            // Get server URL from preferences
            val app = IntelliAttendApplication.getInstance()
            val baseUrl = app.getAppPreferences().baseUrl
            val wsUrl = convertHttpToWsUrl(baseUrl)
            
            Log.d(TAG, "Connecting to WebSocket server: $wsUrl")
            
            webSocketClient = object : WebSocketClient(URI(wsUrl)) {
                override fun onOpen(handshakedata: ServerHandshake?) {
                    Log.d(TAG, "WebSocket connection opened")
                    isConnected = true
                    isConnecting = false
                    
                    // Send connect message
                    sendConnectMessage(student)
                    
                    // Subscribe to notifications
                    subscribeToNotifications()
                    
                    // Start heartbeat
                    startHeartbeat()
                }
                
                override fun onMessage(message: String?) {
                    Log.d(TAG, "Received message: $message")
                    // Handle pong messages or other server responses
                    if (message != null) {
                        try {
                            val json = com.google.gson.Gson().fromJson(message, Map::class.java)
                            val event = json["event"] as? String
                            
                            when (event) {
                                "pong" -> {
                                    // Pong response, do nothing
                                }
                                "connected" -> {
                                    // Connected response, do nothing
                                }
                                "presence_change" -> {
                                    // Handle presence change notification
                                    val studentId = json["student_id"] as? String
                                    val status = json["status"] as? String
                                    val timestamp = json["timestamp"] as? String
                                    
                                    if (studentId != null && status != null && timestamp != null) {
                                        notificationCallback?.invoke(studentId, status, timestamp)
                                    }
                                }
                                else -> {
                                    // Handle other events or do nothing
                                }
                            }
                        } catch (e: Exception) {
                            Log.e(TAG, "Failed to parse message", e)
                        }
                    }
                }
                
                override fun onClose(code: Int, reason: String?, remote: Boolean) {
                    Log.d(TAG, "WebSocket connection closed: $code, $reason, remote: $remote")
                    isConnected = false
                    isConnecting = false
                    stopHeartbeat()
                    
                    // Attempt to reconnect if needed
                    if (remote) {
                        scheduleReconnect(student)
                    }
                }
                
                override fun onError(ex: Exception?) {
                    Log.e(TAG, "WebSocket error", ex)
                    isConnecting = false
                }
            }
            
            webSocketClient?.connect()
        } catch (e: Exception) {
            Log.e(TAG, "Failed to create WebSocket connection", e)
            isConnecting = false
        }
    }
    
    /**
     * Disconnect from presence tracking WebSocket server
     */
    fun disconnect() {
        try {
            stopHeartbeat()
            webSocketClient?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error during disconnect", e)
        } finally {
            isConnected = false
            isConnecting = false
            webSocketClient = null
        }
    }
    
    /**
     * Send connect message to server
     */
    private fun sendConnectMessage(student: Student) {
        try {
            val connectMessage = mapOf(
                "event" to "connect",
                "student_id" to "STU${student.studentId}",
                "device" to android.os.Build.MODEL
            )
            
            val json = com.google.gson.Gson().toJson(connectMessage)
            webSocketClient?.send(json)
            Log.d(TAG, "Sent connect message: $json")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to send connect message", e)
        }
    }
    
    /**
     * Subscribe to presence notifications
     */
    private fun subscribeToNotifications() {
        try {
            val subscribeMessage = mapOf(
                "event" to "subscribe_notifications"
            )
            
            val json = com.google.gson.Gson().toJson(subscribeMessage)
            webSocketClient?.send(json)
            Log.d(TAG, "Sent subscribe notifications message: $json")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to send subscribe notifications message", e)
        }
    }
    
    /**
     * Send ping message to server
     */
    private fun sendPingMessage(student: Student) {
        if (!isConnected) return
        
        try {
            val pingMessage = mapOf(
                "event" to "ping",
                "student_id" to "STU${student.studentId}"
            )
            
            val json = com.google.gson.Gson().toJson(pingMessage)
            webSocketClient?.send(json)
            Log.d(TAG, "Sent ping message: $json")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to send ping message", e)
        }
    }
    
    /**
     * Start heartbeat to keep connection alive
     */
    private fun startHeartbeat() {
        stopHeartbeat() // Stop any existing heartbeat
        
        heartbeatJob = coroutineScope.launch {
            val student = IntelliAttendApplication.getInstance().getAuthRepository().getCurrentStudent()
            if (student == null) {
                Log.w(TAG, "No student data available for heartbeat")
                return@launch
            }
            
            while (isActive && isConnected) {
                delay(HEARTBEAT_INTERVAL)
                if (isConnected) {
                    sendPingMessage(student)
                }
            }
        }
    }
    
    /**
     * Stop heartbeat
     */
    private fun stopHeartbeat() {
        heartbeatJob?.cancel()
        heartbeatJob = null
    }
    
    /**
     * Schedule reconnection attempt
     */
    private fun scheduleReconnect(student: Student) {
        coroutineScope.launch {
            delay(RECONNECT_DELAY)
            if (!isConnected && !isConnecting) {
                Log.d(TAG, "Attempting to reconnect...")
                connect(student)
            }
        }
    }
    
    /**
     * Convert HTTP URL to WebSocket URL
     */
    private fun convertHttpToWsUrl(httpUrl: String): String {
        var wsUrl = if (httpUrl.startsWith("https://")) {
            httpUrl.replaceFirst("https://", "wss://")
        } else {
            httpUrl.replaceFirst("http://", "ws://")
        }.replace("/api/", ":8765/")
        
        // Handle localhost to use the actual server IP if needed
        // If the app is running on a different device, localhost won't work
        if (wsUrl.contains("localhost") || wsUrl.contains("127.0.0.1")) {
            // Try to get the actual server IP from the API URL
            val apiHost = httpUrl.replace(Regex("https?://"), "").takeWhile { it != '/' }
            if (!apiHost.contains("localhost") && !apiHost.contains("127.0.0.1")) {
                val hostWithoutPort = apiHost.split(":")[0]
                wsUrl = wsUrl.replace(Regex("localhost|127.0.0.1"), hostWithoutPort)
            } else {
                // If we still have localhost, replace with the actual server IP
                wsUrl = wsUrl.replace("localhost", "192.168.0.6").replace("127.0.0.1", "192.168.0.6")
            }
        }
        
        return wsUrl
    }
    
    /**
     * Check if currently connected
     */
    fun isConnected(): Boolean {
        return isConnected
    }
}