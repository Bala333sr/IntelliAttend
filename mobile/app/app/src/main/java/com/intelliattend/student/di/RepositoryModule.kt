
package com.intelliattend.student.di

import android.content.Context
import com.intelliattend.student.data.collector.GPSDataCollector
import com.intelliattend.student.data.collector.WiFiDataCollector
import com.intelliattend.student.data.preferences.AppPreferences
import com.intelliattend.student.data.repository.AuthRepository
import com.intelliattend.student.data.repository.AttendanceRepository
import com.intelliattend.student.data.repository.TimetableRepository
import com.intelliattend.student.network.ApiClient
import com.intelliattend.student.network.ApiService
import com.intelliattend.student.network.AttendanceService
import com.intelliattend.student.utils.ConnectivityMonitor
import com.intelliattend.student.utils.OfflineQueueManager
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {

    @Provides
    @Singleton
    fun provideAuthRepository(apiClient: ApiClient, appPreferences: AppPreferences): AuthRepository {
        return AuthRepository(apiClient, appPreferences)
    }

    @Provides
    @Singleton
    fun provideAttendanceRepository(
        @ApplicationContext context: Context,
        attendanceService: AttendanceService,
        gpsDataCollector: GPSDataCollector,
        wifiDataCollector: WiFiDataCollector,
        connectivityMonitor: ConnectivityMonitor,
        offlineQueueManager: OfflineQueueManager
    ): AttendanceRepository {
        return AttendanceRepository(
            context,
            attendanceService,
            gpsDataCollector,
            wifiDataCollector,
            connectivityMonitor,
            offlineQueueManager
        )
    }

    @Provides
    @Singleton
    fun provideTimetableRepository(apiService: ApiService, @ApplicationContext context: Context): TimetableRepository {
        return TimetableRepository(apiService, context)
    }

    @Provides
    @Singleton
    fun provideGpsDataCollector(@ApplicationContext context: Context): GPSDataCollector {
        return GPSDataCollector(context)
    }

    @Provides
    @Singleton
    fun provideWifiDataCollector(@ApplicationContext context: Context): WiFiDataCollector {
        return WiFiDataCollector(context)
    }
}
