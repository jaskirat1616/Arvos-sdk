# iOS App Features

Complete feature list for the ARVOS iOS app.

## Sensor Streaming

### Camera
- **Resolution**: 1920x1080 @ 30 FPS
- **Format**: JPEG compressed
- **Intrinsics**: Camera calibration parameters
- **Synchronization**: Nanosecond timestamps

### LiDAR/Depth
- **Rate**: 5 FPS point clouds
- **Format**: PLY point cloud format
- **Confidence**: Per-point confidence maps
- **Range**: Up to 5 meters (iPhone 12 Pro+)

### IMU
- **Rate**: 100-200 Hz
- **Sensors**: Accelerometer, gyroscope, magnetometer
- **Gravity**: Gravity vector reference
- **Attitude**: Roll, pitch, yaw angles

### ARKit Pose
- **Rate**: 30-60 Hz
- **Tracking**: 6DOF camera pose
- **Quality**: Tracking state flags
- **Transform**: 4x4 transformation matrix

### GPS
- **Rate**: 1 Hz
- **Data**: Latitude, longitude, altitude
- **Accuracy**: Horizontal and vertical accuracy
- **Speed**: Current speed and course

## Streaming Modes

### Full Sensor
Stream all available sensors simultaneously.

### RGBD Camera
Camera + Depth only - perfect for 3D reconstruction.

### IMU Only
Just IMU data - low bandwidth, high frequency.

### Mapping
Pose + IMU - ideal for SLAM algorithms.

### Visual-Inertial
Camera + IMU - sensor fusion applications.

### LiDAR
Depth + IMU - 3D scanning use cases.

### Custom
Configure your own sensor combination.

## Protocols

### WebSocket (Default)
- Bidirectional communication
- Works everywhere
- Good for most use cases

### gRPC
- High performance
- Protocol Buffers
- iOS 18+ required

### MQTT
- Multi-subscriber support
- IoT-friendly
- Requires broker

### HTTP/REST
- Simple POST requests
- Webhook integration
- Easy debugging

### Bluetooth LE
- No Wi-Fi needed
- Low power
- Telemetry only

### MCAP Stream
- Robotics standard
- Foxglove compatible
- Streaming format

### QUIC/HTTP3
- Ultra-low latency
- Better on unstable networks
- iOS 15+ required

[→ Protocol Details](../protocols/overview.md)

## Apple Watch Integration

### Wearable IMU
- 50-100 Hz IMU data
- Accelerometer + gyroscope + gravity
- Nanosecond synchronization

### Attitude
- Quaternion representation
- Euler angles (pitch, roll, yaw)
- Reference frame information

### Motion Activity
- Classification: walking, running, cycling, vehicle, stationary
- Confidence scores
- Real-time updates

[→ Apple Watch Guide](apple-watch.md)

## Local Recording

### MCAP Format
- Industry-standard container
- H.264 video encoding
- Nanosecond timestamps
- Metadata preservation

### Export Formats
- **KITTI** - Autonomous driving datasets
- **TUM** - SLAM datasets
- **EuRoC** - MAV datasets
- **PLY** - Point cloud export
- **CSV** - Tabular data

## User Interface

### Connection Sheet
- Protocol selection
- QR code scanning
- Manual IP entry
- Connection status

### Streaming View
- Real-time sensor visualization
- Statistics display
- Connection quality indicators
- Start/stop controls

### Settings
- Protocol configuration
- Streaming mode selection
- Sensor rate adjustment
- Apple Watch toggle

### Sensor Test
- Individual sensor testing
- Live data visualization
- Sample rate monitoring
- Connection diagnostics

## Next Steps

- [Protocols](protocols.md) - Protocol selection guide
- [Usage Guide](usage.md) - How to use the app
- [Apple Watch](apple-watch.md) - Wearable integration

