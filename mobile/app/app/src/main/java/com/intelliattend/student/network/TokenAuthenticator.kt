
package com.intelliattend.student.network

import com.intelliattend.student.data.preferences.AppPreferences
import com.intelliattend.student.data.repository.AuthRepository
import kotlinx.coroutines.runBlocking
import okhttp3.Authenticator
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route

class TokenAuthenticator(private val appPreferences: AppPreferences) : Authenticator {

    lateinit var authRepository: AuthRepository

    override fun authenticate(route: Route?, response: Response): Request? {
        val email = appPreferences.lastLoggedInEmail
        val password = appPreferences.lastLoggedInPassword

        if (email != null && password != null) {
            return runBlocking {
                val result = authRepository.login(email, password)
                if (result.isSuccess) {
                    val newAccessToken = appPreferences.accessToken
                    response.request.newBuilder()
                        .header("Authorization", "Bearer $newAccessToken")
                        .build()
                } else {
                    null
                }
            }
        } else {
            return null
        }
    }
}
