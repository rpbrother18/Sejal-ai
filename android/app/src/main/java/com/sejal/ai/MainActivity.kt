package com.sejal.ai

import android.app.Activity
import android.graphics.Color
import android.os.Bundle
import android.view.ViewGroup
import android.view.WindowInsets
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

class MainActivity : Activity() {
    private lateinit var log: TextView
    private lateinit var scroll: ScrollView
    private lateinit var input: EditText
    private val endpoint = "http://127.0.0.1:8000/agent"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val mp = ViewGroup.LayoutParams.MATCH_PARENT
        val wc = ViewGroup.LayoutParams.WRAP_CONTENT

        val root = LinearLayout(this)
        root.orientation = LinearLayout.VERTICAL
        root.setBackgroundColor(Color.parseColor("#0F0B1E"))
        root.setOnApplyWindowInsetsListener { v, insets ->
            val types = WindowInsets.Type.systemBars() or WindowInsets.Type.ime()
            val bars = insets.getInsets(types)
            v.setPadding(24, bars.top + 24, 24, bars.bottom + 24)
            insets
        }

        val title = TextView(this)
        title.text = "SEJAL AI"
        title.textSize = 22f
        title.setTextColor(Color.parseColor("#B388FF"))
        root.addView(title, LinearLayout.LayoutParams(mp, wc))

        log = TextView(this)
        log.textSize = 16f
        log.setTextColor(Color.WHITE)
        log.text = "Namaste! Pehle Termux me server chalu karo.\n\n"
        scroll = ScrollView(this)
        scroll.addView(log)
        root.addView(scroll, LinearLayout.LayoutParams(mp, 0, 1f))

        input = EditText(this)
        input.hint = "Kuch poochho..."
        input.setHintTextColor(Color.GRAY)
        input.setTextColor(Color.WHITE)
        root.addView(input, LinearLayout.LayoutParams(mp, wc))

        val btn = Button(this)
        btn.text = "Bhejo"
        btn.setTextColor(Color.WHITE)
        btn.setBackgroundColor(Color.parseColor("#3D5AFE"))
        btn.setOnClickListener { send() }
        root.addView(btn, LinearLayout.LayoutParams(mp, wc))

        setContentView(root)
    }

    private fun append(line: String) {
        log.append(line + "\n\n")
        scroll.post { scroll.fullScroll(ScrollView.FOCUS_DOWN) }
    }

    private fun send() {
        val text = input.text.toString().trim()
        if (text.isEmpty()) return
        input.setText("")
        append("Aap: " + text)
        thread {
            val reply = try {
                post(text)
            } catch (e: Exception) {
                "Backend se connect nahi hua. Termux me server chalu hai?"
            }
            runOnUiThread { append("SEJAL: " + reply) }
        }
    }

    private fun post(text: String): String {
        val conn = URL(endpoint).openConnection() as HttpURLConnection
        try {
            conn.requestMethod = "POST"
            conn.connectTimeout = 5000
            conn.readTimeout = 60000
            conn.doOutput = true
            conn.setRequestProperty("Content-Type", "application/json")
            val body = JSONObject().put("message", text).toString()
            conn.outputStream.use { it.write(body.toByteArray()) }
            val code = conn.responseCode
            if (code !in 200..299) return "Server error " + code
            val raw = conn.inputStream.bufferedReader().readText()
            return JSONObject(raw).optString("reply", raw)
        } finally {
            conn.disconnect()
        }
    }
}
