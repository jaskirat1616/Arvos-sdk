"""
Arvos WebSocket client for receiving sensor data
"""

import asyncio
import websockets
import json
import struct
from typing import Callable, Optional, Dict, Any
from .data_types import (
    IMUData, GPSData, PoseData, CameraFrame, DepthFrame,
    HandshakeMessage, DeviceCapabilities, CameraIntrinsics
)


class ArvosClient:
    """
    Async WebSocket client for receiving data from Arvos iPhone app.

    Example:
        >>> async def on_imu(data: IMUData):
        ...     print(f"IMU: {data.angular_velocity}")
        >>>
        >>> client = ArvosClient()
        >>> client.on_imu = on_imu
        >>> await client.connect("ws://192.168.1.100:9090")
        >>> await client.run()
    """

    def __init__(self):
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.handshake: Optional[HandshakeMessage] = None

        # Callbacks
        self.on_handshake: Optional[Callable[[HandshakeMessage], None]] = None
        self.on_imu: Optional[Callable[[IMUData], None]] = None
        self.on_gps: Optional[Callable[[GPSData], None]] = None
        self.on_pose: Optional[Callable[[PoseData], None]] = None
        self.on_camera: Optional[Callable[[CameraFrame], None]] = None
        self.on_depth: Optional[Callable[[DepthFrame], None]] = None
        self.on_status: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_error: Optional[Callable[[str, Optional[str]], None]] = None
        self.on_disconnect: Optional[Callable[[], None]] = None

        # Statistics
        self.messages_received = 0
        self.bytes_received = 0

    async def connect(self, uri: str, timeout: float = 10.0):
        """Connect to Arvos server"""
        try:
            self.websocket = await asyncio.wait_for(
                websockets.connect(uri),
                timeout=timeout
            )
            self.connected = True
            print(f"Connected to {uri}")
        except asyncio.TimeoutError:
            raise ConnectionError(f"Connection timeout after {timeout}s")
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")

    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            if self.on_disconnect:
                self.on_disconnect()

    async def run(self):
        """Main receive loop - call this after connect()"""
        if not self.websocket:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            async for message in self.websocket:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
            self.connected = False
            if self.on_disconnect:
                self.on_disconnect()
        except Exception as e:
            print(f"Error in receive loop: {e}")
            raise

    async def _handle_message(self, message):
        """Handle incoming message"""
        self.messages_received += 1

        if isinstance(message, str):
            # JSON message
            self.bytes_received += len(message.encode('utf-8'))
            await self._handle_json_message(message)
        elif isinstance(message, bytes):
            # Binary message
            self.bytes_received += len(message)
            await self._handle_binary_message(message)

    async def _handle_json_message(self, message: str):
        """Handle JSON message (IMU, GPS, pose, control)"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "handshake":
                await self._handle_handshake(data)
            elif msg_type == "imu":
                await self._handle_imu(data)
            elif msg_type == "gps":
                await self._handle_gps(data)
            elif msg_type == "pose":
                await self._handle_pose(data)
            elif msg_type == "status":
                if self.on_status:
                    self.on_status(data)
            elif msg_type == "error":
                if self.on_error:
                    self.on_error(data.get("error"), data.get("details"))
            else:
                print(f"Unknown message type: {msg_type}")

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
        except Exception as e:
            print(f"Error handling JSON message: {e}")

    async def _handle_binary_message(self, message: bytes):
        """Handle binary message (camera, depth)"""
        try:
            # Parse binary format: [Header Size (4 bytes)][JSON Header][Binary Data]
            if len(message) < 4:
                print("Binary message too short")
                return

            # Read header size
            header_size = struct.unpack('<I', message[:4])[0]

            if len(message) < 4 + header_size:
                print("Incomplete binary message")
                return

            # Parse header JSON
            header_json = message[4:4+header_size].decode('utf-8')
            header = json.loads(header_json)

            # Extract binary data
            binary_data = message[4+header_size:]

            msg_type = header.get("type")

            if msg_type == "camera":
                await self._handle_camera(header, binary_data)
            elif msg_type == "depth":
                await self._handle_depth(header, binary_data)
            else:
                print(f"Unknown binary message type: {msg_type}")

        except Exception as e:
            print(f"Error handling binary message: {e}")

    async def _handle_handshake(self, data: Dict[str, Any]):
        """Handle handshake message"""
        caps_data = data.get("capabilities", {})
        capabilities = DeviceCapabilities(
            has_lidar=caps_data.get("hasLiDAR", False),
            has_arkit=caps_data.get("hasARKit", False),
            has_gps=caps_data.get("hasGPS", False),
            has_imu=caps_data.get("hasIMU", False),
            supported_modes=caps_data.get("supportedModes", [])
        )

        self.handshake = HandshakeMessage(
            device_name=data.get("deviceName", "Unknown"),
            device_model=data.get("deviceModel", "Unknown"),
            os_version=data.get("osVersion", "Unknown"),
            app_version=data.get("appVersion", "Unknown"),
            capabilities=capabilities,
            timestamp_ns=data.get("timestampNs", 0)
        )

        print(f"Handshake received: {self.handshake.device_name} ({self.handshake.device_model})")
        print(f"  LiDAR: {capabilities.has_lidar}, ARKit: {capabilities.has_arkit}")

        if self.on_handshake:
            self.on_handshake(self.handshake)

    async def _handle_imu(self, data: Dict[str, Any]):
        """Handle IMU data"""
        imu_data = IMUData(
            timestamp_ns=data.get("timestampNs", 0),
            angular_velocity=tuple(data.get("angularVelocity", [0, 0, 0])),
            linear_acceleration=tuple(data.get("linearAcceleration", [0, 0, 0])),
            magnetic_field=tuple(data["magneticField"]) if "magneticField" in data else None,
            attitude=tuple([
                data["attitude"]["roll"],
                data["attitude"]["pitch"],
                data["attitude"]["yaw"]
            ]) if "attitude" in data else None
        )

        if self.on_imu:
            await self.on_imu(imu_data)

    async def _handle_gps(self, data: Dict[str, Any]):
        """Handle GPS data"""
        gps_data = GPSData(
            timestamp_ns=data.get("timestampNs", 0),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            altitude=data.get("altitude", 0.0),
            horizontal_accuracy=data.get("horizontalAccuracy", 0.0),
            vertical_accuracy=data.get("verticalAccuracy", 0.0),
            speed=data.get("speed", 0.0),
            course=data.get("course", 0.0)
        )

        if self.on_gps:
            await self.on_gps(gps_data)

    async def _handle_pose(self, data: Dict[str, Any]):
        """Handle pose data"""
        pose_data = PoseData(
            timestamp_ns=data.get("timestampNs", 0),
            position=tuple(data.get("position", [0, 0, 0])),
            orientation=tuple(data.get("orientation", [0, 0, 0, 1])),
            tracking_state=data.get("trackingState", "unknown")
        )

        if self.on_pose:
            await self.on_pose(pose_data)

    async def _handle_camera(self, metadata: Dict[str, Any], data: bytes):
        """Handle camera frame"""
        intrinsics = None
        if "intrinsics" in metadata:
            intr = metadata["intrinsics"]
            intrinsics = CameraIntrinsics(
                fx=intr.get("fx", 0.0),
                fy=intr.get("fy", 0.0),
                cx=intr.get("cx", 0.0),
                cy=intr.get("cy", 0.0)
            )

        camera_frame = CameraFrame(
            timestamp_ns=metadata.get("timestampNs", 0),
            width=metadata.get("width", 0),
            height=metadata.get("height", 0),
            format=metadata.get("format", "jpeg"),
            data=data,
            intrinsics=intrinsics
        )

        if self.on_camera:
            await self.on_camera(camera_frame)

    async def _handle_depth(self, metadata: Dict[str, Any], data: bytes):
        """Handle depth frame"""
        depth_frame = DepthFrame(
            timestamp_ns=metadata.get("timestampNs", 0),
            point_count=metadata.get("pointCount", 0),
            min_depth=metadata.get("minDepth", 0.0),
            max_depth=metadata.get("maxDepth", 0.0),
            format=metadata.get("format", "point_cloud"),
            data=data
        )

        if self.on_depth:
            await self.on_depth(depth_frame)

    async def send_command(self, command: str, **kwargs):
        """Send command to iPhone app"""
        if not self.websocket:
            raise RuntimeError("Not connected")

        message = {
            "type": "command",
            "command": command,
            **kwargs
        }

        await self.websocket.send(json.dumps(message))

    def get_statistics(self) -> Dict[str, Any]:
        """Get receive statistics"""
        return {
            "connected": self.connected,
            "messages_received": self.messages_received,
            "bytes_received": self.bytes_received,
            "megabytes_received": self.bytes_received / (1024 * 1024)
        }
