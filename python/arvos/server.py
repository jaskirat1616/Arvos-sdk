"""
Arvos WebSocket server for receiving connections from iPhone app
"""

import asyncio
import websockets
import json
import qrcode
from typing import Set, Optional, Callable
from datetime import datetime
import socket


class ArvosServer:
    """
    WebSocket server that accepts connections from Arvos iPhone app.

    Example:
        >>> server = ArvosServer(port=9090)
        >>> server.print_qr_code()  # Display QR code for iPhone to scan
        >>>
        >>> @server.on_connect
        ... async def handle_connect(client_id: str):
        ...     print(f"Client connected: {client_id}")
        >>>
        >>> await server.start()
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 9090):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()

        # Callbacks - users can assign these
        self.on_connect: Optional[Callable[[str], None]] = None
        self.on_disconnect: Optional[Callable[[str], None]] = None
        self.on_message: Optional[Callable[[str, any], None]] = None

        # Message handlers (same as ArvosClient)
        self.on_handshake = None
        self.on_imu = None
        self.on_gps = None
        self.on_pose = None
        self.on_camera = None
        self.on_depth = None
        self.on_status = None
        self.on_error = None

    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Create a socket to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def get_websocket_url(self) -> str:
        """Get WebSocket URL for connection"""
        ip = self.get_local_ip()
        return f"ws://{ip}:{self.port}"

    def print_qr_code(self):
        """Print QR code to terminal for iPhone to scan"""
        url = self.get_websocket_url()
        qr = qrcode.QRCode()
        qr.add_data(url)
        qr.make()

        print("\n" + "="*50)
        print("ARVOS SERVER - Scan this QR code with your iPhone:")
        print("="*50)
        qr.print_ascii()
        print("="*50)
        print(f"Or manually enter: {url}")
        print("="*50 + "\n")

    async def start(self):
        """Start the WebSocket server"""
        print(f"Starting Arvos server on {self.host}:{self.port}")
        self.print_qr_code()

        async with websockets.serve(self._handle_client, self.host, self.port):
            print(f"Server listening...")
            await asyncio.Future()  # Run forever

    async def _handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle new client connection"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.clients.add(websocket)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Client connected: {client_id}")

        if self.on_connect:
            await self.on_connect(client_id)

        try:
            async for message in websocket:
                if self.on_message:
                    await self.on_message(client_id, message)

                # Delegate to specific handlers
                await self._delegate_message(message)

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Client disconnected: {client_id}")

            if self.on_disconnect:
                await self.on_disconnect(client_id)

    async def _delegate_message(self, message):
        """Delegate message to appropriate handler"""
        # Import client handlers to reuse parsing logic
        from .client import ArvosClient

        # Create temporary client instance just for parsing
        temp_client = ArvosClient()

        # Copy handlers from server
        temp_client.on_handshake = self.on_handshake
        temp_client.on_imu = self.on_imu
        temp_client.on_gps = self.on_gps
        temp_client.on_pose = self.on_pose
        temp_client.on_camera = self.on_camera
        temp_client.on_depth = self.on_depth
        temp_client.on_status = self.on_status
        temp_client.on_error = self.on_error

        # Handle message using client's parsing logic
        await temp_client._handle_message(message)

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )

    async def send_to_client(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Send message to specific client"""
        try:
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            pass

    def get_client_count(self) -> int:
        """Get number of connected clients"""
        return len(self.clients)
