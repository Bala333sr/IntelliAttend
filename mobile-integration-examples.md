# 📱 Mobile App Integration Examples for Dynamic IP Discovery

## Current Server Configuration
- **Current IP**: `192.168.0.6:5002`
- **Discovery Endpoint**: `http://192.168.0.6:5002/api/discover`
- **Mobile Config**: `http://192.168.0.6:5002/api/config/mobile`

---

## 🚀 Integration Methods

### **Method 1: Auto-Discovery API (Recommended)**
Mobile app calls discovery endpoint to get current server configuration

### **Method 2: Network Scanning** 
App scans local network to find IntelliAttend server

### **Method 3: QR Code Configuration**
Scan QR code to get server configuration

### **Method 4: Broadcast Listener**
Listen for UDP broadcast messages from server

---

## 📋 React Native Implementation

### **Auto-Discovery Service**

```javascript
// services/ServerDiscovery.js
import AsyncStorage from '@react-native-async-storage/async-storage';

class ServerDiscoveryService {
  constructor() {
    this.baseUrl = null;
    this.discoveryUrls = [
      'http://192.168.0.6:5002/api/discover',
      'http://192.168.1.100:5002/api/discover',
      'http://10.0.0.100:5002/api/discover'
    ];
  }

  async discoverServer() {
    // Try cached URL first
    const cachedConfig = await AsyncStorage.getItem('server_config');
    if (cachedConfig) {
      const config = JSON.parse(cachedConfig);
      if (await this.testConnection(config.api_base_url)) {
        this.baseUrl = config.api_base_url;
        return config;
      }
    }

    // Try known IPs
    for (const discoveryUrl of this.discoveryUrls) {
      try {
        const response = await fetch(discoveryUrl, { timeout: 3000 });
        const data = await response.json();
        
        if (data.success) {
          const config = {
            api_base_url: data.server.api_base,
            server_ip: data.server.network.primary_ip,
            last_updated: data.server.last_updated
          };
          
          // Cache the configuration
          await AsyncStorage.setItem('server_config', JSON.stringify(config));
          this.baseUrl = config.api_base_url;
          
          console.log('✅ Server discovered:', config.server_ip);
          return config;
        }
      } catch (error) {
        console.log(`❌ Failed to connect to ${discoveryUrl}:`, error.message);
      }
    }

    throw new Error('IntelliAttend server not found on network');
  }

  async testConnection(url) {
    try {
      const response = await fetch(`${url}/health`, { timeout: 2000 });
      return response.ok;
    } catch {
      return false;
    }
  }

  async networkScan() {
    // Scan common IP ranges
    const baseIPs = ['192.168.0', '192.168.1', '10.0.0', '172.16.0'];
    const promises = [];

    for (const baseIP of baseIPs) {
      for (let i = 1; i <= 254; i++) {
        const url = `http://${baseIP}.${i}:5002/api/discover`;
        promises.push(this.tryDiscovery(url));
      }
    }

    const results = await Promise.allSettled(promises);
    const successful = results
      .filter(result => result.status === 'fulfilled' && result.value)
      .map(result => result.value);

    return successful[0] || null;
  }

  async tryDiscovery(url) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1000);

      const response = await fetch(url, {
        signal: controller.signal,
        timeout: 1000
      });

      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.server.server_name === 'IntelliAttend') {
          return {
            api_base_url: data.server.api_base,
            server_ip: data.server.network.primary_ip
          };
        }
      }
    } catch (error) {
      // Silent fail for scanning
    }
    return null;
  }

  getBaseUrl() {
    return this.baseUrl;
  }
}

export default new ServerDiscoveryService();
```

### **React Native App Integration**

```javascript
// App.js
import React, { useState, useEffect } from 'react';
import { View, Text, Alert, ActivityIndicator } from 'react-native';
import ServerDiscoveryService from './services/ServerDiscovery';

export default function App() {
  const [serverConfig, setServerConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      console.log('🔍 Discovering IntelliAttend server...');
      const config = await ServerDiscoveryService.discoverServer();
      setServerConfig(config);
      console.log('✅ Connected to server:', config.server_ip);
    } catch (error) {
      console.error('❌ Server discovery failed:', error);
      setError(error.message);
      
      // Try network scan as fallback
      try {
        console.log('🔍 Attempting network scan...');
        const scanResult = await ServerDiscoveryService.networkScan();
        if (scanResult) {
          setServerConfig(scanResult);
          console.log('✅ Server found via scan:', scanResult.server_ip);
        } else {
          Alert.alert(
            'Server Not Found',
            'Could not find IntelliAttend server. Please check your network connection.',
            [{ text: 'Retry', onPress: initializeApp }]
          );
        }
      } catch (scanError) {
        Alert.alert('Connection Error', scanError.message);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#0066cc" />
        <Text>Discovering IntelliAttend server...</Text>
      </View>
    );
  }

  if (error && !serverConfig) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <Text>Error: {error}</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, padding: 20 }}>
      <Text style={{ fontSize: 18, fontWeight: 'bold' }}>
        📡 Connected to IntelliAttend
      </Text>
      <Text>Server IP: {serverConfig?.server_ip}</Text>
      <Text>API Base: {serverConfig?.api_base_url}</Text>
      
      {/* Your app content here */}
    </View>
  );
}
```

### **API Service with Auto-Discovery**

```javascript
// services/ApiService.js
import ServerDiscoveryService from './ServerDiscovery';

class ApiService {
  constructor() {
    this.baseUrl = null;
  }

  async ensureConnection() {
    if (!this.baseUrl) {
      const config = await ServerDiscoveryService.discoverServer();
      this.baseUrl = config.api_base_url;
    }
  }

  async request(endpoint, options = {}) {
    await this.ensureConnection();
    
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      // If server is unreachable, try rediscovery
      if (response.status === 0 || response.status >= 500) {
        console.log('🔄 Server unreachable, attempting rediscovery...');
        const config = await ServerDiscoveryService.discoverServer();
        this.baseUrl = config.api_base_url;
        
        // Retry the request
        const retryResponse = await fetch(`${this.baseUrl}${endpoint}`, {
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
          ...options,
        });
        
        if (!retryResponse.ok) {
          throw new Error(`API request failed: ${retryResponse.statusText}`);
        }
        
        return retryResponse.json();
      }
      
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  // Authentication endpoints
  async studentLogin(email, password) {
    return this.request('/student/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async facultyLogin(email, password) {
    return this.request('/faculty/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async adminLogin(username, password) {
    return this.request('/admin/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  // Attendance endpoints
  async markAttendance(data) {
    return this.request('/mark-attendance', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getSessions() {
    return this.request('/sessions');
  }
}

export default new ApiService();
```

---

## 🤖 Android (Java/Kotlin) Implementation

### **Server Discovery Service (Kotlin)**

```kotlin
// ServerDiscoveryService.kt
import kotlinx.coroutines.*
import okhttp3.*
import org.json.JSONObject
import java.net.SocketTimeoutException
import java.util.concurrent.TimeUnit

class ServerDiscoveryService {
    private val client = OkHttpClient.Builder()
        .connectTimeout(3, TimeUnit.SECONDS)
        .readTimeout(3, TimeUnit.SECONDS)
        .build()
    
    private var baseUrl: String? = null
    private val discoveryUrls = listOf(
        "http://192.168.0.6:5002/api/discover",
        "http://192.168.1.100:5002/api/discover",
        "http://10.0.0.100:5002/api/discover"
    )

    suspend fun discoverServer(): ServerConfig = withContext(Dispatchers.IO) {
        // Try cached configuration first
        val cached = getCachedConfig()
        if (cached != null && testConnection(cached.apiBaseUrl)) {
            baseUrl = cached.apiBaseUrl
            return@withContext cached
        }

        // Try discovery URLs
        for (url in discoveryUrls) {
            try {
                val request = Request.Builder().url(url).build()
                val response = client.newCall(request).execute()
                
                if (response.isSuccessful) {
                    val json = JSONObject(response.body!!.string())
                    if (json.getBoolean("success")) {
                        val server = json.getJSONObject("server")
                        val config = ServerConfig(
                            apiBaseUrl = server.getString("api_base"),
                            serverIp = server.getJSONObject("network").getString("primary_ip"),
                            lastUpdated = server.getString("last_updated")
                        )
                        
                        cacheConfig(config)
                        baseUrl = config.apiBaseUrl
                        return@withContext config
                    }
                }
            } catch (e: Exception) {
                // Continue to next URL
            }
        }
        
        throw Exception("IntelliAttend server not found")
    }

    private suspend fun testConnection(url: String): Boolean = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder().url("$url/health").build()
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }

    suspend fun networkScan(): ServerConfig? = withContext(Dispatchers.IO) {
        val baseIPs = listOf("192.168.0", "192.168.1", "10.0.0")
        val jobs = mutableListOf<Deferred<ServerConfig?>>()

        for (baseIP in baseIPs) {
            for (i in 1..254) {
                val url = "http://$baseIP.$i:5002/api/discover"
                jobs.add(async { tryDiscovery(url) })
            }
        }

        val results = jobs.awaitAll()
        return@withContext results.firstOrNull { it != null }
    }

    private suspend fun tryDiscovery(url: String): ServerConfig? = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder().url(url).build()
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val json = JSONObject(response.body!!.string())
                if (json.getBoolean("success")) {
                    val server = json.getJSONObject("server")
                    return@withContext ServerConfig(
                        apiBaseUrl = server.getString("api_base"),
                        serverIp = server.getJSONObject("network").getString("primary_ip")
                    )
                }
            }
        } catch (e: Exception) {
            // Silent fail
        }
        null
    }

    private fun getCachedConfig(): ServerConfig? {
        // Implementation depends on your caching strategy
        // Could use SharedPreferences, Room DB, etc.
        return null
    }

    private fun cacheConfig(config: ServerConfig) {
        // Cache the configuration
    }
}

data class ServerConfig(
    val apiBaseUrl: String,
    val serverIp: String,
    val lastUpdated: String = ""
)
```

### **Android Main Activity**

```kotlin
// MainActivity.kt
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    private lateinit var discoveryService: ServerDiscoveryService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        discoveryService = ServerDiscoveryService()
        initializeApp()
    }

    private fun initializeApp() {
        lifecycleScope.launch {
            try {
                showLoading("Discovering IntelliAttend server...")
                val config = discoveryService.discoverServer()
                onServerDiscovered(config)
            } catch (e: Exception) {
                try {
                    showLoading("Scanning network...")
                    val config = discoveryService.networkScan()
                    if (config != null) {
                        onServerDiscovered(config)
                    } else {
                        showError("Server not found")
                    }
                } catch (e: Exception) {
                    showError(e.message ?: "Connection failed")
                }
            }
        }
    }

    private fun onServerDiscovered(config: ServerConfig) {
        hideLoading()
        // Update UI with server info
        // Initialize your app with the discovered configuration
    }

    private fun showLoading(message: String) {
        // Show loading indicator
    }

    private fun hideLoading() {
        // Hide loading indicator
    }

    private fun showError(message: String) {
        // Show error message
    }
}
```

---

## 🍎 iOS (Swift) Implementation

### **Server Discovery Service (Swift)**

```swift
// ServerDiscoveryService.swift
import Foundation

class ServerDiscoveryService {
    static let shared = ServerDiscoveryService()
    private var baseURL: String?
    
    private let discoveryURLs = [
        "http://192.168.0.6:5002/api/discover",
        "http://192.168.1.100:5002/api/discover",
        "http://10.0.0.100:5002/api/discover"
    ]
    
    func discoverServer() async throws -> ServerConfig {
        // Try cached configuration first
        if let cached = getCachedConfig(),
           await testConnection(url: cached.apiBaseURL) {
            baseURL = cached.apiBaseURL
            return cached
        }
        
        // Try discovery URLs
        for urlString in discoveryURLs {
            do {
                guard let url = URL(string: urlString) else { continue }
                
                let (data, response) = try await URLSession.shared.data(from: url)
                
                if let httpResponse = response as? HTTPURLResponse,
                   httpResponse.statusCode == 200 {
                    
                    let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
                    
                    if let success = json?["success"] as? Bool, success,
                       let server = json?["server"] as? [String: Any],
                       let apiBase = server["api_base"] as? String,
                       let network = server["network"] as? [String: Any],
                       let serverIP = network["primary_ip"] as? String {
                        
                        let config = ServerConfig(
                            apiBaseURL: apiBase,
                            serverIP: serverIP,
                            lastUpdated: server["last_updated"] as? String ?? ""
                        )
                        
                        cacheConfig(config)
                        baseURL = config.apiBaseURL
                        return config
                    }
                }
            } catch {
                // Continue to next URL
                continue
            }
        }
        
        throw ServerDiscoveryError.serverNotFound
    }
    
    private func testConnection(url: String) async -> Bool {
        guard let healthURL = URL(string: "\(url)/health") else { return false }
        
        do {
            let (_, response) = try await URLSession.shared.data(from: healthURL)
            return (response as? HTTPURLResponse)?.statusCode == 200
        } catch {
            return false
        }
    }
    
    func networkScan() async -> ServerConfig? {
        let baseIPs = ["192.168.0", "192.168.1", "10.0.0"]
        
        return await withTaskGroup(of: ServerConfig?.self) { group in
            for baseIP in baseIPs {
                for i in 1...254 {
                    let url = "http://\(baseIP).\(i):5002/api/discover"
                    group.addTask {
                        await self.tryDiscovery(url: url)
                    }
                }
            }
            
            for await result in group {
                if let config = result {
                    return config
                }
            }
            return nil
        }
    }
    
    private func tryDiscovery(url: String) async -> ServerConfig? {
        guard let discoveryURL = URL(string: url) else { return nil }
        
        do {
            let (data, response) = try await URLSession.shared.data(from: discoveryURL)
            
            if let httpResponse = response as? HTTPURLResponse,
               httpResponse.statusCode == 200 {
                
                let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
                
                if let success = json?["success"] as? Bool, success,
                   let server = json?["server"] as? [String: Any],
                   let apiBase = server["api_base"] as? String,
                   let network = server["network"] as? [String: Any],
                   let serverIP = network["primary_ip"] as? String {
                    
                    return ServerConfig(
                        apiBaseURL: apiBase,
                        serverIP: serverIP
                    )
                }
            }
        } catch {
            // Silent fail for scanning
        }
        
        return nil
    }
    
    private func getCachedConfig() -> ServerConfig? {
        // Implementation using UserDefaults or Core Data
        return nil
    }
    
    private func cacheConfig(_ config: ServerConfig) {
        // Cache the configuration
    }
}

struct ServerConfig {
    let apiBaseURL: String
    let serverIP: String
    let lastUpdated: String
    
    init(apiBaseURL: String, serverIP: String, lastUpdated: String = "") {
        self.apiBaseURL = apiBaseURL
        self.serverIP = serverIP
        self.lastUpdated = lastUpdated
    }
}

enum ServerDiscoveryError: Error {
    case serverNotFound
    case networkError
}
```

---

## 🔧 Quick Setup Script

Create this script to automatically integrate IP discovery into your backend:

```bash
#!/bin/bash
# integrate-ip-discovery.sh

echo "🌐 Integrating IP Discovery Service..."

# Install required packages
pip3 install netifaces qrcode[pil]

# Add to app.py
cat >> /home/anji/IntelliAttend/backend/app.py << 'EOF'

# IP Discovery Service Integration
try:
    from ip_discovery_service import setup_ip_discovery
    discovery_service, broadcast_service = setup_ip_discovery(app, port=5002)
except ImportError:
    print("⚠️  IP Discovery Service not available")
EOF

echo "✅ IP Discovery Service integrated!"
echo "📍 Current IP: $(hostname -I | awk '{print $1}')"
echo "🔗 Discovery URL: http://$(hostname -I | awk '{print $1}'):5002/api/discover"
echo "📱 Mobile Config: http://$(hostname -I | awk '{print $1}'):5002/api/config/mobile"
```

---

## 🎯 Recommended Implementation Strategy

### **For Your Mobile App:**

1. **Use Auto-Discovery (Method 1)** - Most reliable
2. **Implement Network Scanning** as fallback
3. **Cache the discovered configuration**
4. **Add retry logic** for network failures
5. **Provide manual IP entry** as last resort

### **Integration Steps:**

1. **Add IP discovery to backend:**
   ```bash
   cd /home/anji/IntelliAttend/backend
   pip3 install netifaces qrcode[pil]
   # Add ip_discovery_service.py to your backend
   ```

2. **Update your mobile app** with discovery service

3. **Test with different IP addresses** to ensure it works

This solution will automatically handle IP changes and make your mobile app much more robust! 🚀