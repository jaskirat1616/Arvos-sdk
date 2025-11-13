# Complete Setup Guide

Step-by-step guide to set up and test all ARVOS streaming protocols.

## 1. Install Python SDK

```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk
pip install -e .
```

## 2. Install Protocol Dependencies

### Core (Required for all)
```bash
pip install websockets aiohttp qrcode numpy pillow
```

### Protocol-Specific

**HTTP/REST:**
```bash
pip install aiohttp
```

**gRPC:**
```bash
pip install grpcio grpcio-tools protobuf
```

**MQTT:**
```bash
pip install paho-mqtt
brew install mosquitto  # macOS
# or: sudo apt-get install mosquitto  # Linux
```

**Bluetooth LE:**
```bash
pip install bleak
```

**MCAP Stream:**
```bash
pip install mcap
```

**QUIC/HTTP3:**
```bash
pip install aioquic
```

### Install All at Once
```bash
pip install websockets aiohttp qrcode numpy pillow \
            grpcio grpcio-tools protobuf \
            paho-mqtt mcap aioquic bleak
```

## 3. Verify Installation

```bash
cd /Users/jaskiratsingh/Desktop/arvos-sdk
python3 examples/test_all_protocols.py
```

Expected output:
```
✅ HTTPArvosServer - OK
✅ MQTTArvosServer - OK
✅ MCAPStreamServer - OK
✅ GRPCArvosServer - OK
✅ QUICArvosServer - OK
🎉 All servers are ready!
```

## 4. Test Each Protocol

### WebSocket (Start Here - Easiest)

```bash
python3 examples/basic_server.py
```

**In iOS App:**
1. Open ARVOS
2. Tap "CONNECT TO SERVER"
3. Protocol: **WebSocket**
4. Scan QR code
5. Tap "CONNECT"
6. Tap "START STREAMING"

**Expected:** Server prints sensor data.

---

### HTTP/REST

```bash
python3 examples/http_stream_server.py
```

**In iOS App:**
- Protocol: **HTTP/REST**
- Port: **8080**
- Enter server IP

---

### gRPC

**First, generate protobuf (if needed):**
```bash
cd python/arvos/protos
# If sensors.proto exists:
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sensors.proto
cd ../../..
```

**Then run:**
```bash
python3 examples/grpc_stream_server.py
```

**In iOS App:**
- Protocol: **gRPC**
- Port: **50051**
- Enter server IP

**Note:** Requires iOS 18+

---

### MQTT

**Terminal 1 - Start Broker:**
```bash
cat > mosquitto.conf << EOF
listener 1883 0.0.0.0
allow_anonymous true
EOF

mosquitto -c mosquitto.conf
```

**Terminal 2 - Start Server:**
```bash
python3 examples/mqtt_stream_server.py
```

**In iOS App:**
- Protocol: **MQTT**
- Port: **1883**
- Enter broker IP

---

### Bluetooth LE

```bash
python3 examples/ble_receiver.py
```

**In iOS App:**
- Protocol: **Bluetooth LE**
- Tap "CONNECT" (no IP needed)
- Python script auto-discovers

---

### MCAP Stream

```bash
python3 examples/mcap_stream_server.py
```

**In iOS App:**
- Protocol: **MCAP Stream**
- Port: **17500**
- Enter server IP

**View Results:**
```bash
open arvos_stream_*.mcap  # Opens in Foxglove Studio
```

---

### QUIC/HTTP3

```bash
python3 examples/quic_stream_server.py
```

**In iOS App:**
- Protocol: **QUIC/HTTP3**
- Port: **4433**
- Enter server IP
- Accept certificate warning

**Note:** Requires iOS 15+

---

## 5. Troubleshooting

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade websockets aiohttp grpcio paho-mqtt mcap aioquic bleak
```

### Connection Refused
- Check firewall: `sudo ufw allow 9090` (or your port)
- Verify same Wi-Fi network
- Check server is running: `lsof -i :9090`

### No Data
- Ensure "START STREAMING" is tapped
- Check streaming mode is selected
- Verify sensors enabled in app

### MQTT Broker Issues
```bash
# Check broker is running
ps aux | grep mosquitto

# Check broker config
cat mosquitto.conf

# Test broker
mosquitto_sub -h localhost -t test
```

### gRPC Protobuf Issues
```bash
# Regenerate protobuf
cd python/arvos/protos
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sensors.proto
```

---

## 6. Quick Reference

| Protocol | Port | iOS Version | Dependencies |
|----------|------|-------------|--------------|
| WebSocket | 9090 | 16+ | websockets |
| HTTP/REST | 8080 | 16+ | aiohttp |
| gRPC | 50051 | 18+ | grpcio, protobuf |
| MQTT | 1883 | 16+ | paho-mqtt, mosquitto |
| BLE | N/A | 16+ | bleak |
| MCAP | 17500 | 16+ | mcap |
| QUIC/HTTP3 | 4433 | 15+ | aioquic |

---

## 7. Next Steps

- ✅ Test all protocols
- ✅ Try different streaming modes
- ✅ Test with Apple Watch
- ✅ Record data locally
- ✅ Export to KITTI/TUM
- ✅ Integrate with ROS 2

---

## Support

For issues:
1. Check `QUICK_START.md` for protocol-specific guides
2. Check `examples/README_EXAMPLES.md` for example details
3. Run `python3 examples/test_all_protocols.py` to verify setup

