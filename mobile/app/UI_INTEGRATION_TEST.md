# UI Integration Test for Presence Status Display

## Test Scenario
This document outlines how to verify that the presence status is correctly displayed in the mobile app UI.

## Prerequisites
1. Presence tracking servers running (WebSocket on port 8765, REST API on port 5005)
2. Mobile app installed on device/emulator
3. Test student account available (default: alice.williams@student.edu / student123)

## Test Steps

### 1. Verify Server Connectivity
```bash
# Check if REST API server is running
curl -s http://localhost:5005/health | grep -q '"status": "healthy"' && echo "✓ API Server Healthy" || echo "✗ API Server Unhealthy"

# Check if WebSocket server is accessible
python3 -c "import websocket; ws = websocket.create_connection('ws://localhost:8765/'); ws.close(); print('✓ WebSocket Server Accessible')"
```

### 2. Verify Presence Status API
```bash
# Check if student presence status is available
curl -s http://localhost:5005/api/presence/STU123 | grep -q '"status": "online"' && echo "✓ Student STU123 is online" || echo "✗ Student STU123 is offline or not found"
```

### 3. Mobile App Test
1. Open the IntelliAttend mobile app on your device/emulator
2. The app should automatically log in with the test user credentials
3. Navigate to the Home screen
4. Look for the "Connection Status" card below the student profile card
5. The card should display:
   - Green "Online" status with WiFi icon when student is connected
   - Red "Offline" status with WiFiOff icon when student is disconnected
   - Last seen timestamp (e.g., "Just now", "5 minutes ago")

### 4. Verification Points
- [ ] Presence Status Card is visible on Home screen
- [ ] Card shows correct online/offline status
- [ ] Status indicator color matches status (green for online, red for offline)
- [ ] Last seen timestamp is displayed when available
- [ ] Card updates in real-time when presence status changes

### 5. Troubleshooting
If the presence status is not displayed:

1. Check network connectivity on the device
2. Verify that the app can reach the servers (check firewall settings)
3. Confirm that the base URL in app settings points to the correct server
4. Check app logs for any errors in presence status loading
5. Verify that the student is actually connected to the WebSocket server

## Expected Results
When the test is successful, users should see a "Connection Status" card on their Home screen that accurately reflects their online/offline status in real-time.