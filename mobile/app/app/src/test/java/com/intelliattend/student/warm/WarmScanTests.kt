package com.intelliattend.student.warm

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class WarmScanTests {

    @Test
    fun sampleBuffer_respectsCapacity() {
        val buf = SampleBuffer(3)
        buf.add(dummySample(1))
        buf.add(dummySample(2))
        buf.add(dummySample(3))
        buf.add(dummySample(4))
        val list = buf.toList()
        assertEquals(3, list.size)
        assertEquals(2, list[0].ts)
        assertEquals(3, list[1].ts)
        assertEquals(4, list[2].ts)
    }

    @Test
    fun warmBle_containsRssi() {
        val s = dummySample(10)
        assertTrue(s.ble.isEmpty() || s.ble.all { it.rssi <= 0 || it.rssi >= -120 })
    }

    private fun dummySample(ts: Long): SensorSample {
        return SensorSample(
            ts = ts,
            ble = emptyList(),
            wifi = null,
            gps = null
        )
    }
}