"""
Base server class for all ARVOS protocol servers
"""

import asyncio
import socket
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any
from ..client import ArvosClient
from ..data_types import (
    IMUData, GPSData, PoseData, CameraFrame, DepthFrame,
    HandshakeMessage, WatchIMUData, WatchAttitudeData, WatchMotionActivityData
)


class BaseArvosServer(ABC):
    """
    Abstract base class for all ARVOS protocol servers.
    
    All protocol servers should inherit from this class and implement:
    - start() - Start the server
    - stop() - Stop the server
    - get_connection_url() - Return connection URL for clients
    - get_protocol_name() - Return protocol name
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 9090):
        self.host = host
        self.port = port
        self.running = False
        self.connected_clients = 0
        
        # Statistics
        self.messages_received = 0
        self.bytes_received = 0
        
        # Callbacks - users can assign these
        self.on_connect: Optional[Callable[[str], None]] = None
        self.on_disconnect: Optional[Callable[[str], None]] = None
        self.on_handshake: Optional[Callable[[HandshakeMessage], None]] = None
        self.on_imu: Optional[Callable[[IMUData], None]] = None
        self.on_gps: Optional[Callable[[GPSData], None]] = None
        self.on_pose: Optional[Callable[[PoseData], None]] = None
        self.on_camera: Optional[Callable[[CameraFrame], None]] = None
        self.on_depth: Optional[Callable[[DepthFrame], None]] = None
        self.on_status: Optional[Callable[[dict], None]] = None
        self.on_error: Optional[Callable[[str, Optional[str], Optional[str]], None]] = None
        
        # Apple Watch callbacks
        self.on_watch_imu: Optional[Callable[[WatchIMUData], None]] = None
        self.on_watch_attitude: Optional[Callable[[WatchAttitudeData], None]] = None
        self.on_watch_activity: Optional[Callable[[WatchMotionActivityData], None]] = None
        
        # Use ArvosClient for message parsing
        self._parser = ArvosClient()
        self._configure_parser_callbacks()
    
    def _configure_parser_callbacks(self):
        """Configure ArvosClient parser to dispatch to our callbacks"""
        # Direct assignment - ArvosClient handles sync/async internally
        self._parser.on_handshake = self.on_handshake
        self._parser.on_imu = self.on_imu
        self._parser.on_gps = self.on_gps
        self._parser.on_pose = self.on_pose
        self._parser.on_camera = self.on_camera
        self._parser.on_depth = self.on_depth
        self._parser.on_status = self.on_status
        self._parser.on_error = self.on_error
        self._parser.on_watch_imu = self.on_watch_imu
        self._parser.on_watch_attitude = self.on_watch_attitude
        self._parser.on_watch_activity = self.on_watch_activity
    
    async def _invoke_callback(self, callback: Optional[Callable], *args, **kwargs):
        """Invoke a callback, handling both sync and async"""
        if callback is None:
            return
        
        if asyncio.iscoroutinefunction(callback):
            await callback(*args, **kwargs)
        else:
            callback(*args, **kwargs)
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def print_connection_info(self):
        """Print connection information for users"""
        ip = self.get_local_ip()
        url = self.get_connection_url()
        print("\n" + "=" * 60)
        print(f"ARVOS {self.get_protocol_name()} Server")
        print("=" * 60)
        print(f"📡 Server: {self.host}:{self.port}")
        print(f"🌐 Local IP: {ip}")
        print(f"📱 Connection URL: {url}")
        print("=" * 60 + "\n")
    
    @abstractmethod
    async def start(self):
        """Start the server"""
        pass
    
    @abstractmethod
    async def stop(self):
        """Stop the server"""
        pass
    
    @abstractmethod
    def get_connection_url(self) -> str:
        """Get connection URL for clients"""
        pass
    
    @abstractmethod
    def get_protocol_name(self) -> str:
        """Get protocol name"""
        pass

