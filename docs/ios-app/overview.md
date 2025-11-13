# iOS App Overview

The ARVOS iOS app turns your iPhone (and optional Apple Watch) into a professional sensor streaming platform.

!!! note "App Availability"
    The ARVOS iOS app is available on the App Store for download and use. However, the iOS app source code is **not open source** and is not publicly available on GitHub. This documentation covers app usage and features.

## Features

### 📱 iPhone Sensors

- **📷 Camera**: 30 FPS @ 1920x1080 RGB video streaming
- **🔍 LiDAR/Depth**: 5 FPS 3D point clouds with confidence maps
- **📊 IMU**: 100-200 Hz accelerometer + gyroscope + gravity reference
- **🧭 ARKit Pose**: 30-60 Hz 6DOF camera tracking with quality flags
- **📍 GPS**: 1 Hz location data (outdoor)

### ⌚ Apple Watch Integration

- **⌚ IMU**: 50-100 Hz wearable accelerometer + gyroscope + gravity
- **🧭 Attitude**: Quaternion + pitch/roll/yaw angles
- **🚶 Motion Activity**: Classification (walking, running, cycling, vehicle, stationary)

### 🌐 7 Streaming Protocols

Choose the protocol that fits your use case:

- **WebSocket** - General purpose, default
- **gRPC** - High performance, research (iOS 18+)
- **MQTT** - IoT, multi-subscriber
- **HTTP/REST** - Simple integration
- **Bluetooth LE** - Low bandwidth, cable-free
- **MCAP Stream** - Robotics research
- **QUIC/HTTP3** - Ultra-low latency (iOS 15+)

### 📊 Streaming Modes

- **Full Sensor** - All available sensors
- **RGBD Camera** - Camera + Depth only
- **IMU Only** - Just IMU data (low bandwidth)
- **Mapping** - Pose + IMU (SLAM use cases)
- **Visual-Inertial** - Camera + IMU
- **LiDAR** - Depth + IMU
- **Custom** - Configure your own sensor combination

### 💾 Local Recording

- Record to MCAP format
- H.264 video encoding
- Nanosecond timestamps
- Export to KITTI, TUM, EuRoC formats

## Requirements

### iPhone
- iPhone 12 Pro or newer (for LiDAR)
- iOS 16.0+ (iOS 18+ for gRPC)
- Same Wi-Fi network as computer (or Bluetooth for BLE)

### Apple Watch (Optional)
- Apple Watch Series 6 or newer
- watchOS 9.0+
- Paired with streaming iPhone

## Getting Started

1. **Download** the ARVOS app from the App Store
2. **Open** the app and grant necessary permissions (Camera, Location, Motion)
3. **Connect** to your Python server (see [First Connection](../getting-started/first-connection.md))
4. **Start** streaming sensor data!

## App Structure

### Main Views

- **Connection Sheet** - Connect to servers, select protocol
- **Streaming View** - Real-time sensor visualization
- **Settings** - Configure streaming modes, protocols
- **Recording** - Local MCAP recording
- **Sensor Test** - Test individual sensors

### Protocol Selection

The app includes a protocol picker in the connection sheet:
- Select from 7 available protocols
- Automatic port configuration
- Protocol-specific connection options

[→ Protocol Selection Guide](../ios-app/protocols.md)

## Next Steps

- [Features](features.md) - Detailed feature list
- [Protocols](protocols.md) - Protocol selection in app
- [Usage Guide](usage.md) - How to use the app
- [Apple Watch](apple-watch.md) - Wearable sensor integration

