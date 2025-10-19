
package com.intelliattend.student.domain.usecase

import android.content.Context
import com.intelliattend.student.data.repository.AuthRepository
import com.intelliattend.student.network.model.DeviceStatusData
import com.intelliattend.student.utils.DeviceEnforcementUtils

class LoginUseCase(private val authRepository: AuthRepository) {

    suspend operator fun invoke(context: Context, email: String, password: String): Result<Pair<com.intelliattend.student.data.model.Student, DeviceStatusData?>> {
        val deviceInfo = DeviceEnforcementUtils.getDeviceInfo(context, "1.0.0")
        val wifiInfo = DeviceEnforcementUtils.getWiFiInfo(context)
        val gpsInfo = DeviceEnforcementUtils.getCurrentLocation(context)
        val permissionStatus = DeviceEnforcementUtils.getPermissionStatus(context)

        return authRepository.enhancedLogin(
            email = email,
            password = password,
            deviceInfo = deviceInfo,
            wifiInfo = wifiInfo,
            gpsInfo = gpsInfo,
            permissionStatus = permissionStatus
        )
    }
}
