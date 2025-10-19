
package com.intelliattend.student.di

import android.content.Context
import com.intelliattend.student.data.preferences.AppPreferences
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
object AppModule {

    @Provides
    @Singleton
    fun provideContext(@ApplicationContext context: Context): Context {
        return context
    }

    @Provides
    @Singleton
    fun provideAppPreferences(@ApplicationContext context: Context): AppPreferences {
        return AppPreferences(context)
    }

    @Provides
    @Singleton
    fun provideConnectivityMonitor(@ApplicationContext context: Context): ConnectivityMonitor {
        return ConnectivityMonitor(context)
    }

    @Provides
    @Singleton
    fun provideOfflineQueueManager(@ApplicationContext context: Context): OfflineQueueManager {
        return OfflineQueueManager(context)
    }
}
