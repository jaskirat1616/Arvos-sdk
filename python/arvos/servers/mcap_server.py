"""
MCAP Stream server for receiving sensor data from ARVOS iOS app
"""

import asyncio
import json
import logging
import sys
import time
import websockets
from pathlib import Path
from datetime import datetime
from typing import Optional

# Configure websockets loggers to suppress expected handshake errors
# These errors occur when non-WebSocket HTTP requests (like POST) hit the server
for logger_name in ["websockets.server", "websockets.protocol", "websockets.http11"]:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.CRITICAL)  # Only show critical errors
    # Add a filter to suppress InvalidMessage and ValueError for non-WebSocket requests
    class HandshakeErrorFilter(logging.Filter):
        def filter(self, record):
            msg = str(record.getMessage())
            # Suppress expected errors from non-WebSocket HTTP requests
            if any(phrase in msg for phrase in [
                "unsupported HTTP method",
                "did not receive a valid HTTP request",
                "opening handshake failed"
            ]):
                return False
            return True
    logger.addFilter(HandshakeErrorFilter())

# Store original excepthook to filter websocket handshake errors
_original_excepthook = sys.excepthook

def _filter_websocket_exceptions(exc_type, exc_value, exc_traceback):
    """Filter out expected websocket handshake errors from tracebacks"""
    if exc_type in (websockets.exceptions.InvalidMessage, ValueError):
        error_msg = str(exc_value)
        if any(phrase in error_msg for phrase in [
            "unsupported HTTP method",
            "did not receive a valid HTTP request",
            "opening handshake failed"
        ]):
            # Suppress these expected errors - they occur when non-WebSocket HTTP requests hit the server
            return
    # For all other exceptions, use the original handler
    _original_excepthook(exc_type, exc_value, exc_traceback)

# Install the filtered excepthook
sys.excepthook = _filter_websocket_exceptions

try:
    from mcap.writer import Writer
    MCAP_AVAILABLE = True
except ImportError:
    MCAP_AVAILABLE = False
    Writer = None

from .base_server import BaseArvosServer
from ..client import ArvosClient


class MCAPStreamServer(BaseArvosServer):
    """MCAP Stream server - receives data and writes to MCAP file"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 17500, 
                 output_file: Optional[str] = None):
        super().__init__(host, port)
        self.output_file = output_file or f"arvos_stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mcap"
        self.writer: Optional[Writer] = None
        self.mcap_file: Optional[Path] = None
        self.schemas: dict = {}
        self.channels: dict = {}
        self._server_task: Optional[asyncio.Task] = None
        self._server = None  # Store websockets server instance
    
    async def start(self):
        """Start the MCAP stream server"""
        if not MCAP_AVAILABLE:
            print("⚠️  mcap library not found. Install it with: pip install mcap")
            print("   Falling back to basic WebSocket server...")
            await self._start_basic_server()
            return
        
        # Create MCAP file
        self.mcap_file = Path(self.output_file)
        self.writer = Writer(open(self.mcap_file, "wb"))
        self.writer.start()
        
        # Define schemas and channels
        await self._setup_mcap_channels()
        
        # Start WebSocket server
        import websockets
        
        self.running = True
        self.print_connection_info()
        print(f"💾 Writing to MCAP file: {self.mcap_file}")
        print("✅ MCAP stream server started. Waiting for connections...")
        print("Press Ctrl+C to stop.\n")
        
        # Handler for non-WebSocket HTTP requests
        async def process_request(connection, request):
            """Handle non-WebSocket HTTP requests gracefully"""
            # Check if this is a WebSocket upgrade request
            if request.method != "GET" or request.headers.get("Upgrade", "").lower() != "websocket":
                return websockets.http.Response(
                    status=400,
                    headers={"Content-Type": "text/plain"},
                    body=b"This endpoint only accepts WebSocket connections.\n"
                )
            return None  # Let websockets handle WebSocket upgrade requests
        
        # Create a custom logger that suppresses handshake errors
        class SuppressingLogger:
            """Logger that suppresses expected handshake errors"""
            def __init__(self):
                self._logger = logging.getLogger("websockets.suppressed")
                self._logger.setLevel(logging.CRITICAL)
            
            def error(self, msg, *args, **kwargs):
                msg_str = str(msg) % args if args else str(msg)
                if not any(phrase in msg_str for phrase in [
                    "unsupported HTTP method",
                    "did not receive a valid HTTP request", 
                    "opening handshake failed"
                ]):
                    self._logger.error(msg, *args, **kwargs)
            
            def warning(self, msg, *args, **kwargs):
                msg_str = str(msg) % args if args else str(msg)
                if not any(phrase in msg_str for phrase in [
                    "unsupported HTTP method",
                    "did not receive a valid HTTP request",
                    "opening handshake failed"
                ]):
                    self._logger.warning(msg, *args, **kwargs)
            
            def info(self, msg, *args, **kwargs):
                pass  # Suppress info messages
            
            def debug(self, msg, *args, **kwargs):
                pass  # Suppress debug messages
        
        # Wrapper to catch and suppress handshake errors for non-WebSocket requests
        async def handle_client_wrapper(websocket, path):
            """Wrapper to handle connection errors gracefully"""
            try:
                await self._handle_client(websocket, path)
            except (websockets.exceptions.InvalidMessage, ValueError) as e:
                # Suppress errors from non-WebSocket HTTP requests (POST, etc.)
                if "unsupported HTTP method" in str(e) or "did not receive a valid HTTP request" in str(e):
                    # Silently ignore - these are expected for non-WebSocket requests
                    pass
                else:
                    raise
        
        # Use websockets.serve properly - it's an async context manager
        async with websockets.serve(
            handle_client_wrapper, 
            self.host, 
            self.port,
            process_request=process_request,
            logger=SuppressingLogger()
        ) as server:
            self._server = server  # Store for cleanup
            try:
                await asyncio.Future()
            except asyncio.CancelledError:
                pass
    
    async def _start_basic_server(self):
        """Fallback basic WebSocket server if MCAP not available"""
        import websockets
        
        async def handle_client(websocket, path):
            client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            await self._invoke_callback(self.on_connect, client_id)
            self.connected_clients += 1
            
            try:
                async for message in websocket:
                    if isinstance(message, str):
                        await self._parser._handle_json_message(message)
                    else:
                        await self._parser._handle_binary_message(message)
            finally:
                await self._invoke_callback(self.on_disconnect, client_id)
                self.connected_clients -= 1
        
        self.running = True
        self.print_connection_info()
        print("✅ Basic WebSocket server started (MCAP not available)")
        print("Press Ctrl+C to stop.\n")
        
        # Handler for non-WebSocket HTTP requests
        async def process_request(connection, request):
            """Handle non-WebSocket HTTP requests gracefully"""
            # Check if this is a WebSocket upgrade request
            if request.method != "GET" or request.headers.get("Upgrade", "").lower() != "websocket":
                return websockets.http.Response(
                    status=400,
                    headers={"Content-Type": "text/plain"},
                    body=b"This endpoint only accepts WebSocket connections.\n"
                )
            return None  # Let websockets handle WebSocket upgrade requests
        
        # Create a custom logger that suppresses handshake errors
        class SuppressingLogger:
            """Logger that suppresses expected handshake errors"""
            def __init__(self):
                self._logger = logging.getLogger("websockets.suppressed")
                self._logger.setLevel(logging.CRITICAL)
            
            def error(self, msg, *args, **kwargs):
                msg_str = str(msg) % args if args else str(msg)
                if not any(phrase in msg_str for phrase in [
                    "unsupported HTTP method",
                    "did not receive a valid HTTP request", 
                    "opening handshake failed"
                ]):
                    self._logger.error(msg, *args, **kwargs)
            
            def warning(self, msg, *args, **kwargs):
                msg_str = str(msg) % args if args else str(msg)
                if not any(phrase in msg_str for phrase in [
                    "unsupported HTTP method",
                    "did not receive a valid HTTP request",
                    "opening handshake failed"
                ]):
                    self._logger.warning(msg, *args, **kwargs)
            
            def info(self, msg, *args, **kwargs):
                pass  # Suppress info messages
            
            def debug(self, msg, *args, **kwargs):
                pass  # Suppress debug messages
        
        # Wrapper to catch and suppress handshake errors for non-WebSocket requests
        async def handle_client_wrapper(websocket, path):
            """Wrapper to handle connection errors gracefully"""
            try:
                await handle_client(websocket, path)
            except (websockets.exceptions.InvalidMessage, ValueError) as e:
                # Suppress errors from non-WebSocket HTTP requests (POST, etc.)
                if "unsupported HTTP method" in str(e) or "did not receive a valid HTTP request" in str(e):
                    # Silently ignore - these are expected for non-WebSocket requests
                    pass
                else:
                    raise
        
        # Use websockets.serve properly - it's an async context manager
        async with websockets.serve(
            handle_client_wrapper, 
            self.host, 
            self.port,
            process_request=process_request,
            logger=SuppressingLogger()
        ) as server:
            self._server = server  # Store for cleanup
            try:
                await asyncio.Future()
            except asyncio.CancelledError:
                pass
    
    async def _setup_mcap_channels(self):
        """Setup MCAP schemas and channels"""
        # IMU schema
        imu_schema_data = json.dumps({
            "type": "object",
            "properties": {
                "angularVelocity": {"type": "array", "items": {"type": "number"}},
                "linearAcceleration": {"type": "array", "items": {"type": "number"}},
                "timestampNs": {"type": "integer"}
            }
        }).encode()
        self.schemas["imu"] = self.writer.register_schema(
            name="IMUData",
            encoding="json",
            data=imu_schema_data
        )
        self.channels["imu"] = self.writer.register_channel(
            topic="/arvos/imu",
            message_encoding="json",
            schema_id=self.schemas["imu"],
            metadata={}
        )
        
        # GPS schema
        gps_schema_data = json.dumps({
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "altitude": {"type": "number"},
                "horizontalAccuracy": {"type": "number"},
                "verticalAccuracy": {"type": "number"},
                "timestampNs": {"type": "integer"}
            }
        }).encode()
        self.schemas["gps"] = self.writer.register_schema(
            name="GPSData",
            encoding="json",
            data=gps_schema_data
        )
        self.channels["gps"] = self.writer.register_channel(
            topic="/arvos/gps",
            message_encoding="json",
            schema_id=self.schemas["gps"],
            metadata={}
        )
        
        # Pose schema
        pose_schema_data = json.dumps({
            "type": "object",
            "properties": {
                "position": {"type": "array", "items": {"type": "number"}},
                "rotation": {"type": "array", "items": {"type": "number"}},
                "trackingState": {"type": "string"},
                "timestampNs": {"type": "integer"}
            }
        }).encode()
        self.schemas["pose"] = self.writer.register_schema(
            name="PoseData",
            encoding="json",
            data=pose_schema_data
        )
        self.channels["pose"] = self.writer.register_channel(
            topic="/arvos/pose",
            message_encoding="json",
            schema_id=self.schemas["pose"],
            metadata={}
        )
    
    async def _handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        await self._invoke_callback(self.on_connect, client_id)
        self.connected_clients += 1
        
        try:
            async for message in websocket:
                try:
                    if isinstance(message, str):
                        # JSON message
                        data = json.loads(message)
                        self.messages_received += 1
                        self.bytes_received += len(message.encode())
                        
                        # Write to MCAP if available
                        if self.writer:
                            msg_type = data.get("sensorType") or data.get("type", "").lower()
                            timestamp_ns = data.get("timestampNs", int(time.time_ns()))
                            
                            if msg_type == "imu" and "imu" in self.channels:
                                self.writer.add_message(
                                    channel_id=self.channels["imu"],
                                    log_time=timestamp_ns,
                                    data=message.encode(),
                                    publish_time=timestamp_ns
                                )
                            elif msg_type == "gps" and "gps" in self.channels:
                                self.writer.add_message(
                                    channel_id=self.channels["gps"],
                                    log_time=timestamp_ns,
                                    data=message.encode(),
                                    publish_time=timestamp_ns
                                )
                            elif msg_type == "pose" and "pose" in self.channels:
                                self.writer.add_message(
                                    channel_id=self.channels["pose"],
                                    log_time=timestamp_ns,
                                    data=message.encode(),
                                    publish_time=timestamp_ns
                                )
                        
                        # Dispatch via parser
                        await self._parser._handle_json_message(message)
                    else:
                        # Binary data
                        self.messages_received += 1
                        self.bytes_received += len(message)
                        await self._parser._handle_binary_message(message)
                except json.JSONDecodeError:
                    # If message was bytes but we tried to parse as JSON
                    if isinstance(message, bytes):
                        self.messages_received += 1
                        self.bytes_received += len(message)
                        await self._parser._handle_binary_message(message)
        finally:
            await self._invoke_callback(self.on_disconnect, client_id)
            self.connected_clients -= 1
    
    async def stop(self):
        """Stop the MCAP stream server"""
        self.running = False
        
        # Close websockets server if it exists
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        
        if self.writer:
            self.writer.finish()
            if self.mcap_file and self.mcap_file.exists():
                size_kb = self.mcap_file.stat().st_size / 1024
                print(f"\n✅ MCAP file saved: {self.mcap_file}")
                print(f"   File size: {size_kb:.1f} KB")
                print(f"   Messages: {self.messages_received}")
                print(f"💡 Open this file in Foxglove Studio to visualize!")
        
        print("MCAP stream server stopped")
    
    def get_connection_url(self) -> str:
        """Get connection URL"""
        ip = self.get_local_ip()
        return f"ws://{ip}:{self.port}"
    
    def get_protocol_name(self) -> str:
        """Get protocol name"""
        return "MCAP Stream"

