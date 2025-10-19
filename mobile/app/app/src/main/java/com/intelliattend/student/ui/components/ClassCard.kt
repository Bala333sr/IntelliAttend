package com.intelliattend.student.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.intelliattend.student.data.model.ClassInfo
import com.intelliattend.student.ui.theme.CardBackground
import com.intelliattend.student.ui.theme.IntelliBlue
import com.intelliattend.student.ui.theme.IntelliGreen
import com.intelliattend.student.ui.theme.TextPrimary
import com.intelliattend.student.ui.theme.TextSecondary

@Composable
fun ClassCard(
    classInfo: ClassInfo,
    modifier: Modifier = Modifier,
    isUpcoming: Boolean = false,
    icon: @Composable () -> Unit = {}
) {
    Card(
        modifier = modifier
            .fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = CardBackground
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = 2.dp
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            if (isUpcoming) {
                Text(
                    text = "Starts in ${classInfo.timeUntilStart}",
                    color = IntelliGreen,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = classInfo.className,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary
                    )
                    
                    Text(
                        text = classInfo.facultyName,
                        fontSize = 14.sp,
                        color = TextSecondary,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                    
                    Text(
                        text = "${classInfo.startTime} - ${classInfo.endTime}",
                        fontSize = 14.sp,
                        color = TextSecondary,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }
                
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .align(Alignment.CenterVertically),
                    contentAlignment = Alignment.Center
                ) {
                    icon()
                }
            }
        }
    }
}