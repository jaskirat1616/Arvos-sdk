# ARVOS Documentation

**Professional sensor streaming platform for iPhone and Apple Watch**

Turn your iPhone (and optional Apple Watch) into a research-grade sensor platform with LiDAR, cameras, IMU, ARKit pose tracking, and wearable motion sensing.

---

## 🚀 Quick Start

Get started in 30 seconds with the Web Viewer (no installation required):

```bash
cd arvos-sdk/web-viewer
./start-viewer.sh
# Scan QR code with iPhone → Done!
```

Or use the Python SDK for custom applications:

```bash
pip install arvos-sdk
python examples/01_quickstart.py
```

---

## 📱 What ARVOS Streams

ARVOS captures and streams high-quality sensor data from your iPhone and Apple Watch:

### iPhone Sensors

- **📷 Camera**: 30 FPS @ 1920x1080 RGB video
- **🔍 LiDAR/Depth**: 5 FPS 3D point clouds with confidence maps
- **📊 IMU**: 100-200 Hz accelerometer + gyroscope + gravity
- **🧭 ARKit Pose**: 30-60 Hz 6DOF camera tracking with quality flags
- **📍 GPS**: 1 Hz location data (outdoor)

### Apple Watch Sensors (Optional)

- **⌚ IMU**: 50-100 Hz wearable accelerometer + gyroscope + gravity
- **🧭 Attitude**: Quaternion + pitch/roll/yaw angles
- **🚶 Motion Activity**: Classification (walking, running, cycling, vehicle, stationary)

**All sensors are nanosecond-synchronized** for research-grade data collection.

---

## 🌐 7 Streaming Protocols

ARVOS supports multiple streaming protocols to fit different use cases:

| Protocol | Best For | Port | Status |
|----------|----------|------|--------|
| **WebSocket** | General purpose | 9090 | ✅ Complete |
| **gRPC** | High performance, research | 50051 | ✅ Complete |
| **MQTT** | IoT, multi-subscriber | 1883 | ✅ Complete |
| **HTTP/REST** | Simple integration | 8080 | ✅ Complete |
| **Bluetooth LE** | Low bandwidth, cable-free | N/A | ✅ Complete |
| **MCAP Stream** | Robotics research | 17500 | ✅ Complete |
| **QUIC/HTTP3** | Ultra-low latency | 4433 | ✅ Complete |

[→ Protocol Comparison Guide](protocols/comparison.md)

---

## 🎯 Use Cases

### For Researchers
- SLAM algorithm development with ARKit ground truth
- Sensor fusion experiments
- ML dataset collection
- Real-time 3D reconstruction

### For Robotics Engineers
- ROS 2 perception testing
- Mobile sensor platform development
- Algorithm prototyping
- Live demos and presentations

### For Students
- Computer vision learning
- AR experiments
- Sensor data visualization
- Course projects

---

## 📚 Documentation Structure

### Getting Started
- [Quick Start](getting-started/quick-start.md) - Get up and running in minutes
- [Installation](getting-started/installation.md) - Install the Python SDK
- [First Connection](getting-started/first-connection.md) - Connect your iPhone

### iOS App
- [Overview](ios-app/overview.md) - App features and capabilities
- [Protocols](ios-app/protocols.md) - Protocol selection in the app
- [Usage Guide](ios-app/usage.md) - How to use the app
- [Apple Watch](ios-app/apple-watch.md) - Wearable sensor integration

### Python SDK
- [Overview](python-sdk/overview.md) - SDK architecture and design
- [Installation](python-sdk/installation.md) - Installation instructions
- [Quick Start](python-sdk/quick-start.md) - Your first Python server

### Protocols
- [Overview](protocols/overview.md) - All supported protocols
- Individual protocol guides for each streaming method
- [Comparison](protocols/comparison.md) - Choose the right protocol

### API Reference
- [Python SDK](api/python-sdk.md) - Complete API documentation
- [Data Types](api/data-types.md) - Sensor data structures
- [Servers](api/servers.md) - Protocol server classes
- [Clients](api/clients.md) - Client classes

### Examples
- [Overview](examples/overview.md) - All available examples
- [Basic Server](examples/basic-server.md) - Simple WebSocket server
- [Protocol Examples](examples/protocols.md) - Examples for each protocol
- [Visualization](examples/visualization.md) - 3D visualization examples
- [ROS 2](examples/ros2.md) - ROS 2 integration

### Guides
- [Protocol Selection](guides/protocol-selection.md) - Choose the right protocol
- [Performance Optimization](guides/performance.md) - Optimize your setup
- [Troubleshooting](guides/troubleshooting.md) - Common issues and solutions
- [Best Practices](guides/best-practices.md) - Recommended practices

### Web Viewer
- [Overview](web-viewer/overview.md) - Zero-install browser viewer
- [Quick Start](web-viewer/quick-start.md) - Get started in 30 seconds

---

## 💻 Requirements

### iPhone
- iPhone 12 Pro or newer (for LiDAR)
- iOS 16.0+ (iOS 18+ for gRPC)
- Same Wi-Fi network as computer (or Bluetooth for BLE)

### Computer
- Python 3.8+ or modern browser
- Same Wi-Fi network as iPhone (for Wi-Fi protocols)
- Firewall allows selected protocol port

### Apple Watch (Optional)
- Apple Watch Series 6 or newer
- watchOS 9.0+
- Paired with streaming iPhone

---

## 🎓 Learning Resources

- **Protocol Selection**: [Which protocol should I use?](guides/protocol-selection.md)
- **Examples**: [Browse all examples](examples/overview.md)
- **Troubleshooting**: [Common issues](guides/troubleshooting.md)
- **API Reference**: [Complete API docs](api/python-sdk.md)

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](contributing/overview.md) for details.

---

## 📜 License

MIT License - Use freely in your research and projects

---

## 🔗 Links

- **GitHub SDK**: [jaskirat1616/arvos-sdk](https://github.com/jaskirat1616/arvos-sdk)
- **iOS App**: Available on the App Store (code is private)
- **MCAP Tools**: [mcap.dev](https://mcap.dev)
- **ROS 2**: [docs.ros.org](https://docs.ros.org)

---

**Made for the robotics and AR research community** ❤️

