"""
MCAP HTTP Stream server for receiving sensor data from ARVOS iOS app via HTTP POST
This server receives data via HTTP POST endpoints (not WebSocket) and writes to MCAP files.
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional
from aiohttp import web

try:
    from mcap.writer import Writer
    MCAP_AVAILABLE = True
except ImportError:
    MCAP_AVAILABLE = False
    Writer = None

from .base_server import BaseArvosServer


class MCAPHTTPServer(BaseArvosServer):
    """MCAP HTTP Server - receives data via HTTP POST and writes to MCAP file"""

    def __init__(self, host: str = "0.0.0.0", port: int = 17500,
                 output_file: Optional[str] = None):
        super().__init__(host, port)
        self.output_file = output_file or f"arvos_stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mcap"
        self.writer: Optional[Writer] = None
        self.mcap_file: Optional[Path] = None
        self.schemas: dict = {}
        self.channels: dict = {}
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None

    async def start(self):
        """Start the MCAP HTTP server"""
        if not MCAP_AVAILABLE:
            print("⚠️  mcap library not found. Install it with: pip install mcap")
            print("   Server will still accept requests but won't write MCAP files.")
        else:
            # Create MCAP file
            self.mcap_file = Path(self.output_file)
            self.writer = Writer(open(self.mcap_file, "wb"))
            self.writer.start()

            # Define schemas and channels
            await self._setup_mcap_channels()
            print(f"💾 Writing to MCAP file: {self.mcap_file}")

        # Setup routes
        self.app.router.add_post('/api/mcap/telemetry', self.handle_telemetry)
        self.app.router.add_post('/api/mcap/binary', self.handle_binary)
        self.app.router.add_get('/api/mcap/health', self.handle_health)

        # Start server
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()

        self.running = True
        self.print_connection_info()
        print("✅ MCAP HTTP server started. Waiting for POST requests...")
        print("   Endpoints:")
        print(f"   - POST http://{self.get_local_ip()}:{self.port}/api/mcap/telemetry (JSON)")
        print(f"   - POST http://{self.get_local_ip()}:{self.port}/api/mcap/binary (Binary)")
        print(f"   - GET  http://{self.get_local_ip()}:{self.port}/api/mcap/health (Health check)")
        print("Press Ctrl+C to stop.\n")

        # Keep running
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            pass

    async def handle_health(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "ok", "protocol": "MCAP HTTP"})

    async def handle_telemetry(self, request):
        """Handle JSON telemetry data (IMU, GPS, Pose)"""
        try:
            data = await request.json()
            self.messages_received += 1

            # Write to MCAP if available
            if self.writer:
                msg_type = data.get("sensorType") or data.get("type", "").lower()
                timestamp_ns = data.get("timestampNs", int(time.time_ns()))

                json_data = json.dumps(data).encode()

                if msg_type == "imu" and "imu" in self.channels:
                    self.writer.add_message(
                        channel_id=self.channels["imu"],
                        log_time=timestamp_ns,
                        data=json_data,
                        publish_time=timestamp_ns
                    )
                elif msg_type == "gps" and "gps" in self.channels:
                    self.writer.add_message(
                        channel_id=self.channels["gps"],
                        log_time=timestamp_ns,
                        data=json_data,
                        publish_time=timestamp_ns
                    )
                elif msg_type == "pose" and "pose" in self.channels:
                    self.writer.add_message(
                        channel_id=self.channels["pose"],
                        log_time=timestamp_ns,
                        data=json_data,
                        publish_time=timestamp_ns
                    )

            # Parse and dispatch via callbacks
            await self._parser._handle_json_message(json.dumps(data))

            return web.Response(status=200)
        except Exception as e:
            print(f"❌ Error handling telemetry: {e}")
            return web.Response(status=500, text=str(e))

    async def handle_binary(self, request):
        """Handle binary data (camera frames, depth point clouds)"""
        try:
            data = await request.read()
            self.messages_received += 1
            self.bytes_received += len(data)

            # Parse binary message
            await self._parser._handle_binary_message(data)

            # Write to MCAP if available
            if self.writer and "binary" in self.channels:
                timestamp_ns = int(time.time_ns())
                self.writer.add_message(
                    channel_id=self.channels["binary"],
                    log_time=timestamp_ns,
                    data=data,
                    publish_time=timestamp_ns
                )

            return web.Response(status=200)
        except Exception as e:
            print(f"❌ Error handling binary data: {e}")
            return web.Response(status=500, text=str(e))

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

        # Binary data schema (for camera/depth)
        binary_schema_data = json.dumps({
            "type": "object",
            "properties": {
                "dataType": {"type": "string"},
                "size": {"type": "integer"}
            }
        }).encode()
        self.schemas["binary"] = self.writer.register_schema(
            name="BinaryData",
            encoding="json",
            data=binary_schema_data
        )
        self.channels["binary"] = self.writer.register_channel(
            topic="/arvos/binary",
            message_encoding="application/octet-stream",
            schema_id=self.schemas["binary"],
            metadata={}
        )

    async def stop(self):
        """Stop the MCAP HTTP server"""
        self.running = False

        # Close aiohttp server
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

        if self.writer:
            self.writer.finish()
            if self.mcap_file and self.mcap_file.exists():
                size_kb = self.mcap_file.stat().st_size / 1024
                print(f"\n✅ MCAP file saved: {self.mcap_file}")
                print(f"   File size: {size_kb:.1f} KB")
                print(f"   Messages: {self.messages_received}")
                print(f"💡 Open this file in Foxglove Studio to visualize!")

        print("MCAP HTTP server stopped")

    def get_connection_url(self) -> str:
        """Get connection URL"""
        ip = self.get_local_ip()
        return f"http://{ip}:{self.port}"

    def get_protocol_name(self) -> str:
        """Get protocol name"""
        return "MCAP HTTP Stream"
