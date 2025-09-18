package com.intelliattend.student

import android.app.Application
import android.content.Context
import com.intelliattend.student.bt.BluetoothManager
import com.intelliattend.student.data.collector.GPSDataCollector
import com.intelliattend.student.data.collector.WiFiDataCollector
import com.intelliattend.student.data.preferences.AppPreferences
import com.intelliattend.student.data.repository.AuthRepository
import com.intelliattend.student.data.repository.AttendanceRepository
import com.intelliattend.student.network.ApiClient
import com.intelliattend.student.network.AttendanceService

class IntelliAttendApplication : Application() {
    private lateinit var bluetoothManager: BluetoothManager
    private lateinit var appPreferences: AppPreferences
    private lateinit var apiClient: ApiClient
    private lateinit var attendanceService: AttendanceService
    private lateinit var authRepository: AuthRepository
    private lateinit var attendanceRepository: AttendanceRepository
    private lateinit var gpsDataCollector: GPSDataCollector
    private lateinit var wifiDataCollector: WiFiDataCollector

    override fun onCreate() {
        super.onCreate()
        instance = this
        bluetoothManager = BluetoothManager(this)
        appPreferences = AppPreferences(this)
        apiClient = ApiClient.getInstance(this)
        attendanceService = ApiClient.createAttendanceService()
        authRepository = AuthRepository(apiClient, appPreferences)
        gpsDataCollector = GPSDataCollector(this)
        wifiDataCollector = WiFiDataCollector(this)
        attendanceRepository = AttendanceRepository(this, attendanceService, gpsDataCollector, wifiDataCollector)
    }

    companion object {
        private lateinit var instance: IntelliAttendApplication

        fun getInstance(): IntelliAttendApplication {
            return instance
        }

        fun getContext(): Context {
            return instance.applicationContext
        }
    }

    fun getBluetoothManager(): BluetoothManager {
        return bluetoothManager
    }
    
    fun getAppPreferences(): AppPreferences {
        return appPreferences
    }
    
    fun getAuthRepository(): AuthRepository {
        return authRepository
    }
    
    fun getAttendanceRepository(): AttendanceRepository {
        return attendanceRepository
    }
}