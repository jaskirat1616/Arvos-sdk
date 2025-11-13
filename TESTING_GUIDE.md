# Testing Guide: All Streaming Protocols

Complete guide to test all 7 streaming protocols with the ARVOS iOS app.

## Prerequisites

1. **Install Python SDK:**
   ```bash
   cd /Users/jaskiratsingh/Desktop/arvos-sdk
   pip install -e .
   ```

2. **Install protocol-specific dependencies:**
   ```bash
   # For gRPC
   pip install grpcio grpcio-tools protobuf
   
   # For MQTT
   pip install paho-mqtt
   brew install mosquitto  # macOS
   
   # For BLE
   pip install bleak
   
   # For MCAP
   pip install mcap
   
   # For QUIC/HTTP3
   pip install aioquic
   ```

3. **Ensure iPhone and computer are on the same Wi-Fi network** (except for BLE)

---

## 1. WebSocket (Default)

**Server:**
```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk
python examples/basic_server.py
```

**iOS App:**
1. Open ARVOS app
2. Tap "CONNECT TO SERVER"
3. Protocol: **WebSocket** (default)
4. Scan QR code or enter IP manually
5. Port should auto-fill to **9090**
6. Tap "CONNECT"
7. Tap "START STREAMING"

**Expected Output:**
- Server shows: `✅ iPhone connected...`
- Server prints IMU, pose, camera data
- iOS app shows connection status and statistics

---

## 2. gRPC

**Server:**
```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk
python examples/grpc_stream_server.py
```

**iOS App:**
1. Open ARVOS app
2. Tap "CONNECT TO SERVER"
3. Protocol: **gRPC**
4. Enter server IP (from terminal output)
5. Port: **50051** (auto-filled)
6. Tap "CONNECT"
7. Tap "START STREAMING"

**Expected Output:**
- Server shows: `✅ gRPC client connected: ...`
- Server prints protobuf messages
- iOS app shows gRPC connection status

**Note:** Requires iOS 18+ on iPhone

---

## 3. MQTT

**Step 1: Start Mosquitto Broker**
```bash
# Create config file (mosquitto.conf)
echo "listener 1883 0.0.0.0" > mosquitto.conf
echo "allow_anonymous true" >> mosquitto.conf

# Start broker
mosquitto -c mosquitto.conf
```

**Step 2: Start Python Server**
```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk
python examples/mqtt_stream_server.py
```

**iOS App:**
1. Open ARVOS app
2. Tap "CONNECT TO SERVER"
3. Protocol: **MQTT**
4. Enter broker IP (your computer's IP)
5. Port: **1883** (auto-filled)
6. Tap "CONNECT"
7. Tap "START STREAMING"

**Expected Output:**
- Broker shows connection logs
- Server shows: `✅ MQTT client connected`
- Server prints telemetry data
- iOS app shows MQTT connection status

**Troubleshooting:**
- If connection fails, check broker is listening on `0.0.0.0:1883`
- Check macOS firewall allows port 1883
- On NAT64 networks, may need to use IPv6 address

---

## 4. HTTP/REST

**Server:**
```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk
python examples/http_stream_server.py
```

**iOS App:**
1. Open ARVOS app
2. Tap "CONNECT TO SERVER"
3. Protocol: **HTTP/REST**
4. Enter server IP (from terminal output)
5. Port: **8080** (auto-filled)
6. Tap "CONNECT"
7. Tap "START STREAMING"

**Expected Output:**
- Server shows: `✅ HTTP client connected`
- Server prints POST request logs
- iOS app shows HTTP connection status

**Note:** Best for telemetry only. Camera/depth frames may have connection issues on unstable networks.

---

## 5. Bluetooth LE

**Server (Python Receiver):**
```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk
python examples/ble_receiver.py
```

**iOS App:**
1. Open ARVOS app
2. Tap "CONNECT TO SERVER"
3. Protocol: **Bluetooth LE**
4. No IP/port needed - app will advertise
5. Tap "CONNECT"
6. Python script will automatically discover and connect
7. Tap "START STREAMING"

**Expected Output:**
- Python script shows: `Found ARVOS device: ...`
- Python script shows: `✅ Connected to ARVOS`
- Server prints IMU and telemetry data
- iOS app shows BLE connection status

**Note:** 
- No Wi-Fi needed
- Telemetry only (no camera/depth due to bandwidth)
- Make sure Bluetooth is enabled on both devices

---

## 6. MCAP Stream

**Server:**
```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk
python examples/mcap_stream_server.py
```

**iOS App:**
1. Open ARVOS app
2. Tap "CONNECT TO SERVER"
3. Protocol: **MCAP Stream**
4. Enter server IP (from terminal output)
5. Port: **17500** (auto-filled)
6. Tap "CONNECT"
7. Tap "START STREAMING"

**Expected Output:**
- Server shows: `✅ MCAP client connected`
- Server creates MCAP file: `arvos_stream_*.mcap`
- Server prints streaming logs
- iOS app shows MCAP connection status

**View in Foxglove:**
   ```bash
# Open the generated MCAP file in Foxglove Studio
open arvos_stream_*.mcap
```

---

## 7. QUIC/HTTP3

**Server:**
   ```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk
python examples/quic_stream_server.py
```

**Note:** Server will auto-generate self-signed certificates for local testing.

**iOS App:**
1. Open ARVOS app
2. Tap "CONNECT TO SERVER"
3. Protocol: **QUIC/HTTP3**
4. Enter server IP (from terminal output)
5. Port: **4433** (auto-filled)
6. Tap "CONNECT"
7. iOS may show certificate warning - accept for local testing
8. Tap "START STREAMING"

**Expected Output:**
- Server shows: `✅ QUIC/HTTP3 client connected`
- Server prints HTTP/3 request logs
- iOS app shows QUIC connection status

**Troubleshooting:**
- For production, use proper TLS certificates
- Self-signed certs work for local testing only
- Requires iOS 15+

---

## Quick Test Script

Create a test script to verify all protocols:

```bash
#!/bin/bash
# test_all_protocols.sh

echo "Testing all ARVOS protocols..."
echo ""

echo "1. WebSocket (Port 9090)"
python examples/basic_server.py &
WS_PID=$!
sleep 5
echo "✅ WebSocket server running (PID: $WS_PID)"
echo "   Connect from iOS app with protocol: WebSocket"
read -p "Press Enter to stop WebSocket server..."
kill $WS_PID

echo ""
echo "2. gRPC (Port 50051)"
python examples/grpc_stream_server.py &
GRPC_PID=$!
sleep 5
echo "✅ gRPC server running (PID: $GRPC_PID)"
echo "   Connect from iOS app with protocol: gRPC"
read -p "Press Enter to stop gRPC server..."
kill $GRPC_PID

# ... continue for other protocols
```

---

## Verification Checklist

For each protocol, verify:

- [ ] Server starts without errors
- [ ] iOS app can connect
- [ ] Connection status shows "Connected"
- [ ] "START STREAMING" button is enabled
- [ ] Data flows (check server logs)
- [ ] Statistics update in iOS app
- [ ] Can disconnect cleanly

---

## Common Issues

**Connection Refused:**
- Check firewall allows the protocol port
- Verify both devices on same Wi-Fi (except BLE)
- Check server is actually running

**Protocol Not Available:**
- gRPC: Requires iOS 18+
- QUIC: Requires iOS 15+
- Check protocol is selected in app

**No Data:**
- Ensure "START STREAMING" is tapped after connection
- Check streaming mode is selected
- Verify sensors are enabled

**MQTT Issues:**
- Broker must be running first
- Check broker config allows connections from network
- Verify broker IP is correct

**QUIC/HTTP3 Certificate Issues:**
- Accept self-signed certificate in iOS
- For production, use proper certificates
- Check certificate paths in server logs

---

## Performance Testing

To compare protocol performance:

1. Use same streaming mode for all tests
2. Monitor server logs for message rates
3. Check iOS app statistics for latency
4. Compare throughput in server output

**Example:**
```bash
# Test WebSocket
python examples/basic_server.py
# Note: Messages/sec, latency, CPU usage

# Test gRPC
python examples/grpc_stream_server.py
# Compare with WebSocket metrics
```

---

## Next Steps

- Try different streaming modes (RGBD, Visual-Inertial, etc.)
- Test with Apple Watch data
- Record data locally in MCAP format
- Export to KITTI/TUM formats
- Integrate with ROS 2
