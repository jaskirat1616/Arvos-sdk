"""
Base server class for all protocol implementations
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, Dict, Any
import socket
import asyncio


class BaseArvosServer(ABC):
    """
    Abstract base class for all Arvos protocol servers.
    
    All protocol implementations (WebSocket, gRPC, MQTT, etc.) should inherit
    from this class and implement the abstract methods.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 9090):
        """
        Initialize base server.
        
        Args:
            host: Host address to bind to (default: 0.0.0.0 for all interfaces)
            port: Port number to listen on (default: 9090)
        """
        self.host = host
        self.port = port
        self.running = False
        
        # Statistics
        self.bytes_received: int = 0
        self.messages_received: int = 0
        self.connected_clients: int = 0
        
        # Common callbacks - users can assign these
        self.on_connect: Optional[Callable[[str], Any]] = None
        self.on_disconnect: Optional[Callable[[str], Any]] = None
        self.on_message: Optional[Callable[[str, Any], Any]] = None
        
        # Sensor data callbacks
        self.on_handshake: Optional[Callable] = None
        self.on_imu: Optional[Callable] = None
        self.on_gps: Optional[Callable] = None
        self.on_pose: Optional[Callable] = None
        self.on_camera: Optional[Callable] = None
        self.on_depth: Optional[Callable] = None
        self.on_status: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Apple Watch callbacks
        self.on_watch_imu: Optional[Callable] = None
        self.on_watch_attitude: Optional[Callable] = None
        self.on_watch_activity: Optional[Callable] = None
    
    @abstractmethod
    async def start(self):
        """
        Start the server and begin listening for connections.
        
        This method should be implemented by each protocol adapter.
        It should run indefinitely until stop() is called.
        """
        pass
    
    @abstractmethod
    async def stop(self):
        """
        Stop the server and close all connections.
        
        This method should be implemented by each protocol adapter.
        """
        pass
    
    @abstractmethod
    def get_connection_url(self) -> str:
        """
        Get the connection URL/address for this server.
        
        Returns:
            Connection string (e.g., "ws://192.168.1.100:9090", "grpc://localhost:50051")
        """
        pass
    
    @abstractmethod
    def get_protocol_name(self) -> str:
        """
        Get the protocol name for display/logging.
        
        Returns:
            Protocol name (e.g., "WebSocket", "gRPC", "MQTT")
        """
        pass
    
    # Helper methods
    
    def get_local_ip(self) -> str:
        """
        Get the local IP address of this machine.
        
        Returns:
            Local IP address as string
        """
        try:
            # Create a socket to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get server statistics.
        
        Returns:
            Dictionary containing statistics
        """
        return {
            "protocol": self.get_protocol_name(),
            "running": self.running,
            "bytes_received": self.bytes_received,
            "messages_received": self.messages_received,
            "connected_clients": self.connected_clients,
            "host": self.host,
            "port": self.port,
        }
    
    def reset_statistics(self):
        """Reset all statistics counters."""
        self.bytes_received = 0
        self.messages_received = 0
    
    async def _invoke_callback(self, callback: Optional[Callable], *args, **kwargs):
        """
        Safely invoke a callback, handling both sync and async functions.
        
        Args:
            callback: The callback function to invoke
            *args: Positional arguments to pass to callback
            **kwargs: Keyword arguments to pass to callback
        """
        if callback is None:
            return
        
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args, **kwargs)
            else:
                callback(*args, **kwargs)
        except Exception as e:
            print(f"Error in callback {callback.__name__}: {e}")
    
    def print_connection_info(self):
        """Print connection information to console."""
        print("\n" + "=" * 50)
        print(f"ARVOS {self.get_protocol_name()} Server")
        print("=" * 50)
        print(f"Connection URL: {self.get_connection_url()}")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print("=" * 50 + "\n")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} protocol={self.get_protocol_name()} host={self.host} port={self.port}>"

