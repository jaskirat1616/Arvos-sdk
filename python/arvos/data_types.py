"""
Data types for Arvos sensor data
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple
import numpy as np


@dataclass
class IMUData:
    """IMU (accelerometer + gyroscope) data"""
    timestamp_ns: int
    angular_velocity: Tuple[float, float, float]  # rad/s (x, y, z)
    linear_acceleration: Tuple[float, float, float]  # m/s² (x, y, z)
    magnetic_field: Optional[Tuple[float, float, float]] = None  # μT (x, y, z)
    attitude: Optional[Tuple[float, float, float]] = None  # roll, pitch, yaw (rad)

    @property
    def timestamp_s(self) -> float:
        """Timestamp in seconds"""
        return self.timestamp_ns / 1e9

    @property
    def angular_velocity_array(self) -> np.ndarray:
        """Angular velocity as numpy array"""
        return np.array(self.angular_velocity)

    @property
    def linear_acceleration_array(self) -> np.ndarray:
        """Linear acceleration as numpy array"""
        return np.array(self.linear_acceleration)


@dataclass
class GPSData:
    """GPS location data"""
    timestamp_ns: int
    latitude: float  # degrees
    longitude: float  # degrees
    altitude: float  # meters
    horizontal_accuracy: float  # meters
    vertical_accuracy: float  # meters
    speed: float  # m/s
    course: float  # degrees

    @property
    def timestamp_s(self) -> float:
        """Timestamp in seconds"""
        return self.timestamp_ns / 1e9

    @property
    def coordinates(self) -> Tuple[float, float]:
        """Lat/lon tuple"""
        return (self.latitude, self.longitude)


@dataclass
class PoseData:
    """6DOF camera pose from ARKit"""
    timestamp_ns: int
    position: Tuple[float, float, float]  # meters (x, y, z)
    orientation: Tuple[float, float, float, float]  # quaternion (x, y, z, w)
    tracking_state: str  # "normal", "limited_*", "not_available"

    @property
    def timestamp_s(self) -> float:
        """Timestamp in seconds"""
        return self.timestamp_ns / 1e9

    @property
    def position_array(self) -> np.ndarray:
        """Position as numpy array"""
        return np.array(self.position)

    @property
    def orientation_array(self) -> np.ndarray:
        """Orientation quaternion as numpy array"""
        return np.array(self.orientation)

    def is_tracking_good(self) -> bool:
        """Check if tracking quality is good"""
        return self.tracking_state == "normal"


@dataclass
class CameraIntrinsics:
    """Camera intrinsic parameters"""
    fx: float  # focal length x
    fy: float  # focal length y
    cx: float  # principal point x
    cy: float  # principal point y

    def to_matrix(self) -> np.ndarray:
        """Convert to 3x3 intrinsic matrix"""
        return np.array([
            [self.fx, 0, self.cx],
            [0, self.fy, self.cy],
            [0, 0, 1]
        ])


@dataclass
class CameraFrame:
    """Camera image frame"""
    timestamp_ns: int
    width: int
    height: int
    format: str  # "jpeg", "h264"
    data: bytes  # compressed image data
    intrinsics: Optional[CameraIntrinsics] = None

    @property
    def timestamp_s(self) -> float:
        """Timestamp in seconds"""
        return self.timestamp_ns / 1e9

    @property
    def size_kb(self) -> float:
        """Data size in kilobytes"""
        return len(self.data) / 1024.0

    def to_numpy(self) -> Optional[np.ndarray]:
        """Decode JPEG to numpy array (RGB)"""
        try:
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(self.data))
            return np.array(image)
        except ImportError:
            print("PIL/Pillow not installed. Install with: pip install Pillow")
            return None


@dataclass
class DepthFrame:
    """Depth/point cloud frame"""
    timestamp_ns: int
    point_count: int
    min_depth: float  # meters
    max_depth: float  # meters
    format: str  # "raw_depth", "point_cloud"
    data: bytes  # PLY or raw depth data

    @property
    def timestamp_s(self) -> float:
        """Timestamp in seconds"""
        return self.timestamp_ns / 1e9

    @property
    def size_kb(self) -> float:
        """Data size in kilobytes"""
        return len(self.data) / 1024.0

    def to_point_cloud(self) -> Optional[np.ndarray]:
        """Parse PLY data to point cloud array (N x 3 or N x 6)"""
        try:
            import io

            # Find end_header by scanning bytes (not decoding entire file)
            header_end_bytes = 0
            search_pos = 0
            max_header_size = 1024  # PLY headers are typically small

            while search_pos < min(len(self.data), max_header_size):
                # Look for "end_header\n" in bytes
                if self.data[search_pos:search_pos+11] == b'end_header\n':
                    header_end_bytes = search_pos + 11
                    break
                elif self.data[search_pos:search_pos+12] == b'end_header\r\n':
                    header_end_bytes = search_pos + 12
                    break
                search_pos += 1

            if header_end_bytes == 0:
                print("Could not find 'end_header' in PLY data")
                return None

            # Binary data starts after header
            binary_data = self.data[header_end_bytes:]

            # Parse binary PLY (assuming float xyz + uchar rgb)
            # Format: little-endian float32 x, y, z + uint8 r, g, b
            dtype = np.dtype([
                ('x', '<f4'), ('y', '<f4'), ('z', '<f4'),
                ('r', 'u1'), ('g', 'u1'), ('b', 'u1')
            ])

            points = np.frombuffer(binary_data, dtype=dtype)

            if len(points) == 0:
                return None

            # Return as (N, 6) array [x, y, z, r, g, b]
            xyz = np.stack([points['x'], points['y'], points['z']], axis=1)
            rgb = np.stack([points['r'], points['g'], points['b']], axis=1)

            return np.hstack([xyz, rgb])

        except Exception as e:
            print(f"Failed to parse PLY: {e}")
            import traceback
            traceback.print_exc()
            return None


@dataclass
class DeviceCapabilities:
    """iPhone device capabilities"""
    has_lidar: bool
    has_arkit: bool
    has_gps: bool
    has_imu: bool
    supported_modes: List[str]


@dataclass
class HandshakeMessage:
    """Initial handshake from device"""
    device_name: str
    device_model: str
    os_version: str
    app_version: str
    capabilities: DeviceCapabilities
    timestamp_ns: int

    @property
    def timestamp_s(self) -> float:
        """Timestamp in seconds"""
        return self.timestamp_ns / 1e9
