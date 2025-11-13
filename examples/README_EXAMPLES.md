# ARVOS Examples Guide

Complete guide to all example scripts for testing protocols with the iOS app.

## Quick Test

Run this to verify all servers can be imported:
```bash
python3 examples/test_all_protocols.py
```

## Protocol Examples

### 1. WebSocket (Default)
**File:** `basic_server.py`

**Run:**
```bash
python3 examples/basic_server.py
```

**Features:**
- QR code generation
- All sensor types (IMU, GPS, Pose, Camera, Depth)
- Apple Watch support
- Statistics tracking

**iOS App:**
- Protocol: WebSocket
- Port: 9090
- Scan QR code or enter IP

---

### 2. HTTP/REST
**File:** `http_stream_server.py`

**Run:**
```bash
python3 examples/http_stream_server.py
```

**Features:**
- REST API endpoints
- `/api/health` - Health check
- `/api/telemetry` - JSON sensor data
- `/api/binary` - Binary data (camera/depth)

**iOS App:**
- Protocol: HTTP/REST
- Port: 8080
- Enter server IP

**Dependencies:**
```bash
pip install aiohttp
```

---

### 3. gRPC
**File:** `grpc_stream_server.py`

**Run:**
```bash
# First, generate protobuf (if not done):
cd python/arvos/protos
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sensors.proto
cd ../../..

# Then run server:
python3 examples/grpc_stream_server.py
```

**Features:**
- Protocol Buffers
- Bidirectional streaming
- High performance

**iOS App:**
- Protocol: gRPC
- Port: 50051
- Enter server IP

**Dependencies:**
```bash
pip install grpcio grpcio-tools protobuf
```

**Note:** Requires iOS 18+

---

### 4. MQTT
**File:** `mqtt_stream_server.py`

**Run:**
```bash
# Terminal 1: Start Mosquitto broker
mosquitto -c mosquitto.conf

# Terminal 2: Run server
python3 examples/mqtt_stream_server.py
```

**Features:**
- Multi-subscriber support
- Topics: `arvos/telemetry`, `arvos/binary`
- IoT-friendly

**iOS App:**
- Protocol: MQTT
- Port: 1883
- Enter broker IP

**Dependencies:**
```bash
pip install paho-mqtt
brew install mosquitto  # macOS
```

**Mosquitto Config:**
```bash
cat > mosquitto.conf << EOF
listener 1883 0.0.0.0
allow_anonymous true
EOF
```

---

### 5. Bluetooth LE
**File:** `ble_receiver.py`

**Run:**
```bash
python3 examples/ble_receiver.py
```

**Features:**
- No Wi-Fi needed
- Auto-discovery
- Low power

**iOS App:**
- Protocol: Bluetooth LE
- No IP/port needed
- Tap CONNECT (app advertises)

**Dependencies:**
```bash
pip install bleak
```

**Note:** Telemetry only (no camera/depth)

---

### 6. MCAP Stream
**File:** `mcap_stream_server.py`

**Run:**
```bash
python3 examples/mcap_stream_server.py
```

**Features:**
- Writes to MCAP file
- Foxglove Studio compatible
- All sensor types

**iOS App:**
- Protocol: MCAP Stream
- Port: 17500
- Enter server IP

**Dependencies:**
```bash
pip install mcap websockets
```

**View Results:**
```bash
# Open MCAP file in Foxglove Studio
open arvos_stream_*.mcap
```

---

### 7. QUIC/HTTP3
**File:** `quic_stream_server.py`

**Run:**
```bash
python3 examples/quic_stream_server.py
```

**Features:**
- Ultra-low latency
- TLS encryption
- Auto-generates self-signed certs

**iOS App:**
- Protocol: QUIC/HTTP3
- Port: 4433
- Enter server IP
- Accept certificate warning

**Dependencies:**
```bash
pip install aioquic
```

**Note:** Requires iOS 15+

---

## Other Examples

### Visualization
- `live_visualization.py` - Real-time 3D visualization
- `camera_viewer.py` - Camera frame viewer
- `depth_viewer.py` - Depth point cloud viewer
- `point_cloud_viewer.py` - LiDAR visualization

### Data Export
- `save_to_csv.py` - Export to CSV
- `save_camera_frames.py` - Save camera frames

### ROS 2
- `ros2_bridge.py` - ROS 2 integration

### Apple Watch
- `watch_sensor_viewer.py` - Watch sensor visualization
- `simple_watch_receiver.py` - Basic watch receiver

---

## Testing Checklist

For each protocol, verify:

- [ ] Server starts without errors
- [ ] iOS app can connect
- [ ] Connection status shows "Connected"
- [ ] "START STREAMING" button is enabled
- [ ] Data flows (check server logs)
- [ ] Statistics update in iOS app
- [ ] Can disconnect cleanly

---

## Troubleshooting

### Import Errors
```bash
# Install all dependencies
pip install websockets aiohttp qrcode
pip install grpcio grpcio-tools protobuf
pip install paho-mqtt
pip install mcap
pip install aioquic
pip install bleak
```

### Connection Issues
- Check firewall allows protocol port
- Verify same Wi-Fi network (except BLE)
- Check server is running
- Verify IP address is correct

### No Data
- Ensure "START STREAMING" is tapped
- Check streaming mode is selected
- Verify sensors are enabled in app

---

## Next Steps

1. Try different streaming modes
2. Test with Apple Watch
3. Record data locally
4. Export to KITTI/TUM formats
5. Integrate with ROS 2

