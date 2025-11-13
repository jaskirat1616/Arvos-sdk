"""
QUIC/HTTP3 server for receiving sensor data from ARVOS iOS app
"""

import asyncio
import json
import ssl
from pathlib import Path
from typing import Optional, Tuple

try:
    from aioquic.asyncio.server import QuicConnectionProtocol, serve
    from aioquic.quic.configuration import QuicConfiguration
    from aioquic.h3.connection import H3Connection
    from aioquic.h3.events import DataReceived, HeadersReceived
    AIOQUIC_AVAILABLE = True
except ImportError:
    AIOQUIC_AVAILABLE = False
    QuicConnectionProtocol = object
    serve = None
    QuicConfiguration = object
    H3Connection = object
    DataReceived = object
    HeadersReceived = object

from .base_server import BaseArvosServer
from ..client import ArvosClient

# ALPN for HTTP/3
H3_ALPN = ["h3-29", "h3-28", "h3-27", "h3"]


class Http3RequestHandler:
    """Handles HTTP/3 requests"""
    
    def __init__(self, base_server: 'QUICArvosServer'):
        self.base_server = base_server
        self.parser = ArvosClient()
        self._configure_callbacks()
    
    def _configure_callbacks(self):
        """Configure parser callbacks"""
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
    
    async def handle_request(self, h3_connection: H3Connection, stream_id: int, 
                            request_headers: dict, request_data: bytes):
        """Handle HTTP/3 request"""
        method = request_headers.get(b":method", b"GET").decode()
        path = request_headers.get(b":path", b"/").decode()
        
        client_id = f"{self.base_server.host}:{self.base_server.port}"
        await self.base_server._invoke_callback(self.base_server.on_connect, client_id)
        self.base_server.connected_clients += 1
        
        try:
            if path == "/api/health":
                response_headers = [
                    (b":status", b"200"),
                    (b"content-type", b"application/json"),
                ]
                response_data = json.dumps({"status": "ok", "protocol": "QUIC/HTTP3"}).encode()
                h3_connection.send_headers(stream_id, response_headers)
                h3_connection.send_data(stream_id, response_data, end_stream=True)
            
            elif path == "/api/telemetry" and method == "POST":
                self.base_server.messages_received += 1
                self.base_server.bytes_received += len(request_data)
                
                try:
                    message_str = request_data.decode('utf-8')
                    await self.parser._handle_json_message(message_str)
                except Exception as e:
                    if self.base_server.on_error:
                        await self.base_server._invoke_callback(
                            self.base_server.on_error, str(e), None, None
                        )
                
                response_headers = [
                    (b":status", b"200"),
                    (b"content-type", b"application/json"),
                ]
                response_data = json.dumps({"status": "ok"}).encode()
                h3_connection.send_headers(stream_id, response_headers)
                h3_connection.send_data(stream_id, response_data, end_stream=True)
            
            elif path == "/api/binary" and method == "POST":
                self.base_server.messages_received += 1
                self.base_server.bytes_received += len(request_data)
                
                try:
                    await self.parser._handle_binary_message(request_data)
                except Exception as e:
                    if self.base_server.on_error:
                        await self.base_server._invoke_callback(
                            self.base_server.on_error, str(e), None, None
                        )
                
                response_headers = [
                    (b":status", b"200"),
                    (b"content-type", b"application/json"),
                ]
                response_data = json.dumps({"status": "ok"}).encode()
                h3_connection.send_headers(stream_id, response_headers)
                h3_connection.send_data(stream_id, response_data, end_stream=True)
            
            else:
                response_headers = [
                    (b":status", b"404"),
                    (b"content-type", b"text/plain"),
                ]
                response_data = b"Not Found"
                h3_connection.send_headers(stream_id, response_headers)
                h3_connection.send_data(stream_id, response_data, end_stream=True)
        
        finally:
            await self.base_server._invoke_callback(
                self.base_server.on_disconnect, client_id
            )
            self.base_server.connected_clients -= 1


class QUICArvosServer(BaseArvosServer):
    """QUIC/HTTP3 server for receiving sensor data"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 4433,
                 certfile: Optional[str] = None, keyfile: Optional[str] = None):
        super().__init__(host, port)
        self.certfile = certfile or "/tmp/arvos-quic-cert.pem"
        self.keyfile = keyfile or "/tmp/arvos-quic-key.pem"
        self._server_task: Optional[asyncio.Task] = None
        self._handler: Optional[Http3RequestHandler] = None
    
    def _generate_self_signed_cert(self):
        """Generate self-signed certificate for local development"""
        cert_path = Path(self.certfile)
        key_path = Path(self.keyfile)
        
        if not cert_path.exists() or not key_path.exists():
            print("⚠️  Generating self-signed certificates for QUIC/HTTP3...")
            import subprocess
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:2048",
                "-keyout", str(key_path),
                "-out", str(cert_path),
                "-days", "365", "-nodes", "-subj", "/CN=localhost"
            ], check=True, capture_output=True)
            print(f"✅ Generated: {cert_path}")
    
    async def start(self):
        """Start the QUIC/HTTP3 server"""
        if not AIOQUIC_AVAILABLE:
            raise ImportError(
                "aioquic is required for QUIC/HTTP3 support. "
                "Install it with: pip install aioquic"
            )
        
        self._generate_self_signed_cert()
        self._handler = Http3RequestHandler(self)
        
        # Load SSL context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(self.certfile, self.keyfile)
        
        # Configure QUIC
        quic_config = QuicConfiguration(
            alpn_protocols=H3_ALPN,
            is_client=False,
            max_datagram_frame_size=65536
        )
        
        self._server_task = asyncio.create_task(
            serve(self.host, self.port, configuration=quic_config,
                  create_protocol=self._create_protocol)
        )
        
        self.running = True
        self.print_connection_info()
        print("✅ QUIC/HTTP3 server started. Waiting for connections...")
        print("⚠️  Note: iOS requires valid TLS certificates for HTTP/3")
        print("Press Ctrl+C to stop.\n")
        
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            pass
    
    def _create_protocol(self, *args, **kwargs) -> QuicConnectionProtocol:
        """Factory for QUIC connection protocols"""
        # Simplified - full implementation would handle HTTP/3 events properly
        protocol = QuicConnectionProtocol(*args, **kwargs)
        # Add HTTP/3 handling here
        return protocol
    
    async def stop(self):
        """Stop the QUIC/HTTP3 server"""
        self.running = False
        if self._server_task:
            self._server_task.cancel()
            try:
                await self._server_task
            except asyncio.CancelledError:
                pass
        print("QUIC/HTTP3 server stopped")
    
    def get_connection_url(self) -> str:
        """Get connection URL"""
        ip = self.get_local_ip()
        return f"https://{ip}:{self.port}/api"
    
    def get_protocol_name(self) -> str:
        """Get protocol name"""
        return "QUIC/HTTP3"

