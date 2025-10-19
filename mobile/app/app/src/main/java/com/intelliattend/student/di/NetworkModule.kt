
package com.intelliattend.student.di

import android.content.Context
import com.intelliattend.student.data.repository.AuthRepository
import com.intelliattend.student.network.ApiClient
import com.intelliattend.student.network.ApiService
import com.intelliattend.student.network.AttendanceService
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideApiClient(@ApplicationContext context: Context): ApiClient {
        return ApiClient.getInstance(context)
    }

    @Provides
    @Singleton
    fun provideApiService(apiClient: ApiClient): ApiService {
        return apiClient.apiService
    }

    @Provides
    @Singleton
    fun provideAttendanceService(): AttendanceService {
        return ApiClient.createAttendanceService()
    }
}
