# First Connection

Connect your iPhone to the ARVOS server for the first time.

## Prerequisites

- ✅ ARVOS Python SDK installed
- ✅ ARVOS iOS app installed on iPhone
- ✅ Both devices on same Wi-Fi network
- ✅ Server running (see [Quick Start](quick-start.md))

## Step-by-Step Connection

### 1. Start the Server

Run your Python server:

```bash
python my_server.py
```

You should see output like:
```
==================================================
ARVOS SERVER - Scan this QR code with your iPhone:
==================================================
[QR CODE]
==================================================
Or manually enter: ws://192.168.1.100:9090
==================================================
```

### 2. Open ARVOS App

On your iPhone:
1. Open the **ARVOS** app
2. Tap **"CONNECT TO SERVER"** button

### 3. Select Protocol

Choose your protocol:
- **WebSocket** (default) - Works everywhere
- **gRPC** - High performance (iOS 18+)
- **MQTT** - IoT deployments
- **HTTP/REST** - Simple integration
- **Bluetooth LE** - No Wi-Fi needed
- **MCAP Stream** - Robotics research
- **QUIC/HTTP3** - Ultra-low latency

### 4. Connect

**Option A: Scan QR Code**
- Point your iPhone camera at the QR code
- Tap the notification to open in ARVOS app

**Option B: Manual Entry**
- Tap "Enter Manually"
- Enter your computer's IP address (shown in terminal)
- Enter port number (default: 9090 for WebSocket)
- Tap **"CONNECT"**

### 5. Start Streaming

Once connected:
1. Tap **"START STREAMING"** button
2. Select your streaming mode:
   - **Full Sensor** - All sensors
   - **RGBD Camera** - Camera + Depth
   - **IMU Only** - Just IMU data
   - **Mapping** - Pose + IMU
3. Watch data flow to your Python server!

## Troubleshooting

### "Connection Failed"

**Check Network:**
- Ensure both devices on same Wi-Fi
- Try pinging iPhone from computer: `ping <iphone-ip>`
- Try pinging computer from iPhone

**Check Firewall:**
- macOS: System Settings → Firewall → Allow Python
- Linux: `sudo ufw allow 9090`
- Windows: Windows Defender → Allow Python

**Check Port:**
```bash
# Test if port is open
nc -l 9090  # Should listen without errors
```

### "QR Code Not Scanning"

- Increase terminal font size
- Use manual IP entry instead
- Check QR code contains correct IP

### "No Data Received"

- Ensure "START STREAMING" is tapped in app
- Check server callbacks are registered
- Verify protocol matches (WebSocket, gRPC, etc.)

### Protocol-Specific Issues

**gRPC:**
- Requires iOS 18+
- Check port 50051 is open

**MQTT:**
- Ensure Mosquitto broker is running
- Check broker is listening on all interfaces

**HTTP/REST:**
- Use actual LAN IP (not 0.0.0.0)
- Check App Transport Security settings

**Bluetooth LE:**
- Enable Bluetooth on both devices
- Ensure app is advertising (BLE toggle on)

[→ Full Troubleshooting Guide](../guides/troubleshooting.md)

## Next Steps

- [Protocol Examples](../examples/protocols.md) - Try different protocols
- [API Reference](../api/python-sdk.md) - Explore the API
- [Best Practices](../guides/best-practices.md) - Optimize your setup

