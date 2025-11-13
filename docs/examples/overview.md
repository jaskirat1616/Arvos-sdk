# Examples Overview

Complete list of ARVOS SDK examples and tutorials.

## Basic Examples

### Basic Server
Simple WebSocket server example.

[→ Basic Server](basic-server.md)

### Protocol Examples
Examples for each protocol:
- WebSocket
- gRPC
- MQTT
- HTTP/REST
- Bluetooth LE
- MCAP Stream
- QUIC/HTTP3

[→ Protocol Examples](protocols.md)

## Visualization Examples

### Live Visualization
Real-time sensor data visualization.

[→ Live Visualization](visualization.md)

### Point Cloud Viewer
3D LiDAR point cloud visualization.

[→ Point Cloud Viewer](visualization.md#point-cloud-viewer)

### Camera Viewer
Live camera feed display.

[→ Camera Viewer](visualization.md#camera-viewer)

## Integration Examples

### ROS 2 Bridge
Publish ARVOS data to ROS 2 topics.

[→ ROS 2 Integration](ros2.md)

### Apple Watch
Receive and process Apple Watch sensor data.

[→ Apple Watch Examples](apple-watch.md)

## Data Processing Examples

### Save to CSV
Save sensor data to CSV files.

```bash
python examples/save_to_csv.py
```

### Save Camera Frames
Save camera frames as images.

```bash
python examples/save_camera_frames.py
```

## All Examples

Browse all examples in the `examples/` directory:

- `01_quickstart.py` - Quick start tutorial
- `basic_server.py` - Basic WebSocket server
- `grpc_stream_server.py` - gRPC server
- `mqtt_stream_server.py` - MQTT server
- `http_stream_server.py` - HTTP server
- `ble_receiver.py` - BLE receiver
- `mcap_stream_server.py` - MCAP server
- `quic_stream_server.py` - QUIC/HTTP3 server
- `live_visualization.py` - Live visualization
- `point_cloud_viewer.py` - Point cloud viewer
- `camera_viewer.py` - Camera viewer
- `watch_sensor_viewer.py` - Apple Watch viewer
- `ros2_bridge.py` - ROS 2 bridge
- `save_to_csv.py` - CSV export
- `save_camera_frames.py` - Image export

## Next Steps

- [Basic Server](basic-server.md) - Your first example
- [Protocol Examples](protocols.md) - Try all protocols
- [Visualization](visualization.md) - Visual examples

