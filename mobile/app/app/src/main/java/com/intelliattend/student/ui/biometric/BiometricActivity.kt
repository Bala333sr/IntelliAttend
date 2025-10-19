package com.intelliattend.student.ui.biometric

import android.app.Activity
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.intelliattend.student.R
import com.intelliattend.student.utils.BiometricHelper

class BiometricActivity : AppCompatActivity() {

    private lateinit var biometricHelper: BiometricHelper

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_biometric)

        biometricHelper = BiometricHelper(this)
        biometricHelper.authenticate(
            activity = this,
            title = getString(R.string.biometric_title),
            subtitle = getString(R.string.biometric_subtitle),
            description = getString(R.string.biometric_description),
            onSuccess = {
                setResult(Activity.RESULT_OK)
                finish()
            },
            onError = {
                setResult(Activity.RESULT_CANCELED)
                finish()
            },
            onCancel = {
                setResult(Activity.RESULT_CANCELED)
                finish()
            }
        )
    }
}