package com.intelliattend.mobilemodule

import android.content.Context
import com.intelliattend.mobilemodule.collector.EnvironmentalDataCollector
import com.intelliattend.mobilemodule.repository.EnvironmentalDataRepository
import com.intelliattend.mobilemodule.utils.DeviceUtils

/**
 * Main entry point for the IntelliAttend Mobile Module
 * Provides access to WiFi, Bluetooth, and GPS functionality in a unified manner
 */
class IntelliAttendMobileModule(private val context: Context) {
    
    private val environmentalDataCollector: EnvironmentalDataCollector
    private val environmentalDataRepository: EnvironmentalDataRepository
    private val deviceUtils: DeviceUtils
    
    init {
        environmentalDataCollector = EnvironmentalDataCollector(context)
        environmentalDataRepository = EnvironmentalDataRepository(context)
        deviceUtils = DeviceUtils()
    }
    
    /**
     * Get the environmental data collector
     */
    fun getEnvironmentalDataCollector(): EnvironmentalDataCollector {
        return environmentalDataCollector
    }
    
    /**
     * Get the environmental data repository
     */
    fun getEnvironmentalDataRepository(): EnvironmentalDataRepository {
        return environmentalDataRepository
    }
    
    /**
     * Get device utilities
     */
    fun getDeviceUtils(): DeviceUtils {
        return deviceUtils
    }
    
    /**
     * Check if all required permissions are granted
     */
    fun checkPermissions(): Map<String, Boolean> {
        return deviceUtils.checkPermissions(context)
    }
    
    /**
     * Get comprehensive device information
     */
    fun getDeviceInfo() = deviceUtils.getDeviceInfo(context)
    
    companion object {
        /**
         * Create an instance of the IntelliAttend Mobile Module
         */
        fun create(context: Context): IntelliAttendMobileModule {
            return IntelliAttendMobileModule(context)
        }
    }
}