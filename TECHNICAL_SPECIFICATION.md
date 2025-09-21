# IntelliAttend Technical Specification

## 1. Network Architecture

### 1.1 System Components

#### Mobile Application (Android)
- **Platform**: Android 7.0+ (API level 24+)
- **Language**: Kotlin
- **Framework**: Jetpack Compose
- **Network Library**: Retrofit 2.9.0 with OkHttp 4.11.0
- **Authentication**: JWT tokens
- **Communication**: HTTPS REST API

#### Backend Server
- **Framework**: Flask 2.3+
- **Language**: Python 3.8+
- **Database**: MySQL 8.0+
- **Web Server**: Built-in Flask development server (production: Gunicorn/Nginx)
- **Authentication**: JWT Extended
- **QR Generation**: qrcode library with PIL

#### Database
- **Engine**: MySQL 8.0+
- **ORM**: SQLAlchemy
- **Connection Pooling**: Built-in SQLAlchemy pooling
- **Schema**: Normalized relational schema with foreign key constraints

### 1.2 Network Topology

```
[Android App] ---(HTTPS/TLS)--- [Flask Server] ---(MySQL Connector)--- [MySQL Database]
                                      |
                              [QR Code Generator]
                                      |
                            [QR_DATA File System]
```

## 2. Communication Protocols

### 2.1 Transport Layer Security

#### TLS Configuration
- **Protocol**: TLS 1.2+ (TLS 1.3 preferred)
- **Cipher Suites**: 
  - TLS_AES_256_GCM_SHA384
  - TLS_CHACHA20_POLY1305_SHA256
  - TLS_AES_128_GCM_SHA256
  - ECDHE-RSA-AES256-GCM-SHA384
  - ECDHE-RSA-AES128-GCM-SHA256
- **Key Exchange**: ECDHE for Perfect Forward Secrecy
- **Certificate**: X.509 certificates with 2048-bit RSA keys

#### Certificate Management
- **Development**: Self-signed certificates
- **Production**: CA-signed certificates
- **Pinning**: Certificate pinning in mobile app for enhanced security

### 2.2 Application Layer Protocol

#### HTTP/1.1 Implementation
- **Connection**: Persistent connections with keep-alive
- **Compression**: GZIP compression for responses > 1KB
- **Content Negotiation**: JSON for API responses
- **Caching**: HTTP caching headers for static resources

#### REST API Design
- **Endpoints**: Resource-based URL structure
- **Methods**: GET, POST, PUT, DELETE
- **Status Codes**: Standard HTTP status codes
- **Versioning**: Path-based versioning (/api/v1/)

### 2.3 Data Serialization

#### JSON Format
- **Encoding**: UTF-8
- **Structure**: Consistent key naming (camelCase)
- **Validation**: Strict schema validation
- **Size Limits**: 16MB maximum request size

#### Example Request/Response
```http
POST /api/student/login HTTP/1.1
Host: api.intelliattend.com
Content-Type: application/json
Accept: application/json
User-Agent: IntelliAttend/1.0.0 (Android 12; Samsung Galaxy S21)

{
  "email": "student@example.com",
  "password": "securePassword123"
}

HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 342
Date: Mon, 16 Oct 2023 14:30:00 GMT
Server: Flask/2.3.2 Python/3.9.7

{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "student": {
    "studentId": 12345,
    "studentCode": "STU12345",
    "firstName": "John",
    "lastName": "Doe",
    "email": "student@example.com",
    "program": "Computer Science",
    "yearOfStudy": 2
  }
}
```

## 3. Connection Management

### 3.1 Client-Side (Android App)

#### HTTP Client Configuration
```kotlin
// OkHttpClient configuration
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(loggingInterceptor)
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .writeTimeout(30, TimeUnit.SECONDS)
    .connectionPool(ConnectionPool(5, 5, TimeUnit.MINUTES))
    .build()

// Retrofit configuration
val retrofit = Retrofit.Builder()
    .baseUrl(BuildConfig.BASE_URL)
    .client(okHttpClient)
    .addConverterFactory(GsonConverterFactory.create(gson))
    .build()
```

#### Connection Pooling
- **Max Idle Connections**: 5
- **Keep Alive Duration**: 5 minutes
- **Connection Timeout**: 30 seconds
- **Read Timeout**: 30 seconds
- **Write Timeout**: 30 seconds

#### Retry Mechanism
- **Max Retries**: 3
- **Backoff Strategy**: Exponential backoff (1s, 2s, 4s)
- **Retryable Errors**: 500, 502, 503, 504, connection timeouts

### 3.2 Server-Side (Flask)

#### WSGI Server Configuration
```python
# Gunicorn configuration (production)
bind = "0.0.0.0:5002"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
```

#### Database Connection Pooling
```python
# SQLAlchemy configuration
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_recycle': 280,
    'pool_timeout': 20,
    'pool_pre_ping': True
}
```

#### Session Management
- **Session Timeout**: 2 hours
- **JWT Expiration**: 1 hour (access), 30 days (refresh)
- **Rate Limiting**: 100 requests/minute per IP

## 4. Security Implementation

### 4.1 Authentication Flow

#### JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "12345",
    "type": "student",
    "student_id": 12345,
    "iat": 1516239022,
    "exp": 1516242622
  },
  "signature": "HMACSHA256(base64UrlEncode(header) + '.' + base64UrlEncode(payload), secret)"
}
```

#### Token Management
- **Storage**: HTTP-only, secure cookies (web) / SharedPreferences (mobile)
- **Refresh**: Automatic token refresh 5 minutes before expiration
- **Revocation**: Blacklist for logout (Redis cache)

### 4.2 Data Encryption

#### In-Transit Encryption
- **HTTPS/TLS**: All API communication
- **Certificate Pinning**: Mobile app validates server certificate fingerprint
- **HSTS**: HTTP Strict Transport Security headers

#### At-Rest Encryption
- **Passwords**: Bcrypt with 12 rounds
- **Sensitive Data**: AES-256-GCM encryption
- **QR Data**: HMAC-SHA256 signed payloads

### 4.3 Input Validation

#### Server-Side Validation
- **Schema Validation**: JSON schema validation for all API requests
- **SQL Injection**: Parameterized queries with SQLAlchemy ORM
- **XSS Prevention**: HTML escaping for all user-generated content
- **Rate Limiting**: Per-IP and per-user rate limiting

#### Client-Side Validation
- **Form Validation**: Real-time validation with user feedback
- **Data Sanitization**: Removal of potentially harmful characters
- **Size Limits**: Enforced file and data size limits

## 5. API Endpoints Specification

### 5.1 Authentication Endpoints

#### Student Login
- **Method**: POST
- **Path**: `/api/student/login`
- **Headers**: `Content-Type: application/json`
- **Body**:
  ```json
  {
    "email": "string (required, email format)",
    "password": "string (required, 8-128 characters)"
  }
  ```
- **Success Response**: 200 OK
  ```json
  {
    "success": true,
    "access_token": "string (JWT token)",
    "student": {
      "studentId": "integer",
      "studentCode": "string",
      "firstName": "string",
      "lastName": "string",
      "email": "string",
      "program": "string",
      "yearOfStudy": "integer"
    }
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Invalid input
  - 401 Unauthorized: Invalid credentials
  - 500 Internal Server Error: Server error

#### Faculty Login
- **Method**: POST
- **Path**: `/api/faculty/login`
- **Headers**: `Content-Type: application/json`
- **Body**:
  ```json
  {
    "email": "string (required, email format)",
    "password": "string (required, 8-128 characters)"
  }
  ```
- **Success Response**: 200 OK
  ```json
  {
    "success": true,
    "access_token": "string (JWT token)",
    "faculty": {
      "faculty_id": "integer",
      "name": "string",
      "email": "string",
      "department": "string"
    }
  }
  ```

#### Logout
- **Method**: POST
- **Path**: `/api/student/logout` or `/api/faculty/logout`
- **Headers**: `Authorization: Bearer <token>`
- **Success Response**: 200 OK
  ```json
  {
    "success": true,
    "message": "Logged out successfully"
  }
  ```

### 5.2 Attendance Endpoints

#### Submit Attendance
- **Method**: POST
- **Path**: `/api/attendance/scan`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer <token>`
- **Body**:
  ```json
  {
    "qr_data": "string (required, JSON QR data)",
    "biometric_verified": "boolean (required)",
    "location": {
      "latitude": "number (required)",
      "longitude": "number (required)",
      "accuracy": "number (optional)"
    },
    "bluetooth": {
      "rssi": "integer (optional)",
      "devices": "array of strings (optional)"
    },
    "device_info": {
      "deviceId": "string (required)",
      "deviceName": "string (required)",
      "osVersion": "string (required)",
      "appVersion": "string (required)"
    }
  }
  ```
- **Success Response**: 200 OK
  ```json
  {
    "success": true,
    "status": "string (present|late|absent|invalid)",
    "verification_score": "number (0.00-1.00)",
    "verifications": {
      "biometric": "boolean",
      "location": "boolean",
      "bluetooth": "boolean"
    },
    "message": "string"
  }
  ```

### 5.3 Session Management Endpoints

#### Get Current Sessions
- **Method**: GET
- **Path**: `/api/session/current`
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**: `limit=integer (optional, default: 50)`
- **Success Response**: 200 OK
  ```json
  {
    "success": true,
    "sessions": [
      {
        "session_id": "integer",
        "class_name": "string",
        "faculty_name": "string",
        "start_time": "ISO 8601 datetime",
        "end_time": "ISO 8601 datetime"
      }
    ]
  }
  ```

## 6. Error Handling and Monitoring

### 6.1 Error Response Format
```json
{
  "success": false,
  "error": "string (error message)",
  "error_code": "string (optional error code)",
  "details": "object (optional detailed error information)"
}
```

### 6.2 Common Error Codes
- **AUTH_INVALID_CREDENTIALS**: Invalid email or password
- **AUTH_TOKEN_EXPIRED**: JWT token has expired
- **AUTH_TOKEN_INVALID**: JWT token is invalid
- **VALIDATION_ERROR**: Request validation failed
- **RESOURCE_NOT_FOUND**: Requested resource not found
- **RATE_LIMIT_EXCEEDED**: API rate limit exceeded
- **INTERNAL_SERVER_ERROR**: Unexpected server error

### 6.3 Logging and Monitoring
- **Access Logs**: All API requests logged with timestamps
- **Error Logs**: Detailed error information with stack traces
- **Performance Metrics**: Response times, throughput, error rates
- **Security Logs**: Authentication attempts, suspicious activities

## 7. Performance and Scalability

### 7.1 Performance Targets
- **Response Time**: < 500ms for 95% of requests
- **Throughput**: 1000 requests/second
- **Availability**: 99.9% uptime
- **Latency**: < 100ms database queries

### 7.2 Scalability Considerations
- **Horizontal Scaling**: Stateless API services
- **Database Sharding**: Student data partitioned by academic year
- **Load Balancing**: Round-robin distribution
- **Caching**: Redis for session data and frequently accessed resources

### 7.3 Resource Utilization
- **CPU**: < 70% average utilization
- **Memory**: < 80% average utilization
- **Disk I/O**: < 90% average utilization
- **Network**: < 80% bandwidth utilization

This technical specification provides a comprehensive overview of the network protocols, connection management, security implementation, and API design for the IntelliAttend system.