package com.intelliattend.student.ui.scanner

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.BlendMode
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Canvas
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.camera.view.PreviewView
import androidx.lifecycle.viewmodel.compose.viewModel

/**
 * QR Scanner screen with camera preview and scanning logic
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QRScannerScreen(
    onScanComplete: () -> Unit,
    onBack: () -> Unit,
    onNavigateToBluetooth: () -> Unit,
    viewModel: QRScannerViewModel = viewModel()
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    var previewView by remember { mutableStateOf<PreviewView?>(null) }
    val uiState by remember { mutableStateOf(QRScannerUiState()) }

    LaunchedEffect(Unit) {
        viewModel.onScanComplete = { success, _ ->
            if (success) {
                onNavigateToBluetooth()
            }
        }
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Scan QR Code", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = Color.Transparent,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White
                )
            )
        },
        containerColor = Color.Black
    ) { paddingValues ->
        Box(modifier = Modifier
            .fillMaxSize()
            .padding(paddingValues)) {
            // Camera preview
            AndroidView(
                factory = { ctx ->
                    PreviewView(ctx).also { preview ->
                        previewView = preview
                        // viewModel.startCamera(preview, lifecycleOwner)
                    }
                },
                modifier = Modifier.fillMaxSize()
            )

            // Scanning overlay
            ScanningOverlay()

            // Status messages
            Column(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                uiState.message?.let { message ->
                    val isSuccess = message.contains("success", ignoreCase = true)
                    val isError = message.contains("error", ignoreCase = true) || message.contains("failed", ignoreCase = true)

                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = when {
                                isSuccess -> Color.Green.copy(alpha = 0.8f)
                                isError -> Color.Red.copy(alpha = 0.8f)
                                else -> MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.8f)
                            }
                        ),
                        shape = MaterialTheme.shapes.medium
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(16.dp)) {
                            Icon(when {
                                isSuccess -> Icons.Default.CheckCircle
                                isError -> Icons.Default.Error
                                else -> Icons.Default.Info
                            }, contentDescription = null, tint = Color.White)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = message,
                                style = MaterialTheme.typography.bodyMedium,
                                textAlign = TextAlign.Center,
                                color = Color.White
                            )
                        }
                    }
                }
            }
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            // viewModel.cleanup()
        }
    }
}

@Composable
private fun ScanningOverlay() {
    val infiniteTransition = rememberInfiniteTransition()
    val animatedProgress by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        )
    )
    val density = LocalDensity.current.density
    val boxSize = 250.dp

    Canvas(modifier = Modifier.fillMaxSize()) {
        val canvasWidth = size.width
        val canvasHeight = size.height
        val boxSizePx = boxSize.toPx()
        val cornerRadius = CornerRadius(16.dp.toPx())

        val rectPath = androidx.compose.ui.graphics.Path().apply {
            addRoundRect(
                androidx.compose.ui.geometry.RoundRect(
                    left = (canvasWidth - boxSizePx) / 2,
                    top = (canvasHeight - boxSizePx) / 2,
                    right = (canvasWidth + boxSizePx) / 2,
                    bottom = (canvasHeight + boxSizePx) / 2,
                    cornerRadius = cornerRadius
                )
            )
        }
        // Semi-transparent background
        drawRect(color = Color.Black.copy(alpha = 0.6f))

        // Clear the scanning area
        drawPath(path = rectPath, color = Color.Transparent, blendMode = BlendMode.Clear)

        // Draw the border
        drawRoundRect(
            color = Color.White,
            topLeft = Offset((canvasWidth - boxSizePx) / 2, (canvasHeight - boxSizePx) / 2),
            size = Size(boxSizePx, boxSizePx),
            cornerRadius = cornerRadius,
            style = Stroke(width = 2.dp.toPx())
        )

        // Draw the animated scanning line
        val lineHeight = 4.dp.toPx()
        val lineY = ((canvasHeight - boxSizePx) / 2) + (boxSizePx - lineHeight) * animatedProgress
        drawRect(
            brush = Brush.verticalGradient(
                colors = listOf(Color.Transparent, Color.Green, Color.Transparent)
            ),
            topLeft = Offset((canvasWidth - boxSizePx) / 2, lineY),
            size = Size(boxSizePx, lineHeight)
        )
    }
}

data class QRScannerUiState(
    val message: String? = null,
    val isScanning: Boolean = false
)
