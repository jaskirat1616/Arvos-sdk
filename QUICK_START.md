# Quick Start Guide - Testing All Protocols

This guide helps you test all 7 streaming protocols with the ARVOS iOS app.

## Prerequisites

1. **Install Python SDK:**
   ```bash
   cd /Users/jaskiratsingh/Desktop/arvos-sdk
   pip install -e .
   ```

2. **Install protocol-specific dependencies:**
   ```bash
   # Core dependencies
   pip install websockets aiohttp qrcode
   
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

## Testing Each Protocol

### 1. WebSocket (Default - Easiest)

**Start Server:**
```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk
python3 examples/basic_server.py
```

**In iOS App:**
1. Open ARVOS app
2. Tap "CONNECT TO SERVER"
3. Protocol: **WebSocket** (default)
4. Scan QR code or enter IP manually
5. Port: **9090** (auto-filled)
6. Tap "CONNECT"
7. Tap "START STREAMING"

**Expected:** Server shows connection and prints sensor data.

---

### 2. HTTP/REST

**Start Server:**
```bash
python3 examples/http_stream_server.py
```

**In iOS App:**
1. Protocol: **HTTP/REST**
2. Enter server IP (from terminal)
3. Port: **8080** (auto-filled)
4. Tap "CONNECT"
5. Tap "START STREAMING"

**Expected:** Server shows HTTP requests and prints sensor data.

---

### 3. gRPC (iOS 18+)

**Generate Protobuf (first time only):**
```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk/python/arvos/protos
# If sensors.proto exists:
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sensors.proto
```

**Start Server:**
```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk
python3 examples/grpc_stream_server.py
```

**In iOS App:**
1. Protocol: **gRPC**
2. Enter server IP
3. Port: **50051** (auto-filled)
4. Tap "CONNECT"
5. Tap "START STREAMING"

**Expected:** Server shows gRPC connection and prints protobuf messages.

**Note:** Requires iOS 18+ on iPhone.

---

### 4. MQTT

**Step 1: Start Mosquitto Broker**
```bash
# Create config file
cat > mosquitto.conf << EOF
listener 1883 0.0.0.0
allow_anonymous true
EOF

# Start broker
mosquitto -c mosquitto.conf
```

**Step 2: Start Python Server (new terminal)**
```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk
python3 examples/mqtt_stream_server.py
```

**In iOS App:**
1. Protocol: **MQTT**
2. Enter broker IP (your computer's IP)
3. Port: **1883** (auto-filled)
4. Tap "CONNECT"
5. Tap "START STREAMING"

**Expected:** Server shows MQTT subscription and prints telemetry.

---

### 5. Bluetooth LE (No Wi-Fi needed)

**Start Receiver:**
```bash
python3 examples/ble_receiver.py
```

**In iOS App:**
1. Protocol: **Bluetooth LE**
2. No IP/port needed - app will advertise
3. Tap "CONNECT"
4. Python script will auto-discover and connect
5. Tap "START STREAMING"

**Expected:** Python script discovers device and prints telemetry.

**Note:** Telemetry only (no camera/depth due to bandwidth).

---

### 6. MCAP Stream

**Start Server:**
```bash
python3 examples/mcap_stream_server.py
```

**In iOS App:**
1. Protocol: **MCAP Stream**
2. Enter server IP
3. Port: **17500** (auto-filled)
4. Tap "CONNECT"
5. Tap "START STREAMING"

**Expected:** Server creates MCAP file and prints streaming logs.

**View in Foxglove:**
```bash
# Open the generated MCAP file
open arvos_stream_*.mcap
```

---

### 7. QUIC/HTTP3

**Start Server:**
```bash
python3 examples/quic_stream_server.py
```

**In iOS App:**
1. Protocol: **QUIC/HTTP3**
2. Enter server IP
3. Port: **4433** (auto-filled)
4. Tap "CONNECT"
5. Accept certificate warning (for self-signed certs)
6. Tap "START STREAMING"

**Expected:** Server shows QUIC connection and prints HTTP/3 requests.

**Note:** Requires iOS 15+. Self-signed certificates work for local testing.

---

## Troubleshooting

### Connection Refused
- Check firewall allows the protocol port
- Verify both devices on same Wi-Fi (except BLE)
- Check server is actually running

### Protocol Not Available
- **gRPC:** Requires iOS 18+
- **QUIC:** Requires iOS 15+
- Check protocol is selected in app

### No Data
- Ensure "START STREAMING" is tapped after connection
- Check streaming mode is selected
- Verify sensors are enabled

### MQTT Issues
- Broker must be running first
- Check broker config allows connections from network
- Verify broker IP is correct

### Import Errors
```bash
# Install missing dependencies
pip install aiohttp  # For HTTP
pip install grpcio grpcio-tools  # For gRPC
pip install paho-mqtt  # For MQTT
pip install mcap  # For MCAP
pip install aioquic  # For QUIC
```

---

## Example Output

When working correctly, you should see:

```
✅ HTTP client connected: 192.168.1.100:54321
📊 IMU: accel=(0.12, -0.45, 9.81) gyro=(0.01, 0.02, -0.01)
📍 GPS: lat=37.774929, lon=-122.419418, accuracy ±5.0m
🧭 Pose: position=(0.0, 0.0, 0.0) tracking=normal
```

---

## Next Steps

- Try different streaming modes (RGBD, Visual-Inertial, etc.)
- Test with Apple Watch data
- Record data locally in MCAP format
- Export to KITTI/TUM formats
- Integrate with ROS 2

