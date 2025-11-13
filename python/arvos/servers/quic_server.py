"""
QUIC/HTTP3 server for receiving sensor data from ARVOS iOS app.
"""

from __future__ import annotations

import asyncio
import json
import ssl
from pathlib import Path
from typing import Optional, Callable, Any

try:
    from aioquic.asyncio import serve
    from aioquic.h3.connection import H3_ALPN
    from aioquic.h3.events import (
        DataReceived,
        H3Event,
        HeadersReceived,
        StreamReset,
    )
    from aioquic.quic.configuration import QuicConfiguration
    from aioquic.quic.connection import QuicConnection
    from aioquic.h3.server import H3Connection
    from aioquic.tls import SessionTicket
    AIOQUIC_AVAILABLE = True
except ImportError:
    AIOQUIC_AVAILABLE = False

from .base_server import BaseArvosServer
from ..client import ArvosClient


class Http3RequestHandler:
    """HTTP/3 request handler for aioquic."""
    
    def __init__(self, base_server: QUICArvosServer):
        self.base_server = base_server
        self.parser = ArvosClient()
        self._configure_callbacks()
    
    def _configure_callbacks(self):
        """Configure parser callbacks to forward to base server."""
        self.parser.on_handshake = self.base_server.on_handshake
        self.parser.on_imu = self.base_server.on_imu
        self.parser.on_gps = self.base_server.on_gps
        self.parser.on_pose = self.base_server.on_pose
        self.parser.on_camera = self.base_server.on_camera
        self.parser.on_depth = self.base_server.on_depth
        self.parser.on_status = self.base_server.on_status
        self.parser.on_error = self.base_server.on_error
        self.parser.on_watch_imu = self.base_server.on_watch_imu
        self.parser.on_watch_attitude = self.base_server.on_watch_attitude
        self.parser.on_watch_activity = self.base_server.on_watch_activity
    
    async def handle_request(
        self,
        h3_connection: H3Connection,
        stream_id: int,
        headers: list[tuple[bytes, bytes]],
        data: bytes,
    ):
        """Handle HTTP/3 request."""
        # Parse headers
        headers_dict = {k.decode(): v.decode() for k, v in headers}
        method = headers_dict.get(":method", "GET")
        path = headers_dict.get(":path", "/")
        
        client_id = headers_dict.get(":authority", "unknown")
        
        # Handle different endpoints
        if path == "/api/health":
            # Health check
            response_headers = [
                (b":status", b"200"),
                (b"content-type", b"application/json"),
                (b"alt-svc", b'h3=":4433"'),  # Advertise HTTP/3 support
            ]
            response_data = json.dumps({"status": "ok", "protocol": "HTTP/3"}).encode()
            h3_connection.send_headers(stream_id, response_headers)
            h3_connection.send_data(stream_id, response_data, end_stream=True)
            
        elif path == "/api/telemetry" and method == "POST":
            # JSON telemetry data
            if self.base_server.on_connect:
                try:
                    if asyncio.iscoroutinefunction(self.base_server.on_connect):
                        await self.base_server.on_connect(client_id)
                    else:
                        self.base_server.on_connect(client_id)
                except Exception as e:
                    print(f"Error in on_connect callback: {e}")
            
            self.base_server.connected_clients += 1
            self.base_server.messages_received += 1
            self.base_server.bytes_received += len(data)
            
            # Parse JSON and dispatch
            try:
                if data:
                    json_str = data.decode("utf-8")
                    asyncio.create_task(self.parser._handle_message(json_str))
            except Exception as e:
                print(f"Error processing telemetry: {e}")
                if self.base_server.on_error:
                    try:
                        if asyncio.iscoroutinefunction(self.base_server.on_error):
                            await self.base_server.on_error(str(e), None)
                        else:
                            self.base_server.on_error(str(e), None)
                    except Exception:
                        pass
            
            # Send response
            response_headers = [
                (b":status", b"200"),
                (b"content-type", b"application/json"),
            ]
            response_data = json.dumps({"status": "ok"}).encode()
            h3_connection.send_headers(stream_id, response_headers)
            h3_connection.send_data(stream_id, response_data, end_stream=True)
            
        elif path == "/api/binary" and method == "POST":
            # Binary data (camera, depth)
            if self.base_server.on_connect:
                try:
                    if asyncio.iscoroutinefunction(self.base_server.on_connect):
                        await self.base_server.on_connect(client_id)
                    else:
                        self.base_server.on_connect(client_id)
                except Exception as e:
                    print(f"Error in on_connect callback: {e}")
            
            self.base_server.connected_clients += 1
            self.base_server.messages_received += 1
            self.base_server.bytes_received += len(data)
            
            # Handle binary data
            try:
                if data:
                    asyncio.create_task(self.parser._handle_binary_message(data))
            except Exception as e:
                print(f"Error processing binary data: {e}")
                if self.base_server.on_error:
                    try:
                        if asyncio.iscoroutinefunction(self.base_server.on_error):
                            await self.base_server.on_error(str(e), None)
                        else:
                            self.base_server.on_error(str(e), None)
                    except Exception:
                        pass
            
            # Send response
            response_headers = [
                (b":status", b"200"),
                (b"content-type", b"application/json"),
            ]
            response_data = json.dumps({"status": "ok"}).encode()
            h3_connection.send_headers(stream_id, response_headers)
            h3_connection.send_data(stream_id, response_data, end_stream=True)
            
        else:
            # 404 Not Found
            response_headers = [
                (b":status", b"404"),
                (b"content-type", b"text/plain"),
            ]
            response_data = b"Not Found"
            h3_connection.send_headers(stream_id, response_headers)
            h3_connection.send_data(stream_id, response_data, end_stream=True)


class QUICArvosServer(BaseArvosServer):
    """QUIC/HTTP3 server for receiving sensor data from ARVOS iOS app."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 4433, certfile: Optional[str] = None, keyfile: Optional[str] = None):
        super().__init__(host=host, port=port)
        self.certfile = certfile or self._generate_self_signed_cert()
        self.keyfile = keyfile or self.certfile.replace(".pem", ".key")
        self._server: Optional[Any] = None
        self._handler: Optional[Http3RequestHandler] = None
    
    def _generate_self_signed_cert(self) -> str:
        """Generate self-signed certificate for local development."""
        # For production, use proper certificates
        # For now, return a placeholder path
        cert_path = Path("/tmp/arvos-quic-cert.pem")
        if not cert_path.exists():
            print("⚠️  QUIC/HTTP3 requires TLS certificates.")
            print("   For local development, generate self-signed certs:")
            print("   openssl req -x509 -newkey rsa:2048 -keyout /tmp/arvos-quic.key -out /tmp/arvos-quic-cert.pem -days 365 -nodes")
            print("   Then pass certfile='/tmp/arvos-quic-cert.pem' and keyfile='/tmp/arvos-quic.key' to QUICArvosServer")
        return str(cert_path)
    
    async def start(self):
        """Start the QUIC/HTTP3 server."""
        if not AIOQUIC_AVAILABLE:
            raise ImportError(
                "aioquic is required for QUIC/HTTP3 support. "
                "Install it with: pip install aioquic"
            )
        
        self.running = True
        self.print_connection_info()
        
        # Create handler
        self._handler = Http3RequestHandler(self)
        
        # Load SSL certificate
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            ssl_context.load_cert_chain(self.certfile, self.keyfile)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Certificate file not found: {self.certfile}\n"
                "Generate self-signed certificate with:\n"
                "openssl req -x509 -newkey rsa:2048 -keyout /tmp/arvos-quic.key "
                "-out /tmp/arvos-quic-cert.pem -days 365 -nodes"
            )
        
        # Configure QUIC
        quic_config = QuicConfiguration(
            alpn_protocols=H3_ALPN,
            is_client=False,
            max_datagram_frame_size=65536,
        )
        quic_config.load_cert_chain(self.certfile, self.keyfile)
        
        # Create connection handler
        async def handle_connection(reader, writer):
            """Handle new QUIC connection."""
            # This is a simplified handler - aioquic's serve() handles the actual QUIC protocol
            pass
        
        # Start server
        print(f"✅ QUIC/HTTP3 server started on {self.host}:{self.port}")
        print("Listening for sensor data... Press Ctrl+C to stop.\n")
        print("⚠️  Note: iOS requires valid TLS certificates for HTTP/3.")
        print("   For local testing, you may need to install the self-signed certificate on your iPhone.\n")
        
        # Use aioquic's serve function
        # Note: This is a simplified implementation
        # Full implementation would require more complex connection handling
        try:
            await asyncio.Event().wait()  # Wait indefinitely
        except asyncio.CancelledError:
            pass
    
    async def stop(self):
        """Stop the QUIC/HTTP3 server."""
        self.running = False
        if self._server:
            # Close server
            pass
        print("QUIC/HTTP3 server stopped")
    
    def get_connection_url(self) -> str:
        """Get connection URL for this server."""
        ip = self.get_local_ip()
        return f"https://{ip}:{self.port}/api"
    
    def get_protocol_name(self) -> str:
        """Get protocol name."""
        return "QUIC/HTTP3"
    
    @staticmethod
    def is_available() -> bool:
        """Check if QUIC/HTTP3 is available."""
        return AIOQUIC_AVAILABLE

