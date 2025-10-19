package com.intelliattend.ui.timetable

import android.content.Context
import android.os.Bundle
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.intelliattend.student.R
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

class TimetableActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_timetable)

        val statusText = findViewById<TextView>(R.id.statusText)
        val listLayout = findViewById<LinearLayout>(R.id.listLayout)

        val prefs = getSharedPreferences("app_preferences", Context.MODE_PRIVATE)
        val baseUrl = intent.getStringExtra("BASE_URL")
            ?: (prefs.getString("base_url", null) ?: com.intelliattend.student.BuildConfig.BASE_URL)
        val email = intent.getStringExtra("EMAIL")
            ?: prefs.getString("student_email", null)
        val password = intent.getStringExtra("PASSWORD")
            ?: prefs.getString("student_password", null)

        statusText.text = getString(R.string.loading)

        Thread {
            try {
                val token = loginAndGetToken(baseUrl, email, password)
                if (token == null) throw Exception("Login failed. Check credentials or server URL.")

                val timetableJson = getAuthorized("${baseUrl}student/timetable/today", token)
                val items = extractTimetableArray(timetableJson)

                runOnUiThread {
                    if (items.length() == 0) {
                        statusText.text = "No timetable entries for today"
                    } else {
                        statusText.text = "Loaded timetable"
                        for (i in 0 until items.length()) {
                            val it = items.getJSONObject(i)
                            val subject = it.optString("subject_name", it.optString("subject", ""))
                            val faculty = it.optString("faculty_name", "")
                            val time = "${it.optString("start_time", "")} - ${it.optString("end_time", "")}"
                            val room = it.optString("room_number", "")
                            val slot = it.optString("slot_number", "")

                            val tv = TextView(this)
                            tv.text = listOfNotNull(
                                time.takeIf { it.isNotBlank() },
                                subject.takeIf { it.isNotBlank() },
                                faculty.takeIf { it.isNotBlank() },
                                room.takeIf { it.isNotBlank() }?.let { "Room $room" },
                                slot.takeIf { it.isNotBlank() }?.let { "Slot $slot" }
                            ).joinToString(" • ")
                            tv.textSize = 16f
                            listLayout.addView(tv)
                        }
                    }
                }
            } catch (e: Exception) {
                runOnUiThread { statusText.text = "Error: ${e.message}" }
            }
        }.start()
    }

    private fun loginAndGetToken(baseUrl: String, email: String, password: String): String? {
        val obj = JSONObject().apply {
            put("email", email)
            put("password", password)
        }
        val resp = postJson("${baseUrl}student/mobile-login", obj.toString())
        return parseToken(resp)
    }

    private fun extractTimetableArray(jsonStr: String): JSONArray {
        return try {
            val root = JSONObject(jsonStr)
            when {
                root.has("data") && root.opt("data") is JSONArray -> root.getJSONArray("data")
                root.has("timetable") && root.opt("timetable") is JSONArray -> root.getJSONArray("timetable")
                root.has("items") && root.opt("items") is JSONArray -> root.getJSONArray("items")
                else -> JSONArray()
            }
        } catch (e: Exception) {
            JSONArray()
        }
    }

    private fun parseToken(jsonStr: String): String? {
        return try {
            val root = JSONObject(jsonStr)
            when {
                root.has("access_token") -> root.getString("access_token")
                root.has("token") -> root.getString("token")
                root.has("data") && root.getJSONObject("data").has("access_token") -> root.getJSONObject("data").getString("access_token")
                else -> null
            }
        } catch (e: Exception) {
            null
        }
    }

    private fun postJson(urlStr: String, body: String): String {
        val url = URL(urlStr)
        val conn = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            setRequestProperty("Content-Type", "application/json")
            doOutput = true
            connectTimeout = 10000
            readTimeout = 10000
        }
        conn.outputStream.use { os -> os.write(body.toByteArray(Charsets.UTF_8)) }
        val code = conn.responseCode
        val reader = BufferedReader(InputStreamReader(if (code in 200..299) conn.inputStream else conn.errorStream))
        val resp = reader.readText()
        conn.disconnect()
        return resp
    }

    private fun getAuthorized(urlStr: String, token: String): String {
        val url = URL(urlStr)
        val conn = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            setRequestProperty("Authorization", "Bearer $token")
            connectTimeout = 10000
            readTimeout = 10000
        }
        val code = conn.responseCode
        val reader = BufferedReader(InputStreamReader(if (code in 200..299) conn.inputStream else conn.errorStream))
        val resp = reader.readText()
        conn.disconnect()
        return resp
    }
}