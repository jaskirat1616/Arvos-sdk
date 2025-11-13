# Data Types

Complete reference for all ARVOS sensor data types.

## IMUData

IMU sensor data (accelerometer, gyroscope, gravity).

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

### Example

```python
async def on_imu(data: IMUData):
    print(f"Timestamp: {data.timestamp_s}s")
    print(f"Angular velocity: {data.angular_velocity}")
    print(f"Acceleration: {data.linear_acceleration}")
    
    # Access as numpy arrays
    accel = data.linear_acceleration_array
    gyro = data.angular_velocity_array
```

## GPSData

GPS location data.

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

### Example

```python
async def on_gps(data: GPSData):
    lat, lon = data.coordinates
    print(f"Position: {lat:.6f}, {lon:.6f}")
    print(f"Altitude: {data.altitude:.1f}m")
    print(f"Accuracy: ±{data.horizontal_accuracy:.1f}m")
```

## PoseData

ARKit 6DOF camera pose.

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

### Example

```python
async def on_pose(data: PoseData):
    print(f"Position: {data.position}")
    print(f"Orientation: {data.orientation}")
    print(f"Tracking: {data.tracking_state}")
    
    if data.is_tracking_good():
        # Process pose data
        pass
```

## CameraFrame

Camera frame data.

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

### Example

```python
async def on_camera(frame: CameraFrame):
    print(f"Frame: {frame.width}x{frame.height}")
    print(f"Size: {frame.size_kb:.1f} KB")
    
    # Decode to numpy array
    img = frame.to_numpy()
    if img is not None:
        # Process image
        pass
```

## DepthFrame

Depth/LiDAR frame data.

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

### Example

```python
async def on_depth(frame: DepthFrame):
    print(f"Points: {frame.point_count}")
    print(f"Depth range: {frame.min_depth:.2f} - {frame.max_depth:.2f}m")
    
    # Parse point cloud
    points = frame.to_point_cloud()
    if points is not None:
        xyz = points[:, :3]  # 3D positions
        rgb = points[:, 3:]  # RGB colors
```

## WatchIMUData

Apple Watch IMU data.

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

## WatchAttitudeData

Apple Watch attitude data.

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

## WatchMotionActivityData

Apple Watch motion activity.

```python
@dataclass
class WatchMotionActivityData:
    timestamp_ns: int
    state: str  # "walking", "running", "cycling", "vehicle", "stationary", "unknown"
    confidence: float  # 0.0 - 1.0
    
    # Properties
    timestamp_s: float
```

## HandshakeMessage

Device information and capabilities.

```python
@dataclass
class HandshakeMessage:
    device_name: str
    device_model: str
    os_version: str
    app_version: str
    capabilities: DeviceCapabilities
```

## DeviceCapabilities

Device sensor capabilities.

```python
@dataclass
class DeviceCapabilities:
    has_lidar: bool
    has_arkit: bool
    has_gps: bool
    has_imu: bool
    has_watch: bool
    supported_modes: List[str]
```

## Next Steps

- [Python SDK API](python-sdk.md) - Complete API reference
- [Examples](../examples/overview.md) - Usage examples

