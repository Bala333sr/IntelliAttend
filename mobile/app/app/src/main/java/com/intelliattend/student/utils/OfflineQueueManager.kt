
package com.intelliattend.student.utils

import android.content.Context
import android.content.SharedPreferences
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.intelliattend.student.network.model.OfflineAttendanceRequest

class OfflineQueueManager(context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences("offline_queue", Context.MODE_PRIVATE)
    private val gson = Gson()

    fun addToQueue(request: OfflineAttendanceRequest) {
        val queue = getQueue().toMutableList()
        queue.add(request)
        saveQueue(queue)
    }

    fun getQueue(): List<OfflineAttendanceRequest> {
        val json = prefs.getString("queue", null)
        return if (json != null) {
            val type = object : TypeToken<List<OfflineAttendanceRequest>>() {}.type
            gson.fromJson(json, type)
        } else {
            emptyList()
        }
    }

    fun clearQueue() {
        prefs.edit().remove("queue").apply()
    }

    fun updateQueue(queue: List<OfflineAttendanceRequest>) {
        saveQueue(queue)
    }

    private fun saveQueue(queue: List<OfflineAttendanceRequest>) {
        val json = gson.toJson(queue)
        prefs.edit().putString("queue", json).apply()
    }
}
