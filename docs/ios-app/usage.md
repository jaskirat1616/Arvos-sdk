# iOS App Usage Guide

Complete guide to using the ARVOS iOS app.

## First Launch

### Permissions

On first launch, the app will request permissions:

1. **Camera** - Required for camera streaming
2. **Location** - Required for GPS data
3. **Motion & Fitness** - Required for IMU data
4. **Bluetooth** - Required for BLE and Apple Watch

Grant all permissions for full functionality.

### Initial Setup

1. **Open** the ARVOS app
2. **Review** the welcome screen
3. **Grant** necessary permissions
4. **Ready** to connect!

## Connecting to a Server

### Step 1: Start Your Server

On your computer, start a Python server:

```bash
python examples/basic_server.py
```

### Step 2: Open Connection Sheet

In the ARVOS app:
1. Tap **"CONNECT TO SERVER"** button
2. Connection sheet appears

### Step 3: Select Protocol

1. Find **"PROTOCOL"** section
2. Select your protocol (WebSocket is default)
3. Port number auto-fills based on protocol

### Step 4: Enter Server Details

**Option A: Scan QR Code**
- Point camera at QR code shown in terminal
- Tap notification to open in app

**Option B: Manual Entry**
- Tap "Enter Manually"
- Enter computer's IP address
- Verify port number
- Tap **"CONNECT"**

### Step 5: Start Streaming

Once connected:
1. Tap **"START STREAMING"** button
2. Select streaming mode
3. Data flows to your server!

## Streaming Modes

### Full Sensor
Stream all available sensors:
- Camera
- Depth/LiDAR
- IMU
- ARKit Pose
- GPS

**Best for:** Complete data collection

### RGBD Camera
Camera + Depth only:
- RGB video
- Depth point clouds

**Best for:** 3D reconstruction

### IMU Only
Just IMU data:
- Accelerometer
- Gyroscope
- Gravity

**Best for:** Low bandwidth, high frequency

### Mapping
Pose + IMU:
- ARKit pose
- IMU data

**Best for:** SLAM algorithms

### Visual-Inertial
Camera + IMU:
- RGB video
- IMU data

**Best for:** Sensor fusion

### LiDAR
Depth + IMU:
- Point clouds
- IMU data

**Best for:** 3D scanning

### Custom
Configure your own combination:
- Select individual sensors
- Set rates
- Custom configuration

## Local Recording

### Start Recording

1. Tap **"RECORD"** button
2. Select recording location
3. Recording starts
4. Tap **"STOP"** when done

### Recording Format

- **Format**: MCAP
- **Video**: H.264 encoded
- **Timestamps**: Nanosecond precision
- **Metadata**: All sensor metadata preserved

### Export Options

Recorded files can be exported to:
- KITTI format
- TUM format
- EuRoC format
- PLY point clouds
- CSV data

## Apple Watch Integration

### Enable Watch

1. Open **Settings**
2. Find **"Apple Watch"** section
3. Toggle **"Enable Watch Streaming"**
4. Ensure watch is paired and nearby

### Watch Data

Once enabled, watch data streams alongside iPhone data:
- Watch IMU (50-100 Hz)
- Watch attitude
- Motion activity

[→ Apple Watch Guide](apple-watch.md)

## Sensor Test View

Test individual sensors:

1. Open **"Sensor Test"** view
2. Toggle sensors on/off
3. View real-time data
4. Monitor sample rates

### Available Tests

- **IMU** - Accelerometer, gyroscope, gravity
- **Camera** - Live camera preview
- **Depth** - Point cloud visualization
- **Pose** - ARKit tracking visualization
- **GPS** - Location display
- **Apple Watch** - Watch sensor data

## Settings

### Protocol Settings

- Default protocol selection
- Port configuration
- Connection timeout

### Streaming Settings

- Default streaming mode
- Sensor rate limits
- Quality settings

### Recording Settings

- Default recording location
- Video quality
- Compression settings

### Apple Watch Settings

- Enable/disable watch
- Watch sample rate
- Watch data filtering

## Troubleshooting

### Connection Issues

- Check Wi-Fi network
- Verify firewall settings
- Try different protocol
- Check server is running

### No Data Streaming

- Ensure "START STREAMING" is tapped
- Check streaming mode selection
- Verify server callbacks registered
- Check protocol matches

### Performance Issues

- Reduce sensor rates
- Use lower quality settings
- Try different protocol
- Check network signal

[→ Full Troubleshooting Guide](../guides/troubleshooting.md)

## Next Steps

- [Features](features.md) - Complete feature list
- [Protocols](protocols.md) - Protocol selection
- [Apple Watch](apple-watch.md) - Watch integration

