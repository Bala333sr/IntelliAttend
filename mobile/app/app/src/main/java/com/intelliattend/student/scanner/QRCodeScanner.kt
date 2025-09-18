package com.intelliattend.student.scanner

import android.content.Context
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import com.google.mlkit.vision.barcode.BarcodeScanner
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.common.InputImage
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * QR Code Scanner using CameraX and ML Kit
 */
class QRCodeScanner(
    private val context: Context,
    private val previewView: PreviewView,
    private val lifecycleOwner: LifecycleOwner,
    private val onQRCodeDetected: (String) -> Unit,
    private val onError: (String) -> Unit
) {
    
    private var cameraProvider: ProcessCameraProvider? = null
    private var camera: Camera? = null
    private var preview: Preview? = null
    private var imageAnalysis: ImageAnalysis? = null
    private var cameraExecutor: ExecutorService = Executors.newSingleThreadExecutor()
    
    private val barcodeScanner: BarcodeScanner by lazy {
        val options = BarcodeScannerOptions.Builder()
            .setBarcodeFormats(Barcode.FORMAT_QR_CODE)
            .build()
        BarcodeScanning.getClient(options)
    }
    
    private var isScanning = true
    private var lastDetectedTime = 0L
    private val SCAN_COOLDOWN = 2000L // 2 seconds cooldown between scans
    
    /**
     * Start the camera and QR scanning
     */
    fun startScanning() {
        isScanning = true
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
        
        cameraProviderFuture.addListener({
            try {
                cameraProvider = cameraProviderFuture.get()
                bindCameraUseCases()
            } catch (e: Exception) {
                onError("Failed to start camera: ${e.message}")
            }
        }, ContextCompat.getMainExecutor(context))
    }
    
    /**
     * Stop QR scanning
     */
    fun stopScanning() {
        isScanning = false
        cameraProvider?.unbindAll()
    }
    
    /**
     * Pause scanning temporarily
     */
    fun pauseScanning() {
        isScanning = false
    }
    
    /**
     * Resume scanning
     */
    fun resumeScanning() {
        isScanning = true
    }
    
    /**
     * Release resources
     */
    fun release() {
        stopScanning()
        cameraExecutor.shutdown()
        barcodeScanner.close()
    }
    
    private fun bindCameraUseCases() {
        val cameraProvider = this.cameraProvider ?: return
        
        // Preview use case
        preview = Preview.Builder()
            .build()
            .also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }
        
        // Image analysis use case for QR detection
        imageAnalysis = ImageAnalysis.Builder()
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()
            .also {
                it.setAnalyzer(cameraExecutor, QRCodeAnalyzer())
            }
        
        // Camera selector (prefer back camera)
        val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
        
        try {
            // Unbind use cases before rebinding
            cameraProvider.unbindAll()
            
            // Bind use cases to camera
            camera = cameraProvider.bindToLifecycle(
                lifecycleOwner,
                cameraSelector,
                preview,
                imageAnalysis
            )
            
        } catch (e: Exception) {
            onError("Failed to bind camera use cases: ${e.message}")
        }
    }
    
    /**
     * Image analyzer for QR code detection
     */
    private inner class QRCodeAnalyzer : ImageAnalysis.Analyzer {
        
        @androidx.camera.core.ExperimentalGetImage
        override fun analyze(imageProxy: ImageProxy) {
            if (!isScanning) {
                imageProxy.close()
                return
            }
            
            val mediaImage = imageProxy.image
            if (mediaImage != null) {
                val image = InputImage.fromMediaImage(
                    mediaImage, 
                    imageProxy.imageInfo.rotationDegrees
                )
                
                barcodeScanner.process(image)
                    .addOnSuccessListener { barcodes ->
                        processBarcodes(barcodes)
                    }
                    .addOnFailureListener { e ->
                        onError("QR detection failed: ${e.message}")
                    }
                    .addOnCompleteListener {
                        imageProxy.close()
                    }
            } else {
                imageProxy.close()
            }
        }
        
        private fun processBarcodes(barcodes: List<Barcode>) {
            if (!isScanning) return
            
            val currentTime = System.currentTimeMillis()
            if (currentTime - lastDetectedTime < SCAN_COOLDOWN) {
                return
            }
            
            for (barcode in barcodes) {
                when (barcode.valueType) {
                    Barcode.TYPE_TEXT -> {
                        val qrContent = barcode.displayValue
                        if (!qrContent.isNullOrEmpty() && isValidQRCode(qrContent)) {
                            lastDetectedTime = currentTime
                            onQRCodeDetected(qrContent)
                            pauseScanning() // Pause to prevent multiple detections
                            break
                        }
                    }
                }
            }
        }
        
        private fun isValidQRCode(content: String): Boolean {
            // Basic validation - should contain session and token information
            return try {
                // Check if it's JSON and contains expected fields
                content.contains("session_id") && 
                content.contains("token") && 
                content.contains("timestamp")
            } catch (e: Exception) {
                false
            }
        }
    }
}