# Arvos SDK

Python SDK for receiving real-time sensor data from the Arvos iPhone app.

## 🌐 NEW: Web Viewer (Zero Install!)

**Stream iPhone sensors to your browser in 30 seconds - no Python required!**

```bash
cd arvos-sdk/web-viewer
./start-viewer.sh    # Mac/Linux
# OR
start-viewer.bat     # Windows
```

Then scan the QR code with your iPhone. [→ Full Instructions](web-viewer/README.md)

**Perfect for:**
- Quick testing without SDK setup
- Live demos and presentations
- Students and researchers
- Any device with a browser

---

## Overview

Arvos SDK provides Python clients and servers to receive iPhone sensor data over multiple protocols, including:
- **Camera**: RGB video (JPEG compressed)
- **LiDAR/Depth**: 3D point clouds with confidence maps
- **IMU**: Accelerometer + gyroscope + gravity reference
- **ARKit Pose**: 6DOF camera tracking with quality flags
- **GPS**: Location data
- **Apple Watch** *(optional)*: Wearable IMU, attitude, and motion activity data

## 🚀 Supported Protocols

ARVOS supports **7 streaming protocols** to fit different use cases:

| Protocol | Best For | Default Port | Status |
|----------|----------|--------------|--------|
| **WebSocket** | General purpose, default | 9090 | ✅ Complete |
| **gRPC** | High performance, research | 50051 | ✅ Complete (iOS 18+) |
| **MQTT** | IoT, multi-subscriber | 1883 | ✅ Complete |
| **HTTP/REST** | Simple integration, webhooks | 8080 | ✅ Complete |
| **Bluetooth LE** | Low bandwidth, cable-free | N/A | ✅ Complete |
| **MCAP Stream** | Robotics research, Foxglove | 17500 | ✅ Complete |
| **QUIC/HTTP3** | Ultra-low latency | 4433 | ✅ Complete (iOS 15+) |

### Protocol Selection Guide

**WebSocket** (Default)
- ✅ Works everywhere
- ✅ Bidirectional communication
- ✅ Good for most use cases
- Example: `python examples/basic_server.py`

**gRPC**
- ✅ Industry standard for research
- ✅ Protocol Buffers (efficient)
- ✅ Bidirectional streaming
- ⚠️ Requires iOS 18+
- Example: `python examples/grpc_stream_server.py`

**MQTT**
- ✅ Multi-subscriber support
- ✅ IoT-friendly
- ✅ Requires MQTT broker (Mosquitto)
- Example: `python examples/mqtt_stream_server.py`

**HTTP/REST**
- ✅ Simple POST requests
- ✅ Easy webhook integration
- ✅ Works with any HTTP client
- Example: `python examples/http_stream_server.py`

**Bluetooth LE**
- ✅ No Wi-Fi needed
- ✅ Low power
- ⚠️ Low bandwidth (telemetry only)
- Example: `python examples/ble_receiver.py`

**MCAP Stream**
- ✅ Robotics standard format
- ✅ Foxglove Studio compatible
- ✅ Streaming MCAP files
- Example: `python examples/mcap_stream_server.py`

**QUIC/HTTP3**
- ✅ Ultra-low latency
- ✅ Better performance on unstable networks
- ✅ Built-in encryption (TLS required)
- ⚠️ Requires TLS certificates
- ⚠️ Requires aioquic library
- Example: `python examples/quic_stream_server.py`

## Installation

Package available at: https://pypi.org/project/arvos-sdk/

### Basic Installation
```bash
pip install arvos-sdk
```

Or from source:
```bash
git clone https://github.com/jaskirat1616/arvos-sdk.git
cd arvos-sdk
pip install -e .
```

### Protocol-Specific Dependencies

**Core (WebSocket):**
```bash
pip install arvos-sdk  # Includes websockets, qrcode, numpy
```

**gRPC:**
```bash
pip install grpcio grpcio-tools protobuf
```

**MQTT:**
```bash
pip install paho-mqtt
# Also install Mosquitto broker: brew install mosquitto (Mac) or apt-get install mosquitto (Linux)
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

### With Optional Dependencies
```bash
# For visualization examples
pip install -e ".[visualization]"

# For image processing
pip install -e ".[image]"

# For ROS 2 integration
pip install -e ".[ros2]"

# For development
pip install -e ".[dev]"
```

## Quick Start

### 1. Basic WebSocket Server

```python
import asyncio
from arvos import ArvosServer

async def main():
    server = ArvosServer(port=9090)

    # Show QR code for easy connection
    server.print_qr_code()

    # Define callbacks
    async def on_imu(data):
        print(f"IMU: accel={data.linear_acceleration}")

    server.on_imu = on_imu

    await server.start()

asyncio.run(main())
```

### 2. gRPC Server

```python
import asyncio
from arvos.servers import GRPCArvosServer

async def main():
    server = GRPCArvosServer(host="0.0.0.0", port=50051)
    
    def on_imu(data):
        print(f"IMU: {data.angular_velocity}")
    
    server.on_imu = on_imu
    await server.start()

asyncio.run(main())
```

### 3. MQTT Server

**First, start MQTT broker:**
```bash
mosquitto -c mosquitto.conf
```

**Then run the server:**
```python
import asyncio
from arvos.servers import MQTTArvosServer

async def main():
    server = MQTTArvosServer(host="localhost", port=1883)
    
    def on_imu(data):
        print(f"IMU: {data.angular_velocity}")
    
    server.on_imu = on_imu
    await server.start()

asyncio.run(main())
```

### 4. HTTP Server

```python
import asyncio
from arvos.servers import HTTPArvosServer

async def main():
    server = HTTPArvosServer(port=8080)
    
    def on_imu(data):
        print(f"IMU: {data.angular_velocity}")
    
    server.on_imu = on_imu
    await server.start()

asyncio.run(main())
```

### 5. BLE Receiver

```python
import asyncio
from arvos.examples.ble_receiver import main

# Run the BLE receiver example
asyncio.run(main())
```

### 6. MCAP Stream Server

```python
import asyncio
from arvos.servers import MCAPStreamServer

async def main():
    server = MCAPStreamServer(host="0.0.0.0", port=17500, output_file="output.mcap")
    
    def on_imu(data):
        print(f"IMU: {data.angular_velocity}")
    
    server.on_imu = on_imu
    await server.start()

asyncio.run(main())
```

### 7. QUIC/HTTP3 Server

**First, generate TLS certificates:**
```bash
openssl req -x509 -newkey rsa:2048 -keyout /tmp/arvos-quic.key \
    -out /tmp/arvos-quic-cert.pem -days 365 -nodes
```

**Then run the server:**
```python
import asyncio
from arvos.servers import QUICArvosServer

async def main():
    server = QUICArvosServer(
        host="0.0.0.0",
        port=4433,
        certfile="/tmp/arvos-quic-cert.pem",
        keyfile="/tmp/arvos-quic.key"
    )
    
    def on_imu(data):
        print(f"IMU: {data.angular_velocity}")
    
    server.on_imu = on_imu
    await server.start()

asyncio.run(main())
```

**Note:** For local testing, you may need to install the self-signed certificate on your iPhone.

### 8. Save to CSV

```python
python examples/save_to_csv.py
```

### 9. Real-Time 3D Point Cloud (DepthEye Style!)

**High-quality 3D LiDAR visualization with heatmap coloring:**

```bash
python examples/deptheye_style_viewer.py
```

Professional point cloud viewer with:
- Depth-based heatmap coloring (blue=close, red=far)
- Smooth 60 FPS rendering
- Interactive camera controls
- Industrial aesthetic like DepthEye app

### 10. Live Visualization

```python
python examples/live_visualization.py
```

### 11. Apple Watch Sensor Viewer

**Stream wearable sensor data from Apple Watch:**

```bash
python examples/watch_sensor_viewer.py
```

Live viewer for Apple Watch sensors:
- 50-100 Hz IMU (accelerometer + gyroscope + gravity)
- Attitude (quaternion + Euler angles)
- Motion activity classification (walking, running, cycling, vehicle, stationary)
- Real-time statistics and visualization

### 12. ROS 2 Bridge

```bash
python examples/ros2_bridge.py
```

## API Reference

### ArvosServer (WebSocket)

Main server class for receiving connections from Arvos app.

```python
from arvos import ArvosServer

server = ArvosServer(host="0.0.0.0", port=9090)
```

**Methods:**
- `start()` - Start the WebSocket server
- `print_qr_code()` - Display QR code for easy connection
- `get_websocket_url()` - Get connection URL
- `broadcast(message)` - Send message to all clients
- `get_client_count()` - Get number of connected clients

**Callbacks:**
- `on_connect(client_id)` - Client connected
- `on_disconnect(client_id)` - Client disconnected
- `on_handshake(handshake)` - Device info received
- `on_imu(data)` - IMU data received
- `on_gps(data)` - GPS data received
- `on_pose(data)` - Pose data received
- `on_camera(frame)` - Camera frame received
- `on_depth(frame)` - Depth frame received
- `on_status(status)` - Status message received
- `on_error(error, details)` - Error message received
- `on_watch_imu(data)` - Apple Watch IMU data received
- `on_watch_attitude(data)` - Apple Watch attitude data received
- `on_watch_activity(data)` - Apple Watch motion activity received

### Protocol-Specific Servers

All protocol servers inherit from `BaseArvosServer` and share the same callback interface:

```python
from arvos.servers import (
    GRPCArvosServer,
    MQTTArvosServer,
    HTTPArvosServer,
    MCAPStreamServer,
    QUICArvosServer  # Requires aioquic
)

# All servers have the same callback interface
server = GRPCArvosServer(port=50051)
server.on_imu = lambda data: print(f"IMU: {data}")
await server.start()
```

### ArvosClient

Client class for connecting to existing Arvos server (for multi-computer setups).

```python
from arvos import ArvosClient

client = ArvosClient()
await client.connect("ws://192.168.1.100:9090")
await client.run()
```

### Data Types

#### IMUData
```python
@dataclass
class IMUData:
    timestamp_ns: int
    angular_velocity: Tuple[float, float, float]  # rad/s (x, y, z)
    linear_acceleration: Tuple[float, float, float]  # m/s² (x, y, z)
    magnetic_field: Optional[Tuple[float, float, float]]  # μT (x, y, z)
    attitude: Optional[Tuple[float, float, float]]  # roll, pitch, yaw (rad)

    # Properties
    timestamp_s: float  # Timestamp in seconds
    angular_velocity_array: np.ndarray
    linear_acceleration_array: np.ndarray
```

#### GPSData
```python
@dataclass
class GPSData:
    timestamp_ns: int
    latitude: float  # degrees
    longitude: float  # degrees
    altitude: float  # meters
    horizontal_accuracy: float  # meters
    vertical_accuracy: float  # meters
    speed: float  # m/s
    course: float  # degrees

    # Properties
    timestamp_s: float
    coordinates: Tuple[float, float]  # (lat, lon)
```

#### PoseData
```python
@dataclass
class PoseData:
    timestamp_ns: int
    position: Tuple[float, float, float]  # meters (x, y, z)
    orientation: Tuple[float, float, float, float]  # quaternion (x, y, z, w)
    tracking_state: str  # "normal", "limited_*", "not_available"

    # Properties
    timestamp_s: float
    position_array: np.ndarray
    orientation_array: np.ndarray

    # Methods
    is_tracking_good() -> bool
```

#### CameraFrame
```python
@dataclass
class CameraFrame:
    timestamp_ns: int
    width: int
    height: int
    format: str  # "jpeg", "h264"
    data: bytes  # compressed image data
    intrinsics: Optional[CameraIntrinsics]

    # Properties
    timestamp_s: float
    size_kb: float

    # Methods
    to_numpy() -> Optional[np.ndarray]  # Decode to RGB array
```

#### DepthFrame
```python
@dataclass
class DepthFrame:
    timestamp_ns: int
    point_count: int
    min_depth: float  # meters
    max_depth: float  # meters
    format: str  # "raw_depth", "point_cloud"
    data: bytes  # PLY or raw depth data

    # Properties
    timestamp_s: float
    size_kb: float

    # Methods
    to_point_cloud() -> Optional[np.ndarray]  # Parse PLY to (N, 6) array
```

#### WatchIMUData
```python
@dataclass
class WatchIMUData:
    timestamp_ns: int
    angular_velocity: Tuple[float, float, float]  # rad/s (x, y, z)
    linear_acceleration: Tuple[float, float, float]  # m/s² (x, y, z)
    gravity: Tuple[float, float, float]  # m/s² (x, y, z)

    # Properties
    timestamp_s: float
    angular_velocity_array: np.ndarray
    linear_acceleration_array: np.ndarray
    gravity_array: np.ndarray
```

#### WatchAttitudeData
```python
@dataclass
class WatchAttitudeData:
    timestamp_ns: int
    quaternion: Tuple[float, float, float, float]  # x, y, z, w
    pitch: float  # radians
    roll: float   # radians
    yaw: float    # radians
    reference_frame: str

    # Properties
    timestamp_s: float
    quaternion_array: np.ndarray
```

#### WatchMotionActivityData
```python
@dataclass
class WatchMotionActivityData:
    timestamp_ns: int
    state: str  # "walking", "running", "cycling", "vehicle", "stationary", "unknown"
    confidence: float  # 0.0 - 1.0

    # Properties
    timestamp_s: float
```

## Examples

### Live Visualization with Rerun

```bash
pip install rerun-sdk pillow
python examples/rerun_visualizer.py --port 9090
```

This launches the bundled `ArvosServer`, connects to a [Rerun](https://rerun.io/) viewer (spawning one locally by default), and logs every stream the SDK exposes—handshake metadata, IMU, GPS, pose, camera, depth, and Apple Watch sensors.

**Important Notes:**

- **Version Compatibility:** The script automatically checks that your Rerun SDK and CLI versions match. Version mismatches cause critical errors like "Bad chunk schema: Missing row_id column" and data corruption. If versions don't match, the script will exit with fix instructions. To override (not recommended), use `--ignore-version-mismatch`.

- **Troubleshooting:**
  - **Version Mismatch:** Ensure SDK and CLI versions match: `pip show rerun-sdk` and `rerun --version` should show the same version
  - **Port Conflicts:** If port 9090 is in use, use `--port` to specify a different port
  - **Viewer Not Opening:** The script auto-spawns the viewer by default. If it doesn't open, start manually with `rerun` in another terminal
  - **Connection Errors:** Make sure both SDK and viewer are updated: `pip install --upgrade rerun-sdk`

### Save Camera Frames

```python
async def on_camera(frame: CameraFrame):
    # Decode JPEG to numpy array
    img = frame.to_numpy()

    # Save as image
    from PIL import Image
    image = Image.fromarray(img)
    image.save(f"frame_{frame.timestamp_ns}.jpg")
```

### Process Point Clouds

```python
async def on_depth(frame: DepthFrame):
    # Parse PLY point cloud
    points = frame.to_point_cloud()  # (N, 6) array: [x, y, z, r, g, b]

    if points is not None:
        xyz = points[:, :3]  # 3D positions
        rgb = points[:, 3:]  # RGB colors

        print(f"Received {len(points)} points")
```

### IMU Data Analysis

```python
async def on_imu(data: IMUData):
    # Access as numpy arrays
    accel = data.linear_acceleration_array
    gyro = data.angular_velocity_array

    # Calculate magnitude
    accel_mag = np.linalg.norm(accel)

    print(f"Acceleration magnitude: {accel_mag:.2f} m/s²")
```

### GPS Tracking

```python
async def on_gps(data: GPSData):
    lat, lon = data.coordinates

    print(f"Position: {lat:.6f}, {lon:.6f}")
    print(f"Altitude: {data.altitude:.1f}m")
    print(f"Accuracy: ±{data.horizontal_accuracy:.1f}m")
```

### Apple Watch Sensors

```python
from arvos import ArvosServer
from arvos.data_types import WatchIMUData, WatchAttitudeData, WatchMotionActivityData

server = ArvosServer(port=9090)

# Watch IMU data (50-100 Hz)
async def on_watch_imu(data: WatchIMUData):
    accel = data.linear_acceleration_array
    gyro = data.angular_velocity_array

    print(f"Watch IMU: accel={accel}, gyro={gyro}")

# Watch attitude/pose
async def on_watch_attitude(data: WatchAttitudeData):
    import math
    pitch_deg = math.degrees(data.pitch)
    roll_deg = math.degrees(data.roll)
    yaw_deg = math.degrees(data.yaw)

    print(f"Watch Attitude: pitch={pitch_deg:.1f}°, roll={roll_deg:.1f}°, yaw={yaw_deg:.1f}°")

# Watch motion activity classification
async def on_watch_activity(data: WatchMotionActivityData):
    print(f"Activity: {data.state} (confidence: {data.confidence:.1%})")

server.on_watch_imu = on_watch_imu
server.on_watch_attitude = on_watch_attitude
server.on_watch_activity = on_watch_activity

await server.start()
```

## Advanced Usage

### Custom Message Handler

```python
server = ArvosServer(port=9090)

async def on_message(client_id: str, message):
    """Handle raw messages"""
    if isinstance(message, str):
        print(f"JSON from {client_id}: {message}")
    else:
        print(f"Binary from {client_id}: {len(message)} bytes")

server.on_message = on_message
```

### Multi-Client Support

```python
server = ArvosServer(port=9090)

# Track multiple iPhones
clients = {}

async def on_connect(client_id: str):
    clients[client_id] = {
        "imu_count": 0,
        "gps_count": 0
    }

async def on_disconnect(client_id: str):
    stats = clients.pop(client_id)
    print(f"Client {client_id} stats: {stats}")

server.on_connect = on_connect
server.on_disconnect = on_disconnect
```

### Send Commands to iPhone

```python
async def send_command_example():
    client = ArvosClient()
    await client.connect("ws://192.168.1.100:9090")

    # Send start recording command
    await client.send_command("start_recording")

    # Send stop recording command
    await client.send_command("stop_recording")

    # Change mode
    await client.send_command("change_mode", mode="Mapping")
```

## ROS 2 Integration

The ROS 2 bridge publishes standard ROS messages:

**Topics:**
- `/arvos/imu` - `sensor_msgs/Imu`
- `/arvos/gps` - `sensor_msgs/NavSatFix`
- `/arvos/camera/image_raw` - `sensor_msgs/Image`
- `/arvos/camera/info` - `sensor_msgs/CameraInfo`
- `/arvos/depth/points` - `sensor_msgs/PointCloud2`
- `/arvos/tf` - `tf2_msgs/TFMessage`

**Usage:**
```bash
# Terminal 1: Start bridge
python examples/ros2_bridge.py

# Terminal 2: View topics
ros2 topic list
ros2 topic echo /arvos/imu

# Terminal 3: Visualize in RViz
rviz2
```

## Protocol Specification

### WebSocket URL
```
ws://<host>:<port>
```

### Message Format

**JSON Messages** (IMU, GPS, Pose):
```json
{
  "type": "imu",
  "timestampNs": 1700000000000,
  "angularVelocity": [0.01, -0.02, 0.005],
  "linearAcceleration": [0.1, 0.0, -0.01]
}
```

**Binary Messages** (Camera, Depth):
```
[Header Size (4 bytes, little-endian)]
[JSON Header]
[Binary Data]
```

Header example:
```json
{
  "type": "camera",
  "timestampNs": 1700000000000,
  "width": 1920,
  "height": 1080,
  "format": "jpeg",
  "compressedSize": 12345
}
```

## Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=arvos tests/
```

## Troubleshooting

### Connection Issues

**Problem**: Can't connect from iPhone
- Ensure both devices on same Wi-Fi network
- Check firewall settings (allow the protocol's port)
- Try: `nc -l <port>` to test port connectivity
- Verify the correct protocol is selected in the iOS app

**Problem**: QR code not scanning
- Increase terminal font size
- Use manual IP entry instead
- Check QR code contains correct IP and port

**Problem**: Protocol-specific connection failures

**gRPC:**
- Ensure iOS 18+ is installed
- Check that port 50051 is not blocked
- Verify protobuf code is generated correctly

**MQTT:**
- Ensure Mosquitto broker is running: `mosquitto -c mosquitto.conf`
- Check broker is listening on all interfaces (not just localhost)
- Verify broker port (default 1883) is accessible

**HTTP/REST:**
- Use the Mac's actual LAN IP (not 0.0.0.0)
- Check App Transport Security settings in iOS app
- Verify firewall allows port 8080

**Bluetooth LE:**
- Ensure Bluetooth is enabled on both devices
- Check that the iOS app is advertising (BLE toggle enabled)
- Verify Python script can access Bluetooth (may need permissions)

**QUIC/HTTP3:**
- Generate and install TLS certificates
- Ensure aioquic is installed: `pip install aioquic`
- For local testing, install self-signed certificate on iPhone
- Verify port 4433 is not blocked

### Performance Issues

**Problem**: High latency or dropped frames
- Reduce sensor rates in iPhone app settings
- Check Wi-Fi signal strength
- Use wired connection for computer
- Try QUIC/HTTP3 for better performance on unstable networks
- Use gRPC for high-performance scenarios

**Problem**: High CPU usage
- Process frames asynchronously
- Downsample point clouds
- Skip processing some frames
- Use HTTP/REST for simple telemetry (not video)

**Problem**: Low bandwidth (BLE)
- BLE is designed for telemetry only
- Camera/depth frames are automatically dropped
- Use Wi-Fi protocols for high-bandwidth data

### Protocol Selection Guide

**When to use WebSocket:**
- General purpose, default choice
- Works everywhere
- Good balance of features and compatibility

**When to use gRPC:**
- Research applications requiring high performance
- Need Protocol Buffers efficiency
- iOS 18+ available

**When to use MQTT:**
- Multiple subscribers needed
- IoT deployments
- Broker-based architecture preferred

**When to use HTTP/REST:**
- Simple webhook integrations
- REST API compatibility needed
- Easy debugging with standard HTTP tools

**When to use Bluetooth LE:**
- No Wi-Fi available
- Low power requirements
- Telemetry-only use cases

**When to use MCAP Stream:**
- Robotics research
- Foxglove Studio integration
- Standardized data format needed

**When to use QUIC/HTTP3:**
- Ultra-low latency requirements
- Unstable network conditions
- Mobile network scenarios

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Dependencies

### Core Dependencies
- `websockets>=11.0` - WebSocket support
- `qrcode[pil]>=7.4` - QR code generation
- `numpy>=1.20.0` - Numerical operations

### Protocol-Specific Dependencies
- `grpcio>=1.50.0` - gRPC support
- `grpcio-tools>=1.50.0` - gRPC code generation
- `protobuf>=4.21.0` - Protocol Buffers
- `paho-mqtt>=1.6.0` - MQTT client
- `bleak>=0.20.0` - Bluetooth LE support
- `mcap>=0.1.0` - MCAP format support
- `aioquic>=0.9.0` - QUIC/HTTP3 support

### Optional Dependencies
- `matplotlib>=3.5.0` - Visualization
- `Pillow>=9.0.0` - Image processing
- `opencv-python>=4.5.0` - Computer vision
- `rclpy` - ROS 2 integration
- `cv_bridge` - ROS 2 image bridge

## License

MIT License - See LICENSE file for details

## Related Projects

- **Arvos iOS App**: https://github.com/jaskirat1616/Arvos
- **MCAP Tools**: https://mcap.dev
- **ROS 2**: https://docs.ros.org

## Support

- GitHub Issues: https://github.com/jaskirat1616/arvos-sdk/issues
- Documentation: https://github.com/jaskirat1616/arvos-sdk/docs

## Quick Reference

### Protocol Comparison

| Feature | WebSocket | gRPC | MQTT | HTTP | BLE | MCAP | QUIC |
|--------|-----------|------|------|------|-----|------|------|
| **Latency** | Low | Very Low | Medium | Medium | Low | Low | Very Low |
| **Throughput** | High | Very High | Medium | Medium | Low | High | Very Low |
| **Bidirectional** | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Multi-client** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **iOS Version** | 16+ | 18+ | 16+ | 16+ | 16+ | 16+ | 15+ |
| **Setup Complexity** | Low | Medium | Medium | Low | Low | Low | High |
| **Best For** | General | Research | IoT | Webhooks | Cable-free | Robotics | Mobile |

### Example Commands

```bash
# WebSocket (default)
python examples/basic_server.py

# gRPC
python examples/grpc_stream_server.py

# MQTT (requires broker)
mosquitto -c mosquitto.conf &
python examples/mqtt_stream_server.py

# HTTP
python examples/http_stream_server.py

# BLE
python examples/ble_receiver.py

# MCAP
python examples/mcap_stream_server.py

# QUIC/HTTP3
python examples/quic_stream_server.py
```

---

**Arvos SDK** - Turn your iPhone into a sensor robot 🤖📱
