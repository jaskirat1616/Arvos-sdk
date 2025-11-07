# Arvos SDK

Python SDK for receiving real-time sensor data from the Arvos iPhone app.

## Overview

Arvos SDK provides Python clients and servers to receive iPhone sensor data over WebSocket, including:
- **Camera**: RGB video (JPEG compressed)
- **LiDAR/Depth**: 3D point clouds
- **IMU**: Accelerometer + gyroscope
- **ARKit Pose**: 6DOF camera tracking
- **GPS**: Location data

## Installation

### Basic Installation
```bash
pip install -r requirements.txt
```

### From Source
```bash
git clone https://github.com/jaskirat1616/arvos-sdk.git
cd arvos-sdk
pip install -e .
```

### With Optional Dependencies
```bash
# For visualization examples
pip install -e ".[visualization]"

# For image processing
pip install -e ".[image]"

# For development
pip install -e ".[dev]"
```

## Quick Start

### 1. Basic Server

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

### 2. Save to CSV

```python
python examples/save_to_csv.py
```

### 3. Live Visualization

```python
python examples/live_visualization.py
```

### 4. ROS 2 Bridge

```bash
python examples/ros2_bridge.py
```

## API Reference

### ArvosServer

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

## Examples

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
- Check firewall settings (allow port 9090)
- Try: `nc -l 9090` to test port

**Problem**: QR code not scanning
- Increase terminal font size
- Use manual IP entry instead
- Check QR code contains correct IP

### Performance Issues

**Problem**: High latency or dropped frames
- Reduce sensor rates in iPhone app settings
- Check Wi-Fi signal strength
- Use wired connection for computer

**Problem**: High CPU usage
- Process frames asynchronously
- Downsample point clouds
- Skip processing some frames

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

[Add your license here]

## Related Projects

- **Arvos iOS App**: https://github.com/jaskirat1616/Arvos
- **MCAP Tools**: https://mcap.dev
- **ROS 2**: https://docs.ros.org

## Support

- GitHub Issues: https://github.com/jaskirat1616/arvos-sdk/issues
- Documentation: https://github.com/jaskirat1616/arvos-sdk/docs

---

**Arvos SDK** - Turn your iPhone into a sensor robot 🤖📱
