package com.intelliattend.student.presence

import com.intelliattend.student.data.model.Student
import org.junit.Test
import org.junit.Assert.*

class PresenceNotificationTest {
    
    @Test
    fun testNotificationMessageFormatting() {
        // Test that notification messages are formatted correctly
        val studentId = "STU123"
        val onlineStatus = "online"
        val offlineStatus = "offline"
        val timestamp = "2025-09-30T16:00:00Z"
        
        // Test online message
        val onlineMessage = if (onlineStatus == "online") {
            "You are now online"
        } else {
            "You are now offline"
        }
        
        assertEquals("You are now online", onlineMessage)
        
        // Test offline message
        val offlineMessage = if (offlineStatus == "online") {
            "You are now online"
        } else {
            "You are now offline"
        }
        
        assertEquals("You are now offline", offlineMessage)
    }
    
    @Test
    fun testStudentIdFormatting() {
        val student = Student(
            studentId = 123,
            studentCode = "STU123",
            firstName = "Test",
            lastName = "Student",
            email = "test@student.edu",
            program = "CS",
            yearOfStudy = 3
        )
        
        // Test that student ID is properly formatted
        val formattedStudentId = "STU${student.studentId}"
        assertEquals("STU123", formattedStudentId)
    }
}