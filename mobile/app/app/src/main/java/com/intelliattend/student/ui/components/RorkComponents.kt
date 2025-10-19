package com.intelliattend.student.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.intelliattend.student.ui.theme.*

/**
 * Reusable Components for Rork Dark Theme UI
 * Matching the React Native design system
 */

/**
 * Page indicator dots for swipeable carousels
 */
@Composable
fun PageIndicators(
    totalPages: Int,
    currentPage: Int,
    modifier: Modifier = Modifier,
    activeColor: Color = RorkPrimary,
    inactiveColor: Color = RorkBorder
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        repeat(totalPages) { index ->
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .clip(CircleShape)
                    .background(
                        if (index == currentPage) activeColor else inactiveColor
                    )
                    .let {
                        if (index == currentPage) it
                        else it.then(Modifier.padding(0.dp))
                    }
            )
        }
    }
}

/**
 * Modern card with Rork styling
 */
@Composable
fun RorkCard(
    modifier: Modifier = Modifier,
    backgroundColor: Color = RorkCardBackground,
    onClick: (() -> Unit)? = null,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = backgroundColor
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = 0.dp,
            pressedElevation = 2.dp
        ),
        onClick = onClick ?: {}
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            content = content
        )
    }
}

/**
 * Circular percentage indicator with color coding
 */
@Composable
fun PercentageCircle(
    percentage: Int,
    modifier: Modifier = Modifier,
    size: Int = 60
) {
    val color = when {
        percentage >= 95 -> RorkSuccess
        percentage >= 85 -> RorkWarning
        else -> RorkDanger
    }
    
    Box(
        modifier = modifier
            .size(size.dp)
            .clip(CircleShape)
            .background(Color.Transparent)
            .padding(0.dp),
        contentAlignment = Alignment.Center
    ) {
        // Circular border
        Box(
            modifier = Modifier
                .size(size.dp)
                .clip(CircleShape)
                .padding(0.dp),
            contentAlignment = Alignment.Center
        ) {
            // Inner circle with border
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(3.dp)
                    .clip(CircleShape)
                    .background(RorkCardBackground),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "$percentage%",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = color
                )
            }
            
            // Border overlay
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(0.dp)
                    .clip(CircleShape)
            ) {
                Canvas(modifier = Modifier.fillMaxSize()) {
                    drawCircle(
                        color = color,
                        radius = size.dp.toPx() / 2,
                        style = androidx.compose.ui.graphics.drawscope.Stroke(width = 3.dp.toPx())
                    )
                }
            }
        }
    }
}

/**
 * Colored icon container with background
 */
@Composable
fun ColoredIconContainer(
    icon: ImageVector,
    iconColor: Color,
    backgroundColor: Color = iconColor.copy(alpha = 0.2f),
    size: Int = 64,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .size(size.dp)
            .clip(CircleShape)
            .background(backgroundColor),
        contentAlignment = Alignment.Center
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = iconColor,
            modifier = Modifier.size((size / 2).dp)
        )
    }
}

/**
 * Badge for upcoming class notifications
 */
@Composable
fun UpcomingBadge(
    minutesRemaining: Int,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .background(RorkSuccess)
            .padding(vertical = 8.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = "Starts in $minutesRemaining mins",
            color = Color.White,
            fontSize = 14.sp,
            fontWeight = FontWeight.SemiBold
        )
    }
}

/**
 * Online status indicator
 */
@Composable
fun OnlineIndicator(
    isOnline: Boolean = true,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .size(16.dp)
            .clip(CircleShape)
            .background(if (isOnline) RorkOnlineIndicator else RorkOfflineIndicator)
    )
}

