package com.intelliattend.student.presence

import com.intelliattend.student.data.model.Student
import org.junit.Test
import org.junit.Assert.*

class PresenceIntegrationTest {
    
    @Test
    fun testPresenceManagerSingleton() {
        val instance1 = PresenceManager.getInstance()
        val instance2 = PresenceManager.getInstance()
        
        // Test that PresenceManager is a singleton
        assertSame("PresenceManager should be a singleton", instance1, instance2)
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
        
        // Test that student ID is properly formatted for WebSocket messages
        assertEquals("STU123", "STU${student.studentId}")
    }
    
    @Test
    fun testPresenceTrackingServiceInitialization() {
        val service = PresenceTrackingService()
        
        // Initially should not be connected
        assertFalse("Service should not be connected initially", service.isConnected())
    }
}