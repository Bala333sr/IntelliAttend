package com.intelliattend.mobilemodule.collector

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationManager
import androidx.core.app.ActivityCompat
import com.google.android.gms.location.*
import com.google.android.gms.tasks.CancellationTokenSource
import com.intelliattend.mobilemodule.model.GPSData
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume

/**
 * GPS location data collector
 */
class GPSDataCollector(private val context: Context) {
    
    private val fusedLocationClient: FusedLocationProviderClient = 
        LocationServices.getFusedLocationProviderClient(context)
    
    /**
     * Get current GPS location
     */
    suspend fun getCurrentLocation(): Result<GPSData> = suspendCancellableCoroutine { continuation ->
        // Check location permissions
        if (!hasLocationPermission()) {
            continuation.resume(Result.failure(Exception("Location permission not granted")))
            return@suspendCancellableCoroutine
        }
        
        // Check if location services are enabled
        if (!isLocationEnabled()) {
            continuation.resume(Result.failure(Exception("Location services disabled")))
            return@suspendCancellableCoroutine
        }
        
        val cancellationTokenSource = CancellationTokenSource()
        
        continuation.invokeOnCancellation {
            cancellationTokenSource.cancel()
        }
        
        try {
            val locationRequest = CurrentLocationRequest.Builder()
                .setDurationMillis(10000) // 10 seconds timeout
                .setMaxUpdateAgeMillis(60000) // Accept 1 minute old location
                .setPriority(Priority.PRIORITY_HIGH_ACCURACY)
                .build()
            
            fusedLocationClient.getCurrentLocation(
                locationRequest,
                cancellationTokenSource.token
            ).addOnSuccessListener { location ->
                if (location != null) {
                    val gpsData = GPSData(
                        latitude = location.latitude,
                        longitude = location.longitude,
                        accuracy = location.accuracy,
                        altitude = location.altitude,
                        speed = location.speed
                    )
                    continuation.resume(Result.success(gpsData))
                } else {
                    continuation.resume(Result.failure(Exception("Unable to get location")))
                }
            }.addOnFailureListener { exception ->
                continuation.resume(Result.failure(exception))
            }
        } catch (e: SecurityException) {
            continuation.resume(Result.failure(Exception("Location permission denied")))
        } catch (e: Exception) {
            continuation.resume(Result.failure(e))
        }
    }
    
    /**
     * Get last known location (faster but may be outdated)
     */
    suspend fun getLastKnownLocation(): Result<GPSData> = suspendCancellableCoroutine { continuation ->
        if (!hasLocationPermission()) {
            continuation.resume(Result.failure(Exception("Location permission not granted")))
            return@suspendCancellableCoroutine
        }
        
        try {
            fusedLocationClient.lastLocation.addOnSuccessListener { location ->
                if (location != null) {
                    val gpsData = GPSData(
                        latitude = location.latitude,
                        longitude = location.longitude,
                        accuracy = location.accuracy,
                        altitude = location.altitude,
                        speed = location.speed
                    )
                    continuation.resume(Result.success(gpsData))
                } else {
                    continuation.resume(Result.failure(Exception("No last known location")))
                }
            }.addOnFailureListener { exception ->
                continuation.resume(Result.failure(exception))
            }
        } catch (e: SecurityException) {
            continuation.resume(Result.failure(Exception("Location permission denied")))
        } catch (e: Exception) {
            continuation.resume(Result.failure(e))
        }
    }
    
    /**
     * Check if location permissions are granted
     */
    private fun hasLocationPermission(): Boolean {
        return ActivityCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED ||
        ActivityCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    /**
     * Check if location services are enabled
     */
    private fun isLocationEnabled(): Boolean {
        val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
        return locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER) ||
               locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)
    }
    
    /**
     * Calculate distance between two GPS points in meters
     */
    fun calculateDistance(
        lat1: Double, lon1: Double,
        lat2: Double, lon2: Double
    ): Float {
        val results = FloatArray(1)
        Location.distanceBetween(lat1, lon1, lat2, lon2, results)
        return results[0]
    }
    
    /**
     * Check if current location is within geofence
     */
    fun isWithinGeofence(
        currentLocation: GPSData,
        targetLatitude: Double,
        targetLongitude: Double,
        radiusMeters: Float
    ): Boolean {
        val distance = calculateDistance(
            currentLocation.latitude, currentLocation.longitude,
            targetLatitude, targetLongitude
        )
        return distance <= radiusMeters
    }
}