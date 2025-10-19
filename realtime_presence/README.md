# IntelliAttend Real-Time Student Presence Tracking

This module adds real-time online/offline tracking for students using WebSocket and Redis, fully isolated from the existing system.

## Features
- WebSocket server for student connections (login, ping, disconnect)
- Redis-based presence state: `student_id`, `status`, `last_seen`
- Heartbeat/timeout logic (offline after 60s inactivity)
- REST API for querying presence:
  - `GET /api/presence/<student_id>`
  - `GET /api/presence/all`
- No changes to existing IntelliAttend functionality

## Usage
1. Install dependencies:
   - For WebSocket server: `pip install -r requirements.txt`
   - For REST API: `pip install -r api_requirements.txt`
2. Start Redis server (default: localhost:6379)
3. Run WebSocket server: `python server.py`
4. Run REST API: `python api.py`

## Example Client Message
```
{ "event": "connect", "student_id": "S101", "device": "Android 14" }
{ "event": "ping", "student_id": "S101" }
```

## Example REST API Response
```
GET /api/presence/S101
{ "student_id": "S101", "status": "online", "last_seen": "2025-09-28T10:32:12Z" }
```

## Scalability
- Redis enables fast updates and queries for thousands of students
- Can be extended with background workers for periodic DB logging

## Isolation
- All code is in `realtime_presence/` and does not affect existing IntelliAttend modules
