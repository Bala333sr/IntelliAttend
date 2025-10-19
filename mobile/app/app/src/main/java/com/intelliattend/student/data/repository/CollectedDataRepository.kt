package com.intelliattend.student.data.repository

import android.content.Context
import android.content.SharedPreferences
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.intelliattend.student.data.model.CollectedData
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Repository for managing collected data that can be sent to server
 */
class CollectedDataRepository(private val context: Context) {
    
    private val gson = Gson()
    private val prefs: SharedPreferences = context.getSharedPreferences("collected_data", Context.MODE_PRIVATE)
    
    /**
     * Save collected data to local storage
     */
    suspend fun saveCollectedData(data: CollectedData) = withContext(Dispatchers.IO) {
        try {
            val dataList = getAllCollectedData().toMutableList()
            dataList.add(data)
            val json = gson.toJson(dataList)
            prefs.edit().putString("collected_data_list", json).apply()
        } catch (e: Exception) {
            // Handle error
        }
    }
    
    /**
     * Get all collected data that hasn't been sent to server
     */
    suspend fun getAllCollectedData(): List<CollectedData> = withContext(Dispatchers.IO) {
        try {
            val json = prefs.getString("collected_data_list", null)
            if (json != null) {
                val type = object : TypeToken<List<CollectedData>>() {}.type
                gson.fromJson(json, type)
            } else {
                emptyList()
            }
        } catch (e: Exception) {
            emptyList()
        }
    }
    
    /**
     * Get collected data that hasn't been sent to server
     */
    suspend fun getUnsentCollectedData(): List<CollectedData> = withContext(Dispatchers.IO) {
        try {
            getAllCollectedData().filter { !it.isSent }
        } catch (e: Exception) {
            emptyList()
        }
    }
    
    /**
     * Mark collected data as sent
     */
    suspend fun markAsSent(dataId: String) = withContext(Dispatchers.IO) {
        try {
            val dataList = getAllCollectedData().toMutableList()
            val index = dataList.indexOfFirst { it.id == dataId }
            if (index != -1) {
                val updatedData = dataList[index].copy(isSent = true)
                dataList[index] = updatedData
                val json = gson.toJson(dataList)
                prefs.edit().putString("collected_data_list", json).apply()
            }
        } catch (e: Exception) {
            // Handle error
        }
    }
    
    /**
     * Clear all collected data
     */
    suspend fun clearAllData() = withContext(Dispatchers.IO) {
        prefs.edit().remove("collected_data_list").apply()
    }
    
    /**
     * Clear sent data to save space
     */
    suspend fun clearSentData() = withContext(Dispatchers.IO) {
        try {
            val unsentData = getUnsentCollectedData()
            val json = gson.toJson(unsentData)
            prefs.edit().putString("collected_data_list", json).apply()
        } catch (e: Exception) {
            // Handle error
        }
    }
}