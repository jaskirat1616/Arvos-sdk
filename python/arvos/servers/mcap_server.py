"""
MCAP Stream server for receiving sensor data from ARVOS iOS app
"""

import asyncio
import json
import websockets
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from mcap.writer import Writer
    from mcap.mcap0 import Schema, Channel
    MCAP_AVAILABLE = True
except ImportError:
    MCAP_AVAILABLE = False
    Writer = None
    Schema = None
    Channel = None

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
        
        # Use websockets.serve properly - it's an async context manager
        async with websockets.serve(self._handle_client, self.host, self.port) as server:
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
        
        # Use websockets.serve properly - it's an async context manager
        async with websockets.serve(handle_client, self.host, self.port) as server:
            self._server = server  # Store for cleanup
            try:
                await asyncio.Future()
            except asyncio.CancelledError:
                pass
    
    async def _setup_mcap_channels(self):
        """Setup MCAP schemas and channels"""
        # IMU schema
        imu_schema = Schema(
            name="IMUData",
            encoding="json",
            data=json.dumps({
                "type": "object",
                "properties": {
                    "angularVelocity": {"type": "array", "items": {"type": "number"}},
                    "linearAcceleration": {"type": "array", "items": {"type": "number"}},
                    "timestampNs": {"type": "integer"}
                }
            }).encode()
        )
        self.schemas["imu"] = self.writer.add_schema(imu_schema)
        self.channels["imu"] = self.writer.add_channel(
            Channel(topic="/arvos/imu", message_encoding="json", 
                   metadata={}, schema_id=self.schemas["imu"])
        )
        
        # Add other schemas (GPS, Pose, Camera, Depth) similarly
        # ... (simplified for brevity)
    
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
                        if self.writer and "imu" in self.channels:
                            msg_type = data.get("sensorType") or data.get("type", "").lower()
                            if msg_type == "imu":
                                self.writer.add_message(
                                    channel_id=self.channels["imu"],
                                    log_time=0,
                                    data=message.encode(),
                                    publish_time=0
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

